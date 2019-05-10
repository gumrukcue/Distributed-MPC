# -*- coding: utf-8 -*-
"""
Created on Fri Apr 12 16:40:13 2019

@author: egu
"""

from pyomo.environ import *
import numpy as np
import pandas as pd
from dmpc.localTemp import TempLocalAgent
from dmpc.dMPC import DMPC
import time
    
filename='testdata_dmpc_coordinated.xlsx'
xl_file = pd.ExcelFile(filename)   

print("Saving data")
worksheets={}
for i in range(21):
    worksheets[5*i+1]=xl_file.parse("Tabelle1")
    worksheets[5*i+2]=xl_file.parse("Tabelle2")
    worksheets[5*i+3]=xl_file.parse("Tabelle3")
    worksheets[5*i+4]=xl_file.parse("Tabelle4")
    worksheets[5*i+5]=xl_file.parse("Tabelle5")
print("Saved")


def repetitive_simulations(numberOfSimulations,clusterSize):
    print()
    print("Cluster size",clusterSize)
    solver= SolverFactory("gurobi")
    predictionHorizons=[4,8,12,16,24,48,96]

    time_record={}
    for T in predictionHorizons:
        
        print("Prediction horizon",T)
        forecast_dict={}
        deviation_dict={}
        flexibility_dict={}
        aggregated_curve_reference=np.zeros(T)
        
        for i in range(1,clusterSize+1):
            forecast_dict[i]=worksheets[i]['Forecast'].values[:T]
            deviation_dict[i]=worksheets[i]['Deviation'].values[:T]
            flexibility_dict[i]=worksheets[i]['Flexibility'].values[:T]
            aggregated_curve_reference+=forecast_dict[i]   
                       
        forecasts=pd.DataFrame(forecast_dict)
        deviation=pd.DataFrame(deviation_dict)
        flexibility=pd.DataFrame(flexibility_dict)
                  
        op_times=[]
        
        for n in range(numberOfSimulations):
            print("Simulation",n)
              
            aDMPC=DMPC(T,forecasts,deviation,flexibility)
                   
            op_start=time.time()
            res1,res2,restr=aDMPC.distributed_control(solver,list(range(1,clusterSize+1)))
            op_end=time.time()
            op_times.append(op_end-op_start)
              
        mean_opt=sum(op_times)/numberOfSimulations
        
        
        time_record[T]=mean_opt
    
    return time_record


res05=repetitive_simulations(10,5)
res10=repetitive_simulations(10,10)
res15=repetitive_simulations(10,15)
res20=repetitive_simulations(10,20)
res25=repetitive_simulations(10,25)
res50=repetitive_simulations(10,50)
res100=repetitive_simulations(10,100)

analysis = pd.DataFrame(columns=[4,8,12,16,24,48,96])
#%%
analysis.loc[5]  =res05
analysis.loc[10]  =res10
analysis.loc[15]  =res15
analysis.loc[20]  =res20
analysis.loc[25]  =res25
analysis.loc[50]  =res50
analysis.loc[100]  =res100
