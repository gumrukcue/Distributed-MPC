# -*- coding: utf-8 -*-
"""
Created on Wed Mar 13 10:52:48 2019

@author: egu
"""
import numpy as np
import pandas as pd
import time
from pyomo.environ import *

class BESOptimizer(object):
    
    def __init__(self,bes):
        
        k_ini=bes.timer.start
        self.T=bes.timer.T
        self.deltaSec=bes.timer.deltaSec
        
        #Forecasts
        self.PDmnd=dict(enumerate(bes.forecast.P[k_ini].tolist()))    #Electric power demand forecast for the next forecasting horizon: kW array
        self.QDmnd=dict(enumerate(bes.forecast.Q[k_ini].tolist()))   #Thermal power demand forecast for the next forecasting horizon: kW array
        self.PVGen=dict(enumerate(bes.forecast.PV[k_ini].tolist()))   #PV generation forecast for the next forecasting horizon: kW array

        #PV parameters
        #self.PVarrayMax=bes.pv.Pmax         #Maximum power output of PV array 

        #Thermo-electric device parameters
        self.Pnom1=bes.hd1.Pnom             #Nominal P power of heatingdevice1 kW_el
        self.Qnom1=bes.hd1.Qnom             #Nominal Q power of heatingdevice1 kW_th
        self.Pnom2=bes.hd2.Pnom             #Nominal P power of heatingdevice2 kW_el
        self.Qnom2=bes.hd2.Qnom             #Nominal Q power of heatingdevice2 kW_th
        
        #Thermal energy storage parameters
        self.tesCap=bes.tes.capacity        #Thermal energy storage capacity kW-sec
        self.tesQNom=bes.tes.maxQDis        #Nominal Q power of tes device of building energy system kW_th 
        self.tesSoCMax=bes.tes.maxSoC       #Maximum state of the charge tes type: float
        self.tesSoCMin=bes.tes.minSoC       #Minimum state of the charge tes type: float

        #Real parameters
        self.tesSoCIni= bes.tes.soc[k_ini]  #State-of-charge level of tes type: float
        
    def findLocalOptimal(self,solver,objective=0):
        
        locstart=time.time()
     
        model           =ConcreteModel()       
        model.horizon   =RangeSet(0,self.T-1)
        model.TSEhorizon=RangeSet(0,self.T)
        model.deltaSec  =Param(initialize=self.deltaSec)
        
        #Device parameters
        model.Pnom1     =Param(initialize=self.Pnom1)
        model.Qnom1     =Param(initialize=self.Qnom1)
        model.Pnom2     =Param(initialize=self.Pnom2)
        model.Qnom2     =Param(initialize=self.Qnom2)
        model.tesCap    =Param(initialize=self.tesCap)
        model.tesQNom   =Param(initialize=self.tesQNom)
        model.tesSoCMax =Param(initialize=self.tesSoCMax)
        model.tesSoCMin =Param(initialize=self.tesSoCMin)
        
        #Real time parameters
        model.iniSoC    =Param(initialize=self.tesSoCIni)
        
        #Forecast parameters
        model.pDmnd     =Param(model.horizon,initialize=self.PDmnd)
        model.qDmnd     =Param(model.horizon,initialize=self.QDmnd)
        model.pv        =Param(model.horizon,initialize=self.PVGen)
        
        #Variables
        model.modTh1    =Var(model.horizon,domain=NonNegativeReals,bounds=(0,1))                #Modulation level of modulatable thermo-electric device
        model.modTh2    =Var(model.horizon,domain=Binary)                                       #Modulation level of on-off thermo-electric device       
        model.modPV     =Var(model.horizon,domain=NonNegativeReals,bounds=(0,1),initialize=1)   #Utilization rate of home PV          
        model.Q_TSE     =Var(model.horizon,domain=Reals)                             #Thermal power from TSE to thermal load
        model.P_Grid    =Var(model.horizon,domain=Reals)                                        #Electric power from the grid

        #State variable: tes soc        
        model.SOC       =Var(model.TSEhorizon,domain=NonNegativeReals,bounds=(model.tesSoCMin,model.tesSoCMax))
           
        def obj_expression(model):
            if objective==0:    #Default local objective is minimization of the power exchange with grid
                return sum(model.P_Grid[t]*model.P_Grid[t] for t in model.horizon)
            elif objective==1:  #Local objective is minimization of PV curtailment (maximization of PV utilization)
                return sum((1-model.modPV[t])*model.pv[t] for t in model.horizon)
            else:
                #TODO: Code obj function: Minimization of switching events
                assert("Undefined objective function")
        model.OBJ = Objective(rule=obj_expression)
        
        def thermalBalance(model,t):
            return model.qDmnd[t]==model.Q_TSE[t]+model.modTh1[t]*model.Qnom1+model.modTh2[t]*model.Qnom2
        model.const1=Constraint(model.horizon,rule=thermalBalance)
            
        def powerBalance(model,t):
            return model.pDmnd[t]==model.P_Grid[t]+model.pv[t]*model.modPV[t]+model.modTh1[t]*model.Pnom1+model.modTh2[t]*model.Pnom2
        model.const2=Constraint(model.horizon, rule=powerBalance)
    
        def storageConservation(model,t):
            if t==0:
                return model.SOC[t]==model.iniSoC
            else:
                return model.SOC[t]==(model.SOC[t - 1] - model.Q_TSE[t-1]/model.tesCap *model.deltaSec )
        model.const3=Constraint(model.TSEhorizon,rule=storageConservation)
        
        #model.pprint()
        results=solver.solve(model)
        
        locend=time.time()
        print("Local opt finished",locend-locstart)
        
        
        impSch= [model.P_Grid[t]() for t in model.horizon]
        tesSch= [model.Q_TSE[t]() for t in model.horizon]      
        d1Sch=[model.modTh1[t]() for t in model.horizon]
        d2Sch=[model.modTh2[t]() for t in model.horizon]
        pvSch=[model.modPV[t]()*model.pv[t] for t in model.horizon]
        
        optimization_results=pd.DataFrame(data={'P_Import':impSch,'Q_TES':tesSch,
                                                'Mod_hd1':d1Sch,'Mod_hd2':d2Sch,'PV_Gen':pvSch})
        
        return optimization_results
           
           