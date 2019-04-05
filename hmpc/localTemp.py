# -*- coding: utf-8 -*-
"""
Created on Fri Mar 29 14:56:02 2019

@author: egu
"""

import numpy as np
from pyomo.core import Var
import pyomo.kernel as pmo
from pyomo.environ import *

class DecomposedElement(object):
    
    def __init__(self,delta,flex):
       
        self.delta =dict(enumerate(delta)) #Reference curve for consumption through prediction horizon
        self.flex=dict(enumerate(flex))    #Consumption flexibility 

        self.Np=len(self.delta) #Prediction horizon for the optimization problem        
        self.results={}         #Temp dictionary for data handling
                
    def optimize(self,solver):
        
        model = ConcreteModel()        
        model.Np=RangeSet(0,self.Np-1)
        
        #Parameters      
        model.d     =Param(model.Np,initialize=self.delta)
        model.f     =Param(model.Np,initialize=self.flex)
        
        #Variables
        model.u     =Var(model.Np,domain=pmo.Binary)
        model.x_loc =Var(model.Np)
        
        #Constraints
        def controlRule(model,k):
            return model.x_loc[k]==model.d[k]*model.f[k]*model.u[k]
        model.pcc=Constraint(model.Np,rule=controlRule)
        
        #Objective
        def objRule(model):
            return sum(model.x_loc[k] for k in model.Np)
        model.obj=Objective(rule=objRule)
        
        Optresult =solver.solve(model)
        
        #Saving the results to the self.result attribute
        pcc=[]
        u=[]
        for k in model.Np:
            if model.u[k]()==None:
                pcc.append(0.0)
                u.append(0.0)
            else:
                pcc.append(model.f[k]*model.u[k]())
                u.append(model.u[k]())

        self.results['p_flex']=np.array(pcc)
        self.results['u']=np.array(u)

    

    
    