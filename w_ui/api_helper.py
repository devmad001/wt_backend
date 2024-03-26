import os
import sys
import codecs
import json
import re

from fastapi import FastAPI

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")

## Sim user
from w_ui.sim_user import interface_get_job_dict
from w_ui.sim_user import interface_get_job_status

## Recall from app_parenty.py
from w_mindstate.mindstate import Mindstate
from w_utils import am_i_on_server
from a_agent.interface_manager import Manager_Interface

from get_logger import setup_logging
logging=setup_logging()


#0v1# JC  Oct 19, 2023  Init

"""
    UX support
    
    TODO:
    - add tests for imported interfaces
"""


class UX_Helper():
    ## Case statuses?
    ## A bit like user sim but supports link between user dashboard and various services
    def __init__(self):
        self.MANAGER=Manager_Interface()  #See app_parenty entrypoint
        self.MIND=Mindstate()  #See app_parenty entrypoint
        return
    
    def get_job_status(self,case_id=''):
        ## sim_user
        #> has_job_ever_finished, age_since_started_m, age_of_last_active_m, estimated_time_remaining
        job_status=interface_get_job_status(case_id=case_id)
        return job_status
    
    def is_case_ready_to_query(self,case_id='',job_status={}):
        #i)  Did job complete?  (assume haven't erased whats' there or do transaction count)
        #ii) count entities or count transactions
        is_ready_to_query=False

        """  if 'check_if_finished' in b:
        ## job:    'completed_on': 1694556769.4598532,  (define in dict when done)
        job=interface_get_job_dict(case_id=case_id)
        print ("JOB STATUS: "+str(job))

        if job.get('last_active',0):
            print ("[info] job last active: "+str(time.time()-job['last_active'])+"s ago.")
        if 'completed_on' in job:
            print ("[info] job completed on: "+str(job['completed_on']))
            print ("** ready to dump excel")

        """
        if not job_status:
            job_status=self.get_job_status(case_id=case_id)
        # is_job_running, estimated_time_remaining, 
        #   {'is_case_running_in_background': False, 'is_job_running': False, 'has_job_ever_finished': True, 'age_of_last_active_m': 2510.15, 'age_since_started_m': 2522.7591921448707, 'job_raw_page_count': 4, 'estimated_time_remaining': 0}
        
        if job_status.get('has_job_ever_finished',False):
            is_ready_to_query=True

        return is_ready_to_query
    
    def list_case_files(self,case_id):
        ## Via cypher query or job processing status
        job_dict=interface_get_job_dict(case_id=case_id)
        """
         {'case_id': 'case_atm_location', 'version': 1, 'job_id': 'case_atm_location-1', 'base_dir': 'c:/scripts-23/watchtower/wcodebase/a_agent/../w_ui/file_manager/storage/case_atm_location/', 'filenames': ['07A210E6-B60D-46B6-9D40-9B3239237F05-list.pdf'], 'path_filenames': [('c:/scripts-23/watchtower/wcodebase/a_agent/../w_ui/file_manager/storage/case_atm_location/07A210E6-B60D-46B6-9D40-9B3239237F05-list.pdf', '07A210E6-B60D-46B6-9D40-9B3239237F05-list.pdf')], 'state': {'create_run_job': {'time': 1697546295}, 'ocr_conversion': {'time': 1697546295}, 'start_main_processing_pipeline': {'time': 1697546295}, 'running_KBAI_processing_pipeline': {'time': 1697546473, 'meta': {'progress': 1.0}}, 'end_KBAI_processing_pipeline': {'time': 1697546944}, 'end_main_processing_pipeline': {'time': 1697546473}, 'start_KBAI_processing_pipeline': {'time': 1697546473}, 'wt_main_pipeline_finished': {'time': 1697546944}}, 'next_actions': [], 'pages_count': 4, 'page_active': 3, 'last_active': 1697546295}
         """
        print ("[debug1]  JOB DICT: "+str(job_dict))
        job_filenames=job_dict.get('filenames',[])
        return job_filenames
    
    def is_case_started(self,case_id=''):
        job_status=interface_get_job_dict(case_id)
        is_started=False
        create_run_job=job_status.get('state',{}).get('create_run_job',{})
        if create_run_job:
            is_started=True
        #**recall, via the manager we can check on the last state!
        return is_started
    def get_last_state(self,case_id=''):
        last_state=self.MANAGER.what_is_the_last_state_of_case(case_id)
        state=last_state.get('newest_last_ran_state','') #end_KBAI_processing_pipeline
        return state
    
    def is_linux_case_process_running(self,case_id=''):
        """
            ALT::
               job_status=interface_get_job_status(case_id)
    # {'is_case_running_in_background': False, 'is_job_running': False, 'has_job_ever_finished': True, 'age_of_last_active_m': 2510.15, 'age_since_started_m': 2522.7591921448707, 'job_raw_page_count': 4, 'estimated_time_remaining': 0}
        """
        is_running=False
        cases_running=self.MANAGER.which_cases_are_running()
        if case_id in cases_running:
            is_running=True
        return is_running
    
    def get_estimated_time_remaining(self,case_id='',job_status={}):
        if not job_status:
            job_status=self.get_job_status(case_id=case_id)
        # is_job_running, estimated_time_remaining, 
        #   {'is_case_running_in_background': False, 'is_job_running': False, 'has_job_ever_finished': True, 'age_of_last_active_m': 2510.15, 'age_since_started_m': 2522.7591921448707, 'job_raw_page_count': 4, 'estimated_time_remaining': 0}
        return max(job_status.get('estimated_time_remaining',0),0) #>=0
    
    def dump_user_ux_meta(self,case_id=''):
        ## Run above
        job_status=self.get_job_status(case_id=case_id)

        umeta={}
        
        umeta['age_of_last_active_m']=job_status.get('age_of_last_active_m',0)
        umeta['has_job_ever_finished']=job_status.get('has_job_ever_finished',False)
        umeta['job_page_count']=job_status.get('job_raw_page_count',0)

        umeta['is_case_ready_to_query']=self.is_case_ready_to_query(case_id=case_id,job_status=job_status)
        umeta['case_files']=self.list_case_files(case_id=case_id)
        umeta['is_case_running']=self.is_linux_case_process_running(case_id=case_id)
        umeta['estimated_case_running_time_remaining_m']=self.get_estimated_time_remaining(case_id=case_id,job_status=job_status)
        umeta['is_case_started']=self.is_case_started(case_id=case_id)
        umeta['last_state']=self.get_last_state(case_id=case_id) #Uses timestamps!
        
        ## MAP TO USER MESSAGES
        status_words=['Running','Ready to Answer','Pending']
        status_sub_words=[]
        umeta['case_status_sub_word']=''
        
        #[x] include error:
        #- if not process running and started then error

        if umeta['is_case_ready_to_query']:
            umeta['case_status_word']='Ready to Answer'
            umeta['case_status_sub_word']='Active files: '+", ".join(umeta['case_files'])
        elif umeta['is_case_running']:
            umeta['case_status_word']='Running'
            if not umeta['estimated_case_running_time_remaining_m']:
                umeta['case_status_sub_word']='Estimated time remaining: tbd'
            else:
                umeta['case_status_sub_word']='Estimated time remaining: '+str(umeta['estimated_case_running_time_remaining_m'])+' minutes'
        elif umeta['is_case_started'] and not umeta['is_case_running']:
            logging.info("[warning] case started but NOT running")
            umeta['case_status_word']='Error:  Started but NOT running'
            umeta['case_status_sub_word']='Last state: '+re.sub(r'_',' ',umeta['last_state'])

        else:
            umeta['case_status_word']='Pending'
            umeta['case_status_sub_word']='(ready to start processing)'
        
        return umeta

    """ EXTRA:
       simple_case_state=MANAGER.what_is_the_last_state_of_case(case_id)
    liners+=["[case state]: "+str(simple_case_state)+" for: "+str(case_id)]
    """


def dev_extending_status_messages():
    print ("RECALL sim_user:  get job dict, get job status, ")
    
    case_id='case_atm_location'

    """
        USER STATUS META
    """

    """
     UX:
- [status window view] & pin ie (clear state)::

[a]  (case is)  [ready to query]
[b]  [these files are active]

[c]  (case is)  [running case]
[d]  [this is the output]

    """
    UX=UX_Helper()
    
    ## USER STATUS LOGIC
    umeta={}
    umeta['is_case_ready_to_query']=False
    umeta['is_case_running']=False
    umeta['list_pdf_files_in_case']=[]
    umeta['estimated_case_running_time_remaining_m']=0
    
    # EXTRA:
    #? when did the case start running??
    #? when was the last dashboard view? if >30m then load default timeline.
    #   ^ last query?  check query logs or check user state management
    umeta['last_user_query_m']=0
    
    
    ## USER STATUS MESSAGES
    ####################
    
    umeta={}
    
    if 'ok ready' in []:
        umeta['is_case_ready_to_query']=UX.is_case_ready_to_query(case_id=case_id)
        umeta['case_files']=UX.list_case_files(case_id=case_id)
        umeta['is_case_running']=UX.is_linux_case_process_running(case_id=case_id)
        umeta['estimated_case_running_time_remaining_m']=UX.get_estimated_time_remaining(case_id=case_id)
    umeta['is_case_started']=UX.is_case_started(case_id=case_id)
    umeta['last_state']=UX.get_last_state(case_id=case_id) #Uses timestamps!

#    umeta=UX.dump_user_ux_meta(case_id=case_id)

    print ("[dev umeta]: "+str(umeta))

    return



if __name__=='__main__':
    branches=['dev1']
    branches=['dev_extending_status_messages']
    for b in branches:
        globals()[b]()

"""
"""