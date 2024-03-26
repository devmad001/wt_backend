import os, sys
import time
import requests

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")
sys.path.insert(0,LOCAL_PATH+"../../")

from case_state_objs import Cases_State_Manager
from case_state_objs import Case_Proxy
from c_jobs_manager.job_analytics import ALG_has_case_ever_finished_without_error #Smart_Agent, etc
from c_jobs_manager.job_analytics import ALG_is_case_job_running_now

from get_logger import setup_logging
logging=setup_logging()




#0v1# JC Jan 11, 2023  Clean Case states

"""

    PIPELINE HANDLER FOR CASE PROCESSING
    - CASE "Proxy" object is passed through the pipeline
    - Case state movement is dependent on: user input, admin input, backend input
    #(see case_analytics.py for fetching of state status)

"""

"""
DESCRIBE CASE PROCESSING STATE MACHINE
- (org FE_cases_page_state.py)

- check_processing_status  (single case)
- check_actives_processing_status  (many cases)

- init
- details_posted
- start_requested
- processing
- done
- error
(new):
- add_pdfs_continue_processing_requested
- delete_pdfs_requested
- manual_start_requested  (admin)

EXTRA FEATURES?:
- auto cleaner to error or done?
- 

"""

## Globals
ANY_STATE=True
ACTION_TYPES=['init_case','done_case','is_processing','check_update_state_status']
KNOWN_STATES = ['INIT', 'DETAILS_POSTED', 'START_REQUESTED', 'PROCESSING', 'DONE', 'ERROR']
#case_analytics.py# USER_VIEWED_STATES = {'INIT': 'Not started', 'DETAILS_POSTED': 'Awaiting processing', 'START_REQUESTED': 'Awaiting processing', 'PROCESSING': 'Processing', 'DONE': 'Ready', 'ERROR': 'Error'}
 
def AUTO_manage_case_states():
    ##[ ] as needed
    #- time expiry or auto based on no pushed states
    #- refresh cache?
    return

def admin_delete_case(case_id):
    deleted=Cases_State_Manager().delete_case(case_id)
    return deleted

def admin_create_case(case_id, username,case_meta):
    return Cases_State_Manager().create_set_case(case_id,username,case_meta)

def initialize_case_state_dict(case_id, simulated=False ):
    case_state_dict = {
            'processing_start_time': None,
            'processing_end_time': None,
            'last_updated': time.time(),
            'error_info': None,
            'sim_case': simulated
        }
    return case_state_dict


def handle_FSM_backend_processing_request(action_type, case_id, simulated=False, data=None):
    #[ ] This is not being called since FE will ping backend as required
    #** Separate other channel events but assume same FSM
    #>> fwd to normal if standard
    #[ ] ERROR update?
    
    BE_TYPES=['BE_done_processing','BE_FORCE_done_processing']

    if not action_type in BE_TYPES:
        raise Exception("Unknown action_type: "+str(action_type))
    
    if ANY_STATE and (action_type=='BE_done_processing' or action_type=='BE_FORCE_done_processing'):
        
        ## Update case_state_dict + state

        Case=Case_Proxy(case_id)
        state,case_meta,case_state_dict=Case.get_state_info()
        case_state_dict['processing_end_time']=time.time()
        state='DONE'

        Case.set_case_state_info(state,case_state_dict)
        
    return


## Local transition logic support
def local_ok_transition_processing_to_done(case_id):
    #[ ] cache?

    ## Running now? then no to transition
    is_running_now=ALG_is_case_job_running_now(case_id)
    if is_running_now:
        return False

    has_good_finish=ALG_has_case_ever_finished_without_error(case_id)
    logging.info("[debug] has case ever finished if so -- transition to done: "+str(has_good_finish))
    return has_good_finish


def interface_initialize_case(case_id):
    ## Simple interface to initialize case FSM to INIT
    #> include at post_case_details (in FE_case_view.py -> /post_case_details )
    logging.dev("[ ] TODO circular import at case_service.py")
    handle_FSM_case_processing_request('init_case', case_id)
    return

def interface_set_case_to_processing(case_id):
    handle_FSM_case_processing_request('is_processing', case_id)
    return

def handle_FSM_case_processing_request(action_type, case_id, simulated=False, data=None):
    ## UPDATE STATE
    #(see case_analytics.py for fetching of state status)
    
    logging.info("[info] at FSM handler for action: "+str(action_type))
    
    case_updated=False

    meta={}
    meta['actions_log']=[]

    if not action_type in ACTION_TYPES:
        raise Exception("Unknown action_type: "+str(action_type))

    Case=Case_Proxy(case_id)
    state,case_meta,case_state_dict=Case.get_state_info()
    
    ## Checking on status could automatically trigger state transition
    if action_type=='check_update_state_status':
        #** see below
        ## AUTO STATE UPDATE?
        #> if DETAILS_POSTED and not processing then should do transition? *effects only missed cases
        pass

    
    ## APPLY FSM Transitions based on state & action_type received
    if ANY_STATE and action_type=='init_case':
        #[ ] hard force init upon request
        case_updated=True
        state='INIT'
        case_state_dict=initialize_case_state_dict(case_id,simulated=simulated)
        Case.set_case_state_info(state,case_state_dict)

        meta['actions_log'].append('init_case')

    elif ANY_STATE and action_type=='is_processing':
        state='PROCESSING'
        case_updated=True
        #case_state_dict['processing_end_time']=time.time()
        Case.set_case_state_info(state,case_state_dict)

    elif ANY_STATE and action_type=='done_case':
        #[ ] also via BE
        #[ ] case_state['metadata']['processing_end_time'] = time.time()

        case_updated=True
        state='DONE'

        ## [ACTION: transition to DONE]
        case_state_dict['processing_end_time']=time.time()
        Case.set_case_state_info(state,case_state_dict)

        meta['actions_log'].append('done_case')

    elif action_type=='check_update_state_status':
        pass

    else:
        raise Exception("Unknown action_type: "+str(action_type))
    
    ## AUTO LOGIC
    if state=='PROCESSING':
        pass
        #case_updated=True
        #[ ] force out of processing if x>time  (something odd happened - put to done or error)
        #[ ] auto set processing_start_time
        #[ ] auto set processing_end_time
        
        # SET TO ERROR IF TOO LONG?
        
        ## Logic to check if processing is done
        if local_ok_transition_processing_to_done(case_id):
            case_updated=True

            state='DONE'
            case_state_dict['processing_end_time']=time.time()

            Case.set_case_state_info(state,case_state_dict)
            meta['actions_log'].append('done_case')


    return case_updated,meta


def handle_FSM_case_admin_request(action_type, case_id, username='',simulated=False, data=None):
    # NOTES:
    #- don't set_state_dict() by default (since delete will re-init)
    meta={}
    meta['actions_log']=[]

    #Case=Case_Proxy(case_id)
    
    if action_type=='delete_case':
        ## Beware re-init
        deleted=admin_delete_case(case_id)
        logging.info("[delete_case] deleted: "+str(deleted))
        if deleted:
            meta['actions_log']+=['deleted_case']

    elif action_type=='create_case':
        case_meta={} #or use existing but will just do update (not overwrite)
        new_case,did_created=admin_create_case(case_id, username,case_meta)
        meta['actions_log']+=['created_case']

    else:
        raise Exception("Unknown action_type: "+str(action_type))

    return meta



def dev_trial_init_case():

    case_id='65a7d94eac045a667c77c8b1'
    case_id='65a7ce0bac045a667c77c7b5'
    
    print ("[dev] initialize case FSM STATE manually: "+str(case_id))
    interface_initialize_case(case_id)
    
    return




if __name__ == "__main__":
    dev_trial_init_case()



"""
### MANUAL TEST USER CASES PAGE FSM at endpoints
def manual_test_page_state():
    case_id='6596f6efc8fca0cb7b70e219' #Jan5

    ## Local find case ie:  test_case_A
    if False:
        from case_service import list_all_cases
        for case in list_all_cases():
            print ("CASE OPTION: "+str(case.case_id))
        a=okkk

    if 'check force init' in []:
        print ("-"*40)
        force_reinit=True
        status,case_state=interface_FE_user_cases_page_state(case_id, user_input=None, case_state=None, BE_input=None,force_reinit=force_reinit)
        print ("[state] status: "+str(status))
        print ("[state] case_state: "+str(case_state))
    
    if 'force assume post request' in []:
        print ("-"*40)
        user_input_word='post_case_details'
        processing_status,case_state=interface_FE_user_cases_page_state(case_id,user_input=user_input_word)
    
    if 'force start processing' in []:
        print ("-"*40)
        user_input_word='request_start_processing'
        processing_status,case_state=interface_FE_user_cases_page_state(case_id,user_input=user_input_word)

    if 'force done processing' in []:
        print ("-"*40)
        #** use force
        simulate_BE_done_processing(case_id)
##        user_input_word='request_start_processing'
##        processing_status,case_state=interface_FE_user_cases_page_state(case_id,user_input=user_input_word)
#
    print ("-"*40+" PROCESSING STATUS CHECK AT END:")
    user_input_word='check_processing_status'
    processing_status, case_state = interface_FE_user_cases_page_state(case_id,user_input=user_input_word)
    print ("[state] status: "+str(processing_status))
    print ("[state] case_state: "+str(case_state))

    return

"""














