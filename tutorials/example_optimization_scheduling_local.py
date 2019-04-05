# -*- coding: utf-8 -*-
"""
Created on Wed Mar 13 16:08:22 2019

@author: egu
"""
import pandas as pd
import numpy as np
import os

from classes.BES import BES
from classes.Forecast import Forecast
from classes.HD import HeatingDevice
from classes.PV import PV
from classes.TES import TES
from classes.Timer import Timer
from rescheduling.localoptimization import BESOptimizer

timediscretization=900  #15 minutes
reschedulinghorizon=96  #1 day   
aTimer=Timer(2019,3,13,0,0,timediscretization,reschedulinghorizon)

#Forecast Object
aForecast=Forecast()

#Heating Devices --> hd1:gas boiler &  hd2:heat pump
pnom1=0    
qnom1=5   
pnom2=-1.67
qnom2=7.5
HD1=HeatingDevice(aTimer,pnom1,qnom1)
HD2=HeatingDevice(aTimer,pnom2,qnom2)

#Thermal energy storage
tes_capacity=75 #kWh       
tes_maxQDis=7.5 #kW_th
aTES=TES(aTimer,tes_capacity,tes_maxQDis)

#PV
pv_pmax=5   #kW
aPV=PV(aTimer,pv_pmax)

#BES
aBES=BES(aTimer,aForecast,HD1,HD2,aTES,aPV)

#Assigning initial soc to the TES object
inisoc=0.1
aBES.tes.set_soc(aTimer.start,inisoc)

#Assigning parameters to the forecast object
project_folder=os.path.dirname(os.path.dirname(__file__))
scenario_folder=os.path.join(project_folder,'test_scenarios','002')

file=os.path.join(scenario_folder,"00_00.xlsx")
xl_file    =pd.ExcelFile(file)
p_forecast =xl_file.parse('P_Demand')
q_forecast =xl_file.parse('Q_Demand')
pv_forecast=xl_file.parse('PV_Gen')
aBES.forecast.set_P_demand_forecast(aTimer.start,p_forecast[1].values)
aBES.forecast.set_Q_demand_forecast(aTimer.start,q_forecast[1].values)
aBES.forecast.set_PV_pot_forecast(aTimer.start,pv_forecast[1].values)

#Choose a solver
from pyomo.environ import *
solver= SolverFactory("gurobi")

#Initialize an optimization class
besOpt=BESOptimizer(aBES)
optresults=besOpt.findLocalOptimal(solver,1)



