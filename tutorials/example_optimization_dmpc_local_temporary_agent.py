# -*- coding: utf-8 -*-
"""
Created on Thu Apr  4 15:20:50 2019

@author: egu
"""
from pyomo.environ import *
import pandas as pd
from dmpc.localTemp import TempLocalAgent
import time

  
solver= SolverFactory("gurobi")

filename='testdata_dmpc_local.xlsx'
xl_file = pd.ExcelFile(filename)   
worksheet=xl_file.parse("Tabelle1")

ref_curve=worksheet['Reference'].values
fore_curve=worksheet['Forecast'].values
devi_curve=worksheet['Deviation'].values
flex_curve=worksheet['Flexibility'].values

const_start=time.time()
aLocalAgent=TempLocalAgent(ref_curve,fore_curve,devi_curve,flex_curve)
const_end=time.time()
print("Constructing TempLocalAgent object in",const_end-const_start,"seconds")
print(worksheet)

op_start=time.time()
aLocalAgent.optimize(solver)
op_end=time.time()
print("Solving local optimization problem (optimization horizon=16) in",op_end-op_start,"seconds")
print("Results")

res=aLocalAgent.results
results=pd.DataFrame(res)
print(results)
