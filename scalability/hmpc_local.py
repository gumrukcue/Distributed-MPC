# -*- coding: utf-8 -*-
"""
Created on Wed Apr 10 13:03:09 2019

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

def repetitive_simulations(numberOfSimulations,optimizationHorizon):
    
    print("For the optimization horizon",optimizationHorizon)
    
    flexibility=[4]*optimizationHorizon
    delta_signal=[0.2]*optimizationHorizon
    
    
    const_times={}
    op_times={}
    
    for n in range(numberOfSimulations):
        print("Simulation",n)
                
        const_start=time.time()
        aLocalAgent=DecomposedElement(delta_signal,flexibility)
        const_end=time.time()
        const_times[n]=const_end-const_start

        op_start=time.time()
        aLocalAgent.optimize(solver)
        op_end=time.time()
        op_times[n]=op_end-op_start
        
    time_record=pd.DataFrame({'Construction':const_times,'Optimization':op_times})
    min_const=time_record['Construction'].min()
    mean_const=time_record['Construction'].mean()
    max_const=time_record['Construction'].max()
    min_opt=time_record['Optimization'].min()
    mean_opt=time_record['Optimization'].mean()
    max_opt=time_record['Optimization'].max()
    
    return time_record,min_const,mean_const,max_const,min_opt,mean_opt,max_opt

    
res04,minc04,avc04,maxc04,mino04,avo04,maxo04=repetitive_simulations(100,4)
res08,minc08,avc08,maxc08,mino08,avo08,maxo08=repetitive_simulations(100,8)
res12,minc12,avc12,maxc12,mino12,avo12,maxo12=repetitive_simulations(100,12)
res16,minc16,avc16,maxc16,mino16,avo16,maxo16=repetitive_simulations(100,16)
res24,minc24,avc24,maxc24,mino24,avo24,maxo24=repetitive_simulations(100,24)
res48,minc48,avc48,maxc48,mino48,avo48,maxo48=repetitive_simulations(100,48)
res96,minc96,avc96,maxc96,mino96,avo96,maxo96=repetitive_simulations(100,96)

#%%
analysis = pd.DataFrame(index=[4,8,12,16,24,48], columns=['const_min','const_avr','const_max','opt_min','opt_avr','opt_max'])
analysis.loc[4] =[minc04,avc04,maxc04,mino04,avo04,maxo04]
analysis.loc[8] =[minc08,avc08,maxc08,mino08,avo08,maxo08]
analysis.loc[12]=[minc12,avc12,maxc12,mino12,avo12,maxo12]
analysis.loc[16]=[minc16,avc16,maxc16,mino16,avo16,maxo16]
analysis.loc[24]=[minc24,avc24,maxc24,mino24,avo24,maxo24]
analysis.loc[48]=[minc48,avc48,maxc48,mino48,avo48,maxo48]
analysis.loc[96]=[minc96,avc96,maxc96,mino96,avo96,maxo96]


