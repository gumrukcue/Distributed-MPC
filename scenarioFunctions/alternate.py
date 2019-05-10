# -*- coding: utf-8 -*-
"""
Created on Fri Mar 22 08:22:45 2019

@author: egu
"""
import pandas as pd
import numpy as np
import os
from classes.Timer import Timer


def generate_scenario_data(timer,original_data_xl,pDem_dev,qDem_dev,pvPot_dev,scenarioName):
    
    ki=timer.start
    T= timer.T  
    
    basic_p_dmnd=original_data_xl.parse('P_Demand')
    basic_q_dmnd=original_data_xl.parse('Q_Demand')
    basic_pv_pot=original_data_xl.parse('PV_Gen')
    
    if not os.path.exists(scenarioName):
        os.mkdir(scenarioName)
    else:
        pass        
    current_folder=os.path.dirname(__file__)
    targetDirectory=os.path.join(current_folder,scenarioName)

    for t in range(T):
                
        start_ts=ki+t*timer.dT
        target_XL_name=os.path.join(targetDirectory,str(start_ts.strftime("%H_%M"))+'.xlsx')
        writer = pd.ExcelWriter(target_XL_name)
                                
        pDf =basic_p_dmnd[t:t+T].multiply(pDem_dev[start_ts])
        qDf =basic_q_dmnd[t:t+T].multiply(qDem_dev[start_ts])
        pvDf=basic_pv_pot[t:t+T].multiply(pvPot_dev[start_ts])

        pDf['ind_col'] =pd.Series([start_ts+k*timer.dT for k in range(T)], index=pDf.index)
        qDf['ind_col'] =pd.Series([start_ts+k*timer.dT for k in range(T)], index=pDf.index)
        pvDf['ind_col'] =pd.Series([start_ts+k*timer.dT for k in range(T)], index=pDf.index)
        
        pDf=pDf.set_index('ind_col')
        qDf=qDf.set_index('ind_col')
        pvDf=pvDf.set_index('ind_col')
        
        pDf.to_excel(writer,'P_Demand')
        qDf.to_excel(writer,'Q_Demand')
        pvDf.to_excel(writer,'PV_Gen')
    
        writer.save()
              
timediscretization=900  #15 minutes
reschedulinghorizon=96  #1 day   
aTimer=Timer(2019,3,13,0,0,timediscretization,reschedulinghorizon)

initialForecastFile='paper_initialforecast.xlsx'
xl_file = pd.ExcelFile(initialForecastFile)

deviation_file='paper_deviations_1.xlsx'
xl_file_dev   = pd.ExcelFile(deviation_file)
pdemdeviation = xl_file_dev.parse('PDemDev')
qdemdeviation = xl_file_dev.parse('QDemDev')
pvpotdeviation= xl_file_dev.parse('PVPotDev')

#%%
scenarioName='Scenarios/paper_new'
pDevDict =pdemdeviation[1]
qDevDict =qdemdeviation[0]
pvDevDict=pvpotdeviation[1]
generate_scenario_data(aTimer,xl_file,pDevDict,qDevDict,pvDevDict,scenarioName)
