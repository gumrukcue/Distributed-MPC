# -*- coding: utf-8 -*-
"""
Created on Wed Mar 13 15:35:44 2019

@author: egu
"""

class PV(object):
    
    def __init__(self,timer,Pmax):
        self.timer=timer
        self.Pmax=Pmax
        self.P_Pot={}
        self.P_Gen={}
        
    def set_pot(self,ki,P_pot):
        self.P_Pot[ki]=P_pot
    
    def set_gen(self,ki,P_gen):
        self.P_Gen[ki]=P_gen