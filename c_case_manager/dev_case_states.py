import os, sys
import time
import requests

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")
sys.path.insert(0,LOCAL_PATH+"../../")

from z_apiengine.database_models import Case,User
from z_apiengine.database import SessionLocal
from z_apiengine.services.case_service import list_all_cases


from get_logger import setup_logging
logging=setup_logging()



## Include Job status locally for real-time update


#0v1# JC Jan 11, 2023  Clean Case states


"""
    COLLECTION OF FUNCTIONS FOR MANAGING STATES
    - may not just be admin
"""



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

    
def ADMIN_manual_mirror_state_to_state():
    admonll=onliy

    with SessionLocal() as db:
        cases = db.query(Case).all()
        for case in cases:
            try: case_state_state=case.case_state['state']
            except:
                case_state_state={}
            if case_state_state:
                case.state=case_state_state
                print ("COMMIT: "+str(case.state))
                db.commit()

    return
    

if __name__ == "__main__":
    ADMIN_manual_mirror_state_to_state()









