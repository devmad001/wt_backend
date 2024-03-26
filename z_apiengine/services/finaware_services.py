import os
import sys
import codecs
import json
import re

from sqlalchemy.orm import Session

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")
sys.path.insert(0,LOCAL_PATH+"../..")

from database_models import User

from get_logger import setup_logging
logging=setup_logging()

## Inner background services
from w_ui.sim_user import interface_run_pipeline_in_background
from w_ui.sim_user import interface_get_job_dict

## COLLECT FROM OTHER SERVICE ENDPOINTS

from case_service import list_user_cases
from case_service import create_set_case

from user_service import get_user
from user_service import create_set_user

from faq_service import list_user_faqs
from session_service import alg_is_user_session_valid

from status_case_services import API_get_full_case_state
        

#0v1# JC Nov  8, 2023  Setup


"""
    COLLECTION OF FRONT-END FRAUD SERVICES  "shivam"
    
"""


def front_create_set_case(case_id: str, username: str, case_meta: dict):
    ### INCLUDES CREATE USER
    
    # [ ] test session
    # [ ] test case_id <> user_id don't conflict
    
    ## Validate user created or create
    user=get_user(username=username)
    if not user:
        logging.info("[create_set_case] user not found, creating: "+str(username))
        create_set_user(username=username)
        
    ## Validate if case exists that the user matches this user

    case,did_create=create_set_case(case_id=case_id,username=username,case_meta=case_meta)

    return case,did_create

def front_list_user_cases(username: str):
    #[ ] validate includes cases meta
    #[ ] sync'd via back_sync_user_and_cases
    cases=list_user_cases(username=username)
    return cases

################################################################################
# ^^ above are formalized entries


def front_list_user_case_faqs(username: str, case_id:str):
    faqs=list_user_faqs(username=username)
    ## Filter by case at service level
    return faqs

#no# def front_list_user_case_buttons(username: str, case_id: str):
#no#     ## Or, is this at a user.case level?
#no#     buttons=list_buttons(username=username)
#no#     ## Filter by case at service level
#no#     return buttons

def front_get_user_info(username: str):
    user=get_user(username=username)
    return user

def front_start_processing_case(case_id: str):
    ## If user + session valid the
    #[ ] existing code.. w_ui/file_manager/pyfiledrop.py
    is_started,meta=interface_run_pipeline_in_background(case_id=case_id)
    return is_started,meta

def front_get_processing_case_status(case_id: str):
    ##[1] GET JOB STATUSES (integrate into case list)
    ## If user + session valid the
    
    #  {'case_id': 'case_atm_location', 'is_case_started': True, 'is_case_running': False, 'is_case_ready_to_query': True, 'last_state': 'end_KBAI_processing_pipeline', 'case_status_word': 'Ready to Answer', 'case_files': ['07A210E6-B60D-46B6-9D40-9B3239237F05-list.pdf'], 'estimated_case_running_time_remaining_m': 0, 'age_of_last_active_m': 14853.6, 'has_job_ever_finished': True, 'job_page_count': 5}

    data={}
    umeta=API_get_full_case_state(case_id=case_id)
    data['case_state']=umeta #dup case_id ok
    data['case_id']=case_id

    if 'use sim_user job_status' in []:
        job=interface_get_job_dict(case_id=case_id)
        ## Local prune info
        pop_these=['base_dir','path_filenames']
        for item in pop_these:
            job.pop(item,'')

    return data

def front_get_cases_running_with_status(username: str):
    ## Limit by user view?
    raise Exception("Not implemented")
    running_cases={} #case_id index
    running_cases=API_get_running_cases_status()
    return running_cases
    

#################################
# SYNC WITH SHIVAM
#################################
def front_session_is_user_authenticated(username: str, session_id: str):
    ## See session object OR fetch from backend
    return alg_is_user_session_valid(username=username,session_id=session_id)

## OUTGOING SERVICES RELATED TO SHIVAM
def back_fetch_file_from_backend(file_id):
    ## TBD
    #{ ] also, optionally fetch all those they haven't successfully been pulled

    #fetch_file(file_id)
    ## Load backend IP locations

    return

def back_is_user_authenticated(username: str, session_id: str):
    ## Proxy from shivam backend session service
    #** see session_service proxy_auto_validate...  def proxy_auto_validate_user_session(username: str, session_id: str):
    is_authenticated=True
    return is_authenticated

def back_sync_user_and_cases(username: str, session_id: str):
    ## [ ] get user info
    ## [ ] get user cases info <- part of validation on whether use can see cases
    return

def front_create_set_file(user_id: int, case_id: str, filename: str, file_meta: dict, file_url: str = None, is_stored: bool = False):
    # Call the backend function with the provided data
    file = create_set_file(user_id=user_id, case_id=case_id, filename=filename, file_meta=file_meta, file_url=file_url, is_stored=is_stored)

    ## Spawn as backend process
    back_fetch_file_from_backend(file.id)
    return file

def request_to_shivam():
    algs=[]
    """
    [1]  Authentication handshake.  FinAware GET to ShivamAPI  is_user_authenticated(username,session_id)
        - username could be user_id.  Which ever is active in the logged in session
            - alternatively, you could call it:  get_authenticated_username(session_id)

    [2]  Sync user (record(s)) and case (records(s) (and files).  Since user + case creation happen on ShivamAPI, we need to sync them.
            (i)   Option on Case creation (when user clicks "start processing")
            (ii)  Option on normal sync.
            (iii) Option on db sync
            
    [3]  Sync files.
           (options)
            (i)  ShivamAPI push files to FinAwareAPI
            (ii) ShivamAPI Case record should have list of files.  Download links should be available.
            

    """
    return

    
def offer_to_shivam():
    """
    notes+=['list_user_case_buttons']
    notes+=['list_user_case_faqs']

    notes+=['start_processing_case']
    notes+=['get_case_running_status']

    """

    """
    OTHER:
    notes+=['get_case_meta']

    """

    return


def todo_shivam_services():
    notes=[]

    return
    

def test_shivam_services():
    #> see test_shivam_services.py
    
    b=[]
    b+=['start_processing_case']
    b+=['get_case_running_status']

    b+=['list_user_case_buttons']
    b+=['list_user_case_faqs']
    
    if 'get_case_running_status' in b:
        case_id='case_atm_location'

        rr=front_get_processing_case_status(case_id=case_id)
        
        print ("GOT: "+str(rr))


    return


def dev_shivam_services():
    # w_api  api_helper
    #> UX_Helper
    #
    from w_ui.api_helper import UX_Helper
    from a_agent.interface_manager import Manager_Interface
    from w_ui.sim_user import interface_get_job_status

    MANAGER=Manager_Interface()
    cases_running=MANAGER.which_cases_are_running()
    liners+=["[debug view remove]  call active cases running: "+str(cases_running)]
    ## CASE STATE
    simple_case_state=MANAGER.what_is_the_last_state_of_case(case_id)
    liners+=["[case state]: "+str(simple_case_state)+" for: "+str(case_id)]
    #logging.info("[case state]: "+str(simple_case_state)+" for: "+str(case_id))
    ## CHECK DEBUG LOG
    fname,debug_log=MANAGER.dump_latest_log(case_id)

    case_id='case_atm_location'
    UX=UX_Helper()

    estimated_time_remaining=UX.get_estimated_time_remaining()
    
    ## Used in app_parenty.py process_status
    umeta=UX.dump_user_ux_meta(case_id=case_id)


    return

def dev_case_specific():

    return

def dev_global_specific():
    MANAGER=Manager_Interface()
    cases_running=MANAGER.which_cases_are_running()
    return

if __name__=='__main__':
    branches=['dev1']
    branches=['test_shivam_services']
    for b in branches:
        globals()[b]()


"""
"""










