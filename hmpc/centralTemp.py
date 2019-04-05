# -*- coding: utf-8 -*-
"""
Created on Mon Apr  1 16:18:04 2019

@author: egu
"""

import numpy as np
from pyomo.core import Var
import pyomo.kernel as pmo
from pyomo.environ import *

class AggregatedElement(object):
    
    def __init__(self,delta,cluster_ref):
       
        self.delta =dict(enumerate(delta))       #Multipliers
        self.ref=dict(enumerate(cluster_ref))    #Cluster consumption reference

        self.Np=len(self.delta) #Prediction horizon for the optimization problem        
                
    def optimize(self,solver):
        
        model = ConcreteModel()        
        model.Np=RangeSet(0,self.Np-1)
        
        #Parameters      
        model.delta =Param(model.Np,initialize=self.delta)
        model.w     =Param(model.Np,initialize=self.ref)
        
        #Variables
        model.x_real=Var(model.Np)
               
        #Objective
        def objRule(model):
            return sum(((model.w[k]-model.x_real[k])*(model.w[k]-model.x_real[k]))-model.delta[k]*model.x_real[k] for k in model.Np)
        model.obj=Objective(rule=objRule)
        
        Optresult =solver.solve(model)
        
        #Saving the results to the self.result attribute
        x_real_new=[]
        for k in model.Np:
            x_real_new.append(model.x_real[k]())
        
        return np.array(x_real_new)

if __name__=="__main__":            
    import pandas as pd
    from pyomo.environ import *
    
    solver= SolverFactory("gurobi")
        
    reference =[2,2,3,2]
    delta_signal=[-0.5,-0.5,0.5,0.5]
    
    aLocalAgent=AggregatedElement(delta_signal,reference)
    result=aLocalAgent.optimize(solver)