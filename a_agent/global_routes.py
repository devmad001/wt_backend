import os
import sys
import codecs
import json
import datetime
import re

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")

from w_utils import LockedDict

from get_logger import setup_logging
logging=setup_logging()



#0v1# JC  Mar 20, 2024  Setup


"""
    GLOBAL CONFIGURATION ? ROUTES
    - ideally all field changes need to come through this file
    - clear on fixed routes vs dynamic options
    - keep to single dict
    - if forcing a specific case  ___
    - if based on ie/ audit feedback  ___
    - base config on target case keind
    - base config on just want this top mode etc.
    - see GLOBAL_CONFIG & options
    - log config at end of run (Run id for mapping against logs)
    - do performance testing between
    - recall, lower level or dynamic options as well

"""

"""
    RECALL:
    - pass at main pipeline entrypoint at a_agent/sim_wt.py

"""

print ("![ ] log global routes settings (and actuals) to end of run ")

def get_global_routes():

    mode='standard_feb_2024_force_ocr_preprocess' #Bad here org ocr:    case_id='affinity2pageoddyear
    mode='standard_feb_2024'
    mode='try_gpt_4_turbo_page2transactions'
    

    rr=LockedDict()
    
    rr.unlock()

    rr['global_config']={}
    rr['mode']=mode
    rr['version']=1

    rr['global_config']['page2transaction_model']='org_llm_page2transactions'
    
    if mode=='standard_feb_2024':
        rr['descriptions']=[]
        rr['descriptions']+=['standard_feb_2024 includes the original standard flows:']
        rr['descriptions']+=['Use gpt-3.5 for base page2transactions, use OCR when needed (not always)']

        rr['global_config']['force_ocr_preprocess']=False
        rr['global_config']['llm_page2transactions_base_model_name']='gpt-3.5-turbo' 

    elif mode=='standard_feb_2024_force_ocr_preprocess':
        rr['descriptions']=[]
        rr['descriptions']+=['standard_feb_2024 includes the original standard flows:']
        rr['descriptions']+=['Use gpt-3.5 for base page2transactions, use OCR when needed (not always)']

        rr['global_config']['force_ocr_preprocess']=True
        rr['global_config']['llm_page2transactions_base_model_name']='gpt-3.5-turbo' 



        #See w_settings.ini config#  rr['global_config']['llm_page2transactions_smartest_model_name']='gpt-3.5' 
    
    elif mode=='try_gpt_4_turbo_page2transactions':
        rr['descriptions']=[]
        rr['descriptions']+=['try_gpt_4_turbo_page2transactions instead of 3.5 turbo default base']

        rr['global_config']['force_ocr_preprocess']=False
        rr['global_config']['llm_page2transactions_base_model_name']='gpt-4-turbo' 
        

    else:
        raise Exception('mode not found')
        
    rr.lock()

    # gpt-4-turbo-preview
    return rr



def call_get_global_routes():
    
    return





if __name__=='__main__':
    branches=['call_get_global_routes']

    for b in branches:
        globals()[b]()



"""
"""