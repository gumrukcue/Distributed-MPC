# -*- coding: utf-8 -*-
"""
Created on Wed Mar 27 12:58:03 2019

@author: egu
"""
from datetime import date, datetime, timedelta
import os
import pandas as pd
import numpy as np
from pyomo.environ import *

from classes.Cluster import Cluster
from classes.BES import BES
from classes.Forecast import Forecast
from classes.HD import HeatingDevice
from classes.PV import PV
from classes.TES import TES
from classes.Timer import Timer
from rescheduling.localoptimization import BESOptimizer
from rescheduling.clusteroptimization import ClusterOptimizer
from simulations.analysis_functions import complete_analysis

#%%
solver= SolverFactory("gurobi")
timediscretization=900  #15 minutes
reschedulinghorizon=96  #1 day   
aTimer=Timer(2019,3,13,0,0,timediscretization,reschedulinghorizon)

#Forecast Object
Forecast1=Forecast()
Forecast2=Forecast()
Forecast3=Forecast()
Forecast4=Forecast()
Forecast5=Forecast()
Forecast6=Forecast()
Forecast7=Forecast()
Forecast8=Forecast()
Forecast9=Forecast()
Forecast10=Forecast()

pnom_boiler=0
qnom_boiler=7
pnom_hp=-1.67
qnom_hp=7.5
pnom_chp=0.5
qnom_chp=1.5
pnom_no=0
qnom_no=0.00001
    
HD1_01=HeatingDevice(aTimer,pnom_boiler,qnom_boiler)
HD1_02=HeatingDevice(aTimer,pnom_boiler,qnom_boiler)
HD1_03=HeatingDevice(aTimer,pnom_boiler,qnom_boiler)
HD1_04=HeatingDevice(aTimer,pnom_boiler,qnom_boiler)
HD1_05=HeatingDevice(aTimer,pnom_boiler,qnom_boiler)
HD1_06=HeatingDevice(aTimer,pnom_boiler,qnom_boiler)
HD1_07=HeatingDevice(aTimer,pnom_boiler,qnom_boiler)
HD1_08=HeatingDevice(aTimer,pnom_boiler,qnom_boiler)
HD1_09=HeatingDevice(aTimer,pnom_boiler,qnom_boiler)
HD1_10=HeatingDevice(aTimer,pnom_boiler,qnom_boiler)

HD2_01=HeatingDevice(aTimer,pnom_hp,qnom_hp)
HD2_02=HeatingDevice(aTimer,pnom_hp,qnom_hp)
HD2_03=HeatingDevice(aTimer,pnom_chp,qnom_chp)
HD2_04=HeatingDevice(aTimer,pnom_hp,qnom_hp)
HD2_05=HeatingDevice(aTimer,pnom_hp,qnom_hp)
HD2_06=HeatingDevice(aTimer,pnom_chp,qnom_chp)
HD2_07=HeatingDevice(aTimer,pnom_no,qnom_no)
HD2_08=HeatingDevice(aTimer,pnom_no,qnom_no)
HD2_09=HeatingDevice(aTimer,pnom_no,qnom_no)
HD2_10=HeatingDevice(aTimer,pnom_no,qnom_no)

#Thermal energy storage
tes_capacity=75 #kWh       
tes_maxQDis=7.5 #kW_th
TES1 =TES(aTimer,tes_capacity,tes_maxQDis)
TES2 =TES(aTimer,tes_capacity,tes_maxQDis)
TES3 =TES(aTimer,tes_capacity,tes_maxQDis)
TES4 =TES(aTimer,tes_capacity,tes_maxQDis)
TES5 =TES(aTimer,tes_capacity,tes_maxQDis)
TES6 =TES(aTimer,tes_capacity,tes_maxQDis)
TES7 =TES(aTimer,tes_capacity,tes_maxQDis)
TES8 =TES(aTimer,tes_capacity,tes_maxQDis)
TES9 =TES(aTimer,tes_capacity,tes_maxQDis)
TES10=TES(aTimer,tes_capacity,tes_maxQDis)

#PV
PV1 =PV(aTimer,2.3)
PV2 =PV(aTimer,2.7)
PV3 =PV(aTimer,5.2)
PV4 =PV(aTimer,3.0)
PV5 =PV(aTimer,1.7)
PV6 =PV(aTimer,1.9)
PV7 =PV(aTimer,2.1)
PV8 =PV(aTimer,2.2)
PV9 =PV(aTimer,3.0)
PV10=PV(aTimer,2.6)

BES1 =BES(aTimer,Forecast1 ,HD1_01,HD2_01,TES1 ,PV1)
BES2 =BES(aTimer,Forecast2 ,HD1_02,HD2_02,TES2 ,PV2)
BES3 =BES(aTimer,Forecast3 ,HD1_03,HD2_03,TES3 ,PV3)
BES4 =BES(aTimer,Forecast4 ,HD1_04,HD2_04,TES4 ,PV4)
BES5 =BES(aTimer,Forecast5 ,HD1_05,HD2_05,TES5 ,PV5)
BES6 =BES(aTimer,Forecast6 ,HD1_06,HD2_06,TES6 ,PV6)
BES7 =BES(aTimer,Forecast7 ,HD1_07,HD2_07,TES7 ,PV7)
BES8 =BES(aTimer,Forecast8 ,HD1_08,HD2_08,TES8 ,PV8)
BES9 =BES(aTimer,Forecast9 ,HD1_09,HD2_09,TES9 ,PV9)
BES10=BES(aTimer,Forecast10,HD1_10,HD2_10,TES10,PV10)

besdict={1:BES1,2:BES2,3:BES3,4:BES4,5:BES5,
         6:BES6,7:BES7,8:BES8,9:BES9,10:BES10}

mpcP=4
trigger=-10.01
aCluster=Cluster(aTimer,mpcP,trigger,besdict)

#Assigning initial soc to the TES object
BES1.tes.set_soc(aTimer.start,0.3)
BES2.tes.set_soc(aTimer.start,0.3)
BES3.tes.set_soc(aTimer.start,0.3)
BES4.tes.set_soc(aTimer.start,0.3)
BES5.tes.set_soc(aTimer.start,0.3)
BES6.tes.set_soc(aTimer.start,0.3)
BES7.tes.set_soc(aTimer.start,0.3)
BES8.tes.set_soc(aTimer.start,0.3)
BES9.tes.set_soc(aTimer.start,0.3)
BES10.tes.set_soc(aTimer.start,0.3)

#Assigning parameters to the forecast object
project_folder=os.path.dirname(os.path.dirname(__file__))
scenario_folder=os.path.join(project_folder,'test_scenarios','001')

#Continuous simulation
time_range=[aTimer.start+t*aTimer.dT for t in range(2)]#aTimer.T)]
for ts in time_range: 
    
    print(ts)
    file_name=str(ts.strftime("%H_%M"))+'.xlsx'
    
    file=os.path.join(scenario_folder,file_name)
    xl_file    =pd.ExcelFile(file)
    p_forecast =xl_file.parse('P_Demand')
    q_forecast =xl_file.parse('Q_Demand')
    pv_forecast=xl_file.parse('PV_Gen')
    
    for b in sorted(besdict.keys()):
        besdict[b].forecast.set_P_demand_forecast(ts,p_forecast[b].values)
        besdict[b].forecast.set_Q_demand_forecast(ts,q_forecast[b].values)
        besdict[b].forecast.set_PV_pot_forecast(ts,pv_forecast[b].values)
    
    aCluster.combined_method_d(ts,solver)
    aCluster.aggregate_performance_indicators(ts)
    aTimer.updateTimer()
    
#%%
#complete_analysis(aCluster,'dmpc_0.01')
df_clst=aCluster.cluster_optimal_cluster_curve[aCluster.initialstamp]
df_sepe=aCluster.cluster_optimal_schedules[aCluster.initialstamp]
df_flex=aCluster.cluster_optimal_flexibilities[aCluster.initialstamp]
writer=pd.ExcelWriter('Please.xlsx')
#df_clst.to_excel(writer,'Cluster')
df_sepe.to_excel(writer,'Import')
df_flex.to_excel(writer,'Flex')