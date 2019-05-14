# -*- coding: utf-8 -*-
"""
Created on Fri Mar 22 15:20:57 2019

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
  
for n in range(N):        
    
    p_rand_coef1=np.random.uniform(0.88,1.12,20)
    p_rand_coef2=np.random.uniform(0.45,1.55,52)   
    p_rand_coef3=np.random.uniform(0.75,1.25,24)

    q_rand_coef1=np.random.uniform(0.98,1.02,20)
    q_rand_coef2=np.random.uniform(0.85,1.15,52)   
    q_rand_coef3=np.random.uniform(0.95,1.05,24)     
    
    pv_rand_coef=np.random.uniform(0.5,1.15,96)

    p_coef_arr=np.concatenate((p_rand_coef1,p_rand_coef2,p_rand_coef3))
    q_coef_arr=np.concatenate((q_rand_coef1,q_rand_coef2,q_rand_coef3))
    pv_coef_arr=pv_rand_coef
        
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


writer = pd.ExcelWriter("DeviationScenarios3.xlsx")
p_dataf.to_excel(writer,'PDemDev')
q_dataf.to_excel(writer,'QDemDev')
pv_dataf.to_excel(writer,'PVPotDev')
writer.save()

        