import os, sys
import time
import requests

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi import Query

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")
sys.path.insert(0,LOCAL_PATH+"../../")


from get_logger import setup_logging
logging=setup_logging()

#from services.square_service import get_service_square_data_records

## For CASE_Proxy memory:
from case_service import admin_set_case_state
from case_service import admin_set_case_state_dict
from case_service import admin_get_case_state_dict

from case_service import list_all_cases

## Include Job status locally for real-time update


#0v3# JC Jan 13, 2023   < REPLACED WITH PROPER FSM @ case_pipeline >
#0v2# JC Jan  5, 2023   Check Smart_Agent if Job has finished in real-time (patch)
#0v1# JC Dec  6, 2023

raise Exception("DEPRECATED:  use case_pipeline.py instead")


"""
    MANAGE STATE MACHINE FOR USER CASES PAGE
    - supports UI, persistent db state, and backend processing option
    - good standalone & easy check, cache and update
    - org was FE_simulate_user_flow...
"""

 

class CASE_Proxy:
    ## Abstract methods ok
    def __init__(self,case_id):
        self.case_id=case_id
        return
    
    def set_state_key(self,kkey,vvalue):
        return admin_set_case_state(self.case_id,kkey,vvalue) #returns full dict
    
    def set_state_word(self,word):
        print ("[debug] case_id: "+str(self.case_id)+" STATE: "+str(word))
        return self.set_state_key('state_word',word)
    
    def get_state_dict(self):
        state_dict=admin_get_case_state_dict(self.case_id)
        if not state_dict: state_dict={}
        return state_dict

    def set_state_dict(self,state_dict):
        if state_dict:  #Basic check
            admin_set_case_state_dict(self.case_id,state_dict)
        return
    

def describe_case_processing_states(case_id, user_input=None, case_state=None, BE_input=None, force_reinit=False,verbose=True,force_done=False):
    ## Performance:  This take 0.6s on local cpu (db queries?)
    
    # force_reinit:  used for dev purposes, resets state to init state

    start_time=time.time()

    ASSUME_SIMULATED_CASE=False  #Captured in state for simulation reasons

    if case_state is None:
        case_state = {}

    Case = CASE_Proxy(case_id)
    
    processing_status={}
    processing_status['case_state']= 'Unknown'
    processing_status['report_available']=False

    # Load case state
    case_state = Case.get_state_dict()
    
    if verbose:
        print ("[debug] case state stored: "+str(case_state))

    states = ['INIT', 'DETAILS_POSTED', 'START_REQUESTED', 'PROCESSING', 'DONE', 'ERROR']
    user_viewed_states = {'INIT': 'Not started', 'DETAILS_POSTED': 'Awaiting processing', 
                          'START_REQUESTED': 'Awaiting processing', 'PROCESSING': 'Processing', 
                          'DONE': 'Ready', 'ERROR': 'Error'}
                          
    ## Custom logic to reinitalize previously queued states for redo (though should have had some uploaded)
    #[ ] can remove once no longer simulated
    reinitialize_simulated_case_to_init_state=False
#tbd#    if 'metadata' in case_state:
#tbd#        if 'sim_case' in case_state['metadata']:
#tbd#            if case_state['metadata']['sim_case']!=ASSUME_SIMULATED_CASE:
#tbd#                reinitialize_simulated_case_to_init_state=True


    ### INITIALIZE
    if 'state' not in case_state or force_reinit:
        print ("[debug] case state at: "+str(case_id)+" is: "+str(case_state))
        # Initialize the state for new cases
        case_state = {
            'state': 'INIT',
            'metadata': {
                'processing_start_time': None,
                'processing_end_time': None,
                'last_updated': time.time(),
                'error_info': None,
                'sim_case': ASSUME_SIMULATED_CASE
            }
        }
        print ("[info] USER CASES PAGE Case status (re)-initialized")
        print ("====================================>>> STATE SET TO INIT AT: "+str(case_id))
        

    ##############################################################################################
    ## External case done processing update
    ##
    current_state = case_state['state']
    if BE_input == 'BE_done_processing' and current_state == 'PROCESSING':
        case_state['state'] = 'DONE'
        case_state['metadata']['processing_end_time'] = time.time()
        current_state = case_state['state']
    
    if force_done:
        print ("*** FORCING DONE AT: "+str(case_id))
        current_state = case_state['state']
        if True or BE_input == 'BE_done_processing' and current_state == 'PROCESSING':
            case_state['state'] = 'DONE'
            case_state['metadata']['processing_end_time'] = time.time()
            current_state = case_state['state']
        
    ##############################################################################################
    ### JAN 5 patch   [ ] formalize
    if current_state == 'PROCESSING':
        ## Check patch
        has_finished=local_patch_has_case_ever_finished(case_id)
        if has_finished:
            case_state['state'] = 'DONE'
            case_state['metadata']['processing_end_time'] = time.time()
            current_state = case_state['state']
    ##############################################################################################

    # simulation logic
    if not 'sim_case' in case_state['metadata']:
        case_state['metadata']['sim_case'] = ASSUME_SIMULATED_CASE

    if case_state['metadata']['sim_case']:
        if current_state == 'PROCESSING':
            # If more then 5 minutes processing, move to done state
            if time.time() - case_state['metadata']['processing_start_time'] > 5 * 60:
                case_state['state'] = 'DONE'
                case_state['metadata']['processing_end_time'] = time.time()
                current_state = case_state['state']
    ##############################################################################################


    current_state = case_state['state']

    logging.info("[debug user_input]: "+str(user_input))
    ## Handle different user inputs to change state
    if user_input == 'post_case_details':
        if current_state in ['INIT', 'ERROR']:
            case_state['state'] = 'DETAILS_POSTED'

    elif user_input == 'request_start_processing':
        if current_state == 'DETAILS_POSTED':
            case_state['state'] = 'START_REQUESTED'
            case_state['metadata']['processing_start_time'] = time.time()

            case_state['state'] = 'PROCESSING'

    elif user_input == 'check_processing_status':
        # No state change, just checking current status

        # Map the internal state to a user-viewable state
        processing_status['case_state'] = user_viewed_states.get(current_state, 'Unknown')

    elif user_input == 'get_finished_report':
        if current_state == 'DONE':
            case_state['metadata']['processing_end_time'] = time.time()
    current_state = case_state['state']
    

    ### UPDATE OR SET PROCESSING STATUS

    ## logic for processing, such as setting state to 'PROCESSING' or 'DONE'
    if current_state in ['DONE']:
        processing_status['report_available'] = True
        
    ## Also update above via logic so consider separate function
    processing_status['case_state']=user_viewed_states.get(current_state, 'Unknown')

    # Update last_updated time
    case_state['metadata']['last_updated'] = time.time()

#D1    print ("case_state PRE: "+str(case_state))
    # Save the updated state
    
    ## Always update?

    Case.set_state_dict(case_state)
    
    ## (DEV REMOVE OK)
#D1    print ("[debug set]: "+str(case_state))
#D1    case_state=Case.get_state_dict()
#D1    print ("[case_state debug get]: "+str(case_state))
#D1    if not case_state:
#D1        raise Exception("ERROR: case_state not saved properly")
    
    processing_status['case_id']=case_id
    case_state['case_id']=case_id
    
    print ("RAW STATE DICT: "+str(case_state))
    
    runtime=time.time()-start_time
    print ("[debug] case state run: "+str(runtime)+" seconds")

    return processing_status,case_state



def simulate_BE_done_processing(case_id):
    # (for testing can have transition on time check)
    describe_case_processing_states(case_id, BE_input='BE_done_processing')
    return

def force_done_processing(case_id):
    # (for testing can have transition on time check)
    describe_case_processing_states(case_id, BE_input='BE_done_processing',force_done=True)
    return


def dev_call_case_states():
    print ("Simulate walk through")

    case_id='6570af77949fdfbf2c5810e8'

    ## EXPECTED INPUTS
    user_input=None  #ok
    user_input='post_case_details'
    user_input='request_start_processing'
    user_input='check_processing_status'
    user_input='get_finished_report'
    
    ## EXPECTED OUTPUTS
    #processing_status
    #processing_status['case_state']:  'Not started', 'Awaiting processing', 'Processing', 'Ready', 'Error'
    #processing_status['report_available']: True/False

    status,case_state=describe_case_processing_states(case_id, user_input=user_input)
    print ("USING INPUT: "+str(user_input)+" status: "+str(status))
  
    return

def interface_FE_user_cases_page_state(case_id, user_input=None, case_state=None, BE_input=None,force_reinit=False):
    ### HANDLE STATE
    processing_status={}
    case_state={}
    if case_id:
        processing_status,case_state=describe_case_processing_states(case_id, user_input=user_input, case_state=case_state, BE_input=BE_input, force_reinit=force_reinit)
        #** don't manipulate data here but can use the state to know what to return (since this tied into API backend)
    return processing_status,case_state



def interface_list_cases_states(user_id='',all_states=False):
    ## Support User Cases Page view side bar status
    #- ultimately mapped to response format.  
    #- watch cause will want to filter by case ownership
    #b)  include case name

    tups=[]
    for case in list_all_cases(user_id=user_id):
        case_id=case.case_id

        case_state=case.case_state
        case_meta=case.case_meta

        #^^ case_meta from User Cases Page
        # {'name': '5dcffba0-27fb-4ef7-9f10-a87059922802.pdf', 'size': '0', 'username': '6571b86a88061612aa2fc8b7', 'file_urls': ['https://storage.cloud.google.com/watertower_bucket/input/5dcffba0-27fb-4ef7-9f10-a87059922802.pdf'], 'description': '', 'originalName': 'bank state 3.pdf', 'threatTagging': '1', 'case_creation_date': '2023-12-28T14:58:49.120Z', 'publicCorruptionTag': ''}

        if not case_state: continue

        ## Active states? 'state': 'INIT', 'm
        #['INIT', 'DETAILS_POSTED', 'START_REQUESTED', 'PROCESSING', 'DONE', 'ERROR']
        if not all_states and case_state['state'] in ['INIT', 'DETAILS_POSTED']:
            pass

        else:
            ## Consider active
#            print ("CASE OPTION: "+str(case.case_id)+" --> "+str(case.case_state))
            
            ## Get or refresh latest state
            processing_status,case_state=interface_FE_user_cases_page_state(case_id)
            tup=[(case_id,processing_status,case_state,case_meta)]

#            print ("> "+str(tup))
            tups+=tup
            

    return tups


### MANUAL TEST USER CASES PAGE FSM at endpoints
def manual_test_page_state():
    case_id='6570af77949fdfbf2c5810e8'
    
    case_id='test_case_A'
    case_id='6571bfe12901cd15485de444'
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


def admin_view_all_user_cases_page_status():
    for case in list_all_cases():

        case_id=case.case_id
        case_dict=case.case_meta
        case_state=case.case_state
        

#        if not case_id=='65987c726c33e2599cce5eba': continue

        file_urls=case_dict.get('file_urls',[])

#        print ("[debug all]:: "+str(case_dict))
        
        if not case_state: continue
        
        print ("STATE: "+str(case_state['state']))
        
#beware#        if case_state['state']=='PROCESSING':
        a=checkkok
        if case_state['state']=='DETAILS_POSTED':
            force_done_processing(case_id)
        continue

        force_done_processing(case_id)

        if file_urls and '//' in str(file_urls): #'STRING' bad
#            if not '12-08' in str(case_dict): continue
            if not case_state: continue #pre bad save

            print ("-"*40)

            print ("CASE OPTION: "+str(case.case_id)+" --> "+str(case_dict))
            print ("CASE OPTION: "+str(case.case_id)+" --> "+str(case_state))


    return


def local_patch_has_case_ever_finished(case_id):
    from a_agent.iagent import Smart_Agent
    logging.info("[Smart_Agent] circular import patch!")

    ## Smart_Agent talks directly with backend pipeline status
    Agent=Smart_Agent()
    has_finished=Agent.dev_has_case_finished_ever(case_id)
    return has_finished


def call_local_patch_case_status():
    case_id='6596f6efc8fca0cb7b70e219'
    has_finished=local_patch_has_case_ever_finished(case_id)
    print ("Has finished: "+str(has_finished))

    return


if __name__ == "__main__":

#    dev_call_case_states()
#    simulate_BE_done_processing('6570af77949fdfbf2c5810e8')
#    test_FE_state_interface()
    admin_view_all_user_cases_page_status()
#    manual_test_page_state()
#    call_local_patch_case_status()










