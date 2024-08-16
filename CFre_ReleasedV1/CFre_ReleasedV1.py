#-*- coding: UTF-8 -*- 
from abaqus import *
from abaqusConstants import *
from odbAccess import *
from caeModules import *
from driverUtils import executeOnCaeStartup
import xlwt
import xlrd
import random
import numpy as np
import operator
import visualization
import re
import time
import os
import Tkinter as tk
from abaqus import getInput,getInputs
import sys


wkpath = os.path.abspath('.') + '/'  # 工作目录
# os.chdir(wkpath)
forpath = os.path.dirname(os.path.abspath(__file__))  # 子程序文件及插件程序位置

executeOnCaeStartup()  # 启动CAE
session.viewports['Viewport: 1'].partDisplay.geometryOptions.setValues(referenceRepresentation=ON)

#### 功能函数 ####
# 找出最大值所在step和frame，返回该frame的fliedoutput[].values，积分点数值
def findMaxElem(odb,inst,typ):
    # 最大值的单元标签
    maxValue = None
    step = odb.steps.values()[-1]
    frame = step.frames[1]
    damage = frame.fieldOutputs[typ]
    for damageValue in damage.values:
        if (not maxValue or damageValue.data > maxValue.data):
                maxValue = damageValue
    print typ, 'is:', maxValue.data, ',element Label is:', maxValue.elementLabel

    # 获得最后一个载荷步第一个frame的场输出fld
    fieldOuts = odb.steps[step.name].frames[frame.frameId].fieldOutputs[typ]
    f = fieldOuts.getSubset(region=inst, position=CENTROID).values
    fld=np.zeros(len(f), dtype=np.float_)
    for i in range(len(f)):
        fld[i] = f[i].data
    return fld

def pointData(myodb, typ, assem_name, value_point):
    xy=session.xyDataListFromField(odb=myodb, outputPosition=NODAL, variable=((
        typ, INTEGRATION_POINT), ), nodeLabels=((assem_name, tuple(value_point)), ))
    value = []
    for j in range(len(value_point)):
        x0 = session.xyDataObjects[typ+' (Avg: 75%) PI: '+assem_name+' N: '+value_point[j]]
        for i in range(len(x0)-1):
            if x0[i][1] != 0 and x0[i+1][1] == 0:
                value.append(x0[i][1])
                break
            if i == len(x0)-2:
                value.append(x0[i+1][1])
        del session.xyDataObjects[typ+' (Avg: 75%) PI: '+assem_name+' N: '+value_point[j]]
    print typ, 'for point', value_point, 'is:', value
    return value

# 用户输入材料属性
def properties():
    window = tk.Tk()
    window.title('User Defined Material')
    window.geometry('450x280')
    font1 = ('Arial', 10)
    # density,conductivity,expansion
    x1 = 10
    x2 = 90
    tk.Label(window, text='General', font=('Arial', 12)).place(x=30, y=10)
    tk.Label(window, text='density:', font=font1).place(x=x1, y=50)
    xg1 = tk.DoubleVar()
    entry1 = tk.Entry(window, textvariable=xg1, width=8)
    entry1.place(x=x2, y=50)
    tk.Label(window, text='conductivity:', font=font1).place(x=x1, y=120)
    xg2 = tk.DoubleVar()
    entry2 = tk.Entry(window, textvariable=xg2, width=8)
    entry2.place(x=x2, y=120)
    tk.Label(window, text='expansion:', font=font1).place(x=x1, y=190)
    xg3 = tk.DoubleVar()
    entry3 = tk.Entry(window, textvariable=xg3, width=8)
    entry3.place(x=x2, y=190)
    # fai,n1,wfcrit,A,n,m
    x1 = 170
    x2 = 220
    tk.Label(window, text='Creep', font=('Arial', 12)).place(x=190, y=10)
    tk.Label(window, text='fai:', font=font1).place(x=x1, y=40)
    xc1 = tk.DoubleVar()
    entry1 = tk.Entry(window, textvariable=xc1, width=8)
    entry1.place(x=x2, y=40)
    tk.Label(window, text='n1:', font=font1).place(x=x1, y=70)
    xc2 = tk.DoubleVar()
    entry2 = tk.Entry(window, textvariable=xc2, width=8)
    entry2.place(x=x2, y=70)
    tk.Label(window, text='wfcrit:', font=font1).place(x=x1, y=100)
    xc3 = tk.DoubleVar()
    entry3 = tk.Entry(window, textvariable=xc3, width=8)
    entry3.place(x=x2, y=100)
    tk.Label(window, text='A:', font=font1).place(x=x1, y=130)
    xc4 = tk.DoubleVar()
    entry4 = tk.Entry(window, textvariable=xc4, width=8)
    entry4.place(x=x2, y=130)
    tk.Label(window, text='n:', font=font1).place(x=x1, y=160)
    xc5 = tk.DoubleVar()
    entry5 = tk.Entry(window, textvariable=xc5, width=8)
    entry5.place(x=x2, y=160)
    tk.Label(window, text='m:', font=font1).place(x=x1, y=190)
    xc6 = tk.DoubleVar()
    entry6 = tk.Entry(window, textvariable=xc6, width=8)
    entry6.place(x=x2, y=190)
    # E,u,Xsigma,Xepsilon,k,n
    x1 = 310
    x2 = 370
    tk.Label(window, text='Fatigue', font=('Arial', 12)).place(x=350, y=10)
    tk.Label(window, text='E:', font=font1).place(x=x1, y=40)
    xf1 = tk.DoubleVar()
    entry1 = tk.Entry(window, textvariable=xf1, width=8)
    entry1.place(x=x2, y=40)
    tk.Label(window, text='u:', font=font1).place(x=x1, y=70)
    xf2 = tk.DoubleVar()
    entry2 = tk.Entry(window, textvariable=xf2, width=8)
    entry2.place(x=x2, y=70)
    tk.Label(window, text='sigmaf:', font=font1).place(x=x1, y=100)
    xf3 = tk.DoubleVar()
    entry3 = tk.Entry(window, textvariable=xf3, width=8)
    entry3.place(x=x2, y=100)
    tk.Label(window, text='epsilonf:', font=font1).place(x=x1, y=130)
    xf4 = tk.DoubleVar()
    entry4 = tk.Entry(window, textvariable=xf4, width=8)
    entry4.place(x=x2, y=130)
    tk.Label(window, text='K\':', font=font1).place(x=x1, y=160)
    xf5 = tk.DoubleVar()
    entry5 = tk.Entry(window, textvariable=xf5, width=8)
    entry5.place(x=x2, y=160)
    tk.Label(window, text='n\':', font=font1).place(x=x1, y=190)
    xf6 = tk.DoubleVar()
    entry6 = tk.Entry(window, textvariable=xf6, width=8)
    entry6.place(x=x2, y=190)
    Xg = []
    Xc = []
    Xf = []
    def OK():
        Xg.append([xg1.get(), xg2.get(), xg3.get()])
        Xc.append([xc1.get(), xc2.get(), xc3.get(), xc4.get(), xc5.get(), xc6.get()])
        Xf.append([xf1.get(), xf2.get(), xf3.get(), xf4.get(), xf5.get(), xf6.get()])
        window.destroy()
    btn1 = tk.Button(window, text='OK', font=('Arial', 10), command=OK)
    btn1.place(x=150, y=240)
    btn2 = tk.Button(window, text='Cancel', font=('Arial', 10), command=window.destroy)
    btn2.place(x=250, y=240)
    window.mainloop()
    return Xg, Xc, Xf

# multi condition功能提取字符串中的数值
def range2num(range_str):
    range_list = range_str.split(',')
    start = float(range_list[0])
    stop = float(range_list[1])
    num = float(range_list[2])
    if num == 1:
        cond_list = [start]
    else:
        cond_list = [start+(stop-start)/(num-1)*i for i in range(int(num))]
    return cond_list

# exe版lhs辅助函数
def list2str(x):
    x_str = ''
    for i in range(len(x)):
        x_str = x_str+str(x[i])+','
    return x_str[:-1]
    
# exe版temp_lhs辅助函数
def tuple2str(x):
    x_str = ''
    for i in range(len(x)):
        for j in range(len(x[0])-1):
            x_str = x_str + str(x[i][j]) + ','
    return x_str[:-1]


######## 读取初始参数，离散化抽样 ########
def sampling(temp,Mn,keys,ST, density, conductivity,expansion,E,u,fai,n1,wfcrit,Xsigma,Xepsilon,load,geom,nbA,nbn,nbm, roK,ron,
                values,dpth,val_load,dwell,amp,Ma,D1,C1,D2,C2,D5,C5,C3,C4,C42):
    
    choose = [E,u,density,conductivity,expansion,fai,n1,wfcrit,nbA,nbn,nbm,Xsigma,Xepsilon,roK,ron]
    for i in range(len(choose)):
        choose[i] = int(choose[i])
    X11 = np.zeros((5, ST+1), dtype=np.float_)
    Xg = [0.0]*5

    # 参数温度相关
    u_rnd = np.zeros((1, ST+1), dtype=np.float_)
    E_rnd = np.zeros((1, ST+1), dtype=np.float_)
    ela_rnd = np.zeros((2, ST+1), dtype=np.float_)
    den_rnd = np.zeros((1, ST+1), dtype=np.float_)
    con_rnd = np.zeros((1, ST+1), dtype=np.float_)
    ex_rnd = np.zeros((1, ST+1), dtype=np.float_)
    if temp:
        Matn = mdb.models[Mn].materials.keys(0)[0]
        # 弹性
        if E or u:
            ela_data = mdb.models[Mn].materials[Matn].elastic.table
            if E and not u:
                Eu_data = np.array(ela_data)[:,:2]
            elif not E and u:
                Eu_data = np.array(ela_data)[:,1:]
            else:
                Eu_data = ela_data
            if mdb.models[Mn].materials[Matn].elastic.temperatureDependency == ON:
                os.system('{}/lhs.exe {} {} {} {} {}'.format(forpath, 1, tuple2str(Eu_data), ST,D5,C5))
            else:
                os.system('{}/lhs.exe {} {} {} {} {}'.format(forpath, 1, list2str(Eu_data[0]), ST,D5,C5))
            ela_rnd = np.load("{}/lhs_data.npy".format(wkpath))
        # 密度
        if density:
            den_data = mdb.models[Mn].materials[Matn].density.table
            if mdb.models[Mn].materials[Matn].density.temperatureDependency == ON:
                os.system('{}/lhs.exe {} {} {} {} {}'.format(forpath, 1, tuple2str(den_data), ST,D1,C1))
            else:
                os.system('{}/lhs.exe {} {} {} {} {}'.format(forpath, 1, den_data[0][0], ST,D1,C1))
            den_rnd = np.load("{}/lhs_data.npy".format(wkpath))
        # 热导率
        if conductivity:
            con_data = mdb.models[Mn].materials[Matn].conductivity.table
            if mdb.models[Mn].materials[Matn].conductivity.temperatureDependency == ON:
                os.system('{}/lhs.exe {} {} {} {} {}'.format(forpath, 1, tuple2str(con_data),ST,D1,C1))
            else:
                os.system('{}/lhs.exe {} {} {} {} {}'.format(forpath, 1, con_data[0][0],ST,D1,C1))
            con_rnd = np.load("{}/lhs_data.npy".format(wkpath))
        # 热延性
        if expansion:  
            ex_data = mdb.models[Mn].materials[Matn].expansion.table
            if mdb.models[Mn].materials[Matn].expansion.temperatureDependency == ON:
                os.system('{}/lhs.exe {} {} {} {} {}'.format(forpath, 1, tuple2str(ex_data),ST,D1,C1))
            else:
                os.system('{}/lhs.exe {} {} {} {} {}'.format(forpath, 1, ex_data[0][0],ST,D1,C1))
            ex_rnd = np.load("{}/lhs_data.npy".format(wkpath))
    
    # 自定义参数
    if Ma == 'User Define':
        Xg, Xc, Xf = properties()
    # 从数据库读参数
    else:
        filename= os.path.join(forpath, 'material_database.dat')
        f=file(filename,'r')
        k=1
        while True:
            line=f.readline()
            if len(line)==0:
                break
            data=line.strip().split(',')
            if Ma == data[0]:
                if not temp:
                    Xg = [float(data[i]) for i in range(2,7)]
                Xc = [float(data[i]) for i in range(7,13)]
                Xf = [float(data[i]) for i in range(13,17)]
                sigmay = float(data[17])
            k+=1
        f.close()

    ## LHS抽样 ##
    # Material----------------------------------------------------------------------
    if Xg[0] != 0:
        os.system('{}/lhs.exe {} {} {} {} {} {}'.format(forpath, 0, list2str(Xg), list2str(choose[0:len(Xg)]), ST, D1, C1))
        X11 = np.load("{}/lhs_data.npy".format(wkpath))
    # Creep------------------------------------------------------------------------
    [str1,str2] = str(Xc[3]).split('e')  # A数值太小
    Xc[3] = float(str1)
    os.system('{}/lhs.exe {} {} {} {} {} {}'.format(forpath, 0, list2str(Xc), list2str(choose[len(Xg):len(Xg)+len(Xc)]), ST, D2, C2))
    X22 = np.load("{}/lhs_data.npy".format(wkpath))
    # Fatigue----------------------------------------------------------------------
    os.system('{}/lhs.exe {} {} {} {} {} {}'.format(forpath, 0, list2str(Xf), list2str(choose[len(Xg)+len(Xc):len(Xg)+len(Xc)+len(Xf)]), ST, D5, C5))
    X33 = np.load("{}/lhs_data.npy".format(wkpath))
    # 载荷--------------------------------------------------------------------------
    value_load = np.zeros((1,ST+1), dtype=np.float_)
    dwtime = np.zeros((1,ST+1), dtype=np.float_)
    if load:
        os.system('{}/lhs.exe {} {} {} {} {} {}'.format(forpath, 0, list2str([val_load]), list2str([int(load)]), ST, 'ND', C4))
        value_load = np.load("{}/lhs_data.npy".format(wkpath))
        if dwell == '':
            value_dw = float(0.0)
            C42 = float(1.0)
        else:
            value_dw = float(dwell)
            C42 = float(C42)
        os.system('{}/lhs.exe {} {} {} {} {} {}'.format(forpath, 0, list2str([value_dw]), list2str([value_dw]), ST, 'ND', C42))
        dwtime = np.load("{}/lhs_data.npy".format(wkpath))
    # 几何-------------------------------------------------------------------------
    value_geo = values.split(',')  # 均值列表
    nvalue=len(value_geo)
    geo = np.zeros((nvalue, ST+1), dtype=np.float_)
    dp = np.zeros((1,ST+1), dtype=np.float_)
    key_arr = keys.__str__().split(',')
    nk = len(key_arr)
    if key_arr[-1]==')':
        nk=nk-1
    dimension_label = np.zeros(nk, dtype=np.int_)
    if geom:
        for i in range(nvalue):
            value_geo[i] = float(value_geo[i])  # 转换数据类型
        for i in range(nk):
            res = re.findall(r'\[(.*?)\]', key_arr[i])
            dimension_label[i] = int(res[-1])  # 尺寸序号
        if nk != nvalue:
            raise ValueError('the size of Key must be the same as the size of Value')
        os.system('{}/lhs.exe {} {} {} {} {} {}'.format(forpath, 0, list2str(value_geo), list2str(value_geo), ST, 'ND', C3))
        geo = np.load("{}/lhs_data.npy".format(wkpath))
        if dpth == '':
            value_dp = 0.0
        else:
            value_dp = float(dpth)
        os.system('{}/lhs.exe {} {} {} {} {} {}'.format(forpath, 0, list2str([value_dp]), list2str([value_dp]), ST, 'ND', C3))
        dp = np.load("{}/lhs_data.npy".format(wkpath))
    print 'Sampling done...'
    return choose,u_rnd,E_rnd,ela_rnd,den_rnd,con_rnd,ex_rnd,Xg,Xc,Xf,X11,X22,X33,value_load,dwtime,value_geo,dimension_label,geo,dp,nk

######## 批量有限元计算函数 ########
def FE(temp,nCpus,Mn,Pn,Jn,ST,paraIV,paraV,load,geom,Fn,values,dpth, loadname,direc,dwell,amp,Ma, point,D1,C1,D2,C2,D5,C5,C3,C4,C42,nk,
        choose,u_rnd,E_rnd,ela_rnd,den_rnd,con_rnd,ex_rnd,Xg,Xc,Xf,X11,X22,X33,value_load,dwtime,value_geo,dimension_label,geo,dp):

    E,u,density,conductivity,expansion,fai,n1,wfcrit,nbA,nbn,nbm,Xsigma,Xepsilon,roK,ron = choose
    data1 = np.zeros((ST+1, 2), dtype=np.float_)  # 最大总损伤所在单元蠕变/疲劳损伤数据
    data2 = np.zeros((ST+1, 2), dtype=np.float_)
    data3 = np.zeros((ST+1, 2), dtype=np.float_)
    
    ## 读取评估目标点 ##
    if point != '':
        value_point = point.split(',')  # 均值列表
        creep_value = np.zeros((ST+1, len(value_point)), dtype=np.float_)
        fatigue_value = np.zeros((ST+1, len(value_point)), dtype=np.float_)
        
    ########################   STEP2 载入模型，赋值属性，提交作业重复ST次   ########################
    time_arr = []
    for j in range (ST+1):
        print >> sys.__stdout__, 'Times: ', j
        print 'Times: ', j
        p = mdb.models[Mn].parts[Pn]
        session.viewports['Viewport: 1'].setValues(displayedObject=p)

        # ------------------------------材料赋予-----------------------------------------------
        if temp:  #温度相关
            Matn = mdb.models[Mn].materials.keys(0)[0]
            # 弹性
            if E or u:
                ela_data = mdb.models[Mn].materials[Matn].elastic.table
                table_E = []
                table_u = []
                if E and not u: 
                    for i in range(len(ela_data)):
                        table_E.append(ela_rnd[i, j])
                        table_u.append(ela_data[i][1])
                elif not E and u:
                    for i in range(len(ela_data)):
                        table_E.append(ela_data[i][0])
                        table_u.append(ela_rnd[i, j])
                else:
                    for i in range(len(ela_data)):
                        table_E.append(ela_rnd[2*i, j])
                        table_u.append(ela_rnd[2*i + 1, j])
                
                if mdb.models[Mn].materials[Matn].elastic.temperatureDependency == ON:
                    table_temp_Eu = [t[-1] for t in ela_data]
                    table_Eu = zip(table_E, table_u, table_temp_Eu)
                    mdb.models[Mn].materials[Matn].elastic.setValues(table=tuple(table_Eu))
                else:
                    mdb.models[Mn].materials[Matn].elastic.setValues(table=((table_E[0, j], table_u[0, j]),))
            # 密度
            if density:
                if mdb.models[Mn].materials[Matn].density.temperatureDependency == ON:
                    den_data = mdb.models[Mn].materials[Matn].density.table
                    table_den=[]
                    for i in range(len(den_data)):
                        table_den.append((den_rnd[i,j],den_data[i][1]))
                    mdb.models[Mn].materials[Matn].density.setValues(table=tuple(table_den))
                else:
                    mdb.models[Mn].materials[Matn].density.setValues(table=((den_rnd[0, j], ), ))
            # 热导率
            if conductivity:
                if mdb.models[Mn].materials[Matn].conductivity.temperatureDependency == ON:
                    con_data = mdb.models[Mn].materials[Matn].conductivity.table
                    table_con = []
                    for i in range(len(con_data)):
                        table_con.append((con_rnd[i, j], con_data[i][1]))
                    mdb.models[Mn].materials[Matn].conductivity.setValues(table=tuple(table_con))
                else:
                    mdb.models[Mn].materials[Matn].conductivity.setValues(table=((table_con[0, j], ), ))
            # 热延性
            if expansion:
                if mdb.models[Mn].materials[Matn].expansion.temperatureDependency == ON:
                    ex_data = mdb.models[Mn].materials[Matn].expansion.table
                    table_ex=[]
                    for i in range(len(ex_data)):
                        table_ex.append((ex_rnd[i,j],ex_data[i][1]))
                    mdb.models[Mn].materials[Matn].expansion.setValues(table=tuple(table_ex))
                else:
                    mdb.models[Mn].materials[Matn].expansion.setValues(table=((table_ex[0, j], ), ))
        else:
            if len(mdb.models[Mn].materials) == 0:  # 没有材料，创建材料
                mdb.models[Mn].Material(name=Ma)
                mdb.models[Mn].materials[Ma].Depvar(n=10)
                mdb.models[Mn].materials[Ma].UserOutputVariables(n=100)
                mdb.models[Mn].materials[Ma].Creep(law=USER, table=())

                mdb.models[Mn].materials[Ma].Elastic(table=((X11[0, j], X11[1, j]),))
                mdb.models[Mn].materials[Ma].Density(table=((X11[2, j], ), ))
                mdb.models[Mn].materials[Ma].Conductivity(table=((X11[3, j],),))
                mdb.models[Mn].materials[Ma].Expansion(table=((X11[4,j], ), ))
                table = []
                for strain in range(500):
                    stress = sigmay + X33[2, j] * (strain / 20000.0) ** X33[3, j]
                    table.append((stress, strain/10000.0))
                mdb.models[Mn].materials[Ma].Plastic(dataType=STABILIZED, table=tuple(table))
                
                if p.sectionAssignments==[]:
                    mdb.models[Mn].HomogeneousSolidSection(name='Section-1', material=Ma, thickness=None)
                    c = p.cells
                    region = p.Set(cells=c, name='Set-1')
                    p.SectionAssignment(region=region, sectionName='Section-1', offset=0.0, offsetType=MIDDLE_SURFACE, offsetField='',
                        thicknessAssignment=FROM_SECTION)
            else:  # 已有材料
                Matn = mdb.models[Mn].materials.keys(0)[0]
                if E or u:
                    mdb.models[Mn].materials[Matn].elastic.setValues(table=((X11[0, j], X11[1, j]),))
                if density:
                    mdb.models[Mn].materials[Matn].density.setValues(table=((X11[2, j], ), ))
                if conductivity:
                    mdb.models[Mn].materials[Matn].conductivity.setValues(table=((X11[3, j],),))
                if expansion:
                    mdb.models[Mn].materials[Matn].expansion.setValues(table=((X11[4,j], ), ))
                if roK or ron:
                    table = []
                    for strain in range(500):
                        stress = sigmay + X33[2, j] * (strain / 20000.0) ** X33[3, j]
                        table.append((stress, strain / 10000.0))
                    mdb.models[Mn].materials[Ma].plastic.setValues(table=tuple(table))

        # ------------------------------变载荷----------------------------------------------------
        subroutine = forpath + '/CreepFatigue.for'
        if load:
            if direc == 'CF1':
                mdb.models[Mn].loads[loadname].setValues(cf1=value_load[0,j])
            elif direc == 'CF2':
                mdb.models[Mn].loads[loadname].setValues(cf2=value_load[0,j])
            elif direc == 'CF3':
                mdb.models[Mn].loads[loadname].setValues(cf3=value_load[0,j])
            elif direc == 'U1':
                mdb.models[Mn].boundaryConditions[loadname].setValues(u1=value_load[0,j])
            elif direc == 'U2':
                mdb.models[Mn].boundaryConditions[loadname].setValues(u2=value_load[0,j])
            elif direc == 'U3':
                mdb.models[Mn].boundaryConditions[loadname].setValues(u3=value_load[0,j])
            elif direc == 'UR1':
                mdb.models[Mn].boundaryConditions[loadname].setValues(ur1=value_load[0,j])
            elif direc == 'UR2':
                mdb.models[Mn].boundaryConditions[loadname].setValues(ur2=value_load[0,j])
            elif direc == 'UR3':
                mdb.models[Mn].boundaryConditions[loadname].setValues(ur3=value_load[0,j])
            else:
                mdb.models[Mn].loads[loadname].setValues(magnitude=value_load[0,j])
            
            if dwell != '':
                step_num_all=len(mdb.models[Mn].steps)
                step_num = 0
                for i in range(step_num_all-1):
                    if not mdb.models[Mn].steps['Step-'+str(i+1)].suppressed:
                        step_num += 1
                cycles = step_num/3
                for i in range(step_num):
                    if i%3 == 2:
                        mdb.models[Mn].steps['Step-'+str(i)].setValues(timePeriod=dwtime[0,j], 
                            initialInc=1.0, minInc=1e-05, maxInc=dwtime[0,j], cetol=0.001)
                if amp != '':  # 有载荷谱名称
                    tm=[]
                    gap=dwtime[0,j]+4
                    for i in range(cycles):
                        tm.append(i * gap)
                        tm.append(i * gap + 1)
                        tm.append(i * gap + 1 + dwtime[0,j])
                        tm.append(i * gap + 3 + dwtime[0,j])
                    tm.append(gap * cycles)
                    node = [0.0, 1.0, 1.0, -1.0] * cycles + [0.0]
                    amp_table = zip(tm,node)
                    mdb.models[Mn].amplitudes[amp].setValues(timeSpan=TOTAL, smooth=SOLVER_DEFAULT, data=tuple(amp_table))

        # ------------------------------模型参数写入FOR文件----------------------------------
        Change = [Xsigma, Xepsilon, fai, n1, wfcrit, nbA, nbn, nbm]
        with open(subroutine, "r+") as f:
            infos=f.readlines()
            f.seek(0,0)
            if True in Change:  # 如果都没选就不覆盖
                for line in infos:
                    if "      Xsigma=" in line:
                        if Xsigma:
                            line = '      Xsigma='+str(X33[0,j])+'\n'
                    elif "      Xepsilon=" in line:
                        if Xepsilon:
                            line = '      Xepsilon='+str(X33[1,j])+'\n'
                    elif  "      fai=" in line:
                        if fai:
                            line = '      fai='+str(X22[0,j])+'\n'
                    elif "      temp_n1=" in line:
                        if n1:
                            line = '      temp_n1='+str(X22[1,j])+'\n'
                    elif "      wfcrit=" in line:
                        if wfcrit:
                            line = '      wfcrit='+str(X22[2,j])+'\n'
                    elif "      A=" in line:
                        if nbA:
                            line = '      A='+str(X22[3,j])+'e'+str2+'\n'
                    elif "      XN=" in line:
                        if nbn:
                            line = '      XN='+str(X22[4,j])+'\n'
                    elif "      XM=" in line:
                        if nbm:
                            line = '      XM='+str(X22[5,j])+'\n'
                    if not temp and E:
                        if "      E=" in line:
                            line = '      E='+str(X11[0,j])+'\n'
                    f.write(line)

        # ------------------------------几何重建-------------------------------------------
        if geom:
            p = mdb.models[Mn].parts[Pn]
            s = p.features[Fn].sketch
            mdb.models[Mn].ConstrainedSketch(name='__edit__', objectToCopy=s)
            s2 = mdb.models[Mn].sketches['__edit__']
            g, v, d, c = s2.geometry, s2.vertices, s2.dimensions, s2.constraints
            s2.setPrimaryObject(option=SUPERIMPOSE)
            p.projectReferencesOntoSketch(sketch=s2,upToFeature=p.features[Fn], filter=COPLANAR_EDGES)
            for i in range(nk):
                d[int(dimension_label[i])].setValues(value=geo[i,j], )
            s2.unsetPrimaryObject()
            p.features[Fn].setValues(sketch=s2)
            del mdb.models[Mn].sketches['__edit__']
            if dpth != '':
                p.features[Fn].setValues(depth=dp[0,j])  # 厚度
            p.regenerate()
            p.generateMesh()
            a = mdb.models[Mn].rootAssembly
            a.regenerate()
        print 'Rewriting done...'

        # ------------------------------提交作业---------------------------------------------
        mdb.Job(name=Jn, model=Mn, description='', type=ANALYSIS,
                atTime=None, waitMinutes=0, waitHours=0, queue=None, memory=90,
                memoryUnits=PERCENTAGE, getMemoryFromAnalysis=True,
                explicitPrecision=SINGLE, nodalOutputPrecision=SINGLE, echoPrint=OFF,
                modelPrint=OFF, contactPrint=OFF, historyPrint=OFF,
                userSubroutine=subroutine, scratch='',
                resultsFormat=ODB, multiprocessingMode=DEFAULT, numCpus=nCpus, numDomains=nCpus, numGPUs=0)
        mdb.jobs[Jn].submit() 
        mdb.jobs[Jn].waitForCompletion()


        ############################        STEP3 数据输出            ################################
        odb = session.openOdb(wkpath+Jn+'.odb')  #当前目录下
        assem_name = Pn.upper()+'-1'  #装配体部件名大写

        # 读取输入点的位置
        if point != '':
            session.viewports['Viewport: 1'].setValues(displayedObject=odb)
            session.viewports['Viewport: 1'].makeCurrent()
            creep_value[j, :] = pointData(odb, 'UVARM33', assem_name, value_point)
            fatigue_value[j, :] = pointData(odb, 'UVARM35', assem_name, value_point)
        else:
            # 对这一帧的场输出求最大,得到最大值在数组中的位置,最终得到最大值单元的蠕变和疲劳积分点数据
            inst = odb.rootAssembly.instances[assem_name]
            creep_array=findMaxElem(odb,inst,'UVARM33')
            fatigue_array=findMaxElem(odb,inst,'UVARM35')
            total_array=findMaxElem(odb,inst,'UVARM38')
            creep_label, a_maxvalue = max(enumerate(creep_array), key=operator.itemgetter(1))
            fatigue_label, b_maxvalue = max(enumerate(fatigue_array), key=operator.itemgetter(1))
            total_label, c_maxvalue = max(enumerate(total_array), key=operator.itemgetter(1))
            data1[j, :] = [creep_array[total_label], fatigue_array[total_label]]  # 存放最大总损伤单元的蠕变/疲劳损伤数据
            data2[j, :] = [creep_array[fatigue_label], fatigue_array[fatigue_label]]  # 存放最大疲劳损伤单元的蠕变/疲劳损伤数据
            data3[j, :] = [creep_array[creep_label], fatigue_array[creep_label]]  # 存放最大蠕变损伤单元的蠕变/疲劳损伤数据
        odb.close()

        # 读运行时间
        with open(wkpath+Jn+'.dat', 'r') as f:
            txt = f.readlines()
            key = [k for k in range(0, len(txt))]
            result = {k: v for k, v in zip(key, txt[::-1])}
            info = result[1].rstrip()  # CPU
            info2 = result[0].rstrip()  # WALL
            print info,'for',nCpus,'CPUs\n',info2
            runtime = info.split('=')
            time_arr.append(runtime[1])

    ################################      STEP4 退出循环，数据写入表格，计算可靠度     #########################
    # 耗时文件
    timebook = xlwt.Workbook()
    sheet = timebook.add_sheet('Sheet1')
    for i in range(ST+1):
        sheet.write(i, 0, time_arr[i])
    timebook.save(wkpath+Jn+'time.xls')
    
    # 数据集写入xls，输入随机变量，输出最大损伤单元的蠕变和疲劳
    if dpth == '':
        dpth=0.0
    if not geom:
        value_geo=[float(0.0)]
    Xtt = np.concatenate((X11,X22,X33, value_load,dwtime, geo,dp),axis=0)
    col = 0
    random_cv = ''
    random_distr = ''
    trainbook=xlwt.Workbook()
    sheet=trainbook.add_sheet('Sheet1')
    variables = ['E','u','density','conductivity','expansion','fai','n1','wfcrit','NB-A','NB-n','NB-m','Xsigma','Xepsilon','RO-K','RO-n']
    if not temp:
        for i in range(len(choose)): #  choose = [E,u,density,conductivity,expansion,fai,n1,wfcrit,nbA,nbn,nbm,Xsigma,Xepsilon,roK,ron]
            if choose[i]:
                if i < len(Xg):
                    if D1 == 'CONST':
                        continue
                    random_cv += (str(C1)+',')
                    random_distr += (D1+',')
                elif i >= len(Xg) and i < len(Xg)+len(Xc):
                    if D2 == 'CONST':
                        continue
                    random_cv += (str(C2)+',')
                    random_distr += (D2+',')
                elif i >= len(Xg)+len(Xc):
                    if D5 == 'CONST':
                        continue
                    random_cv += (str(C5)+',')
                    random_distr += (D5+',')
                sheet.write(0, col, variables[i]) #名称
                for j in range(ST+1):
                    sheet.write(j + 1, col, Xtt[i,j])
                col += 1

    else:
        #获取最高温度对应的材料参数值存入表格
        if not E and u:
            gen_last = zip(E_rnd[-1], ela_rnd[-1], den_rnd[-1], con_rnd[-1], ex_rnd[-1])
        elif E and not u:
            gen_last = zip(ela_rnd[-1], u_rnd[-1], den_rnd[-1], con_rnd[-1], ex_rnd[-1])
        else:
            gen_last = zip(ela_rnd[-2], ela_rnd[-1], den_rnd[-1], con_rnd[-1], ex_rnd[-1])
        
        # 材料参数
        if D1 != 'CONST':
            for i in range(5):
                if choose[i]:
                    sheet.write(0, col, variables[i]) #名称
                    for j in range(ST+1):
                        sheet.write(j + 1, col, gen_last[j][i])
                    col += 1
                    random_cv += (str(C1)+',')
                    random_distr += (D1+',')
        # 模型参数
        if D2 != 'CONST' and D5 != 'CONST':
            for i in range(5,len(choose)):
                if choose[i]:
                    if i < len(Xg) + len(Xc):
                        if D2 == 'CONST':
                            continue
                        random_cv += (str(C2) + ',')
                        random_distr += (D2 + ',')
                    elif i >= len(Xg) + len(Xc):
                        if D5 == 'CONST':
                            continue
                        random_cv += (str(C5) + ',')
                        random_distr += (D5 + ',')
                    sheet.write(0, col, variables[i])  # 名称
                    for j in range(ST+1):
                        sheet.write(j + 1, col, Xtt[i, j])
                    col += 1

    if load and paraV:
        sheet.write(0, col, 'load')
        for k in range(ST+1):
            sheet.write(k + 1, col, Xtt[i+1,k])
        col += 1
        random_cv += (str(C4)+',')
        random_distr += (D1+',')
        if dwell != '':
            sheet.write(0, col, 'dwell time')
            for k in range(ST+1):
                sheet.write(k + 1, col, Xtt[i+2,k])
            col += 1
            random_cv += (str(C42)+',')
            random_distr += (D1+',')

    if geom and paraIV:
        for j in range(len(value_geo)):  
            sheet.write(0, col, 'dimension'+str(j)) #名称
            for k in range(ST+1):
                sheet.write(k + 1, col, Xtt[i+3+j,k])
            col += 1
            random_cv += (str(C3)+',')
            random_distr += (D1+',')
        if dpth != 0.0:
            sheet.write(0, col, 'depth') #名称
            for k in range(ST+1):
                sheet.write(k + 1, col, Xtt[-1,k])
            col += 1
            random_cv += (str(C3)+',')
            random_distr += (D1+',')
    
    # 写入损伤
    for i in range(ST+2):
        sheet.write(i, col, '')
    if point != '':
        for j in range(len(value_point)):
            sheet.write(0, col+2*j+1, 'dc-N:'+value_point[j]+' *e3')
            sheet.write(0, col+2*j+2, 'df-N:'+value_point[j]+' *e3')
            for i in range(ST+1):
                sheet.write(i + 1, col+2*j+1, creep_value[i,j]*1000)
                sheet.write(i + 1, col+2*j+2, fatigue_value[i,j]*1000)
    else:
        sheet.write(0, col+1, 'dc *e3')
        sheet.write(0, col+2, 'df *e3')
        if not total_label == fatigue_label:  # fatigue
            sheet.write(0, col+3, 'dc-maxdf')
            sheet.write(0, col+4, 'df-maxdf')
        if total_label != creep_label and total_label != fatigue_label:  # creep
            sheet.write(0, col+5, 'dc-maxdc')
            sheet.write(0, col+6, 'df-maxdc')
        elif total_label != creep_label and total_label == fatigue_label:
            sheet.write(0, col+3, 'dc-maxdc')
            sheet.write(0, col+4, 'df-maxdc')
        for i in range(ST+1):
            sheet.write(i + 1, col+1, data1[i,0]*1000)
            sheet.write(i + 1, col+2, data1[i,1]*1000)
            if not total_label == fatigue_label:  # fatigue
                sheet.write(i + 1, col+3, data2[i,0]*1000)
                sheet.write(i + 1, col+4, data2[i,1]*1000)
            if total_label != creep_label and total_label != fatigue_label:  # creep
                sheet.write(i + 1, col+5, data3[i,0]*1000)
                sheet.write(i + 1, col+6, data3[i,1]*1000)
            elif total_label != creep_label and total_label == fatigue_label:
                sheet.write(i + 1, col+3, data3[i,0]*1000)
                sheet.write(i + 1, col+4, data3[i,1]*1000)
    trainbook.save(wkpath+Jn+'dataSet.xls') # 数据集文件
    # 剔除偏离过大的数据
    inbook = xlrd.open_workbook(wkpath+Jn+'dataSet.xls')
    sheet = inbook.sheet_by_index(0)
    flag = []
    for k in range(1,sheet.ncols-col):
        target = sheet.col_values(col+k)
        for i in range(1, len(target)):
            if (target[i] > 4.0*target[1] or target[i] < 0.08*target[1]) and (i not in flag):
                flag.append(i)
    data_sheet1 = []
    data_sheet2 = []
    for j in range(len(target)):
        if j in flag:
            data_sheet2.append(sheet.row_values(j))
        else:
            data_sheet1.append(sheet.row_values(j))
    outbook = xlwt.Workbook()
    sheet1 = outbook.add_sheet('Sheet1')
    sheet2 = outbook.add_sheet('Sheet2')
    for i in range(len(data_sheet1)):
        for j in range(len(data_sheet1[0])):
            sheet1.write(i, j, data_sheet1[i][j])
    for i in range(len(data_sheet2)):
        for j in range(len(data_sheet2[0])):
            sheet2.write(i, j, data_sheet2[i][j])
    outbook.save(wkpath+Jn+'dataSet.xls')
    
    print 'Writing Excel done...'
    random_cv = random_cv[:-1]
    random_distr = random_distr[:-1]
    return random_cv,random_distr


#### 调用机器学习函数 ####
def hybrid(temp,Ma,nCpus,Mn,Pn,Jn,ST,PDID,LLI,SDI,train,xlsname, loadname,direc,dwell,amp,Fn,values,dpth, 
              load,geom, ml,EX,sample, life,mcs,corre,Pf,joint,sensicurve,sensi, point,D1,C1,D2,C2,D5,C5,C3,C4,C42,nk,paraIV,paraV,
              choose,u_rnd,E_rnd,ela_rnd,den_rnd,con_rnd,ex_rnd,Xg,Xc,Xf,X11,X22,X33,value_load,dwtime,value_geo,dimension_label,geo,dp):
    start=time.clock()
    t1 = time.time()
    # 运行有限元
    if train == 'No Training' or train == 'Train with the Data from FEM': 
        random_cv,random_distr = FE(temp,nCpus,Mn,Pn,Jn,ST,paraIV,paraV,
                load,geom,Fn,values,dpth, loadname,direc,dwell,amp,Ma, point,D1,C1,D2,C2,D5,C5,C3,C4,C42,nk,
                choose,u_rnd,E_rnd,ela_rnd,den_rnd,con_rnd,ex_rnd,Xg,Xc,Xf,X11,X22,X33,value_load,dwtime,value_geo,dimension_label,geo,dp)
        print 'FEM Finished...'
    # 运行代理模型
    if train == 'Train with the Data from .xls File' or train == 'Train with the Data from FEM': 
        if train == 'Train with the Data from .xls File':
            path = xlsname
            random_cv, random_distr = getInputs(fields=(('CVs:','0.01,0.03,0.05'),('Distri:','ND,LND,2WD')),
                    label='Please input probabilistic distribution features of random variables:',dialogTitle='Variables')
        else:
            path = wkpath+Jn+'dataSet.xls'
        if EX:
            nsample=sample
        else:
            nsample=0
        fig = str(int(life))+str(int(mcs))+str(int(corre))+str(int(Pf))+str(int(joint))+str(int(sensicurve))  # 是否绘制图片，1或0
        ml = re.findall(r'\((.*?)\)', ml) #机器学习模型
        ml = ''.join(ml)
        os.system('{}/model.exe {} {} {} {} {} {} {}'.format(forpath, ml,path,nsample,random_cv,random_distr,fig,sensi))
        print 'Data Processing Finished...'

    end=time.clock()
    t2 = time.time()
    print 'Running CPU time: %s Seconds'%(end-start)
    print 'Running clock time: %s Seconds'%(t2-t1)
    

#### 主函数 ####
def ReliabilityFunction(temp,Ma,nCpus,Mn,Pn,Jn,ST,D1,C1,D2,C2,D5,C5,PDID,LLI,SDI,train,xlsname, loadname,direc,val_load,C4,dwell,amp,C42,Fn,values,C3,dpth,nbA,nbn,nbm,
              density,conductivity,expansion,E,u,fai,n1,wfcrit,Xsigma,Xepsilon,roK,ron,load,geom, ml,EX,sample,  life,mcs,corre,Pf,joint,sensicurve,sensi, para1,para2,para3,
              para4,para5,para6,para7,para8,para9,para10, multi1,range1, point, keys=' '):
    
    ## 读取初始参数，离散化抽样
    choose,u_rnd,E_rnd,ela_rnd,den_rnd,con_rnd,ex_rnd,Xg,Xc,Xf,X11,X22,X33,value_load,dwtime,value_geo,dimension_label,geo,dp,nk = sampling(temp,
        Mn,keys,ST, density, conductivity,expansion,E,u,fai,n1,wfcrit,Xsigma,Xepsilon,load,geom,nbA,nbn,nbm, roK,ron,values,dpth,val_load,dwell,amp,Ma,D1,C1,D2,C2,D5,C5,C3,C4,C42)

    ## 执行有限元+机器学习+作图
    if sensi == '':
        sensi = 1
    hybrid(temp,Ma,nCpus,Mn,Pn,Jn,ST,PDID,LLI,SDI,train,xlsname, loadname,direc,dwell,amp,Fn,values,dpth, 
              load,geom, ml,EX,sample, life,mcs,corre,Pf,joint,sensicurve,sensi, point,D1,C1,D2,C2,D5,C5,C3,C4,C42,nk,1,1,
              choose,u_rnd,E_rnd,ela_rnd,den_rnd,con_rnd,ex_rnd,Xg,Xc,Xf,X11,X22,X33,value_load,dwtime,value_geo,dimension_label,geo,dp)
              
    # 多源不确定性
    store = [D1,D2,D5,X11,X22,X33,u_rnd,E_rnd,ela_rnd,den_rnd,con_rnd,ex_rnd,geo,dp,dwtime,value_load]
    if int(para1)+int(para2)+int(para3)+int(para4)+int(para5) > 0:
        Jncase = Jn + 'case1'
        if int(para1) == 0:
            D1 = 'CONST'
            X11 = np.reshape(Xg*(ST+1),(ST+1,5)).T
            u_rnd = np.array([u_rnd[0][0]]*(ST+1))
            E_rnd = np.array([E_rnd[0][0]]*(ST+1))
            ela_rnd = np.reshape(list(ela_rnd[:,0])*(ST+1),(ST+1,len(ela_rnd[:,0]))).T
            den_rnd = np.array([den_rnd[0][0]]*(ST+1))
            con_rnd = np.array([con_rnd[0][0]]*(ST+1))
            ex_rnd = np.array([ex_rnd[0][0]]*(ST+1))
        if int(para2) == 0:
            D2 = 'CONST'
            X22 = np.reshape(Xc*(ST+1),(ST+1,6)).T
        if int(para3) == 0:
            D5 = 'CONST'
            X33 = np.reshape(Xf*(ST+1),(ST+1,4)).T
        if int(para4) == 0:
            geo = np.reshape(value_geo*(ST+1),(ST+1,len(value_geo))).T
            dp = np.array([[dp[0][0]]*(ST+1)])
        if int(para5) == 0:
            dwtime = np.array([[dwtime[0][0]]*(ST+1)])
            value_load = np.array([[value_load[0][0]]*(ST+1)])
        hybrid(temp,Ma,nCpus,Mn,Pn,Jncase,ST,PDID,LLI,SDI,train,xlsname, loadname,direc,dwell,amp,Fn,values,dpth, 
              load,geom, ml,EX,sample, life,mcs,corre,Pf,joint,sensicurve,sensi, point,D1,C1,D2,C2,D5,C5,C3,C4,C42,nk,int(para4),int(para5),
              choose,u_rnd,E_rnd,ela_rnd,den_rnd,con_rnd,ex_rnd,Xg,Xc,Xf,X11,X22,X33,value_load,dwtime,value_geo,dimension_label,geo,dp)
        D1,D2,D5,X11,X22,X33,u_rnd,E_rnd,ela_rnd,den_rnd,con_rnd,ex_rnd,geo,dp,dwtime,value_load = store
    if int(para6)+int(para7)+int(para8)+int(para9)+int(para10) > 0:
        Jncase = Jn + 'case2'
        if int(para6) == 0:
            D1 = 'CONST'
            X11 = np.reshape(Xg*(ST+1),(ST+1,5)).T
            u_rnd = np.array([u_rnd[0][0]]*(ST+1))
            E_rnd = np.array([E_rnd[0][0]]*(ST+1))
            ela_rnd = np.reshape(list(ela_rnd[:,0])*(ST+1),(ST+1,len(ela_rnd[:,0]))).T
            den_rnd = np.array([den_rnd[0][0]]*(ST+1))
            con_rnd = np.array([con_rnd[0][0]]*(ST+1))
            ex_rnd = np.array([ex_rnd[0][0]]*(ST+1))
        if int(para7) == 0:
            D2 = 'CONST'
            X22 = np.reshape(Xc*(ST+1),(ST+1,6)).T
        if int(para8) == 0:
            D5 = 'CONST'
            X33 = np.reshape(Xf*(ST+1),(ST+1,4)).T
        if int(para9) == 0:
            geo = np.reshape(value_geo*(ST+1),(ST+1,len(value_geo))).T
            dp = np.array([[dp[0][0]]*(ST+1)])
        if int(para10) == 0:
            dwtime = np.array([[dwtime[0][0]]*(ST+1)])
            value_load = np.array([[value_load[0][0]]*(ST+1)])
        hybrid(temp,Ma,nCpus,Mn,Pn,Jncase,ST,PDID,LLI,SDI,train,xlsname, loadname,direc,dwell,amp,Fn,values,dpth, 
              load,geom, ml,EX,sample, life,mcs,corre,Pf,joint,sensicurve,sensi, point,D1,C1,D2,C2,D5,C5,C3,C4,C42,nk,int(para9),int(para10),
              choose,u_rnd,E_rnd,ela_rnd,den_rnd,con_rnd,ex_rnd,Xg,Xc,Xf,X11,X22,X33,value_load,dwtime,value_geo,dimension_label,geo,dp)
        D1,D2,D5,X11,X22,X33,u_rnd,E_rnd,ela_rnd,den_rnd,con_rnd,ex_rnd,geo,dp,dwtime,value_load = store
    if multi1 != '':
        cond_list = range2num(range1)
        if multi1 == 'Magnitude':
            for i in range(len(cond_list)):
                val_load = cond_list[i]
                Jnmulti = Jn + multi1 + str(i)
                # 抽样
                choose,u_rnd,E_rnd,ela_rnd,den_rnd,con_rnd,ex_rnd,Xg,Xc,Xf,X11,X22,X33,value_load,dwtime,value_geo,dimension_label,geo,dp,nk = sampling(temp,Mn,keys,ST, density,
                    conductivity,expansion,E,u,fai,n1,wfcrit,Xsigma,Xepsilon,load,geom,nbA,nbn,nbm, roK,ron,values,dpth,val_load,dwell,amp,Ma,D1,C1,D2,C2,D5,C5,C3,C4,C42)
                # 运行
                hybrid(temp,Ma,nCpus,Mn,Pn,Jnmulti,ST,PDID,LLI,SDI,train,xlsname, loadname,direc,dwell,amp,Fn,values,dpth, 
                    load,geom, ml,EX,sample, life,mcs,corre,Pf,joint,sensicurve,sensi, point,D1,C1,D2,C2,D5,C5,C3,C4,C42,nk,1,1,
                    choose,u_rnd,E_rnd,ela_rnd,den_rnd,con_rnd,ex_rnd,Xg,Xc,Xf,X11,X22,X33,value_load,dwtime,value_geo,dimension_label,geo,dp)
        if multi1 == 'Hold_Time':
            for i in range(len(cond_list)):
                dwell = cond_list[i]
                Jnmulti = Jn + multi1 + str(i)
                # 抽样
                choose,u_rnd,E_rnd,ela_rnd,den_rnd,con_rnd,ex_rnd,Xg,Xc,Xf,X11,X22,X33,dwtime,value_geo,dimension_label,geo,dp,nk = sampling(temp,Mn,keys,ST, density,
                    conductivity,expansion,E,u,fai,n1,wfcrit,Xsigma,Xepsilon,load,geom,nbA,nbn,nbm, roK,ron,values,dpth,val_load,dwell,amp,Ma,D1,C1,D2,C2,D5,C5,C3,C4,C42)
                # 运行
                hybrid(temp,Ma,nCpus,Mn,Pn,Jnmulti,ST,PDID,LLI,SDI,train,xlsname, loadname,direc,val_load,dwell,amp,Fn,values,dpth, 
                    load,geom, ml,EX,sample, life,mcs,corre,Pf,joint,sensicurve,sensi, point,D1,C1,D2,C2,D5,C5,C3,C4,C42,nk,1,1,
                    choose,u_rnd,E_rnd,ela_rnd,den_rnd,con_rnd,ex_rnd,Xg,Xc,Xf,X11,X22,X33,value_load,dwtime,value_geo,dimension_label,geo,dp)
        if multi1 == 'CV_Material':
            for i in range(len(cond_list)):
                C1 = cond_list[i]
                Jnmulti = Jn + multi1 + str(i)
                # 抽样
                choose,u_rnd,E_rnd,ela_rnd,den_rnd,con_rnd,ex_rnd,Xg,Xc,Xf,X11,X22,X33,value_load,dwtime,value_geo,dimension_label,geo,dp,nk = sampling(temp,Mn,keys,ST, density,
                    conductivity,expansion,E,u,fai,n1,wfcrit,Xsigma,Xepsilon,load,geom,nbA,nbn,nbm, roK,ron,values,dpth,val_load,dwell,amp,Ma,D1,C1,D2,C2,D5,C5,C3,C4,C42)
                # 运行
                hybrid(temp,Ma,nCpus,Mn,Pn,Jnmulti,ST,PDID,LLI,SDI,train,xlsname, loadname,direc,dwell,amp,Fn,values,dpth, 
                    load,geom, ml,EX,sample, life,mcs,corre,Pf,joint,sensicurve,sensi, point,D1,C1,D2,C2,D5,C5,C3,C4,C42,nk,1,1,
                    choose,u_rnd,E_rnd,ela_rnd,den_rnd,con_rnd,ex_rnd,Xg,Xc,Xf,X11,X22,X33,value_load,dwtime,value_geo,dimension_label,geo,dp)
        if multi1 == 'CV_Creep':
            for i in range(len(cond_list)):
                C2 = cond_list[i]
                Jnmulti = Jn + multi1 + str(i)
                # 抽样
                choose,u_rnd,E_rnd,ela_rnd,den_rnd,con_rnd,ex_rnd,Xg,Xc,Xf,X11,X22,X33,value_load,dwtime,value_geo,dimension_label,geo,dp,nk = sampling(temp,Mn,keys,ST, density,
                    conductivity,expansion,E,u,fai,n1,wfcrit,Xsigma,Xepsilon,load,geom,nbA,nbn,nbm, roK,ron,values,dpth,val_load,dwell,amp,Ma,D1,C1,D2,C2,D5,C5,C3,C4,C42)
                # 运行
                hybrid(temp,Ma,nCpus,Mn,Pn,Jnmulti,ST,PDID,LLI,SDI,train,xlsname, loadname,direc,dwell,amp,Fn,values,dpth, 
                    load,geom, ml,EX,sample, life,mcs,corre,Pf,joint,sensicurve,sensi, point,D1,C1,D2,C2,D5,C5,C3,C4,C42,nk,1,1,
                    choose,u_rnd,E_rnd,ela_rnd,den_rnd,con_rnd,ex_rnd,Xg,Xc,Xf,X11,X22,X33,value_load,dwtime,value_geo,dimension_label,geo,dp)
        if multi1 == 'CV_Fatigue':
            for i in range(len(cond_list)):
                C5 = cond_list[i]
                Jnmulti = Jn + multi1 + str(i)
                # 抽样
                choose,u_rnd,E_rnd,ela_rnd,den_rnd,con_rnd,ex_rnd,Xg,Xc,Xf,X11,X22,X33,value_load,dwtime,value_geo,dimension_label,geo,dp,nk = sampling(temp,Mn,keys,ST, density,
                    conductivity,expansion,E,u,fai,n1,wfcrit,Xsigma,Xepsilon,load,geom,nbA,nbn,nbm, roK,ron,values,dpth,val_load,dwell,amp,Ma,D1,C1,D2,C2,D5,C5,C3,C4,C42)
                # 运行
                hybrid(temp,Ma,nCpus,Mn,Pn,Jnmulti,ST,PDID,LLI,SDI,train,xlsname, loadname,direc,dwell,amp,Fn,values,dpth, 
                    load,geom, ml,EX,sample, life,mcs,corre,Pf,joint,sensicurve,sensi, point,D1,C1,D2,C2,D5,C5,C3,C4,C42,nk,1,1,
                    choose,u_rnd,E_rnd,ela_rnd,den_rnd,con_rnd,ex_rnd,Xg,Xc,Xf,X11,X22,X33,value_load,dwtime,value_geo,dimension_label,geo,dp)
        if multi1 == 'CV_Geometry':
            for i in range(len(cond_list)):
                C3 = cond_list[i]
                Jnmulti = Jn + multi1 + str(i)
                # 抽样
                choose,u_rnd,E_rnd,ela_rnd,den_rnd,con_rnd,ex_rnd,Xg,Xc,Xf,X11,X22,X33,value_load,dwtime,value_geo,dimension_label,geo,dp,nk = sampling(temp,Mn,keys,ST, density,
                    conductivity,expansion,E,u,fai,n1,wfcrit,Xsigma,Xepsilon,load,geom,nbA,nbn,nbm, roK,ron,values,dpth,val_load,dwell,amp,Ma,D1,C1,D2,C2,D5,C5,C3,C4,C42)
                # 运行
                hybrid(temp,Ma,nCpus,Mn,Pn,Jnmulti,ST,PDID,LLI,SDI,train,xlsname, loadname,direc,dwell,amp,Fn,values,dpth, 
                    load,geom, ml,EX,sample, life,mcs,corre,Pf,joint,sensicurve,sensi, point,D1,C1,D2,C2,D5,C5,C3,C4,C42,nk,1,1,
                    choose,u_rnd,E_rnd,ela_rnd,den_rnd,con_rnd,ex_rnd,Xg,Xc,Xf,X11,X22,X33,value_load,dwtime,value_geo,dimension_label,geo,dp)
        if multi1 == 'CV_Load':
            for i in range(len(cond_list)):
                C4 = cond_list[i]
                Jnmulti = Jn + multi1 + str(i)
                # 抽样
                choose,u_rnd,E_rnd,ela_rnd,den_rnd,con_rnd,ex_rnd,Xg,Xc,Xf,X11,X22,X33,value_load,dwtime,value_geo,dimension_label,geo,dp,nk = sampling(temp,Mn,keys,ST, density,
                    conductivity,expansion,E,u,fai,n1,wfcrit,Xsigma,Xepsilon,load,geom,nbA,nbn,nbm, roK,ron,values,dpth,val_load,dwell,amp,Ma,D1,C1,D2,C2,D5,C5,C3,C4,C42)
                # 运行
                hybrid(temp,Ma,nCpus,Mn,Pn,Jnmulti,ST,PDID,LLI,SDI,train,xlsname, loadname,direc,dwell,amp,Fn,values,dpth, 
                    load,geom, ml,EX,sample, life,mcs,corre,Pf,joint,sensicurve,sensi, point,D1,C1,D2,C2,D5,C5,C3,C4,C42,nk,1,1,
                    choose,u_rnd,E_rnd,ela_rnd,den_rnd,con_rnd,ex_rnd,Xg,Xc,Xf,X11,X22,X33,value_load,dwtime,value_geo,dimension_label,geo,dp)
        