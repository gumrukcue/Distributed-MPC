# -*- coding: utf-8 -*-
"""
Created on Tue Mar 12 12:18:29 2019

@author: egu
"""

import numpy as np
import pandas as pd
import time
from dmpc.localTemp import TempLocalAgent

class DMPC(object):
    
    convergenceThreshold=0.001
    
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

    #TODO: remove agents if they are completely inflexible
    #TODO: sort_agents()
    #TODO: Convergence criteria    
    
    def distributed_control(self,solver,agentIDs):
        
        it=0                #iteration number        
        temp_loc_curve={}   #Temporary local curve
        temp_loc_switch={}  #Temporary local switching states 
        temp_loc_flag={}    #Temporary local convergence flag 
        temp_clus_curve=np.zeros(self.prediction_horizon) #Temporary cluster curve  
        
        for i in agentIDs:            
            temp_loc_switch[i]=np.zeros(self.prediction_horizon)
            temp_loc_flag[i]=0
            temp_loc_curve[i]=self.consumption_forecasts[i].values+self.consumption_deviations[i].values
            temp_clus_curve+=temp_loc_curve[i]
            
        convergence=False

        while convergence==False:
            start=time.time()
        
            #print('Iteration',it)        
            for i in agentIDs:
                temp_rest_curve=temp_clus_curve-temp_loc_curve[i]   #Temporary curve of the rest of the cluster
                temp_loc_ref=self.clusterReference-temp_rest_curve  #Temporary local reference curve
                
                #Initialize the temporary local optimization object with local forecast, deviation and flexibilites
                fore_curve=self.consumption_forecasts[i].values.tolist()
                devi_curve=self.consumption_deviations[i].values.tolist()
                flex_curve=self.consumption_flexibilities[i].values.tolist()
                aLocalAgent=TempLocalAgent(temp_loc_ref,fore_curve,devi_curve,flex_curve)
                
                #Solve the local optimization problem to calculate new temporary curves and switching states
                aLocalAgent.optimize(solver)                
                temp_loc_curve[i]=aLocalAgent.results['pcc']
                temp_loc_switch[i]=aLocalAgent.results['u']
                new_temp_clus_curve=temp_rest_curve+temp_loc_curve[i]  #The new cluster curve after local optimization
            
                #if all(temp_glob_sol_new==temp_glob_sol):
                #Check if the new temporary cluster curve is similar to the previous one
                if all(abs(temp_clus_curve-new_temp_clus_curve)<self.convergenceThreshold):
                    temp_loc_flag[i]=1  #Raise the local convergence flag
                else:
                    temp_loc_flag[i]=0
                                 
                temp_clus_curve=new_temp_clus_curve   #This will be sent to the next agent in the series calculations

            #Check if all the agents raised the local convergence flag
            if all(item==1 for item in list(temp_loc_flag.values())):
                convergence=True
                end=time.time() #Stop the iteration if global convergence occures
            else:
                convergence=False
                it+=1           #Go to the next iteration
        #print('Converged in:',end-start)   
        #print("DMPC converged after",it+1,"iterations")

        converged_loc_curves=pd.DataFrame(temp_loc_curve)
        converged_loc_switch=pd.DataFrame(temp_loc_switch)
        converged_clu_curve=pd.DataFrame(new_temp_clus_curve)
        
        return converged_loc_curves,converged_loc_switch,converged_clu_curve
          


        

