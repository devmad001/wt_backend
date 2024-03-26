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




#0v1# JC Jan 11, 2023  Clean Case states


"""
    ADMIN CONTROLS OF CASE
    - mostly state related
    - see handle_FSM_case_admin_request  for cleaner state changes
    
    - Also have activities here for joining with backend
"""


    
def DEV_manual_mirror_state_to_state():
    ## Sample modify records for admin
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
    



def dev_recall_case_processing_start():
    print ("?? what calls a case -- starts? post_case_details?")
    
    """
    [ STEP 1 ] --> create case in db
    FE_case_view.py -> /post_case_details
    front_create_set_case(case_id=case_id,username=username, case_meta=case_meta)
    from services.finaware_services import front_create_set_case
    from case_service import create_set_case
    ^^ CREATES CASE


    [ STEP 2 ] --> start case processing?
    start case processing
    
    **JON: see entry.
    case_analytics
    job_analytics entrypoint recall.
    
     python ENTRYPOINT_mega_job.py


    """

    print ("[1] is there a case?")
    
    print ("[2] check status")
    
    print ("[3] put into formal queue")

    return





from case_analytics import interface_get_case_status
def dev1():
    a=a111

    print ("ENTRY STATE NEE.  65a7d94eac045a667c77c8b1")
    case_id='65a7d94eac045a667c77c8b1'
    case_id='65a7ce0bac045a667c77c7b5'

    cdict=interface_get_case_status(case_id)
    print ("STATUS: "+str(cdict))
    
    if cdict['state']==None:
        print ("BEWARE: case never initialized")
        
        ## Recall how case is normally initialized.
        
        handle_FSM_case_processing_request('init_case',case_id)


    
    return


def dev_admin_force_done():
#    a=a111
    from case_pipeline import handle_FSM_case_processing_request
    case_id='65a7d94eac045a667c77c8b1'
    case_id='65a7ce0bac045a667c77c7b5'
    case_id='65a80a1bb3ac164610ea58ba'
    
    case_id='65a813bbb3ac164610ea5ac4' #new age for init
    case_id='65a847d0b3ac164610ea617b' # marner not done was before ok now

    handle_FSM_case_processing_request('is_processing',case_id)
#    handle_FSM_case_processing_request('done_case',case_id)
#    handle_FSM_case_processing_request('init_case',case_id)
    
    return

def get_status():
    case_id='65a82cc9b3ac164610ea5e64'
    cdict=interface_get_case_status(case_id)
    print ("STATUS: "+str(cdict))
    return

def ADMIN_force_stuff():
    print ("ADMIN FORCE STUFF **delete all?!")
    from case_state_objs import Cases_State_Manager
    from z_apiengine.services.case_service import update_case_state

    CM=Cases_State_Manager()
    ccounts={}
    for case in CM.iter_cases():
        print ("CASE ID: "+str(case.case_id)+" -> "+str(case.state))
        try: ccounts[str(case.state)]+=1
        except: ccounts[str(case.state)]=1

        if not str(case.state)=='DONE':
            print ("FOR update ^ to done")
            stopp=manual_check
#            update_case_state(case.case_id,'DONE')

    print ("OK: "+str(ccounts))
    return


if __name__ == "__main__":
#    dev1()
#    dev_admin_force_done()
#    get_status()
    ADMIN_force_stuff()



















