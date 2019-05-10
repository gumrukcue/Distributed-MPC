# -*- coding: utf-8 -*-
"""
Created on Wed Mar 13 15:17:52 2019

@author: guemruekcue
"""

import time
import numpy as np
from pyomo.core import Var
from pyomo.environ import *
from datetime import date, datetime, timedelta,timezone
import pandas as pd
       
class BES(object):

    def __init__(self,timer,forecast,device1,device2,tes,pv):
        """
        Building Energy System 
        
        Elements
            timer   : Timer object
            forecast: Forecast object
            hd1     : HeatingDevice object
            hd2     : HeatingDevice object
            tes     : TES object
            pv      : PV object
        """
        self.timer=timer
        self.forecast=forecast
        self.hd1=device1
        self.hd2=device2
        self.tes=tes
        self.pv=pv
               
        #Attributes for data handling
        self.Act_P_demand={}
        self.Act_Q_demand={}      
        self.Act_P_Import={}
        
        self.Act_F_use={}
        
    #Functions for data handling
    def set_act_p_demand(self,ki,P):
        self.Act_P_demand[ki]=P
    def set_act_q_demand(self,ki,Q):
        self.Act_Q_demand[ki]=Q        
    def set_act_p_import(self,ki,P):
        self.Act_P_Import[ki]=P
    
    def calculate_net_p_import(self,ki):
        
        if not ki in self.Act_P_demand.keys():        
            self.set_act_p_demand(ki,self.forecast.P[ki][0])
            self.set_act_q_demand(ki,self.forecast.Q[ki][0])
            
        p_dmnd=self.Act_P_demand[ki]        
        p_pv=self.pv.P_Gen[ki]
        p_hd1=self.hd1.P_gen[ki]
        p_hd2=self.hd2.P_gen[ki]
        p_imp=p_dmnd-p_pv-p_hd1-p_hd2
        
        self.Act_P_Import[ki]=p_imp
                                    
    def calculate_flexibility(self,ki,mpc_prediction_horizon,tesSch,hdSch):
        """
        Calculates flexibility of the BES in the prediction horizon following ki
        for given TES and HeatingDevice schedules
        
        Positive flexibility: larger consumption possible
        Negative flexibility: smaller consumption possible
        """
            
        cand_flex=np.ones(mpc_prediction_horizon)
        cand_flex[hdSch!=0]=0
        real_flex=[]    
        soc_sch=[self.tes.soc[ki]]
              
        for t in range(mpc_prediction_horizon):
            next_soc_pre_flex=soc_sch[t]-tesSch[t]*self.timer.deltaSec/self.tes.capacity
            
            if cand_flex[t]==0:
                flex_pot=0
                soc_next=next_soc_pre_flex
            elif next_soc_pre_flex+self.hd2.Qnom*self.timer.deltaSec/self.tes.capacity>1:
                flex_pot=0
                soc_next=next_soc_pre_flex
            else:
                flex_pot=1
                soc_next=next_soc_pre_flex+self.hd2.Qnom*self.timer.deltaSec/self.tes.capacity
            soc_sch.append(soc_next)
            real_flex.append(-flex_pot*self.hd2.Pnom)

        return real_flex
    
    def calculate_p_forecast_error(self,ki,predictionHorizon):
        #ref_k: time stamp of the reference forecast to be compared against the up-to-date forecast
        ts_list=list(sorted(self.forecast.P.keys()))       
        ref_k=ts_list[len(ts_list)-2] 
        new_k=ki
        
        shiftedTs=int((new_k-ref_k)/self.timer.dT)
        
        reference_curve=self.forecast.P[ref_k][shiftedTs:shiftedTs+predictionHorizon]
        updated_curve  =self.forecast.P[new_k][:predictionHorizon]
        
        self.set_act_p_demand(ki,updated_curve[0])
        
        return reference_curve-updated_curve
        
    def calculate_q_forecast_error(self,ki,predictionHorizon):
        #ref_k: time stamp of the reference forecast to be compared against the up-to-date forecast
        ts_list=list(sorted(self.forecast.Q.keys()))       
        ref_k=ts_list[len(ts_list)-2] 
        new_k=ki
        
        shiftedTs=int((new_k-ref_k)/self.timer.dT)
        
        reference_curve=self.forecast.Q[ref_k][shiftedTs:shiftedTs+predictionHorizon]
        updated_curve  =self.forecast.Q[new_k][:predictionHorizon]
                
        self.set_act_q_demand(ki,updated_curve[0])
        
        return reference_curve-updated_curve        
        
    def calculate_pv_forecast_error(self,ki,predictionHorizon):
        #ref_k: time stamp of the reference forecast to be compared against the up-to-date forecast
        ts_list=list(sorted(self.forecast.PV.keys()))       
        ref_k=ts_list[len(ts_list)-2] 
        new_k=ki
        
        shiftedTs=int((new_k-ref_k)/self.timer.dT)
        
        reference_curve=self.forecast.PV[ref_k][shiftedTs:shiftedTs+predictionHorizon]
        updated_curve  =self.forecast.PV[new_k][:predictionHorizon]
                
        self.pv.set_pot(ki,updated_curve[0])
        
        return reference_curve-updated_curve        
    
    def calculate_local_deviation(self,ki,predictionHorizon):
        
        dev_dem=self.calculate_p_forecast_error(ki,predictionHorizon)
        dev_gen=self.calculate_pv_forecast_error(ki,predictionHorizon)
        
        dev_q_dem=self.calculate_q_forecast_error(ki,predictionHorizon)
        
        return abs(dev_dem-dev_gen)
        


    
        
