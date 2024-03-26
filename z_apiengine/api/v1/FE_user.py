import os, sys
import time

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi import Query
from pydantic import BaseModel, Field, condecimal
from typing import List, Optional
from decimal import Decimal


LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")
sys.path.insert(0,LOCAL_PATH+"../../")

from c_jobs_manager.mega_job import interface_get_verbose_job_status
from c_case_manager.case_analytics import interface_get_user_cases_statuses


from get_logger import setup_logging
logging=setup_logging()


#0v4# JC Jan 13, 2024  Use new case states
#0v3# JC Dec 12, 2023  Tie into backend job manager c_jobs_manager/mega_job -> interface_manager.py -> get_verbose_state_of_case
#0v2# JC Dec  9, 2023  Include states from Case state machine
#0v1# JC Dec  5, 2023


"""
    USER VIEW
    - store key & user id
    - link user to case??

"""


router = APIRouter()


#** cache stats?
def local_get_case_states_and_map_to_view(user_id=''):
    ###  RECALL SETUP:
    #- FE queue
    #- BE queue
    #- Job status

    """
    case_id, processing_status,case_state @FE_cases_page_states.py

    [('6573a74f50560b89044dcf58', {'case_state': 'Ready', 'report_available': True, 'case_id': '6573a74f50560b89044dcf58'}, {'state': 'DONE', 'metadata': {'sim_case': True, 'error_info': None, 'last_updated': 1702146352.077727, 'processing_end_time': 1702145696.0883467, 'processing_start_time': 1702145194.5354607}, 'case_id': '6573a74f50560b89044dcf58'})]
     states = ['INIT', 'DETAILS_POSTED', 'START_REQUESTED', 'PROCESSING', 'DONE', 'ERROR']
    user_viewed_states = {'INIT': 'Not started', 'DETAILS_POSTED': 'Awaiting processing', 
                          'START_REQUESTED': 'Awaiting processing', 'PROCESSING': 'Processing', 
                          'DONE': 'Ready', 'ERROR': 'Error'}
                          
    """

    ASSUME_SIMULATED_CASE=False #Dec 28# True  #see FE_cases_page_states too
    ASSUMED_PROCESSING_TIME=5*60 # if time.time() - case_state['metadata']['processing_start_time'] > 5 * 60:
    
    #target is base model: title, state, percent, remaining_minutes

    viewable_cases=[]

    cdicts=interface_get_user_cases_statuses(user_id)

    logging.info("[debug] user cases count: "+str(len(cdicts)))

    MG=None  #easy mem for interface object
#ORG#    for case_id, case_state, processing_status,case_meta in tups:
    for cdict in cdicts:
        ## Direct map at start for obvious
        case_id=cdict['case_id']
        state=cdict['state']
        case_meta=cdict['case_meta']
        
        ## Map to view
        remaining_minutes=0

        originalName=case_meta.get('originalName','') #name, size, username, file_urls, description, origalName, threatTagging, case_creation_date, publicCorruptionTag
        
        view_case={}
        if originalName:
            view_case['title']='Case: '+originalName
        else:
            view_case['title']='Case: '+case_id

        view_case['state']=state

        ## Remote calc time remaining
        
        ## Get varbose job details (but slow so only if not DONE or ERROR)
        if not state in ['DONE','ERROR']:
            pass
            start_time=time.time()
            vstats,MG=interface_get_verbose_job_status(case_id,MG)
            runtime=time.time()-start_time
            logging.info("[debug] FE_user.py VERBOSE case status runtime: "+str(runtime))
            
            if vstats:
                if vstats['is_done_processing']:
                   percent_complete=100
                else:
                   percent_complete=vstats['percent_complete']
                   remaining_minutes=vstats['remaining_minutes']
            else:
                percent_complete=0
                remaining_minutes=0
        else:
            percent_complete=100
            remaining_minutes=0
               

        view_case['percent']=percent_complete
        view_case['remaining_minutes']=int(remaining_minutes) #** type required

        
        logging.info("[debug] FE_user.py case status CASE: "+str(view_case))
        
        viewable_cases+=[view_case]

    return viewable_cases


class Case(BaseModel):
    title: str
    state: str
    percent: condecimal(max_digits=10, decimal_places=2)  # Using condecimal for Decimal type
    remaining_minutes: int

class CaseList(BaseModel):
    cases: List[Case]

@router.get("/list_cases_statuses", response_model=CaseList)
async def list_cases_statuses(user_id: str, fin_session_id: Optional[str] = None):
    """
    List the statuses of cases for a given user.

    - **user_id**: The unique identifier of the user.
    - **fin_session_id**: An optional (for now) fin_session_id
    """
    cases = []  # Logic to retrieve list of cases based on user_id and fin_session_id

    # Example: cases = [{'title': 'Case 1', 'state': 'Normalizing pdf', 'percent': Decimal('50.0'), 'remaining_minutes': 120}, ...]
    
    #logging.info("[debug] listing case statuses but consider caching...")
    logging.info("[debug] list_cases_statuses user_id: "+str(user_id))
    viewable_cases=local_get_case_states_and_map_to_view(user_id=user_id)
    cases=viewable_cases+cases
    
    ## Auto validation
    # set state value to '' if state value is not string
    for case in cases:
        if not isinstance(case['state'], str):
            case['state'] = ''
    
    ## Sort cases by state if state in ['Processing','Awaiting processing','Ready'] As top priority then the rest
    cases=sorted(cases, key=lambda k: k['state'] in ['Processing','Awaiting processing','Ready'], reverse=True)

    return CaseList(cases=cases)


class CaseIDList(BaseModel):
    case_ids: List[str]

@router.get("/list_user_finished_cases_ids", response_model=CaseIDList)
async def list_user_finished_cases_ids(user_id: str, fin_session_id: Optional[str] = None):
    """
    List the case IDs for a given user. This endpoint retrieves all the case identifiers associated with the specified user.

    - **user_id**: The unique identifier of the user for whom the case IDs are being queried.
    - **fin_session_id**: An optional (for now) fin_session_id identifier that can be used for additional filtering or context.

    Returns a list of case IDs as strings.
    """
    # Replace with actual logic to fetch case IDs from your data source
    case_ids = ['DummyCase1','NotARealCase','Dummy3']
    case_ids = []  # Example: ['case123', 'case456', 'case789', ...]

    return CaseIDList(case_ids=case_ids)




if __name__ == "__main__":
    local_get_case_states_and_map_to_view(user_id='6571b86a88061612aa2fc8b7')
