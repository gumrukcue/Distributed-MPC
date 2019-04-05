# -*- coding: utf-8 -*-
"""
Created on Mon Mar 18 09:14:51 2019

@author: egu
"""

import pandas as pd
import numpy as np

from classes.BES import BES
from classes.Forecast import Forecast
from classes.HD import HeatingDevice
from classes.PV import PV
from classes.TES import TES
from classes.Timer import Timer
from rescheduling.localoptimization import BESOptimizer
from rescheduling.clusteroptimization import ClusterOptimizer

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
HD16=HeatingDevice(aTimer,pnom1,qnom1)
HD26=HeatingDevice(aTimer,pnom2,qnom2)

#Thermal energy storage
tes_capacity=75 #kWh       
tes_maxQDis=7.5 #kW_th
TES1=TES(aTimer,tes_capacity,tes_maxQDis)
TES2=TES(aTimer,tes_capacity,tes_maxQDis)
TES3=TES(aTimer,tes_capacity,tes_maxQDis)
TES4=TES(aTimer,tes_capacity,tes_maxQDis)
TES5=TES(aTimer,tes_capacity,tes_maxQDis)
TES6=TES(aTimer,tes_capacity,tes_maxQDis)

#PV
pv_pmax=5   #kW
PV1=PV(aTimer,pv_pmax)
PV2=PV(aTimer,pv_pmax)
PV3=PV(aTimer,pv_pmax)
PV4=PV(aTimer,pv_pmax)
PV5=PV(aTimer,pv_pmax)
PV6=PV(aTimer,pv_pmax)

#BES
BES1=BES(aTimer,Forecast1,HD11,HD21,TES1,PV1)
BES2=BES(aTimer,Forecast2,HD12,HD22,TES2,PV2)
BES3=BES(aTimer,Forecast3,HD13,HD23,TES3,PV3)
BES4=BES(aTimer,Forecast4,HD14,HD24,TES4,PV4)
BES5=BES(aTimer,Forecast5,HD15,HD25,TES5,PV5)
BES6=BES(aTimer,Forecast6,HD16,HD26,TES6,PV6)

#Assigning initial soc to the TES object
BES1.tes.set_soc(aTimer.start,0.4)
BES2.tes.set_soc(aTimer.start,0.3)
BES3.tes.set_soc(aTimer.start,0.5)
BES4.tes.set_soc(aTimer.start,0.1)
BES5.tes.set_soc(aTimer.start,0.9)
BES6.tes.set_soc(aTimer.start,0.7)

#Assigning parameters to the forecast object
filename='data_forecasts.xlsx'
xl_file = pd.ExcelFile(filename)
df_forecast=xl_file.parse('Example')
BES1.forecast.set_P_demand_forecast(aTimer.start,df_forecast['P_Dmnd'].values)
BES2.forecast.set_P_demand_forecast(aTimer.start,df_forecast['P_Dmnd'].values)
BES3.forecast.set_P_demand_forecast(aTimer.start,df_forecast['P_Dmnd'].values)
BES4.forecast.set_P_demand_forecast(aTimer.start,df_forecast['P_Dmnd'].values)
BES5.forecast.set_P_demand_forecast(aTimer.start,df_forecast['P_Dmnd'].values)
BES6.forecast.set_P_demand_forecast(aTimer.start,df_forecast['P_Dmnd'].values)

BES1.forecast.set_Q_demand_forecast(aTimer.start,df_forecast['Q_Dmnd'].values)
BES2.forecast.set_Q_demand_forecast(aTimer.start,df_forecast['Q_Dmnd'].values)
BES3.forecast.set_Q_demand_forecast(aTimer.start,df_forecast['Q_Dmnd'].values)
BES4.forecast.set_Q_demand_forecast(aTimer.start,df_forecast['Q_Dmnd'].values)
BES5.forecast.set_Q_demand_forecast(aTimer.start,df_forecast['Q_Dmnd'].values)
BES6.forecast.set_Q_demand_forecast(aTimer.start,df_forecast['Q_Dmnd'].values)

BES1.forecast.set_PV_pot_forecast(aTimer.start,df_forecast['PV_Gen'].values)
BES2.forecast.set_PV_pot_forecast(aTimer.start,df_forecast['PV_Gen'].values)
BES3.forecast.set_PV_pot_forecast(aTimer.start,df_forecast['PV_Gen'].values)
BES4.forecast.set_PV_pot_forecast(aTimer.start,df_forecast['PV_Gen'].values)
BES5.forecast.set_PV_pot_forecast(aTimer.start,df_forecast['PV_Gen'].values)
BES6.forecast.set_PV_pot_forecast(aTimer.start,df_forecast['PV_Gen'].values)

#Choose a solver
from pyomo.environ import *
solver= SolverFactory("gurobi")

besdict={1:BES1,2:BES2,3:BES3,4:BES4,5:BES5,6:BES6}

#Initialize an optimization class
#For a zero energy cluster
referencecurve=np.zeros(96)
clustOpt=ClusterOptimizer(aTimer,besdict,referencecurve)
result=clustOpt.findClusterOptimal(solver)
