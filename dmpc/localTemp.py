# -*- coding: utf-8 -*-
"""
Created on Tue Mar 12 12:26:43 2019

@author: egu
"""
import numpy as np
from pyomo.core import Var
import pyomo.kernel as pmo
from pyomo.environ import *

class TempLocalAgent(object):
    
    def __init__(self,ref,fore,devi,flex):
       
        self.ref =dict(enumerate(ref ))  #Reference curve for consumption through prediction horizon
        self.fore=dict(enumerate(fore))  #Consumption forecast
        self.devi=dict(enumerate(devi))  #Consumption forecast error
        self.flex=dict(enumerate(flex))  #Consumption flexibility 

        self.Np=len(self.ref) #Prediction horizon for the optimization problem        
        self.results={} #Temp dictionary for data handling
                
    def optimize(self,solver):
        
        model = ConcreteModel()        
        model.Np=RangeSet(0,self.Np-1)
        
        #Parameters      
        model.x_for =Param(model.Np,initialize=self.fore)
        model.v     =Param(model.Np,initialize=self.devi)
        model.f     =Param(model.Np,initialize=self.flex)
        model.w     =Param(model.Np,initialize=self.ref)
        
        #Variables
        model.u     =Var(model.Np,domain=pmo.Binary)
        model.x_real=Var(model.Np)
        
        #Constraints
        def controlRule(model,k):
            return model.x_real[k]==model.x_for[k]+model.v[k]+model.f[k]*model.u[k]
        model.pcc=Constraint(model.Np,rule=controlRule)
        
        #Objective
        def objRule(model):
            return sum((model.w[k]-model.x_real[k])*(model.w[k]-model.x_real[k]) for k in model.Np)
        model.obj=Objective(rule=objRule)
        
        Optresult =solver.solve(model)
        
        #Saving the results to the self.result attribute
        pcc=[]
        u=[]
        for k in model.Np:
            pcc.append(model.x_real[k]())
            u.append(0.0 if model.u[k]()==None else model.u[k]())
        
        self.results['pcc']=np.array(pcc)
        self.results['u']=np.array(u)

        #print(Optresult.solver.status, Optresult.solver.termination_condition)
        