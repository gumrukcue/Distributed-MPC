# -*- coding: utf-8 -*-
"""
Created on Mon Mar 18 11:48:17 2019

@author: egu
"""

import numpy as np
import pandas as pd
from rescheduling.clusteroptimization import ClusterOptimizer
from rescheduling.localoptimization import BESOptimizer
from dmpc.localTemp import TempLocalAgent
from dmpc.dMPC import DMPC
from hmpc.centralTemp import AggregatedElement
from hmpc.localTemp import DecomposedElement
from hmpc.hMPC import HDMPC

class Cluster(object):

    def __init__(self,timer,mpc_prediction_horizon,trigger,besdict,facilitydict=None):
        
        self.initialstamp=timer.start
        
        self.timer=timer
        self.mpc_prediction_horizon=mpc_prediction_horizon
        self.besdict=besdict
        self.facilitydict=facilitydict
        self.triggering_threshold=trigger*(sum(besdict[b].pv.Pmax for b in besdict.keys()))
        
        self.local_optimal_schedules={}
        self.local_optimal_flexibilities={}
        self.local_optimal_cluster_curve={}
    
        self.cluster_optimal_schedules={}
        self.cluster_optimal_flexibilities={}
        self.cluster_optimal_cluster_curve={}
        
        self.cluster_deviations={} #Demand-Generation forecasting error
        
        self.if_rescheduled={}
        self.rescheduling_results={}
        self.dmpc_results={}
        self.hmpc_results={}
        
        self.cluster_pv_potential ={}
        self.cluster_pv_generation={}
        self.cluster_p_demand     ={}
        
    def aggregate_performance_indicators(self,ki):
        
        if not ki==self.initialstamp:
        
            self.cluster_pv_potential[ki] =0
            self.cluster_pv_generation[ki]=0
            self.cluster_p_demand[ki]     =0
           
            for b in sorted(self.besdict.keys()):
                bes=self.besdict[b]
                pv=bes.pv
                
                self.cluster_pv_potential[ki]+=pv.P_Pot[ki]
                self.cluster_pv_generation[ki]+=pv.P_Gen[ki]
                self.cluster_p_demand[ki]+=bes.Act_P_demand[ki]
                   
    def local_optimals(self,solver):
        #TODO: Works really slow in some cases
        
        ki=self.timer.start
        
        self.local_optimal_schedules[ki]=pd.DataFrame(index=list(range(self.mpc_prediction_horizon)),columns=sorted(self.besdict.keys()))
        self.local_optimal_flexibilities[ki]=pd.DataFrame(index=list(range(self.mpc_prediction_horizon)),columns=sorted(self.besdict.keys()))
        self.local_optimal_cluster_curve[ki]=np.zeros(self.mpc_prediction_horizon)
        
        for b in sorted(self.besdict.keys()):
            #print("Building",b)
            bes=self.besdict[b]
            besOpt=BESOptimizer(bes)
            local_optimal_results=besOpt.findLocalOptimal(solver)
            
            loc_opt_tesSch=local_optimal_results['Q_TES'][:self.mpc_prediction_horizon].values
            loc_opt_hdSch =local_optimal_results['Mod_hd2'][:self.mpc_prediction_horizon].values
            
            #print("Local optimal flexibility")
            self.local_optimal_flexibilities[ki][b]=bes.calculate_flexibility(ki,self.mpc_prediction_horizon,loc_opt_tesSch,loc_opt_hdSch)            
            self.local_optimal_schedules[ki][b]=local_optimal_results['P_Import'][:self.mpc_prediction_horizon]            
            self.local_optimal_cluster_curve[ki]+=self.local_optimal_schedules[ki][b].values   
    
    def reschedule(self,ki,solver):
        
        #print("Rescheduling for",ki)
        #TODO: Add arguments for different reference curves
        referencecurve=np.zeros(self.timer.T)
        central_rescheduler=ClusterOptimizer(self.timer,self.besdict,referencecurve)
        scheduling_results=central_rescheduler.findClusterOptimal(solver)

        self.cluster_optimal_schedules[ki]=pd.DataFrame(index=list(range(self.timer.T)),columns=sorted(self.besdict.keys()))
        self.cluster_optimal_flexibilities[ki]=pd.DataFrame(index=list(range(self.timer.T)),columns=sorted(self.besdict.keys()))
        self.cluster_optimal_cluster_curve[ki]=np.zeros(self.timer.T)
              
        for b in sorted(self.besdict.keys()):
            bes=self.besdict[b]
            
            cls_opt_tesSch=scheduling_results[b]['Q_TES'].values
            cls_opt_hdSch =scheduling_results[b]['Mod_hd2'].values          

            self.cluster_optimal_flexibilities[ki][b]=bes.calculate_flexibility(ki,self.timer.T,cls_opt_tesSch,cls_opt_hdSch)            
            self.cluster_optimal_schedules[ki][b]=scheduling_results[b]['P_Import']
            self.cluster_optimal_cluster_curve[ki]+=self.cluster_optimal_schedules[ki][b].values
            
        self.rescheduling_results[ki]=scheduling_results 

    def calculate_deviations(self,ki):        
                
        cluster_dev=np.zeros(self.mpc_prediction_horizon)
        deviations={}      
        for b in sorted(self.besdict.keys()):
            
            local_dev=self.besdict[b].calculate_local_deviation(ki,self.mpc_prediction_horizon)
            cluster_dev+=local_dev 
            deviations[b]=local_dev
                            
        self.cluster_deviations[ki]=pd.DataFrame(deviations)

        return cluster_dev
           
    def combined_method_d(self,ki,solver):
                
        if list(self.cluster_optimal_schedules.keys())==[]:
            #print("First scheduling")
            self.reschedule(ki,solver)
            self.simulate_rescheduling(ki)
            self.if_rescheduled[ki]=0
        else:
            cluster_dev=self.calculate_deviations(ki)
            #print("Aggregated deviation in",ki)
            #print(cluster_dev)
            if all(cluster_dev>self.triggering_threshold):
                #Trigger rescheduling
                self.reschedule(ki,solver)
                self.simulate_rescheduling(ki)
                self.if_rescheduled[ki]=1
            else:           
                sch_k=max(list(self.cluster_optimal_schedules.keys()))
                dev_k=max(list(self.cluster_deviations.keys()))
                self.dMPC(sch_k,dev_k,solver)
                self.simulate_dmpc(ki)
                self.if_rescheduled[ki]=0
                
                  
    def dMPC(self,sch_k,dev_k,solver,customRefCurve=False):
        """
        Generates an DMPC instance with the available forecasts, flexibilities and deviations
        """
        ts_shift=int((dev_k-sch_k)/self.timer.dT)
        
        if ts_shift<=self.timer.T-self.mpc_prediction_horizon:
            mpc_pred_horizon=self.mpc_prediction_horizon
        else:
            mpc_pred_horizon=self.timer.T-ts_shift
               
        forecast_dict   =self.cluster_optimal_schedules[sch_k][ts_shift:ts_shift+mpc_pred_horizon]
        flexibility_dict=self.cluster_optimal_flexibilities[sch_k][ts_shift:ts_shift+mpc_pred_horizon]
        deviation_dict  =self.cluster_deviations[dev_k][:mpc_pred_horizon]
                  
        dmpc=DMPC(mpc_pred_horizon,forecast_dict,deviation_dict,flexibility_dict,customRefCurve)
        agentIDs=self.besdict.keys()    #Random sorting in the iteration round
        
        #print("DMPC running for prediction horizon starting by",dev_k)
        converged_loc_curves,converged_loc_switch,converged_clu_curve=dmpc.distributed_control(solver,agentIDs)
        
        self.dmpc_results[dev_k]={'P_Import':converged_loc_curves,'Switching':converged_loc_switch}
        
        return converged_loc_curves,converged_loc_switch,converged_clu_curve
               
    def combined_method_h(self,ki,solver):
                
        if list(self.cluster_optimal_schedules.keys())==[]:
            #print("First scheduling")
            self.reschedule(ki,solver)
            self.simulate_rescheduling(ki)
            self.if_rescheduled[ki]=0
        else:
            cluster_dev=self.calculate_deviations(ki)
            #print("Aggregated deviation in",ki)
            #print(cluster_dev)
            if all(cluster_dev>self.triggering_threshold):
                #Trigger rescheduling
                self.reschedule(ki,solver)
                self.simulate_rescheduling(ki)
                self.if_rescheduled[ki]=1
            else:           
                sch_k=max(list(self.cluster_optimal_schedules.keys()))
                dev_k=max(list(self.cluster_deviations.keys()))
                self.hMPC(sch_k,dev_k,solver)
                self.simulate_hmpc(ki)
                self.if_rescheduled[ki]=0

    def hMPC(self,sch_k,dev_k,solver,customRefCurve=False):
        """
        Generates an HDMPC instance with the available forecasts, flexibilities and deviations
        """
        ts_shift=int((dev_k-sch_k)/self.timer.dT)
        
        if ts_shift<=self.timer.T-self.mpc_prediction_horizon:
            mpc_pred_horizon=self.mpc_prediction_horizon
        else:
            mpc_pred_horizon=self.timer.T-ts_shift
        
        forecast_dict   =self.cluster_optimal_schedules[sch_k][ts_shift:ts_shift+mpc_pred_horizon]
        flexibility_dict=self.cluster_optimal_flexibilities[sch_k][ts_shift:ts_shift+mpc_pred_horizon]
        deviation_dict  =self.cluster_deviations[dev_k][:mpc_pred_horizon]
                  
        hmpc=HDMPC(mpc_pred_horizon,forecast_dict,deviation_dict,flexibility_dict,customRefCurve)
        agentIDs=self.besdict.keys()    #Random sorting in the iteration round
        
        #print("HMPC running for prediction horizon starting by",dev_k)
        loc_curves,loc_switch,clu_curve=hmpc.hierarchical_control(solver,agentIDs)
        
        self.hmpc_results[dev_k]={'P_Import':loc_curves,'Switching':loc_switch}
        
        return loc_curves,loc_switch,clu_curve
            
    def simulate_rescheduling(self,ki):

        for b in sorted(self.besdict.keys()):            

            #self.besdict[b].Act_F_use[ki]=
            
            self.besdict[b].tes.set_gen(ki,self.rescheduling_results[ki][b]['Q_TES'][0])
            self.besdict[b].hd1.set_state(ki,self.rescheduling_results[ki][b]['Mod_hd1'][0])
            self.besdict[b].hd2.set_state(ki,self.rescheduling_results[ki][b]['Mod_hd2'][0])
            self.besdict[b].pv.set_gen(ki,self.rescheduling_results[ki][b]['PV_Gen'][0])            
            self.besdict[b].calculate_net_p_import(ki)
        
    def simulate_dmpc(self,ki):
        
        sch_k=max(list(self.rescheduling_results.keys()))
        dmpc_k=ki
        ts_shift=int((dmpc_k-sch_k)/self.timer.dT)
        
        for b in sorted(self.besdict.keys()):
            
            self.besdict[b].Act_F_use[ki]=self.dmpc_results[dmpc_k]['Switching'][b][0]
            
            real_mod_hd2=self.rescheduling_results[sch_k][b]['Mod_hd2'][ts_shift]+self.dmpc_results[dmpc_k]['Switching'][b][0]
            real_q_tes=self.rescheduling_results[sch_k][b]['Q_TES'][ts_shift]-real_mod_hd2*self.besdict[b].hd2.Qnom
            real_pv=min(self.rescheduling_results[sch_k][b]['PV_Gen'][ts_shift],self.besdict[b].forecast.PV[dmpc_k][0])
            
            self.besdict[b].tes.set_gen(dmpc_k,real_q_tes)
            self.besdict[b].hd1.set_state(dmpc_k,self.rescheduling_results[sch_k][b]['Mod_hd1'][ts_shift])
            self.besdict[b].hd2.set_state(dmpc_k,real_mod_hd2)
            
            #self.besdict[b].pv.set_gen(dmpc_k,self.rescheduling_results[sch_k][b]['PV_Gen'][ts_shift])           
            self.besdict[b].pv.set_gen(dmpc_k,real_pv)
            self.besdict[b].calculate_net_p_import(dmpc_k)
                
    def simulate_hmpc(self,ki):
        
        sch_k=max(list(self.rescheduling_results.keys()))
        hmpc_k=ki
        ts_shift=int((hmpc_k-sch_k)/self.timer.dT)
        
        for b in sorted(self.besdict.keys()):
            
            self.besdict[b].Act_F_use[ki]=self.hmpc_results[hmpc_k]['Switching'][b][0]
            
            real_mod_hd2=self.rescheduling_results[sch_k][b]['Mod_hd2'][ts_shift]+self.hmpc_results[hmpc_k]['Switching'][b][0]
            real_q_tes=self.rescheduling_results[sch_k][b]['Q_TES'][ts_shift]-real_mod_hd2*self.besdict[b].hd2.Qnom
            real_pv=min(self.rescheduling_results[sch_k][b]['PV_Gen'][ts_shift],self.besdict[b].forecast.PV[hmpc_k][0])
            
            
            self.besdict[b].tes.set_gen(hmpc_k,real_q_tes)
            self.besdict[b].hd1.set_state(hmpc_k,self.rescheduling_results[sch_k][b]['Mod_hd1'][ts_shift])
            self.besdict[b].hd2.set_state(hmpc_k,real_mod_hd2)
            
            #self.besdict[b].pv.set_gen(hmpc_k,self.rescheduling_results[sch_k][b]['PV_Gen'][ts_shift])
            self.besdict[b].pv.set_gen(hmpc_k,real_pv)
            self.besdict[b].calculate_net_p_import(hmpc_k)
        
        
        
        
            