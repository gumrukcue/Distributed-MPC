# -*- coding: utf-8 -*-
"""
Created on Wed Jul 25 13:17:03 2018

@author: gumrukcue
"""
from datetime import date, datetime, timedelta

class Timer(object):
    
    def __init__(self,year,month,day,hour=0,minute=0,timediscretization=900,reschedulinghorizon=96):
        """
        Timer class specifies the discretization over time, number of time steps to be shifted
        :param timediscretization: 
            integer: number of seconds in one time step --> default 15 minutes
        :param reschedulinghorizon: 
            integer: number of time steps of total rescheduling horizon --> default 24 hours
        """
        
        self.dT=timedelta(seconds=timediscretization)
        self.deltaSec=timediscretization
        self.T=reschedulinghorizon       
        self.start=datetime(year,month,day,hour,minute)
        
    def updateTimer(self):
        """
        Updates the shifted number of time steps i.e. start time step of the new rescheduling horizon
        """
        self.start+=self.dT


if __name__=="__main__":
    
    aTimer=Timer(2019,3,13)
    print("Static timer properties")
    print("Time discretization:",aTimer.dT)
    print("Time discretization in seconds:",aTimer.deltaSec)
    print("Number of the time intervals in a rescheduling horizon:",aTimer.T)
    print("Rescheduling horizon start",aTimer.start)
    print("Rescheduling horizon end",aTimer.start+aTimer.dT*aTimer.T)
    print()
    print("Horizon shifted")
    aTimer.updateTimer()
    print("Rescheduling horizon start",aTimer.start)
    print("Rescheduling horizon end",aTimer.start+aTimer.dT*aTimer.T)
    
    
        
