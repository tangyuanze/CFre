# -*- coding:utf-8 -*-
import os
import numpy as np
import matplotlib.pyplot as plt
import random
from scipy.stats import norm, lognorm, exponweib, pearsonr
import xlwt
from sklearn import preprocessing
import xlrd
import xlutils.copy
from minepy import MINE

plt.rcParams['xtick.direction'] = 'in'  # 将x周的刻度线方向设置向内
plt.rcParams['ytick.direction'] = 'in'  # 将y轴的刻度方向设置向内

p = 0.576


def mcs(means_in, noutput, model, CV, distr, fig, store_path):
    ninput = len(means_in)
    # MCS抽样#
    num = int(noutput / 2)  # 计算点数量
    n_sample = 11000
    X = means_in
    X1 = np.zeros((n_sample, ninput), dtype=np.float_)  # 放抽样结果
    Y = np.zeros((n_sample, noutput), dtype=np.float_)
    for i in range(n_sample):  # 抽输入
        for j in range(ninput):
            l = norm.cdf(X[j] - 3 * CV[j] * X[j], X[j], CV[j] * abs(X[j]))  # 抽样范围
            h = norm.cdf(X[j] + 3 * CV[j] * X[j], X[j], CV[j] * abs(X[j]))
            if distr[j] == 'LND':
                X1[i, j] = lognorm.ppf((random.uniform(l, h)), 1, loc=X[j], scale=CV[j] * abs(X[j]))
            elif distr[j] == '2WD':
                X1[i, j] = exponweib.ppf((random.uniform(l, h)), 1, 0, loc=X[j], scale=CV[j] * abs(X[j]))
            else:
                X1[i, j] = norm.ppf((random.uniform(l, h)), loc=X[j], scale=CV[j] * abs(X[j]))
    scaler = preprocessing.MinMaxScaler()
    X11 = scaler.fit_transform(X1)
    for j in range(n_sample):  # 算输出
        Y[j] = model.predict(X11[j].reshape(1, -1))  # 10^3
    Y = Y[(Y > 0).all(1)]  # 去掉为0的元素
    n_sample = len(Y)
    # print('sample num:', n_sample)

    dt = np.zeros((n_sample, num), dtype=np.float_)
    N = np.zeros((n_sample, num), dtype=np.float_)
    for i in range(num):
        dt[:, i] = Y[:, i * 2] + Y[:, i * 2 + 1]
        N[:, i] = 1 / dt[:, i] * 1000

    xybook = xlwt.Workbook()
    sheet = xybook.add_sheet('mcsin')  # mcs抽输入
    for i in range(len(Y)):
        for j in range(ninput):
            sheet.write(i, j, X11[i, j])
    sheet = xybook.add_sheet('mcsout')  # 输出
    for i in range(len(Y)):
        for j in range(num * 2):
            sheet.write(i, j, Y[i, j])
        for j in range(num):
            sheet.write(i, 2 * num + 1 + j, dt[i, j])
            sheet.write(i, 3 * num + 2 + j, N[i, j])
    xybook.save(store_path)

    # 拟合正态分布及直方图,dc,dt正态,df,N对数正态
    if fig[1] == '1':
        col = 20
        for i in range(num):
            plt.figure(i, figsize=(18, 8))
            Yc = Y[:, i * 2]  # dc
            mu = float(np.mean(Yc))
            sigma = float(np.std(Yc))
            x = np.arange(min(Yc), max(Yc), 0.01 * mu)
            try:
                yc = norm.pdf(x, mu, sigma)
            except ZeroDivisionError:
                print('sigma=0 as the y_predict maybe too small, try *10^3 ')
            ax1 = plt.subplot(141)
            ax1.hist(Yc, col, color='blue', alpha=0.3, density=True)  # edgecolor='black'
            ax1.set_xlabel('Creep damage, dc(x10$^{-3}$)', fontdict={'family': 'Times New Roman', 'size': 14})
            ax1.set_ylabel('Frequency', fontdict={'family': 'Times New Roman', 'size': 14})
            ax2 = ax1.twinx()
            ax2.plot(x, yc, 'r')
            ax2.set_yticks([])
            labels = ax1.get_xticklabels() + ax1.get_yticklabels()
            [label.set_fontname('Times New Roman') for label in labels]
            plt.title('%s~Normal(%.5f,%.5f)' % ('dc', float(np.mean(Yc / 1000)), float(np.std(Yc / 1000))),
                      fontdict={'family': 'Times New Roman', 'size': 14})

            Yf = Y[:, i * 2 + 1]  # df
            logY = np.log(Yf)
            s = float(np.std(logY))
            scale = float(np.exp(np.mean(logY)))
            x = np.arange(min(Yf), max(Yf), 0.01 * abs(float(np.mean(Yf))))
            try:
                yf = lognorm.pdf(x, s=s, scale=scale)
            except ZeroDivisionError:
                print('sigma=0 as the y_predict maybe too small, try *10^3 ')
            ax1 = plt.subplot(142)
            ax1.hist(Yf, col, color='blue', alpha=0.3, density=True)
            ax1.set_xlabel('Fatigue damage, df(x10$^{-3}$)', fontdict={'family': 'Times New Roman', 'size': 14})
            ax1.set_yticks([])
            ax2 = ax1.twinx()
            ax2.plot(x, yf, 'r')
            ax2.set_yticks([])
            labels = ax1.get_xticklabels() + ax1.get_yticklabels()
            [label.set_fontname('Times New Roman') for label in labels]
            plt.title(
                '%s~LogNormal(%.5f,%.5f)' % ('df', float(np.mean(np.log(Yf / 1000))), float(np.std(np.log(Yf / 1000)))),
                fontdict={'family': 'Times New Roman', 'size': 14})

            d = dt[:, i]  # dt
            mu = float(np.mean(d))
            sigma = float(np.std(d))
            x = np.arange(min(d), max(d), 0.01 * mu)
            try:
                yd = norm.pdf(x, mu, sigma)
            except ZeroDivisionError:
                print('sigma=0 as the y_predict maybe too small, try *10^3 ')
            ax1 = plt.subplot(143)
            ax1.hist(d, col, color='blue', alpha=0.3, density=True)
            ax1.set_xlabel('Total damage, dt(x10$^{-3}$)', fontdict={'family': 'Times New Roman', 'size': 14})
            ax1.set_yticks([])
            ax2 = ax1.twinx()
            ax2.plot(x, yd, 'r')
            ax2.set_yticks([])
            labels = ax1.get_xticklabels() + ax1.get_yticklabels()
            [label.set_fontname('Times New Roman') for label in labels]
            plt.title('%s~Normal(%.5f,%.5f)' % ('dt', float(np.mean(d / 1000)), float(np.std(d / 1000))),
                      fontdict={'family': 'Times New Roman', 'size': 14})

            Nt = N[:, i]  # N
            logN = np.log(Nt)
            s = float(np.std(logN))
            scale = float(np.exp(np.mean(logN)))
            x = np.arange(min(Nt), max(Nt), 0.01 * abs(float(np.mean(Nt))))
            try:
                yf = lognorm.pdf(x, s=s, scale=scale)
            except ZeroDivisionError:
                print('sigma=0 as the y_predict maybe too small, try *10^3 ')
            ax1 = plt.subplot(144)
            ax1.hist(Nt, col, color='blue', alpha=0.3, density=True)
            ax1.set_xlabel('Creep-fatigue life, N', fontdict={'family': 'Times New Roman', 'size': 14})
            ax1.set_yticks([])
            ax2 = ax1.twinx()
            ax2.plot(x, yf, 'r')
            ax2.set_yticks([])
            labels = ax1.get_xticklabels() + ax1.get_yticklabels()
            [label.set_fontname('Times New Roman') for label in labels]
            plt.title(
                '%s~LogNormal(%.4f,%.4f)' % ('N', float(np.mean(np.log(Nt))), float(np.std(np.log(Nt)))),
                fontdict={'family': 'Times New Roman', 'size': 14})
            plt.savefig(store_path[:-11] + '-mcs' + str(i) + '.png')
            plt.clf()
            plt.close()
        # plt.show()

    return X1, Y


def pfailure(Y, store_path):
    n_sample = len(Y)
    dc = np.zeros(n_sample, dtype=np.float_)
    df = np.zeros(n_sample, dtype=np.float_)
    for i in range(n_sample):
        dc[i] = Y[i][0] / 1000
        df[i] = Y[i][1] / 1000

    D = np.zeros(n_sample, dtype=np.float_)
    N = np.zeros(n_sample, dtype=np.float_)
    for i in range(n_sample):
        D[i] = dc[i] + df[i]
        N[i] = 1 / D[i]

    nd = np.arange(1, 4000, 1.0)
    N1 = np.log10(N)
    mean_N1 = np.mean(N1)
    std_N1 = np.std(N1)
    Pf1 = norm.cdf((np.log10(nd) - mean_N1) / std_N1, 0, 1)  # LLI
    plt.figure(4, figsize=(6.4, 4.8))
    plt.plot(nd, Pf1, 'r', label='LLI')

    mud = np.mean(D)
    sigmad = (np.std(D)) ** 2
    Pf2 = norm.cdf((nd * mud - 1) / np.sqrt(0.1496 ** 2 + sigmad * nd ** 2), 0, 1)  # SDI
    plt.plot(nd, Pf2, 'b', label='SDI')

    Pf3 = np.zeros(len(nd), dtype=np.float_)
    for i in range(len(nd)):
        F = 0
        for j in range(n_sample):
            point = (nd[i] * dc[j]) ** p + (nd[i] * df[j]) ** p
            if point > 1:
                F += 1
        Pf3[i] = F / n_sample
    plt.plot(nd, Pf3, 'g', label='PDID')  #

    rd = xlrd.open_workbook(store_path, formatting_info=True)  # 打开文件
    wt = xlutils.copy.copy(rd)  # 复制
    sheet = wt.add_sheet('Pf')
    sheet.write(0, 0, 'Nd')
    sheet.write(0, 1, 'LLI')
    sheet.write(0, 2, 'SDI')
    sheet.write(0, 3, 'PDID')
    for i in range(len(nd)):
        sheet.write(i + 1, 0, nd[i])
        sheet.write(i + 1, 1, Pf1[i])
        sheet.write(i + 1, 2, Pf2[i])
        sheet.write(i + 1, 3, Pf3[i])
    wt.save(store_path)  # 保存

    plt.ylim(0.01, 0.99)
    plt.xlabel('Design life, $\\it{Nd}$ (cycles)', fontweight='bold')
    plt.ylabel('Failure probability, $\\it{Pf}$', fontweight='bold')
    plt.legend()
    plt.grid(True)
    plt.savefig(store_path[:-11] + '-failure probability.png')
    plt.clf()
    plt.close()
    # plt.show()


def joint_evaluation_PDID(dc1, df1, dc2, df2, dc3, df3, store_path):
    # 热点法
    n = len(dc1)
    nd = np.arange(1.0, 2000.0, 1.0)
    Pf_hot = np.zeros(len(nd), dtype=np.float_)
    for i in range(len(nd)):
        F = 0
        for j in range(n):
            point = (nd[i] * dc1[j]) ** p + (nd[i] * df1[j]) ** p
            if point > 1:
                F += 1
        Pf_hot[i] = F / n

    # 联合失效概率
    Pf1 = Pf_hot
    Pf2 = np.zeros(len(nd), dtype=np.float_)
    Pf3 = np.zeros(len(nd), dtype=np.float_)
    for i in range(len(nd)):
        F = 0
        for j in range(n):
            point = (nd[i] * dc2[j]) ** p + (nd[i] * df2[j]) ** p
            if point > 1:
                F += 1
        Pf2[i] = F / n

    for i in range(len(nd)):
        F = 0
        for j in range(n):
            point = (nd[i] * dc3[j]) ** p + (nd[i] * df3[j]) ** p
            if point > 1:
                F += 1
        Pf3[i] = F / n

    Pf_joint = 1 - ((1 - Pf1) * (1 - Pf2) * (1 - Pf3))

    rd = xlrd.open_workbook(store_path, formatting_info=True)  # 打开文件
    wt = xlutils.copy.copy(rd)  # 复制
    try:
        sheet = wt.get_sheet(2)
    except IndexError:
        sheet = wt.add_sheet('Pf')
    sheet.write(0, 4, 'joint')
    for i in range(len(nd)):
        sheet.write(i + 1, 4, Pf_joint[i])
    wt.save(store_path)  # 保存

    # 画图
    plt.figure(6, figsize=(6.4, 4.8))
    plt.ylim(0.01, 0.99)
    plt.plot(nd, Pf_hot, 'b', label='Hotspot-based')
    plt.plot(nd, Pf_joint, 'r', label='Joint-failure')
    plt.xlabel('Design Life, $\\it{Nd}$ (cycles)', fontdict={'family': 'Times New Roman', 'size': 14})
    plt.ylabel('Failure Probability, $\\it{Pf}$', fontdict={'family': 'Times New Roman', 'size': 14})
    plt.legend()
    plt.grid(True)
    # plt.show()
    plt.savefig(store_path[:-11] + '-joint failure.png')
    plt.clf()
    plt.close()


def calc_sensitivity(indata, outdata):
    pf = np.linspace(0.01, 0.99, 99)
    u = np.average(indata, axis=0)  # mu of input
    o = np.std(indata, axis=0)  # sigma
    ndata = len(outdata)  # 数据点数量
    ninput = len(indata[0])  # 标签个数

    dc = np.zeros(ndata, dtype=np.float_)
    df = np.zeros(ndata, dtype=np.float_)
    for i in range(ndata):
        dc[i] = outdata[i][0] / 1000
        df[i] = outdata[i][1] / 1000
    N = np.power(1 / (dc ** p + df ** p), 1 / p)
    nd = norm.ppf(pf, 0, 1) * np.std(N) + np.mean(N)
    for k in range(len(pf)):
        if nd[k] > 0:
            flag = k
            break
    pf = pf[flag:]
    nd = nd[flag:]

    n = len(nd)  # 作图点数量
    F = np.zeros(ndata, dtype=np.int_)
    dpdu = np.zeros(ndata, dtype=np.float_)
    dpdo = np.zeros(ndata, dtype=np.float_)
    alfa = np.zeros((ninput, n), dtype=np.float_)
    yita = np.zeros((ninput, n), dtype=np.float_)
    for j in range(ninput):
        for i in range(ndata):
            point = (nd[j] * dc[i]) ** p + (nd[j] * df[i]) ** p  # PDID准则
            if point < 1:
                F[i] = 1

        for i in range(ndata):
            dpdu[i] = F[i] * (indata[i][j] - u[j]) / (o[j] ** 2)
            dpdo[i] = (F[i] / o[j]) * (((indata[i][j] - u[j]) / o[j]) ** 2 - 1)
        du = np.mean(dpdu)
        do = np.mean(dpdo)

        for k in range(n):
            alfa[j][k] = du * u[j] / pf[k]  # j个变量j行
            yita[j][k] = do * o[j] / pf[k]

    return alfa, yita, pf, nd


def sensitivity(indata, outdata, variable, store_path, reliability):  # sensi为1则不画饼图
    # 计算
    alfa, yita, pf, nd = calc_sensitivity(indata, outdata)
    s = np.sqrt(alfa ** 2 + yita ** 2)

    # 作图
    fontdict = {'family': 'Times New Roman', 'size': 14}
    plt.figure(10, figsize=(6, 6))

    plt.subplot(211)
    for j in range(len(variable)):
        plt.plot(nd, alfa[j], label=variable[j])
    plt.ylabel('Sensitivity factor for mean', fontdict=fontdict)
    plt.title('Sensitivity at different design life', fontdict=fontdict)
    plt.legend()

    plt.subplot(212)
    for j in range(len(variable)):
        plt.plot(nd, yita[j], label=variable[j])
    plt.xlabel('Design Life, $\\it{Nd}$ (cycles)', fontdict=fontdict)
    plt.ylabel('Sensitivity factor for std.', fontdict=fontdict)
    plt.savefig(store_path[:-11] + '-Sensitivity at different design life.png')
    plt.clf()
    plt.close()
    # plt.show()

    # 存储
    rd = xlrd.open_workbook(store_path, formatting_info=True)  # 打开文件
    wt = xlutils.copy.copy(rd)  # 复制
    sheet = wt.add_sheet('sensitivity', cell_overwrite_ok=True)
    sheet.write(0, 0, 'Failure probability')
    sheet.write(0, 1, 'Design life')
    for i in range(len(pf)):  # 数据点个数
        sheet.write(i+1, 0, pf[i])
        sheet.write(i+1, 1, nd[i])
    for i in range(len(alfa)):  # 变量数
        sheet.write(0, i+2, variable[i])
        for j in range(len(alfa[0])):
            sheet.write(j+1, i+2, s[i][j])

    sheet = wt.add_sheet('sensi_factor', cell_overwrite_ok=True)
    for i in range(len(alfa)):  # 变量数
        sheet.write(0, 2*i, variable[i])
        sheet.write(1, 2*i, 'alfa')
        sheet.write(1, 2*i+1, 'yita')
        for j in range(len(alfa[0])):
            sheet.write(j+2, 2*i, alfa[i][j])
            sheet.write(j+2, 2*i+1, yita[i][j])
    wt.save(store_path)

    # 特定可靠度
    if reliability != 1.0:
        flag = np.abs(1 - reliability - pf).argmin()
        sensi = [s[i][flag] for i in range(len(variable))]
        account = [sensi[i]/sum(sensi) for i in range(len(variable))]
        expl = []
        for i in range(len(variable)):
            expl.append(0.05)
        plt.figure(11, figsize=(7, 6))
        plt.pie(account, labels=variable, autopct='%1.2f%%', pctdistance=0.9, shadow=True, explode=expl)
        plt.title('Failure probability sensitivity', fontdict={'family': 'Times New Roman', 'size': 14})
        plt.savefig(store_path[:-11] + '-Sensitivity.png')
        plt.clf()
        plt.close()
        # plt.show()


def life_evaluation(means_out, store_path):
    dc = means_out[0]/1000
    df = means_out[1]/1000
    plt.figure(7)
    x = [0, 1]  #
    y = [1, 0]
    plt.plot(x, y, color='black', markersize=1, label='Linear damage summation')
    x = [0, 0.3, 1]  #
    y = [1, 0.3, 0]
    plt.plot(x, y, color='black', markersize=1, linestyle=':', label='Bilinear damage summation')
    x = np.linspace(0, 1, 100)  #
    y = np.power(1 - x ** 0.576, 1 / 0.576)
    plt.plot(x, y, color='black', markersize=1, linestyle='-.', label='Continuous damage summation')
    x = np.linspace(0, 1 / (dc / df + 1), 10)  #
    y = dc / df * x
    plt.plot(x, y, color='b', marker='o', markerfacecolor='white', label='Creep-fatigue damage trajectory')

    life1 = int(1/(dc + df))
    if dc > df:
        life2 = int((3/(7*df+3*dc)))
    else:
        life2 = int((3/(3*df+7*dc)))
    life3 = int(np.power(1 / (dc ** 0.576 + df ** 0.576), 1 / 0.576))  # int((np.power(1/(1+(dc/df)**0.576), 1/0.576)) / df)

    plt.xlim((0, 1))
    plt.ylim((0, 1))
    fontdict = {'family': 'Times New Roman', 'size': 16}
    plt.xlabel('Accumulated fatigue damage, $\\it{D_{f}}$', fontdict=fontdict)
    plt.ylabel('Accumulated creep damage, $\\it{D_{c}}$', fontdict=fontdict)
    plt.title('Life evaluation under different summation', fontdict=fontdict)
    plt.legend()
    plt.text(0.62, 0.6, 'Creep-fatigue life:', fontdict=fontdict, color='b')
    plt.text(0.85, 0.4, str(life1) + '\n' + str(life2) + '\n' + str(life3), fontdict=fontdict, color='b')
    # plt.show()
    plt.savefig(store_path[:-11] + '-deterministic life evaluation.png')
    plt.clf()
    plt.close()


def correlation(indata, outdata, variable, store_path):
    N = 1 / (outdata[:, 0] + outdata[:, 1])

    # Peason
    person = []
    pvalue = []  # 小于0.05认为相关
    for i in range(len(indata[0])):
        r = pearsonr(indata[:, i], N)
        person.append(r[0])
        pvalue.append(r[1])
    print("\nPearson coefficient：", person)
    print("P-Value (Linear correlation if less than 0.05)：", pvalue)
    dic = dict(zip(variable, person))
    sort_list = sorted(dic.items(), key=lambda kv: (kv[1], kv[0]))
    # 画图
    plt.figure(8)
    nvar = len(variable)
    b = plt.barh(range(nvar), [sort_list[i][1] for i in range(nvar)], color='darkorange', height=0.8, alpha=0.7)
    # 添加数据标签
    for rect in b:
        w = rect.get_width()
        plt.text(w, rect.get_y() + rect.get_height() / 2, '%.3f' % w, ha='center', va='center', family='Times New Roman')
    # 设置Y轴刻度线标签
    plt.yticks(range(nvar), [sort_list[i][0] for i in range(nvar)], family='Times New Roman', fontsize=14)
    plt.title('Pearson correlation coefficient')
    # 设置上边和右边无边框,y轴位置
    # ax = plt.gca()
    # ax.spines['right'].set_color('none')
    # ax.spines['top'].set_color('none')
    # ax.yaxis.set_ticks_position('left')
    # ax.spines['left'].set_position(('data', 0))
    plt.savefig(store_path[:-11] + '-pearson correlation analysis.png')
    plt.clf()
    plt.close()

    # MIC
    mine = MINE(alpha=0.6, c=15, est="mic_approx")
    mic = []
    for i in range(len(indata[0])):
        mine.compute_score(indata[:, i], N)
        mic.append(mine.mic())
    print("\nMIC:", mic)
    dic = dict(zip(variable, mic))
    sort_list = sorted(dic.items(), key=lambda kv: (kv[1], kv[0]))
    # 画图
    plt.figure(9)
    b = plt.barh(range(nvar), [sort_list[i][1] for i in range(nvar)], height=0.8, color='limegreen', alpha=0.7)
    # 添加数据标签
    for rect in b:
        w = rect.get_width()
        plt.text(w, rect.get_y() + rect.get_height() / 2, '%.3f' % w, ha='center', va='center', family='Times New Roman')
    # 设置Y轴刻度线标签
    plt.yticks(range(nvar), [sort_list[i][0] for i in range(nvar)], family='Times New Roman', fontsize=14)
    plt.title('MIC correlation coefficient')
    plt.savefig(store_path[:-11] + '-MIC correlation analysis.png')
    plt.clf()
    plt.close()
    # plt.show()


def read_result_excel(xls, label):
    rd = xlrd.open_workbook(xls, formatting_info=True)
    sheet1 = rd.sheet_by_name('mcsout')
    dt_index = 0
    for i in range(sheet1.ncols):
        if sheet1.cell(0, i) == '':
            dt_index = i + 1
    dt = sheet1.col_values(dt_index)
    mu = float(np.mean(dt))
    sigma = float(np.std(dt))
    x = np.arange(min(dt), max(dt), 0.01 * mu)
    yd = norm.pdf(x, mu, sigma)
    plt.figure('multimcsout')
    plt.plot(x, yd, label=label)

    sheet2 = rd.sheet_by_name('Pf')
    nd = sheet2.col_values(0)[1:]
    pf = sheet2.col_values(1)[1:]
    plt.figure('multipf')
    plt.plot(nd, pf, label=label)


def uncertainties(store_path):
    path = store_path.rsplit('/', 1)
    if len(path) == 1:
        path = store_path.rsplit('\\', 1)
    if 'case1' in path[1]:
        read_result_excel(store_path, 'case1')  # 读case1
        case2_path = store_path[:-12] + '2mcsData.xls'
        if case2_path in os.listdir(path[0]):
            read_result_excel(case2_path, 'case2')  # 找case2,有则读case2

    if 'case2' in path[1]:
        read_result_excel(store_path, 'case2')
        case1_path = store_path[:-12] + '1mcsData.xls'
        if case1_path in os.listdir(path[0]):
            read_result_excel(case1_path, 'case1')

    if 'case1' in path[1] or 'case2' in path[1]:
        Jn_path = store_path[:-16] + 'mcsData.xls'
        read_result_excel(Jn_path, 'case0')  # 读Jnmcsdata

        plt.figure('multimcsout')
        plt.xlabel('Total damage, dt(x10$^{-3}$)')
        plt.ylabel('Probability density')
        plt.title('Comparison between multiple uncertainty sources', fontdict={'family': 'Times New Roman', 'size': 14})
        plt.legend()
        plt.savefig('multi_uncertainties_mcsout.png')

        plt.figure('multipf')
        plt.ylim(0.01, 0.99)
        plt.xlabel('Design life, $\\it{Nd}$ (cycles)')
        plt.ylabel('Failure probability, $\\it{Pf}$')
        plt.title('Comparison between multiple uncertainty sources', fontdict={'family': 'Times New Roman', 'size': 14})
        plt.legend()
        plt.savefig('multi_uncertainties_pf.png')
        plt.clf()
        plt.close()
        # plt.show()


# 主函数 #
def draw(means_in, means_out, model, variable, CV, distr, fig, sensi, xlspath):
    noutput = len(means_out)
    store_path = xlspath[:-11] + 'mcsData.xls'

    if fig[0] == '1':
        life_evaluation(means_out, store_path)

    X, Y = mcs(means_in, noutput, model, CV, distr, fig, store_path)

    if fig[2] == '1':
        correlation(X, Y, variable, store_path)

    # 调用pf maxdt-point
    if fig[3] == '1':
        pfailure(Y, store_path)

    # 调用joint failure
    num = int(noutput / 2)
    if fig[4] == '1':
        if num == 2:
            joint_evaluation_PDID(Y[:, 0] / 1000, Y[:, 1] / 1000, Y[:, 2] / 1000, Y[:, 3] / 1000,
                                  np.zeros((len(Y), 1), dtype=np.float_), np.zeros((len(Y), 1), dtype=np.float_), store_path)
        elif num == 3:
            joint_evaluation_PDID(Y[:, 0] / 1000, Y[:, 1] / 1000, Y[:, 2] / 1000, Y[:, 3] / 1000, Y[:, 4] / 1000,
                                  Y[:, 5] / 1000, store_path)
        else:
            print('\nThree dangerous points are very close so Joint Failure Evaluation is not recommended')

    # 调用sensitivity maxdt-point，可靠度为sensi下的敏感性
    if fig[5] == '1':
        sensitivity(X, Y, variable, store_path, sensi)

    # 多敏感性影响计算
    uncertainties(store_path)

