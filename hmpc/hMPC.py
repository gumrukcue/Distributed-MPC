# -*- coding: utf-8 -*-
"""
Created on Fri Mar 29 15:16:40 2019

@author: egu
"""

import numpy as np
import pandas as pd
import time
from hmpc.localTemp import DecomposedElement
from hmpc.centralTemp import AggregatedElement

class HDMPC(object):
    
    max_iteration=3
    alpha=0.05     #sub-gradient updaters
    
    def __init__(self,predHorizon,fores,devis,flexes,customRefCurve=False):
        
        self.prediction_horizon=predHorizon
        
        #Household data as data frames
        #e.g. fores
        #columns: household ID
        #value: individual consumption forecast as np.array
        self.consumption_forecasts=fores
        self.consumption_deviations=devis
        self.consumption_flexibilities=flexes
        
        if customRefCurve==False:
            #Cluster reference is aggregated cluster consumption forecast if not specified
            self.clusterReference=self.consumption_forecasts.sum(axis=1)
        else:
            self.clusterReference=customRefCurve
    
    def hierarchical_control(self,solver,agentIDs):
        
        temp_loc_curves=dict.fromkeys(agentIDs)     #Store local power curves' temporarily in the dictionary
        temp_loc_switch=dict.fromkeys(agentIDs)     #Store control variables' values temporarily in the dictionary
        uncontrolled_consumption=self.consumption_forecasts.sum(axis=1).values+self.consumption_deviations.sum(axis=1).values #The cluster would consume this much if nothing is controlled
        delta=np.zeros(self.prediction_horizon)      #Initialize the dual variables as zero 
        
        it=0                #iteration number                
                              
        start=time.time()
        while it<self.max_iteration:    
        
            agg_flexible_consumption=np.zeros(self.prediction_horizon)
            
            #Subgradient iterations
            #TODO: Paralel computing
            for i in agentIDs:               
                #Initialize the temporary local optimization object with flexibilites and dual variables
                flex_curve=self.consumption_flexibilities[i].values.tolist()
                aLocalAgent=DecomposedElement(delta,flex_curve)
                
                #Solve the problems to calculate power consumption due to local optimal flexibility use and switching states
                aLocalAgent.optimize(solver)                
                temp_loc_switch[i]=aLocalAgent.results['u']
                temp_loc_curves[i]=self.consumption_forecasts[i].values+self.consumption_deviations[i].values+aLocalAgent.results['p_flex']
                agg_flexible_consumption+=aLocalAgent.results['p_flex']

            #Cluster's aggregated power profile when local agents are coordinated with actual dual variables: delta
            cluster_total_consumption=uncontrolled_consumption+agg_flexible_consumption
            
            #In order to update the dual variables
            CentralAgent=AggregatedElement(delta,self.clusterReference)
            cluster_temp_consumption =CentralAgent.optimize(solver) #x^real,l+1
            delta=delta+self.alpha*cluster_total_consumption-self.alpha*cluster_temp_consumption

            it+=1           #Go to the next iteration
        
        end=time.time() #Stop the iteration if  convergence occurs
        #print('Converged in:',end-start)   

        coordinated_loc_curves=pd.DataFrame(temp_loc_curves)
        coordinated_loc_switch=pd.DataFrame(temp_loc_switch)
        coordinated_clu_curve=pd.DataFrame(cluster_total_consumption)
        
        return coordinated_loc_curves,coordinated_loc_switch,coordinated_clu_curve
          

if __name__=="__main__":            
    import pandas as pd
    from pyomo.environ import *
    
    filename='dmpc_testdata.xlsx'
    xl_file = pd.ExcelFile(filename)   
    
    
    worksheets={}
    worksheets[1]=xl_file.parse("Tabelle1")
    worksheets[2]=xl_file.parse("Tabelle2")
    worksheets[3]=xl_file.parse("Tabelle3")
    worksheets[4]=xl_file.parse("Tabelle4")
    worksheets[5]=xl_file.parse("Tabelle5")

    predictionHorizon=4
    forecast_dict={}
    deviation_dict={}
    flexibility_dict={}
    
    for i in range(1,6):
        forecast_dict[i]=worksheets[i]['Forecast'].values
        deviation_dict[i]=worksheets[i]['Deviation'].values
        flexibility_dict[i]=worksheets[i]['Flexibility'].values
    
    forecasts=pd.DataFrame(forecast_dict)
    deviation=pd.DataFrame(deviation_dict)
    flexibility=pd.DataFrame(flexibility_dict)
    
    aHDMPC=HDMPC(predictionHorizon,forecasts,deviation,flexibility)
    solver= SolverFactory("gurobi")
    
    local_curves,switching_numbers,cluster_curve=aHDMPC.hierarchical_control(solver,[1,2,3,4,5])

        

