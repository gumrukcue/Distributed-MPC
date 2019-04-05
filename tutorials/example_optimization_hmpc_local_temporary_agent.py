# -*- coding: utf-8 -*-
"""
Created on Thu Apr  4 16:04:05 2019

@author: egu
"""



from pyomo.environ import *
import pandas as pd
from hmpc.localTemp import DecomposedElement
import time

import pandas as pd
from pyomo.environ import *

solver= SolverFactory("gurobi")
    
flexibility =[4,4,4,4,
              4,4,4,4,
              4,4,4,4,
              4,4,4,4]
delta_signal=[-0.5,-0.5,0.5,0.5,
              -0.5,-0.5,0.5,0.5,
              -0.5,-0.5,0.5,0.5,
              -0.5,-0.5,0.5,0.5,]

const_start=time.time()
aLocalAgent=DecomposedElement(delta_signal,flexibility)
const_end=time.time()
print("Constructing DecomposedElement object in",const_end-const_start,"seconds")

op_start=time.time()
aLocalAgent.optimize(solver)
op_end=time.time()
print("Solving local optimization problem (optimization horizon=16) in",op_end-op_start,"seconds")

#%%
print("Flexibility use depend on the sign of delta")
print("i.e. negative sign of delta motivates more consumption")
print("i.e. positive sign of delta motivates more consumption")
res=aLocalAgent.results
results={}
results['delta']=delta_signal
results['flex']=flexibility
results['flexibity used']=res['u']
print(pd.DataFrame(results))