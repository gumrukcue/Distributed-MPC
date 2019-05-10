# -*- coding: utf-8 -*-
"""
Created on Wed Apr 10 13:35:24 2019

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

print("Saving data")
worksheets={}
for i in range(500):
    worksheets[5*i+1]=xl_file.parse("Tabelle1")
    worksheets[5*i+2]=xl_file.parse("Tabelle2")
    worksheets[5*i+3]=xl_file.parse("Tabelle3")
    worksheets[5*i+4]=xl_file.parse("Tabelle4")
    worksheets[5*i+5]=xl_file.parse("Tabelle5")
print("Saved")


def repetitive_simulations(numberOfSimulations,clusterSize):
    
    predictionHorizon=4
    solver= SolverFactory("gurobi")
    forecast_dict={}
    deviation_dict={}
    flexibility_dict={}
        
    print()
    print("Cluster size",clusterSize)
    
    print("Constructing the dictionaries")
    for i in range(1,clusterSize+1):
        forecast_dict[i]=worksheets[i]['Forecast'].values
        deviation_dict[i]=worksheets[i]['Deviation'].values
        flexibility_dict[i]=worksheets[i]['Flexibility'].values
 
    forecasts=pd.DataFrame(forecast_dict)
    deviation=pd.DataFrame(deviation_dict)
    flexibility=pd.DataFrame(flexibility_dict)
    print("Constructed")
    
    const_times={}
    op_times={}
    for n in range(numberOfSimulations):
        #print("Simulation",n)
          
        const_start=time.time()
        aHMPC=HDMPC(predictionHorizon,forecasts,deviation,flexibility)
        const_end=time.time()
        const_times[n]=const_end-const_start
               
        op_start=time.time()
        local_curves,switching_numbers,cluster_curve=aHMPC.hierarchical_control(solver,list(range(1,clusterSize+1)))
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

res05,minc05,avc05,maxc05,mino05,avo05,maxo05=repetitive_simulations(10,5)
res10,minc10,avc10,maxc10,mino10,avo10,maxo10=repetitive_simulations(10,10)
res15,minc15,avc15,maxc15,mino15,avo15,maxo15=repetitive_simulations(10,15)
res20,minc20,avc20,maxc20,mino20,avo20,maxo20=repetitive_simulations(10,20)
res25,minc25,avc25,maxc25,mino25,avo25,maxo25=repetitive_simulations(10,25)
res50,minc50,avc50,maxc50,mino50,avo50,maxo50=repetitive_simulations(10,50)
res100,minc100,avc100,maxc100,mino100,avo100,maxo100=repetitive_simulations(10,100)
res150,minc150,avc150,maxc150,mino150,avo150,maxo150=repetitive_simulations(10,150)
res200,minc200,avc200,maxc200,mino200,avo200,maxo200=repetitive_simulations(10,200)
#%%
res250,minc250,avc250,maxc250,mino250,avo250,maxo250=repetitive_simulations(10,250)
#res500,minc500,avc500,maxc500,mino500,avo500,maxo500=repetitive_simulations(10,500)
#res1000,minc1000,avc1000,maxc1000,mino1000,avo1000,maxo1000=repetitive_simulations(10,1000)

#%%
analysis = pd.DataFrame(index=[5,10,15,20,25,50,100], columns=['const_min','const_avr','const_max','opt_min','opt_avr','opt_max'])
analysis.loc[5]  =[minc05,avc05,maxc05,mino05,avo05,maxo05]
analysis.loc[10] =[minc10,avc10,maxc10,mino10,avo10,maxo10]
analysis.loc[15] =[minc15,avc15,maxc15,mino15,avo15,maxo15]
analysis.loc[20] =[minc20,avc20,maxc20,mino20,avo20,maxo20]
analysis.loc[25] =[minc25,avc25,maxc25,mino15,avo25,maxo25]
analysis.loc[50] =[minc50,avc50,maxc50,mino50,avo50,maxo50]
analysis.loc[100]=[minc100,avc100,maxc100,mino100,avo100,maxo100]
analysis.loc[150]=[minc150,avc150,maxc150,mino150,avo150,maxo150]
#analysis.loc[200]=[minc200,avc200,maxc200,mino200,avo200,maxo200]
#analysis.loc[250]=[minc250,avc250,maxc250,mino250,avo250,maxo250]
        