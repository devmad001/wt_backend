import os
import sys
import codecs
import json
import re
import time
import requests

import configparser as ConfigParser


LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")


from a_query.admin_query import admin_remove_case_from_kb
from a_agent.sim_wt import get_job_state
from a_agent.sim_wt import wt_main_pipeline


from get_logger import setup_logging
logging=setup_logging()


#0v1# JC  Feb  2, 2024  Setup



"""
    EASY RERUN ENTIRE CASE
    - A few optional entrypoints but this makes sense stand-alone here for now
"""



def auto_rerun_entire_case(case_id):
    ## direct past from dev_challenges
    #[ ] optionall do it via job queue but this is direct running

    options={}
    
    if False:
        options['only_pages']=[6]
        options['force_ocr']=False   #Will not go False because have global forced 

    print ("[auto_rerun_entire_case] case_id: "+str(case_id))
    print ("**beware, will remove case knowledge graph and rerun entire case**")
   

    admin_remove_case_from_kb(case_id=case_id)

    get_job_state(case_id=case_id) #WILL ALSO SYNC

    manual_skip_caps=['start_KBAI_processing_pipeline']
    meta=wt_main_pipeline(case_id=case_id,options=options,manual_skip_caps=manual_skip_caps)

    manual_skip_caps=['start_main_processing_pipeline']
    meta=wt_main_pipeline(case_id=case_id,options=options,manual_skip_caps=manual_skip_caps)

    print ("[debug] done rerun entire case: "+str(case_id))

    return



def call_auto_rerun_entire_case():
    # (think dev_challenge)


    ## For updating check amount and check check matcher
    case_id='case_December 2021 Skyview Capital Bank Statement' #Ok
    case_id='case_schoolkids'

    #Feb 17
#    case_id='65d11a8c04aa75114767637a'  #<-- timeout
#    case_id='65ca54869b6ff316a779e6d5' #dpi
#    case_id='65caaffb9b6ff316a779f525' #dpi
#    case_id='65cd01899b6ff316a77a1988' #dpi

    #Feb 18 both timeout so rerun
#    case_id='65d11a8c04aa75114767637a'  #<-- timeout  try single thread
    case_id='65cd01899b6ff316a77a1988' #dpi    timeout on retry single t



    print ("RERUNNING: "+str(case_id))
    auto_rerun_entire_case(case_id)

    return


if __name__=='__main__':
    branches=['call_auto_rerun_entire_case']
    for b in branches:
        globals()[b]()





