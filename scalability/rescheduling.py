# -*- coding: utf-8 -*-
"""
Created on Wed Apr 10 14:23:40 2019

@author: egu
"""

import pandas as pd
import numpy as np
import os
import copy

from classes.BES import BES
from classes.Forecast import Forecast
from classes.HD import HeatingDevice
from classes.PV import PV
from classes.TES import TES
from classes.Timer import Timer
from classes.localoptimization import BESOptimizer
from classes.clusteroptimization import ClusterOptimizer

from pyomo.environ import *
import time

timediscretization=900  #15 minutes
reschedulinghorizon=96  #1 day   
aTimer=Timer(2019,3,13,0,0,timediscretization,reschedulinghorizon)

def basicscenario():
    #Forecast Objects
    Forecast1=Forecast()
    Forecast2=Forecast()
    Forecast3=Forecast()
    Forecast4=Forecast()
    Forecast5=Forecast()
    
    #Heating Devices --> hd1:gas boiler &  hd2:heat pump
    pnom1=0    
    qnom1=5   
    pnom2=-1.67
    qnom2=7.5
    HD11=HeatingDevice(aTimer,pnom1,qnom1)
    HD21=HeatingDevice(aTimer,pnom2,qnom2)
    HD12=HeatingDevice(aTimer,pnom1,qnom1)
    HD22=HeatingDevice(aTimer,pnom2,qnom2)
    HD13=HeatingDevice(aTimer,pnom1,qnom1)
    HD23=HeatingDevice(aTimer,pnom2,qnom2)
    HD14=HeatingDevice(aTimer,pnom1,qnom1)
    HD24=HeatingDevice(aTimer,pnom2,qnom2)
    HD15=HeatingDevice(aTimer,pnom1,qnom1)
    HD25=HeatingDevice(aTimer,pnom2,qnom2)
    
    #Thermal energy storage
    tes_capacity=75 #kWh       
    tes_maxQDis=7.5 #kW_th
    TES1=TES(aTimer,tes_capacity,tes_maxQDis)
    TES2=TES(aTimer,tes_capacity,tes_maxQDis)
    TES3=TES(aTimer,tes_capacity,tes_maxQDis)
    TES4=TES(aTimer,tes_capacity,tes_maxQDis)
    TES5=TES(aTimer,tes_capacity,tes_maxQDis)
    
    #PV
    pv_pmax=5   #kW
    PV1=PV(aTimer,pv_pmax)
    PV2=PV(aTimer,pv_pmax)
    PV3=PV(aTimer,pv_pmax)
    PV4=PV(aTimer,pv_pmax)
    PV5=PV(aTimer,pv_pmax)
    
    #BES
    BES1=BES(aTimer,Forecast1,HD11,HD21,TES1,PV1)
    BES2=BES(aTimer,Forecast2,HD12,HD22,TES2,PV2)
    BES3=BES(aTimer,Forecast3,HD13,HD23,TES3,PV3)
    BES4=BES(aTimer,Forecast4,HD14,HD24,TES4,PV4)
    BES5=BES(aTimer,Forecast5,HD15,HD25,TES5,PV5)
    
    #Assigning initial soc to the TES object
    BES1.tes.set_soc(aTimer.start,0.4)
    BES2.tes.set_soc(aTimer.start,0.3)
    BES3.tes.set_soc(aTimer.start,0.5)
    BES4.tes.set_soc(aTimer.start,0.1)
    BES5.tes.set_soc(aTimer.start,0.9)
    
    #Assigning parameters to the forecast object
    project_folder=os.path.dirname(os.path.dirname(__file__))
    scenario_folder=os.path.join(project_folder,'test_scenarios','002')
    file="00_00.xlsx"
    filename=os.path.join(scenario_folder,file)
    xl_file = pd.ExcelFile(filename)
    p_forecast =xl_file.parse('P_Demand')
    q_forecast =xl_file.parse('Q_Demand')
    pv_forecast=xl_file.parse('PV_Gen')

    BES1.forecast.set_P_demand_forecast(aTimer.start,p_forecast[1].values)
    BES2.forecast.set_P_demand_forecast(aTimer.start,p_forecast[2].values)
    BES3.forecast.set_P_demand_forecast(aTimer.start,p_forecast[3].values)
    BES4.forecast.set_P_demand_forecast(aTimer.start,p_forecast[4].values)
    BES5.forecast.set_P_demand_forecast(aTimer.start,p_forecast[5].values)
    
    BES1.forecast.set_Q_demand_forecast(aTimer.start,q_forecast[1].values)
    BES2.forecast.set_Q_demand_forecast(aTimer.start,q_forecast[2].values)
    BES3.forecast.set_Q_demand_forecast(aTimer.start,q_forecast[3].values)
    BES4.forecast.set_Q_demand_forecast(aTimer.start,q_forecast[4].values)
    BES5.forecast.set_Q_demand_forecast(aTimer.start,q_forecast[5].values)
    
    BES1.forecast.set_PV_pot_forecast(aTimer.start,pv_forecast[1].values)
    BES2.forecast.set_PV_pot_forecast(aTimer.start,pv_forecast[2].values)
    BES3.forecast.set_PV_pot_forecast(aTimer.start,pv_forecast[3].values)
    BES4.forecast.set_PV_pot_forecast(aTimer.start,pv_forecast[4].values)
    BES5.forecast.set_PV_pot_forecast(aTimer.start,pv_forecast[5].values)
    
    basicbesdict={1:BES1,2:BES2,3:BES3,4:BES4,5:BES5}

    return basicbesdict

basbess=basicscenario()

def repetitive_simulations(basicdict,numberOfSimulations,clusterSize):
    print()
    print("Cluster size",clusterSize*5)
    solver= SolverFactory("gurobi")

    basicbesdict=basicscenario()
    
    besdict=basicbesdict
    if clusterSize>1:
        for i in range(clusterSize):
            besdict[1+i*5]=copy.copy(besdict[1])
            besdict[2+i*5]=copy.copy(besdict[2])
            besdict[3+i*5]=copy.copy(besdict[3])
            besdict[4+i*5]=copy.copy(besdict[4])
            besdict[5+i*5]=copy.copy(besdict[5])

    print("BESs:",sorted(besdict.keys()))
    #Initialize an optimization class
    #For a zero energy cluster
    referencecurve=np.ones(96)
    
    const_times={}
    op_times={}
    for n in range(numberOfSimulations):
        #print("Simulation",n)
        const_start=time.time()
        clustOpt=ClusterOptimizer(aTimer,besdict,referencecurve)
        const_end=time.time()
        const_times[n]=const_end-const_start
               
        op_start=time.time()
        result=clustOpt.findClusterOptimal(solver)
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

res05,minc05,avc05,maxc05,mino05,avo05,maxo05=repetitive_simulations(basbess,1,1)
res10,minc10,avc10,maxc10,mino10,avo10,maxo10=repetitive_simulations(basbess,1,2)
res15,minc15,avc15,maxc15,mino15,avo15,maxo15=repetitive_simulations(basbess,1,3)
res20,minc20,avc20,maxc20,mino20,avo20,maxo20=repetitive_simulations(basbess,1,4)
res25,minc25,avc25,maxc25,mino25,avo25,maxo25=repetitive_simulations(basbess,1,5)
res50,minc50,avc50,maxc50,mino50,avo50,maxo50=repetitive_simulations(basbess,1,10)
res100,minc100,avc100,maxc100,mino100,avo100,maxo100=repetitive_simulations(basbess,1,20)
res150,minc150,avc150,maxc150,mino150,avo150,maxo150=repetitive_simulations(basbess,1,30)
res200,minc200,avc200,maxc200,mino200,avo200,maxo200=repetitive_simulations(basbess,1,40)
res250,minc250,avc250,maxc250,mino250,avo250,maxo250=repetitive_simulations(basbess,1,50)


#%%
analysis = pd.DataFrame(index=[5,10,15,20,25,50,100], columns=['const_min','const_avr','const_max','opt_min','opt_avr','opt_max'])
analysis.loc[5]  =[minc05,avc05,maxc05,mino05,avo05,maxo05]
analysis.loc[10] =[minc10,avc10,maxc10,mino10,avo10,maxo10]
analysis.loc[15] =[minc15,avc15,maxc15,mino15,avo15,maxo15]
analysis.loc[20] =[minc20,avc20,maxc20,mino20,avo20,maxo20]
analysis.loc[25] =[minc25,avc25,maxc25,mino15,avo25,maxo25]
analysis.loc[50] =[minc50,avc50,maxc50,mino50,avo50,maxo50]
analysis.loc[100]=[minc100,avc100,maxc100,mino100,avo100,maxo100]
#%%
analysis.loc[150]=[minc150,avc150,maxc150,mino150,avo150,maxo150]
analysis.loc[200]=[minc200,avc200,maxc200,mino200,avo200,maxo200]
analysis.loc[250]=[minc250,avc250,maxc250,mino250,avo250,maxo250]


    
    