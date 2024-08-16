
    
      SUBROUTINE CREEP(DECRA,DESWA,STATEV,SERD,EC,ESW,P,QTILD,
     1 TEMP,DTEMP,PREDEF,DPRED,TIME,DTIME,CMNAME,LEXIMP,LEND,
     2 COORDS,NSTATV,NOEL,NPT,LAYER,KSPT,KSTEP,KINC)
C
      INCLUDE 'ABA_PARAM.INC'
C
      CHARACTER*80 CMNAME
C
      DIMENSION DECRA(5),DESWA(5),STATEV(*),PREDEF(*),DPRED(*),
     1 TIME(3),COORDS(*),EC(2),ESW(2)
C
      DO 3 KK=1,5
    3 DECRA(KK)=0.D0
    
C ***INPUT HOLD TIME    

      IF (KINC .EQ. 1) THEN
      STATEV(5)=0 
      ELSE
C deformation increment
      STATEV(5)=EC(1)-STATEV(2) 
C EC(1):creep deformation at the start of increment
      ENDIF

C ***EXECUTE STRAIN HARDNING DURING DWELL PERIOD     
      STATEV(6)=TEMP
      
      A=5.8e-23
      XN=5.2
      XM=-0.36

      C1=1./(1.+XM)
C DECRA(1):creep strain increment, DECRA(5):pian strain/pian q, QTILD:equivalent stress
C       time hardening
C       IF (TERM4 .EQ. 0) THEN
C       TERM1=A*QTILD**XN*C1
C       DECRA(1)=TERM1*(TIME(1)**(1.+XM)-(TIME(1)-DTIME)**(1.+XM))
C       DECRA(5)=DECRA(1)*XN/QTILD 
C strain hardening
      TERM1=(A*QTILD**XN*C1)**C1
      TERM2=TERM1*DTIME+(STATEV(5))**C1
      STATEV(1)=TERM2/TERM1
      DECRA(1)=(TERM2**(1.+XM)-(STATEV(5)))
      DECRA(5)=XN*DTIME*TERM2**XM*TERM1/QTILD

C ***RUTURN EFFCTIVE CREEP STRAIN AT THE END OF DWELL PERIOD      
      IF (KINC .EQ. 1) THEN
      STATEV(2)=EC(1)
      ENDIF
   10 CONTINUE

      RETURN
      END
      
    
      SUBROUTINE UVARM(UVAR,DIRECT,T,TIME,DTIME,CMNAME,ORNAME,
     1 NUVARM,NOEL,NPT,LAYER,KSPT,KSTEP,KINC,NDI,NSHR,COORD,
     2 JMAC,JMATYP,MATLAYO,LACCFLA)
      INCLUDE 'ABA_PARAM.INC'
C
      CHARACTER*80 CMNAME,ORNAME
      CHARACTER*3 FLGRAY(15)
      DIMENSION UVAR(NUVARM),DIRECT(3,3),T(3,3),TIME(2)
      DIMENSION ARRAY(15),JARRAY(15),JMAC(*),JMATYP(*),COORD(*)
      INTEGER i,j,k
      real*8 one
      
      REAL*8 mat1,mat2,mat3,mat4,mat5,mat6,mat7,mat8,mat9,mat10,
     1 mat11,mat12,mat13,mat14,mat15,mat16,mat17,mat18,mat19,mat20 
      REAL*8 theta,phi,alpha,A,B,p_crit,Xsigma,Xepsilon,b0,c0,th1,th2
      REAL*8 VHP3,VHP4,V3,V4,temp_n1,temp1,temp2,temp3,temp4,temp5,
     1 temp_aa,temp_bb,sig_mean,win,wf,wmin,wfcrit,E,E_eff,XR,XD      
      Parameter (PI=3.1415926)
      DIMENSION mat1(3,3),mat2(3,3),mat3(3,3),mat4(3,3),mat5(3,3),
     1 mat6(3,3),mat7(3,3),mat8(3,3),mat9(3,3),mat10(3,3),mat11(3,3),
     2 mat12(3,3),mat13(3,3),mat14(3,3),mat15(3,3),mat16(3,3),
     3 mat17(3,3),mat18(3,3),mat19(3,3),mat20(3,3),mat21(3,3)
      DIMENSION valt1(3,3),valt2(3,3),valt3(3,3),valt4(3,3),valt5(3,3),
     1 valt6(3,3),valt7(3,3),valt8(3,3),valt9(3,3),valt10(3,3),
     2 valt11(3,3),valt12(3,3),valt13(3,3),valt14(3,3),valt15(3,3),
     3 valt16(3,3),valt17(3,3),valt18(3,3),valt19(3,3),valt20(3,3),
     4 valt21(3,3)

c error counter:
      jerror = 0

c *** SEDE模型常数 114 0.14 46
      fai=114
      temp_n1=0.1400162214786639
      wfcrit=45.779801532179974

c ***弹性模量
      E=168000
c ***泊松比
      Poi=0.3
c ***拉伸疲劳强度1476
      Xsigma=1466.7253218891012
c ***拉伸延性0.162
      Xepsilon=0.16124733744223282
c ***用于critical plane的幂指数
      b0=-1.0*0.086
      c0=-1.0*0.58
c ***诺顿方程的n
      XN=5.2
c ***用于三维的弹性模量
      E_eff=3.0*E/(2.0*(1.0+Poi))
c ***估算一个所能用到疲劳最大寿命      
      xnfmax=200000
	  one=1.0d0  

c*************************************************************************      
c ***求三个主应力
         call getvrm('SP',array,jarray,flgray,jrcd,jmac,jmatyp,matlayo
     &            ,laccfla)
        jerror = jerror + jrcd
        UVAR(1)= array (1)
        UVAR(2)= array (2)
        UVAR(3)= array (3)
        
c ***求绝对值最大主应力  
        if (abs (UVAR(3)) .GE. abs (UVAR(1))) then
           UVAR(4)=UVAR(3)
        else
           UVAR(4)=UVAR(1)
        endif
        
c ***获得应力        
        call getvrm('S',array,jarray,flgray,jrcd,jmac,jmatyp,matlayo
     &            ,laccfla)
        jerror = jerror + jrcd
        VHP4 = (array(1) + array(2) + array(3))/3.0
        V4=1.5*((array(1)-VHP4)**2.0+(array(2)-VHP4)**2.0+
     1       (array(3)-VHP4)**2.0+2.0*array(4)**2.0+
     2        2.0*array(5)**2.0+2.0*array(6)**2.0)
       UVAR(5) = SQRT(V4)
        
c ***给Mises应力加上方向        
      if (UVAR(4) .NE. 0) then
          UVAR(6) = UVAR(5)*UVAR(4)/(abs (UVAR(4)))
      else
          UVAR(6) = UVAR(5)
      endif

c ***获得应力三轴度        
      if (UVAR(5) .NE. 0) then
          UVAR(7) = VHP4/SQRT(V4)
      end if      
        
c************************************************************************* 
c ***求三个主应变
         call getvrm('EP',array,jarray,flgray,jrcd,jmac,jmatyp,matlayo
     &            ,laccfla)
        jerror = jerror + jrcd
        UVAR(8)= array (1)
        UVAR(9)= array (2)
        UVAR(10)= array (3)
        
c ***求绝对值最大主应变  
        if (abs (UVAR(10)) .GE. abs (UVAR(8))) then
           UVAR(11)=UVAR(10)
        else
           UVAR(11)=UVAR(8)
        endif
        
c ***求等效总应变      
        call getvrm('E',array,jarray,flgray,jrcd,jmac,jmatyp,matlayo
     &            ,laccfla)
        jerror = jerror + jrcd
        VVHP4 = (array(1)+array(2)+array(3))/3.0
        temp4 = (array(1)-VVHP4)**2.0+(array(2)-VVHP4)**2.0
     &   +(array(3)-VVHP4)**2.0
        temp4 = temp4+0.5*(array(4)**2.0+array(5)**2.0+array(6)**2.0)
        temp4 = temp4 * 2.0/3.0
        UVAR(12)= SQRT(temp4)
        
c ***给总应变加正负号        
      if (UVAR(11) .NE. 0) then
          UVAR(13) = UVAR(12)*UVAR(11)/
     &                  (abs (UVAR(11)))
      else
          UVAR(13) = UVAR(12)
      endif         

c************************************************************************* 
c ***把谷值的场变量装入矩阵
      IF ((mod(KSTEP-4,3) .eq. 0) .and. (KINC .eq. 1)) THEN
      
c ***将第一段谷值应力分量装入矩阵mat1        
        call getvrm('S',array,jarray,flgray,jrcd,jmac,jmatyp,matlayo
     &            ,laccfla)
        jerror = jerror + jrcd                
      do i=1,3
        do j=1,3
         if (i.EQ.j) then
         valt1(i,j)=array(i)
         UVAR(43+i)=array(i)
         else
         valt1(i,j)=array(i+j+1)
         UVAR(44+i+j)=array(i+j+1)
         end if
        end do
      end do
      
c ***将第一段谷值应变分量装入矩阵mat2     
        call getvrm('E',array,jarray,flgray,jrcd,jmac,jmatyp,matlayo
     &            ,laccfla)
        jerror = jerror + jrcd                     
        do i=1,3
         do j=1,3
          if (i.EQ.j) then
          valt2(i,j)=array(i)
          UVAR(49+i)=array(i)
          else
          valt2(i,j)=array(i+j+1)
          UVAR(50+i+j)=array(i+j+1)
          end if
         end do
        end do
      ENDIF
c************************************************************************* 
c ***把第一段大保载前的场变量装入矩阵
      IF ((mod(KSTEP-2,3) .eq. 0) .and. (KINC .eq. 1)) THEN
          
c ***峰值应力         
        call getvrm('SINV',array,jarray,flgray,jrcd,jmac,jmatyp,matlayo
     &            ,laccfla)
        jerror = jerror + jrcd
        UVAR(14)= array(1)
        
c ***WEN-TU的多轴延性因子          
        UVAR(15)=(exp(2.0/3.0*(XN-0.5)/(XN+0.5)))/
     &     (exp(2.0*(XN-0.5)/(XN+0.5))*UVAR(7))

c ***峰值的等效塑性应变
        call getvrm('PE',array,jarray,flgray,jrcd,jmac,jmatyp,matlayo
     &            ,laccfla)
        jerror = jerror + jrcd
        VVHP2 = (array(1)+array(2)+array(3))/3.0
        temp2 = (array(1)-VVHP2)**2.0+(array(2)-VVHP2)**2.0
     &   +(array(3)-VVHP2)**2.0
        temp2 = temp2+0.5*(array(4)**2.0+array(5)**2.0+array(6)**2.0)
        temp2 = temp2 * 2.0/3.0
        UVAR(16)= SQRT(temp2)        
      
c ***将第一段峰值应力分量装入矩阵mat1        
        call getvrm('S',array,jarray,flgray,jrcd,jmac,jmatyp,matlayo
     &            ,laccfla)
        jerror = jerror + jrcd                
      do i=1,3
        do j=1,3
         if (i.EQ.j) then
         mat1(i,j)=array(i)
         else
         mat1(i,j)=array(i+j+1)
         end if
        end do
      end do 
      
c ***将第一段峰值应变分量装入矩阵mat2     
        call getvrm('E',array,jarray,flgray,jrcd,jmac,jmatyp,matlayo
     &            ,laccfla)
        jerror = jerror + jrcd                     
        do i=1,3
         do j=1,3
          if (i.EQ.j) then
          mat2(i,j)=array(i)
          else
          mat2(i,j)=array(i+j+1)
          end if
         end do
        end do
        valt1(1,1)=UVAR(44)
        valt1(2,2)=UVAR(45)
        valt1(3,3)=UVAR(46)
        valt1(1,2)=UVAR(47)
        valt1(2,1)=UVAR(47)
        valt1(1,3)=UVAR(48)
        valt1(3,1)=UVAR(48)
        valt1(2,3)=UVAR(49)
        valt1(3,2)=UVAR(49)
        valt2(1,1)=UVAR(50)
        valt2(2,2)=UVAR(51)
        valt2(3,3)=UVAR(52)
        valt2(1,2)=UVAR(53)
        valt2(2,1)=UVAR(53)
        valt2(1,3)=UVAR(54)
        valt2(3,1)=UVAR(54)
        valt2(2,3)=UVAR(55)
        valt2(3,2)=UVAR(55)
c ***获得部分应变范围的临界平面        
c ********临界平面法坐标转换
      dpasso=5.0/180.0*PI
      do theta=0,PI,dpasso
       do phi=0,PI,dpasso
         do alpha=0,PI,dpasso
c ***参考坐标系的峰值n方向矩阵(mat3),峰值q方向矩阵(mat4)
            mat3(1,1)=sin (theta)* cos (phi)
            mat3(2,1)=sin (theta)* sin (phi)
            mat3(3,1)=cos (theta)
            mat3(1,2)=0
            mat3(2,2)=0
            mat3(3,2)=0
            mat3(1,3)=0
            mat3(2,3)=0
            mat3(3,3)=0
            mat4(1,1)=-1.0*cos (alpha)* sin (phi)-sin (alpha)*
     &                 cos (theta)* cos (phi)
            mat4(2,1)=cos (alpha)* cos (phi)-sin (alpha)*
     &                 cos (theta)* sin (phi)
            mat4(3,1)=sin (alpha)* sin (theta)
            mat4(1,2)=0
            mat4(2,2)=0
            mat4(3,2)=0
            mat4(1,3)=0
            mat4(2,3)=0
            mat4(3,3)=0
c另一个矩阵系            
            valt3(1,1)=sin (theta)* cos (phi)
            valt3(2,1)=sin (theta)* sin (phi)
            valt3(3,1)=cos (theta)
            valt3(1,2)=0
            valt3(2,2)=0
            valt3(3,2)=0
            valt3(1,3)=0
            valt3(2,3)=0
            valt3(3,3)=0
            valt4(1,1)=-1.0*cos (alpha)* sin (phi)-sin (alpha)*
     &                 cos (theta)* cos (phi)
            valt4(2,1)=cos (alpha)* cos (phi)-sin (alpha)*
     &                 cos (theta)* sin (phi)
            valt4(3,1)=sin (alpha)* sin (theta)
            valt4(1,2)=0
            valt4(2,2)=0
            valt4(3,2)=0
            valt4(1,3)=0
            valt4(2,3)=0
            valt4(3,3)=0
c ***参考坐标系峰值/谷值q矩阵的转置         
            mat5=transpose (mat4)
            valt5=transpose (valt4)
c ***考虑q方向峰值/谷值剪应变(mat6)
            mat6=matmul (matmul(mat5,mat2), mat3)
            valt6=matmul (matmul(valt5,valt2), valt3)
c ***参考坐标系峰值/谷值矩阵的转置(mat7)         
            mat7=transpose (mat3)
            valt7=transpose (valt3)
c ***考虑n方向的峰值/guzhi正应力(mat8),以及q方向峰值/guzhi剪应力(mat9)
            mat8=matmul (matmul(mat7,mat1), mat3)
            mat9=matmul (matmul(mat5,mat1), mat3)
            valt8=matmul (matmul(valt7,valt1), valt3)
            valt9=matmul (matmul(valt5,valt1), valt3)
            UVAR(17)=mat8(1,1)
            UVAR(18)=mat9(1,1)
            UVAR(40)=valt8(1,1)
            UVAR(41)=valt9(1,1)
c ***考虑n方向的峰值/guzhi正应变(mat10),以及q方向峰值/guzhi剪应变(mat11)
            mat10=matmul (matmul(mat7,mat2), mat3)
            mat11=matmul (matmul(mat5,mat2), mat3)
            valt10=matmul (matmul(valt7,valt2), valt3)
            valt11=matmul (matmul(valt5,valt2), valt3)
            UVAR(19)=mat10(1,1) 
            UVAR(20)=2.0*mat11(1,1)
            UVAR(42)=valt10(1,1) 
            UVAR(43)=2.0*valt11(1,1)  
c *** 计算MGSA参数
        UVAR(21)=(UVAR(18))/(Xsigma/SQRT(3.0))
     &      *(UVAR(20)-UVAR(43))/2
     &      +(UVAR(17))/(Xsigma)
     &      *(UVAR(19)-UVAR(42))/2
c *** 找出最大的MGSA参数(UVAR22)            
            IF (UVAR(22).LE.UVAR(21)) THEN
                UVAR(22)=UVAR(21)
                UVAR(23)=180.0*theta/PI
                UVAR(24)=180.0*phi/PI
                UVAR(25)=180.0*alpha/PI                
            ELSE
                GO TO 4100
            ENDIF              
4100        CONTINUE    
         end do
        end do       
       end do       
      ENDIF   
      
c************************************************************************* 
c ***获得第一段保载后的场变量
      IF (mod(KSTEP-2,3) .eq. 0) THEN
c ***读取温度
      call getvrm('SDV',array,jarray,flgray,jrcd,jmac,jmatyp,matlayo
     &            ,laccfla)
        jerror = jerror + jrcd
        UVAR(80)= array(6)
c ***每个KINC增加的蠕变应变
      call getvrm('CE',array,jarray,flgray,jrcd,jmac,jmatyp,matlayo
     &            ,laccfla)
        jerror = jerror + jrcd
        VVHP5 = (array(1)+array(2)+array(3))/3.0
        temp5 = (array(1)-VVHP5)**2.0+(array(2)-VVHP5)**2.0
     &   +(array(3)-VVHP5)**2.0
        temp5 = temp5+0.5*(array(4)**2.0+array(5)**2.0+array(6)**2.0)
        temp5 = temp5 * 2.0/3.0
        VCE1= UVAR(26)
        UVAR(26)= SQRT(temp5)
        UVAR(27)= UVAR(26)-VCE1 
c ***每个KINC的所需的时间增量
        UVAR(28)=DTIME
c ***每个KINC的能量密度耗散率 
        IF (UVAR(28) .NE. 0) then
        UVAR(29) = UVAR(5)*UVAR(27)/ UVAR(28)        
c ***计算该能量耗散率条件下的失效应变能密度
        UVAR(30)=abs(UVAR(15)*2.931377*exp(28.15/(0.008314*(UVAR(80)
     &  +273.15)))*UVAR(29)**temp_n1)
c        UVAR(30)=abs(UVAR(15)*fai*UVAR(29)**temp_n1)
c ***每个KINC真实的失效应变能密度          
        UVAR(31)=abs(min(UVAR(30),wfcrit)) 
c *** 每个KINC的蠕变损伤
        UVAR(32)=abs ((UVAR(29)/UVAR(31)-UVAR(29)/wfcrit)*(UVAR(28))) 
c *** 一个周次蠕变损伤的叠加
        UVAR(33)=UVAR(33) + UVAR(32)       
        ENDIF
      ENDIF

c*************************************************************************          
c结算第一个保载后的疲劳和蠕变损伤 
c************************************************************************* 
      IF ((mod(KSTEP-3,3) .eq. 0) .and. (KINC .eq. 1)) THEN   
c *** 计算第一段的MGSA纯疲劳寿命   多轴疲劳-临界平面法
      DO xnf=1,xnfmax,0.5
         XR=(Xsigma/SQRT(3.0))/(E_eff/3.0)*(2.0*xnf)**(2*b0)+
     &    (Xepsilon*SQRT(3.0))*(2.0*xnf)**(c0)
         XD=abs(XR-UVAR(22))

 
c*** 由matlab算得大概十万分之一合适
         IF (XD.LE.1E-5) THEN
         UVAR(34)=xnf 
         GO TO 100
         END IF
      END DO
  100 CONTINUE
      IF (UVAR(34).EQ.0) THEN
          UVAR(34)=xnfmax
      END IF
      
c *** 计算一个周次的疲劳损伤
         UVAR(35)=one/ UVAR(34)
         write (7,*) 'one=', one
c *** 计算累积的蠕变损伤
         UVAR(36)=UVAR(33)+UVAR(36)
c *** 计算累积的疲劳损伤
         UVAR(37)=UVAR(35)+UVAR(37)
c *** 计算一个周次的蠕变疲劳损伤
         UVAR(38)=UVAR(33)+UVAR(35)
c *** 计算累积的蠕变疲劳总损伤         
         UVAR(39)=UVAR(36)+UVAR(37)
      ENDIF
c *** 结算第一个保载后的疲劳和蠕变损伤 
      IF ((mod(KSTEP-3,3) .eq. 0) .and. (KINC .eq. 2)) THEN  
c *** 置零
         UVAR(22)=0
         UVAR(33)=0              
      ENDIF

      
c**********************************************************************     
      
C If error, write comment to .DAT file:
      IF(JRCD.NE.0)THEN
       WRITE(6,*) 'REQUEST ERROR IN UVARM FOR ELEMENT NUMBER ',
     1     NOEL,'INTEGRATION POINT NUMBER ',NPT
      ENDIF


       
      RETURN
      END



































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































