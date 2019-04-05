# -*- coding: utf-8 -*-
"""
Created on Wed Apr  3 11:41:43 2019

@author: egu
"""

import pandas as pd

def complete_analysis(cluster,scenarioName):
    
    writer = pd.ExcelWriter('Results_'+scenarioName+'.xlsx')
    
    #time_range=sorted(self.besdict[min(self.besdict.keys)].keys())
    #agg_dmnd=dict.fromkeys(time_range,values=np.zeros(self.timer.T))
    besDF={}
    
    for b in sorted(cluster.besdict.keys()):         
        bes=cluster.besdict[b]
        
        p_dmnd=bes.Act_P_demand
        p_pv_gen=bes.pv.P_Gen
        p_pv_pot=bes.pv.P_Pot
        p_hd1=bes.hd1.P_gen
        p_hd2=bes.hd2.P_gen
        p_imp=bes.Act_P_Import
        
        q_dmnd=bes.Act_Q_demand
        q_hd1=bes.hd1.Q_gen
        q_hd2=bes.hd2.Q_gen
        q_tes=bes.tes.Q_gen
        soc=bes.tes.soc
         
        #To be able to calculate the number of switching events
        hd2_state=bes.hd2.state             #Find the state of the hd2 at each time step    
        hd2_fin_pos=pd.Series(hd2_state)    #Convert dictionary to pandas series for easy calculation
        hd2_ini_pos=hd2_fin_pos.shift(1)     #Shift the series down to compare hd2_state in succesive time steps
        
        #If hd2_state in two successive time steps are different; no switching event has taken place
        if_switched=abs(hd2_fin_pos-hd2_ini_pos).to_dict() 
        
        besDF[b]=pd.DataFrame([p_dmnd,p_pv_gen,p_hd1,p_hd2,p_imp,q_dmnd,q_hd1,q_hd2,q_tes,soc,if_switched,p_pv_pot]).T
        besDF[b].columns=['p_dmnd','p_pv_real','p_hd1','p_hd2','p_imp','q_dmnd','q_hd1','q_hd2','q_tes','tes_soc','switch','p_pv_pot']
        
        besDF[b].to_excel(writer,'bes'+str(b))
        
    agg_p_dmnd=sum(besDF[b]['p_dmnd'] for b in besDF.keys())
    agg_p_imp =sum(besDF[b]['p_imp'] for b in besDF.keys())
    agg_pv_gen=sum(besDF[b]['p_pv_real'] for b in besDF.keys())
    agg_pv_pot=sum(besDF[b]['p_pv_pot'] for b in besDF.keys())
    agg_sw    =sum(besDF[b]['switch'] for b in besDF.keys())
    
    if_resched=cluster.if_rescheduled
    
    aggDF=pd.concat([agg_p_dmnd,agg_p_imp,agg_pv_gen,agg_pv_pot,agg_sw],axis=1)
    aggDF['If_rescheduled']=pd.Series(if_resched)
    aggDF.to_excel(writer,'Cluster')
    writer.save()
    
def save_performance_indicators(cluster):
    besDF={}
    
    for b in sorted(cluster.besdict.keys()):         
        bes=cluster.besdict[b]
        
        p_dmnd=bes.Act_P_demand
        p_pv_gen=bes.pv.P_Gen
        p_pv_pot=bes.pv.P_Pot
        p_hd1=bes.hd1.P_gen
        p_hd2=bes.hd2.P_gen
        p_imp=bes.Act_P_Import
        
        q_dmnd=bes.Act_Q_demand
        q_hd1=bes.hd1.Q_gen
        q_hd2=bes.hd2.Q_gen
        q_tes=bes.tes.Q_gen
        soc=bes.tes.soc
         
        #To be able to calculate the number of switching events
        hd2_state=bes.hd2.state             #Find the state of the hd2 at each time step    
        hd2_fin_pos=pd.Series(hd2_state)    #Convert dictionary to pandas series for easy calculation
        hd2_ini_pos=hd2_fin_pos.shift(1)     #Shift the series down to compare hd2_state in succesive time steps
        
        #If hd2_state in two successive time steps are different; no switching event has taken place
        if_switched=abs(hd2_fin_pos-hd2_ini_pos).to_dict() 
        
        besDF[b]=pd.DataFrame([p_dmnd,p_pv_gen,p_hd1,p_hd2,p_imp,q_dmnd,q_hd1,q_hd2,q_tes,soc,if_switched,p_pv_pot]).T
        besDF[b].columns=['p_dmnd','p_pv_real','p_hd1','p_hd2','p_imp','q_dmnd','q_hd1','q_hd2','q_tes','tes_soc','switch','p_pv_pot']
        
    agg_p_dmnd=sum(besDF[b]['p_dmnd'] for b in besDF.keys())
    agg_p_imp =sum(besDF[b]['p_imp'] for b in besDF.keys())
    agg_pv_gen=sum(besDF[b]['p_pv_real'] for b in besDF.keys())
    agg_pv_pot=sum(besDF[b]['p_pv_pot'] for b in besDF.keys())
    agg_sw    =sum(besDF[b]['switch'] for b in besDF.keys())
    
    if_resched=cluster.if_rescheduled
    
    PI=pd.concat([agg_p_dmnd,agg_p_imp,agg_pv_gen,agg_pv_pot,agg_sw],axis=1)
    PI['If_rescheduled']=pd.Series(if_resched)
    
    return PI


    