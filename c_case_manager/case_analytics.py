import os, sys
import time
import requests

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")
sys.path.insert(0,LOCAL_PATH+"../../")

from z_apiengine.services.case_service import query_cases_by_various
from z_apiengine.services.case_service import query_list_cases_grouped_by_username_ordered_by_created
from z_apiengine.services.case_service import canned_queries
from z_apiengine.services.case_service import list_user_cases
from z_apiengine.services.case_service import list_all_cases
from z_apiengine.services.case_service import list_all_cases_sorted_by_newest
from z_apiengine.services.case_service import get_case_orm

from case_pipeline import handle_FSM_case_processing_request



from get_logger import setup_logging
logging=setup_logging()




#0v1# JC Jan 12, 2023  Clean Case states


"""
    CASE ANALYTICS
    - States may be a combination of BE and FE, state and metadata
    - mostly covered in case state manager
    - however, ongoing additions expected and included here for efficiency
"""

USER_VIEWED_STATES = {'INIT': 'Not started', 'DETAILS_POSTED': 'Awaiting processing', 
                          'START_REQUESTED': 'Awaiting processing', 'PROCESSING': 'Processing', 
                          'DONE': 'Ready', 'ERROR': 'Error'}
                          
def interface_get_realtime_case_processing_status():
    ## Estimated time remaining
    ## Estimated total time
    ## Percent complete

    return


def interface_list_cases_states():
    #** States may be a combination of BE and FE, state and metadata
    #? cache option?
    
    ## CHECK FOR CASE STATE UPDATE
    #- if state is processing then check for update? ie/ may need to be auto handled if forgotton
    
    ## STATE-LEVEL DETAILS

    ## META LEVEL

    ## CALCULATED
    
    return

#case_pipeline.py: KNOWN_STATES = ['INIT', 'DETAILS_POSTED', 'START_REQUESTED', 'PROCESSING', 'DONE', 'ERROR']
def handle_case_state_update(case):
    #case_orm
    cdict={}

    if not case:
        logging.warning("[warning] case does not exist: "+str(case))
        return cdict

    case_is_old_ignore=False   # Real-time & active status need not be checked
    
    ## Top-level case status
    if case.state in ['DONE','ERROR']:
        case_is_old_ignore=True
    
    ## Stored Case state

    ################################################
    ## Check for FSM updates
    ################################################
    if not case_is_old_ignore:
        ## Refresh Case object "state"
        action_type='check_update_state_status'
        case_updated,meta=handle_FSM_case_processing_request(action_type,case.case_id)
        if case_updated:
            case=get_case_orm(case.case_id) ## Refresh object on state change

    ## Add normal or real-time meta?
    

    ################################################
    ## Format for display (dict)
    ################################################

    cdict['case_id']=case.case_id
    cdict['state']=case.state
    cdict['state_message']=USER_VIEWED_STATES.get(case.state,'Unknown status')
    cdict['case_meta']=case.case_meta #Used by FE_user.py -> /list_cases_statuses
    cdict['case_state']=case.case_state #ie/ last_updated time

    cdict['is_active']= not case_is_old_ignore
    # database_models -> user, case_state (dict), case_meta (dict),

    return cdict


def dev1():
    print ("DEV case_analytics.py")

    ## Efficient case query
    #- go straight to db
    
    username=''
    age_hours=24*3
    
    if 'not done' in []:
        not_state_name='DONE'
        #cases=query_cases_by_various(age_hours=age_hours,not_state_name=not_state_name,username=username)
        cases=query_cases_by_various(not_state_name=not_state_name,username=username)
        for case in cases:
            print(case.__dict__)
            
    if 'recent users' in []:
        cases=query_list_cases_grouped_by_username_ordered_by_created()
        for case in cases:
            print(str(case))
            
    if 'canned_queries':
        #[x]
        branch='list_recent_cases'
        print (">> "+str(branch))
        results=canned_queries(branch=branch)
        
        for result in results:
            print(str(result))

    return


def interface_get_BE_cases_statuses(limit=1000,verbose=False,all_cases=False):
    #> Used in mega_job
    #[ ] sort by: date, status, or filter out
    cdicts=[]
    for case_orm in list_all_cases_sorted_by_newest(limit=limit):
        cdict=handle_case_state_update(case_orm)
        if cdict['is_active'] or all_cases:
            cdicts+=[cdict]
            if verbose:
               print ("[case_analytics.py] case: "+str(cdict))
    return cdicts

def interface_get_user_cases_statuses(user_id,verbose=False):
    #[ ] sort by: date, status, or filter out

    cdicts=[]
    for case_orm in list_user_cases(username=user_id):
        cdict=handle_case_state_update(case_orm)
        cdicts+=[cdict]
        
        if cdict['is_active']:
            if verbose:
                print ("case: "+str(cdict))

    return cdicts

def interface_get_case_status(case_id):
    ## Used by front-end api services!
    #- good to have single entry for any assumed logic
    cdict={}
    case_orm=get_case_orm(case_id)
    if case_orm:
        cdict=handle_case_state_update(case_orm)
    return cdict


def dev_user_queries():
    user_id='6571b86a88061612aa2fc8b7'  ## shivam debug
    cases=list_user_cases(username=user_id)
    
    for case in cases:
        print ("case: "+str(case))

    return

def dev_case_status_normal_query():
    user_id='6571b86a88061612aa2fc8b7'  ## shivam debug
    user_id='65945610a3487347150591e4'  #  evan?
    
    print ("> populating user page view with cases list and status for user: "+str(user_id))
    
    cdicts=interface_get_user_cases_statuses(user_id)

    return

def dump_all():
    for cdict in interface_get_BE_cases_statuses(limit=1000,verbose=False,all_cases=True):
#        print (str(cdict))
#        a=kk
        case_id=cdict['case_id']
        case_name=cdict['case_meta'].get('originalName','')
        user_id=cdict['case_meta'].get('username','')

        url='https://watchdev.epventures.co/fin-aware/dashboard?case_id='+case_id
        
        print (str(url)+"&originalName="+str(case_name)+"&username="+str(user_id))


    return

if __name__ == "__main__":
    #dev1()
    #dev_user_queries()
    #@dev_case_status_normal_query()
    dump_all()






"""


"""










