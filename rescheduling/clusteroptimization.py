# -*- coding: utf-8 -*-
"""
Created on Mon Mar 18 09:00:50 2019

@author: egu
"""
import time
import numpy as np
import pandas as pd
from pyomo.environ import *

class ClusterOptimizer(object):
        
    def __init__(self,timer,besdict,customRefCurve):
        
        k_ini=timer.start
        self.T=timer.T
        self.deltaSec=timer.deltaSec
        self.clusterIndexSet=sorted(besdict.keys())
        self.clusterReference=dict(enumerate(customRefCurve.tolist()))
                
        self.PDmnd={}
        self.QDmnd={}
        self.PVGen={}
        self.Pnom1={}
        self.Qnom1={}
        self.Pnom2={}
        self.Qnom2={}
        self.tesCap={}
        self.tesQNom={}
        self.tesSoCMax={}
        self.tesSoCMin={}
        self.tesSoCIni={}
        
        for b in self.clusterIndexSet:

            for t in range(self.T):          
                self.PDmnd[b,t]=float(besdict[b].forecast.P[k_ini][t])   #Electric power demand forecast for the next forecasting horizon: kW array
                self.QDmnd[b,t]=float(besdict[b].forecast.Q[k_ini][t])   #Thermal power demand forecast for the next forecasting horizon: kW array
                self.PVGen[b,t]=float(besdict[b].forecast.PV[k_ini][t])  #PV generation forecast for the next forecasting horizon: kW array   
            #PV parameters
            #self.PVarrayMax=bes.pv.Pmax         #Maximum power output of PV array 
            
            #Thermo-electric device parameters
            self.Pnom1[b]=besdict[b].hd1.Pnom             #Nominal P power of heatingdevice1 kW_el
            self.Qnom1[b]=besdict[b].hd1.Qnom             #Nominal Q power of heatingdevice1 kW_th
            self.Pnom2[b]=besdict[b].hd2.Pnom             #Nominal P power of heatingdevice2 kW_el
            self.Qnom2[b]=besdict[b].hd2.Qnom             #Nominal Q power of heatingdevice2 kW_th
            
            #Thermal energy storage parameters
            self.tesCap[b]=besdict[b].tes.capacity        #Thermal energy storage capacity kW-sec
            self.tesQNom[b]=besdict[b].tes.maxQDis        #Nominal Q power of tes device of building energy system kW_th 
            self.tesSoCMax[b]=besdict[b].tes.maxSoC       #Maximum state of the charge tes type: float
            self.tesSoCMin[b]=besdict[b].tes.minSoC       #Minimum state of the charge tes type: float
    
            #Real parameters
            self.tesSoCIni[b]= besdict[b].tes.soc[k_ini]  #State-of-charge level of tes type: float
        
    def findClusterOptimal(self,solver):
     
        model           =ConcreteModel() 
        model.cluster   =Set(initialize=self.clusterIndexSet)
        model.horizon   =RangeSet(0,self.T-1)
        model.TSEhorizon=RangeSet(0,self.T)
        model.deltaSec  =Param(initialize=self.deltaSec)
        
        #Device parameters
        model.Pnom1     =Param(model.cluster,initialize=self.Pnom1)
        model.Qnom1     =Param(model.cluster,initialize=self.Qnom1)
        model.Pnom2     =Param(model.cluster,initialize=self.Pnom2)
        model.Qnom2     =Param(model.cluster,initialize=self.Qnom2)
        model.tesCap    =Param(model.cluster,initialize=self.tesCap)
        model.tesQNom   =Param(model.cluster,initialize=self.tesQNom)
        model.tesSoCMax =Param(model.cluster,initialize=self.tesSoCMax)
        model.tesSoCMin =Param(model.cluster,initialize=self.tesSoCMin)
        
        #Real time parameters
        model.iniSoC    =Param(model.cluster,initialize=self.tesSoCIni)
        model.cRef      =Param(model.horizon,initialize=self.clusterReference)
        
        #Forecast parameters
        model.pDmnd     =Param(model.cluster,model.horizon,initialize=self.PDmnd)
        model.qDmnd     =Param(model.cluster,model.horizon,initialize=self.QDmnd)
        model.pv        =Param(model.cluster,model.horizon,initialize=self.PVGen)
        
        #Variables
        model.modTh1    =Var(model.cluster,model.horizon,domain=NonNegativeReals,bounds=(0,1))                #Modulation level of modulatable thermo-electric device
        model.modTh2    =Var(model.cluster,model.horizon,domain=Binary)                                       #Modulation level of on-off thermo-electric device       
        model.modPV     =Var(model.cluster,model.horizon,domain=NonNegativeReals,bounds=(0,1),initialize=1)   #Utilization rate of home PV          
        model.Q_TSE     =Var(model.cluster,model.horizon,domain=Reals,initialize=0)                           #Thermal power from TSE to thermal load
        model.P_Grid    =Var(model.cluster,model.horizon,domain=Reals)                                        #Electric power from the grid
        
        #State variable: tes soc        
        def socbounds(model, b,t):
           return (model.tesSoCMin[b], model.tesSoCMax[b])       
        model.SOC       =Var(model.cluster,model.TSEhorizon,domain=NonNegativeReals,bounds=socbounds)  

        def obj_expression(model):
            return sum((model.cRef[t]-sum(model.P_Grid[b,t] for b in model.cluster))*(model.cRef[t]-sum(model.P_Grid[b,t] for b in model.cluster)) for t in model.horizon)
        model.OBJ = Objective(rule=obj_expression)
        
        def thermalBalance(model,b,t):
            return model.qDmnd[b,t]==model.Q_TSE[b,t]+model.modTh1[b,t]*model.Qnom1[b]+model.modTh2[b,t]*model.Qnom2[b]
        model.const1=Constraint(model.cluster,model.horizon,rule=thermalBalance)
            
        def powerBalance(model,b,t):
            return model.pDmnd[b,t]==model.P_Grid[b,t]+model.pv[b,t]*model.modPV[b,t]+model.modTh1[b,t]*model.Pnom1[b]+model.modTh2[b,t]*model.Pnom2[b]
        model.const2=Constraint(model.cluster,model.horizon, rule=powerBalance)
    
        def storageConservation(model,b,t):
            if t==0:
                return model.SOC[b,t]==model.iniSoC[b]
            else:
                return model.SOC[b,t]==(model.SOC[b,t - 1] - model.Q_TSE[b,t-1]/model.tesCap[b] *model.deltaSec)
        model.const3=Constraint(model.cluster,model.TSEhorizon,rule=storageConservation)

        start=time.time()
        results=solver.solve(model)
        end=time.time()
        #print('Rescheduled in:',end-start)

        optimization_results={}
        
        for b in model.cluster:
            impSch= [model.P_Grid[b,t]() for t in model.horizon]
            tesSch= [model.Q_TSE[b,t]() for t in model.horizon]     
            d1Sch = [model.modTh1[b,t]() for t in model.horizon]
            d2Sch = [model.modTh2[b,t]() for t in model.horizon]
            pvSch = [model.modPV[b,t]()*model.pv[b,t] for t in model.horizon]
            optimization_results[b] =pd.DataFrame(data={'P_Import':impSch,'Q_TES':tesSch,'Mod_hd1':d1Sch,'Mod_hd2':d2Sch,'PV_Gen':pvSch})
        
        return optimization_results