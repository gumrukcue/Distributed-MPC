# -*- coding: utf-8 -*-
"""
Created on Thu Apr  4 16:03:38 2019

@author: egu
"""

from pyomo.environ import *
import numpy as np
import pandas as pd
from hmpc.hMPC import HDMPC
from hmpc.localTemp import DecomposedElement
from hmpc.centralTemp import AggregatedElement
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
aHMPC=HDMPC(predictionHorizon,forecasts,deviation,flexibility)
const_end=time.time()
print("Constructing HMPC object in",const_end-const_start,"seconds")

solver= SolverFactory("gurobi")
print("Solving hierarchical distributed mpc problem with dual decomposition")

op_start=time.time()
local_curves,switching_numbers,cluster_curve=aHMPC.hierarchical_control(solver,[1,2,3,4,5])
op_end=time.time()
print("Optimization with 16 optimization horizon and 5 households is solved in",op_end-op_start,"seconds")
#%%
print("Cluster power curve:")
results=pd.DataFrame({'schedule':aggregated_curve_reference,
                     'uncontrolled':aggregated_curve_uncontrolled,
                     'hmpc':cluster_curve[0].values})
print(results)

