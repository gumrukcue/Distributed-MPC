# -*- coding: utf-8 -*-
"""
Created on Wed Jul 25 13:14:51 2018

@author: gumrukcue
"""

class TES(object):
    
    def __init__(self,timer,capacity,maxDis,minSoC=0.0,maxSoC=1.0):
        """
        Thermal Energy Storage Class 
        
        Parameters
        :param capacity:Storage capacity of Thermal Energy Storage(TES) device. type: kWh
        :param maxPdis: Maximum thermal discharge power from TES device 
        :param minSoC:  Minimum state of the charge TES device type: float
        :param maxSoC:  Minimum state of the charge TES device type: float
        
        """        
        self.timer=timer
        self.capacity=capacity*3600 #Converts into kW-second       
        self.maxQDis=maxDis
        self.minSoC=minSoC
        self.maxSoC=maxSoC
        
        #Data saving
        self.soc={}
        self.Q_gen={}
            
    def set_soc(self,ki,SoC):
        """
        Input
        :SoC: state-of-charge of capacity at time ki
        """      
        self.soc[ki]=SoC
        
    def set_gen(self,ki,q):
        """
        Input
        :q: Thermal power generation at time ki
        """   
        self.Q_gen[ki]=q
		
        ki_next=ki+self.timer.dT
        final_soc=self.soc[ki]-q*self.timer.deltaSec/self.capacity
        self.set_soc(ki_next,final_soc)

    
    
        
