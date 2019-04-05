# -*- coding: utf-8 -*-
"""
Created on Wed Mar 13 15:18:53 2019

@author: egu
"""

class Forecast(object):
    
    def __init__(self):
               
        self.P={}
        self.Q={}
        self.PV={}
        
    def set_P_demand_forecast(self,ki,timeSeries):
        self.P[ki]=timeSeries
    def set_Q_demand_forecast(self,ki,timeSeries):
        self.Q[ki]=timeSeries
    def set_PV_pot_forecast(self,ki,timeSeries):
        self.PV[ki]=timeSeries