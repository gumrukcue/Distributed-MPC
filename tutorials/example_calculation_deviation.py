# -*- coding: utf-8 -*-
"""
Created on Mon Mar 25 10:59:37 2019

@author: egu
"""

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

solver= SolverFactory("gurobi")
timediscretization=900  #15 minutes
reschedulinghorizon=96  #1 day   
aTimer=Timer(2019,3,13,0,0,timediscretization,reschedulinghorizon)

#Forecast Object
Forecast1=Forecast()
Forecast2=Forecast()
Forecast3=Forecast()
#Heating Devices --> hd1:gas boiler &  hd2:heat pump
pnom1=0    
qnom1=7   
pnom2=-1.67
qnom2=7.5
HD11=HeatingDevice(aTimer,pnom1,qnom1)
HD21=HeatingDevice(aTimer,pnom2,qnom2)
HD12=HeatingDevice(aTimer,pnom1,qnom1)
HD22=HeatingDevice(aTimer,pnom2,qnom2)
HD13=HeatingDevice(aTimer.start,pnom1,qnom1)
HD23=HeatingDevice(aTimer.start,pnom2,qnom2)
#Thermal energy storage
tes_capacity=75 #kWh       
tes_maxQDis=7.5 #kW_th
TES1=TES(aTimer,tes_capacity,tes_maxQDis)
TES2=TES(aTimer,tes_capacity,tes_maxQDis)
TES3=TES(aTimer,tes_capacity,tes_maxQDis)
#PV
pv_pmax=5   #kW
PV1=PV(aTimer,pv_pmax)
PV2=PV(aTimer,pv_pmax)
PV3=PV(aTimer,pv_pmax)
#BES
BES1=BES(aTimer,Forecast1,HD11,HD21,TES1,PV1)
BES2=BES(aTimer,Forecast2,HD12,HD22,TES2,PV2)
BES3=BES(aTimer,Forecast3,HD13,HD23,TES3,PV3)
besdict={1:BES1,2:BES2,3:BES3}
mpcP=4
trigger=0.01
aCluster=Cluster(aTimer,mpcP,trigger,besdict)

#Assigning initial soc to the TES object
BES1.tes.set_soc(aTimer.start,0.4)
BES2.tes.set_soc(aTimer.start,0.3)
BES3.tes.set_soc(aTimer.start,0.5)

#Folder for forecast parameters
project_folder=os.path.dirname(os.path.dirname(__file__))
scenario_folder=os.path.join(project_folder,'test_scenarios','100')
print("Forecast parameters are taken from",scenario_folder)
print("Ini forecast: 00_00.xlsx")

ki=aTimer.start
file0=os.path.join(scenario_folder,'00_00.xlsx')
xl_file_0 = pd.ExcelFile(file0)
p_forecast0 =xl_file_0.parse('P_Demand')
q_forecast0 =xl_file_0.parse('Q_Demand')
pv_forecast0=xl_file_0.parse('PV_Gen')
BES1.forecast.set_P_demand_forecast(ki,p_forecast0[1].values)
BES2.forecast.set_P_demand_forecast(ki,p_forecast0[2].values)
BES3.forecast.set_P_demand_forecast(ki,p_forecast0[3].values)
BES1.forecast.set_Q_demand_forecast(ki,q_forecast0[1].values)
BES2.forecast.set_Q_demand_forecast(ki,q_forecast0[2].values)
BES3.forecast.set_Q_demand_forecast(ki,q_forecast0[3].values)
BES1.forecast.set_PV_pot_forecast(ki,pv_forecast0[1].values)
BES2.forecast.set_PV_pot_forecast(ki,pv_forecast0[2].values)
BES3.forecast.set_PV_pot_forecast(ki,pv_forecast0[3].values)

print("Timer updated")
print("Next forecast: 00_15.xlsx")
aTimer.updateTimer()
ki=aTimer.start
file1=os.path.join(scenario_folder,'00_15.xlsx')
xl_file_1 = pd.ExcelFile(file1)
p_forecast1 =xl_file_1.parse('P_Demand')
q_forecast1 =xl_file_1.parse('Q_Demand')
pv_forecast1=xl_file_1.parse('PV_Gen')
BES1.forecast.set_P_demand_forecast(ki,p_forecast1[1].values)
BES2.forecast.set_P_demand_forecast(ki,p_forecast1[2].values)
BES3.forecast.set_P_demand_forecast(ki,p_forecast1[3].values)
BES1.forecast.set_Q_demand_forecast(ki,q_forecast1[1].values)
BES2.forecast.set_Q_demand_forecast(ki,q_forecast1[2].values)
BES3.forecast.set_Q_demand_forecast(ki,q_forecast1[3].values)
BES1.forecast.set_PV_pot_forecast(ki,pv_forecast1[1].values)
BES2.forecast.set_PV_pot_forecast(ki,pv_forecast1[2].values)
BES3.forecast.set_PV_pot_forecast(ki,pv_forecast1[3].values)

aggregated_dev=aCluster.calculate_deviations(ki)
print("Forecast error detected at ki (for whole cluster):")
print(aggregated_dev)




