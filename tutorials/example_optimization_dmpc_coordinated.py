# -*- coding: utf-8 -*-
"""
Created on Thu Apr  4 15:24:27 2019

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

worksheets={}
worksheets[1]=xl_file.parse("Tabelle1")
worksheets[2]=xl_file.parse("Tabelle2")
worksheets[3]=xl_file.parse("Tabelle3")
worksheets[4]=xl_file.parse("Tabelle4")
worksheets[5]=xl_file.parse("Tabelle5")

predictionHorizon=16
forecast_dict={}
deviation_dict={}
flexibility_dict={}

aggregated_curve_reference=np.zeros(predictionHorizon)
aggregated_curve_uncontrolled=np.zeros(predictionHorizon)
for i in range(1,6):
    forecast_dict[i]=worksheets[i]['Forecast'].values
    deviation_dict[i]=worksheets[i]['Deviation'].values
    flexibility_dict[i]=worksheets[i]['Flexibility'].values
    aggregated_curve_reference+=forecast_dict[i]
    aggregated_curve_uncontrolled+=forecast_dict[i]+deviation_dict[i]
    
forecasts=pd.DataFrame(forecast_dict)
deviation=pd.DataFrame(deviation_dict)
flexibility=pd.DataFrame(flexibility_dict)

const_start=time.time()
aDMPC=DMPC(predictionHorizon,forecasts,deviation,flexibility)
const_end=time.time()
print("Constructing DMPC object in",const_end-const_start,"seconds")

solver= SolverFactory("gurobi")
print("Solving distributed mpc problem ")
op_start=time.time()
res1,res2,restr=aDMPC.distributed_control(solver,[1,2,3,4,5])
op_end=time.time()
#%%
aggregated_curve_dmpc=restr[0].values
print("Optimization with 16 optimization horizon and 5 households is solved in",op_end-op_start,"seconds")
print("Cluster power curve:")
results=pd.DataFrame({'schedule':aggregated_curve_reference,
                     'uncontrolled':aggregated_curve_uncontrolled,
                     'dmpc':aggregated_curve_dmpc})
print(results)
