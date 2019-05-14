# -*- coding: utf-8 -*-
"""
Created on Fri May 10 16:57:50 2019

@author: egu
"""

import pandas as pd
import numpy as np
import os
from classes.Timer import Timer


#PV forecast increases by 10
timediscretization=900  #15 minutes
reschedulinghorizon=96  #1 day   
aTimer=Timer(2019,3,13,0,0,timediscretization,reschedulinghorizon)

timestamps=[]
coefficients=[]
N=10 #number of scenarios

p_coef_dict=dict.fromkeys(list(range(N)))
q_coef_dict=dict.fromkeys(list(range(N)))
pv_coef_dict=dict.fromkeys(list(range(N)))

duration={2:1,4:3,6:6}
nb_of_devint= {2:8,4:4,6:4}
magnitude={2:0.25,4:0.35,6:0.6}  

dur_pv={2:4,4:4,6:4}
num_pv={2:2,4:2,6:4}
mag_pv=0.2

for n in range(1,N+1):        
    
    p_rand_coef1=np.ones(30)
    p_rand_coef3=np.ones(8)
    p_rand_coef5=np.ones(6)
    p_rand_coef7=np.ones(8)

    p_rand_coef2=np.concatenate(tuple([1-np.random.uniform(0,magnitude[2])]*duration[2] for i in range(nb_of_devint[2])))
    p_rand_coef4=np.concatenate(tuple([1+np.random.uniform(0,magnitude[4])]*duration[4] for i in range(nb_of_devint[4])))
    p_rand_coef6=np.concatenate(tuple([1-np.random.uniform(0,magnitude[6])]*duration[6] for i in range(nb_of_devint[6])))
       
    q_rand_coef1=np.random.uniform(0.98,1.02,20)
    q_rand_coef2=np.random.uniform(0.85,1.15,52)   
    q_rand_coef3=np.random.uniform(0.95,1.05,24)     
    
    pv_rand_coef1=np.ones(32)
    pv_rand_coef2=np.concatenate(tuple([1+np.random.uniform(0,mag_pv)]*dur_pv[2] for i in range(num_pv[2])))
    pv_rand_coef3=np.ones(4)
    pv_rand_coef4=np.concatenate(tuple([1-np.random.uniform(0,mag_pv)]*dur_pv[4] for i in range(num_pv[4])))
    pv_rand_coef5=np.ones(4)
    pv_rand_coef6=np.concatenate(tuple([1+np.random.uniform(0,mag_pv)]*dur_pv[6] for i in range(num_pv[6])))
    pv_rand_coef7=np.ones(24)

    p_coef_arr=np.concatenate((p_rand_coef1,p_rand_coef2,p_rand_coef3,p_rand_coef4,p_rand_coef5,p_rand_coef6,p_rand_coef7))
    q_coef_arr=np.concatenate((q_rand_coef1,q_rand_coef2,q_rand_coef3))
    pv_coef_arr=np.concatenate((pv_rand_coef1,pv_rand_coef2,pv_rand_coef3,pv_rand_coef4,pv_rand_coef5,pv_rand_coef6,pv_rand_coef7))
        
    p_coef_dict[n]={}
    q_coef_dict[n]={}
    pv_coef_dict[n]={}
    
    for t in range(aTimer.T):
        p_coef_dict[n][aTimer.start+t*aTimer.dT]=p_coef_arr[t]
        q_coef_dict[n][aTimer.start+t*aTimer.dT]=q_coef_arr[t]
        pv_coef_dict[n][aTimer.start+t*aTimer.dT]=pv_coef_arr[t]
                 
p_dataf=pd.DataFrame(p_coef_dict)
p_dataf[0] = pd.Series(np.ones(aTimer.T), index=p_dataf.index)
q_dataf=pd.DataFrame(q_coef_dict)
q_dataf[0] = pd.Series(np.ones(aTimer.T), index=q_dataf.index)
pv_dataf=pd.DataFrame(pv_coef_dict)
pv_dataf[0] = pd.Series(np.ones(aTimer.T), index=pv_dataf.index)


writer = pd.ExcelWriter("paper_deviations_3.xlsx")
p_dataf.to_excel(writer,'PDemDev')
q_dataf.to_excel(writer,'QDemDev')
pv_dataf.to_excel(writer,'PVPotDev')
writer.save()

        