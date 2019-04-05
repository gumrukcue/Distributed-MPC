# -*- coding: utf-8 -*-
"""
Created on Thu Mar 21 11:34:24 2019

@author: egu
"""

import pandas as pd


#Household data
house={}
house[1] ={'PV':2.3,'Max Occupants':3}
house[2] ={'PV':2.7,'Max Occupants':3}
house[3] ={'PV':5.2,'Max Occupants':4}
house[4] ={'PV':3.0,'Max Occupants':2}
house[5] ={'PV':1.7,'Max Occupants':3}
house[6] ={'PV':1.9,'Max Occupants':3}
house[7] ={'PV':2.1,'Max Occupants':3}
house[8] ={'PV':2.2,'Max Occupants':4}
house[9] ={'PV':3.0,'Max Occupants':2}
house[10]={'PV':2.6,'Max Occupants':3}

#Use the reference data to generate the forecast parameters
filename='data_forecasts.xlsx'
xl_file = pd.ExcelFile(filename)
df_forecast=xl_file.parse('Example')

ref_p_dmnd_curve=df_forecast['P_Dmnd'].values
ref_q_dmnd_curve=df_forecast['Q_Dmnd'].values
ref_pv_gen_curve=df_forecast['PV_Gen'].values

#By scaling up/down with respect to the reference parameters
ref_pv=2.0
ref_no=3
ext_pv=23.2


pvDict={}
pDemDict={}
qDemDict={}

for h in sorted(house.keys()):
    
    pDemDict[h]=ref_p_dmnd_curve*house[h]['Max Occupants']/ref_no
    qDemDict[h]=ref_q_dmnd_curve
    pvDict[h]  =ref_pv_gen_curve*house[h]['PV']/ref_pv
pvDict['Ext']=ref_pv_gen_curve*ext_pv/ref_pv
    
pDf=pd.DataFrame(pDemDict)
qDf=pd.DataFrame(qDemDict)
pvDf=pd.DataFrame(pvDict)

writer = pd.ExcelWriter('StartScenario.xlsx')
pDf.to_excel(writer,'P_Demand')
qDf.to_excel(writer,'Q_Demand')
pvDf.to_excel(writer,'PV_Gen')
writer.save()


