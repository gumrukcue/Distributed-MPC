# -*- coding: utf-8 -*-
"""
Created on Wed Jul 25 13:16:15 2018

@author: gumrukcue
"""

class HeatingDevice(object):
    
    def __init__(self,timer,Pnom,Qnom,modulation=False):
        """
        Thermal  
        
        Parameters
        :generation: positive sign
        :param Pnom:  Nominal electric power of heating device kW_el
        :param Qnom:  Nominal thermal power  of heating device  kW_th
        """        
        self.timer=timer
        self.Pnom=Pnom
        self.Qnom=Qnom
        
        #Data saving
        self.state={} #Modulation level of heating device
        self.P_gen={} #P generation
        self.Q_gen={} #Q generation

    def set_state(self,ki,modTh):
        """
        Input
        :modTh: Modulation level of heating device
        """      
        self.state[ki]=modTh
        self.P_gen[ki]=modTh*self.Pnom
        self.Q_gen[ki]=modTh*self.Qnom
        