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


from w_ui.api_helper import UX_Helper
from get_logger import setup_logging
logging=setup_logging()



#0v1# JC Nov 15, 2023  Setup


"""
"""


def dev_shivam_services():
    # w_api  api_helper
    #> UX_Helper
    #
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


def API_get_full_case_state(case_id):
    ## Support
    #MANAGER=Manager_Interface()
    UX=UX_Helper()

    dd={}
    dd['case_id']=case_id

    ## MAP EXPECTED KNOWN
    expected=[]
    expected+=['is_case_started']
    expected+=['is_case_running']
    expected+=['is_case_ready_to_query']
    expected+=['last_state']
    expected+=['case_status_word'] # Running, Ready to Answer, Pending
    expected+=['case_files']
    expected+=['estimated_case_running_time_remaining_m']
    
    ##[ ] second estimation (interface_manager.py)
    #times=Manager.estimate_run_times(case_id)

    expected+=['job_page_count']
    expected+=['age_of_last_active_m']
    expected+=['has_job_ever_finished']
    
    umeta=UX.dump_user_ux_meta(case_id=case_id)
    
    for k in expected:
        dd[k]=umeta.get(k,None)
    
    return dd

def test_case_state():
    #  {'case_id': 'case_atm_location', 'is_case_started': True, 'is_case_running': False, 'is_case_ready_to_query': True, 'last_state': 'end_KBAI_processing_pipeline', 'case_status_word': 'Ready to Answer', 'case_files': ['07A210E6-B60D-46B6-9D40-9B3239237F05-list.pdf'], 'estimated_case_running_time_remaining_m': 0, 'age_of_last_active_m': 14853.6, 'has_job_ever_finished': True, 'job_page_count': 5}

    #+job_page_count
    
    case_id='case_atm_location'
    umeta=API_get_full_case_state(case_id)
    print ("GOT: "+str(umeta))

    return

def API_get_running_cases_status():
    # How to limit by username or owner or scope?
    MANAGER=Manager_Interface()
    cases_running=MANAGER.which_cases_are_running()
    #>log, last state, 
    
    ## Include estimated time

    #[ method 1 ] umeta.get('estimated_case_running_time_remaining_m',None)
    #[ method 2 ] Manager.estimate_run_times(case_id)
    running={}
    for case_id in cases_running:
        running[case_id]=API_get_full_case_state(case_id)

    return running


if __name__=='__main__':
    branches=['dev1']
    branches=['test_shivam_services']
    branches=['dev_get_full_case_state']
    branches=['test_case_state']

    for b in branches:
        globals()[b]()


"""
"""










