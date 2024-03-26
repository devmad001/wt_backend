import os
import sys
import codecs
import time
import json
import re

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")

from a_agent.iagent import Smart_Agent

## Main pipeline (base extraction)

#from modules_hub import TASK_convert_raw_image_pdfs_to_text
#from modules_hub import TASK_run_main_pipeline
#from modules_hub import TASK_call_KB_update_pipeline
#from modules_hub import TASK_dump_excel

from sim_wt import wt_main_pipeline
from sim_wt import get_job_state

from get_logger import setup_logging

logging=setup_logging()


#0v2# JC  Dec 10, 2023  Tie in FE, job queue, and now google file sync option here locally
#0v1# JC  Sep 29, 2023  Init


"""
   SINGLE ENTRYPOINT
   - esp for partial pipeline runs
   - may need another agent but hopefully not

"""

"""
    ON RE-RUNS
    - recall, KB AI will self-check if algs have been applied at field level

"""



def call_normal_full_run(case_id='',b=[],options=[]):
    ## ENTRYPOINT focused RUN_sim_wt.py
    #- use from dev_challenges / w_qa
    
    if not b:
        b+=['normal sample run']
        b+=['skip some run caps sample run']
        b+=['specific pages sample run']
        b+=['just check state']
        b=['just check state']

        b=['normal sample run']
    
    ## DEV
    if not case_id:
        #Chase statements 1.pdf
        case_id='case_schoolkids'
        case_id='case_o1_case_single'


    if 'normal sample run' in b:
        wt_main_pipeline(case_id)
        
    elif 'specific pages sample run' in b:
        subset=['create_job','start_main_processing_pipeline']
        options['only_pages']=[3]
        wt_main_pipeline(case_id,subset,options=options)

    elif 'skip some run caps sample run' in b:
        manual_skip_caps=['ocr_conversion'] #attempt

        subset=['create_job','start_main_processing_pipeline']
        options={}
        options['only_pages']=[3]
        wt_main_pipeline(case_id,subset,options=options)
        
    elif 'just check state' in b:
        job_state=get_job_state(case_id=case_id)


    return

"""
RECALL ARCHITECTURE:
- RUN_sim_wt.py -> sim_wt.py -> wt_main_pipeline
- "get job state", "run main pipeline"
- ^ Smart_Agent() manages jobs
- ^ each case has state and possible active job?
- ^ capability "need request"

HOW TO USE IT?
- get 1 case job state
- run a specific case
  --> run case first-pass page2transaction
  --> run case KB markup
- Q&A interact or follow up.
  --> chatbot
  --> dump excel

"""

def MAIN_ENTRYPOINT_processing_pipeline():
    Agent=Smart_Agent() #<-- iagent.py Smart_Agent

    ## Manage multiple cases
    cases=[]
    cases+=['demo_a']
    
    
    b=['job_state']
    b+=['run_main_pipeline']
    b+=['run_kbai_pipeline']
    
    for case_id in cases:
        MAIN_ENTRYPOINT_CASE_processing_pipeline(case_id,Agent=Agent)
    
    return

from c_case_manager.case_pipeline import interface_set_case_to_processing
def local_set_FE_case_state_to_processing(case_id):
    logging.info("[local_set_FE_case_state_to_processing] case_id: "+str(case_id))
    interface_set_case_to_processing(case_id)
    return


def MAIN_ENTRYPOINT_CASE_processing_pipeline(case_id,Agent=None):
    logging.info("[MAIN_ENTRYPOINT_CASE_processing_pipeline] case_id: "+str(case_id))

    if not Agent: Agent=Smart_Agent() #<-- iagent.py Smart_Agent


    b=['job_state']
    b+=['run_main_pipeline']
    b+=['run_kbai_pipeline']

    meta_main={}
    meta_kbai={}
    
    ## ECHO LAST STATE:
    stats,min_age_key,min_age_value=Agent.get_case_jobs_newest_states(case_id)
    print ("Case: "+str(case_id)+" last active: "+str(int(min_age_value/60))+" minutes ago at state: "+str(min_age_key))

    start_time=time.time()
    ## JOB STATE
    job_state=get_job_state(case_id=case_id)
    
    ## CASE STATE?
    #> for now, force state to processing
    local_set_FE_case_state_to_processing(case_id)
    
    ## RUN FULL PIPELINE
    # (call in 2 step though)
    
    if 'run_main_pipeline' in b:
        manual_skip_caps=['start_KBAI_processing_pipeline']
        meta_main=wt_main_pipeline(case_id=case_id,manual_skip_caps=manual_skip_caps)

    if 'run_kbai_pipeline' in b:
        manual_skip_caps=['start_main_processing_pipeline']
        meta_kbai=wt_main_pipeline(case_id=case_id,manual_skip_caps=manual_skip_caps)

    run_time=time.time()-start_time
    
    ## BASIC META
    print ("="*30+" Done MAIN ENTRYPOINT FOR: "+str(case_id))
    print ("[main_pipeline meta]: "+str(meta_main))
    print ("[kbai_pipeline meta]: "+str(meta_kbai))

    return meta_main,meta_kbai

def status_of_all():
    #ie/ what cases are running?
    Agent=Smart_Agent() #<-- iagent.py Smart_Agent
    
    if False:
        case_ids={}
        jobs=[]
        for job in Agent.iter_all_jobs():
            jobs+=[job]
            case_ids[job['case_id']]=True
    #        print ("JOB: "+str(job))
    
        sorted_jobs = sorted(jobs, key=lambda x: x.get('last_active', 0), reverse=True)
        
        for job in sorted_jobs:
            print ("NEWEST JOB: "+str(job))
            print ("^"*40)
            break
    

    case_id='demo_a'
    
    stats,min_age_key,min_age_value=Agent.get_case_jobs_newest_states(case_id)
    
    ### Last run state details
    print ("Case: "+str(case_id)+" last active: "+str(int(min_age_value/60))+" minutes ago at state: "+str(min_age_key))
    

    return

def dev_trial_manual_call():
    # Old case?
    case_id='65a80064b3ac164610ea50e4'  #PJ 1 page
    
    MAIN_ENTRYPOINT_CASE_processing_pipeline(case_id,Agent=None)

    return

if __name__=='__main__':
    branches=['call_normal_full_run']

    branches=['status_of_all']
    branches=['MAIN_ENTRYPOINT_processing_pipeline']
    branches=['dev_trial_manual_call']


    for b in branches:
        globals()[b]()


"""
"""