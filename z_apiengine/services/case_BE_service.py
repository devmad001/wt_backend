import os
import sys
import codecs
import json
import re
import time
import json

from sqlalchemy.orm import Session

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")
sys.path.insert(0,LOCAL_PATH+"../..")

from database_models import Case,User

from c_case_manager.case_analytics import interface_get_user_cases_statuses
from c_case_manager.case_analytics import interface_get_case_status

from get_logger import setup_logging
logging=setup_logging()


        
#0v3# JC Jan 13, 2023  Clean with new FSM
#0v2# JC Dec 24, 2023  get or generate report 
#0v1# JC Dec  6, 2023  TEST


"""
    CASE BACKEND SERVICE
    - used by FE_case_view.py
    - abstract in BE_proxy.py

"""


def get_case_report(case_id):
    #[ ] TODO:  requires setup
    from c_macros.m_reports.report_case_summary import INTERFACE_generate_get_report  #JC debug
    sample_report_data = {}
    try: sample_report_data=INTERFACE_generate_get_report(case_id)
    except: pass
    report_data=sample_report_data
    return {"data": report_data}

#    """
#    Retrieves the report for a given case by case_id.
#    - requires Case processing state to be complete
#    - ? required to match CaseReportData output? in FE_case_view??
#    """
#DEL#    user_input_word='get_finished_report'
#DEL#    processing_status,case_state=interface_FE_user_cases_page_state(case_id,user_input=user_input_word)
#DEL#    
#DEL#    ## ORG
#DEL#    if processing_status.get('report_available',False):
#DEL#        #[ ]# load report from back end
#DEL#        sample_report_data = {
#DEL#            "account_holder_name": "John Doe",
#DEL#            "account_holder_address": "123 Main St, Anytown, AN",
#DEL#            "number_of_transactions": 100,
#DEL#            "opening_balance": 5000.00,
#DEL#            "closing_balance": 4500.00,
#DEL#            "number_of_inflows": 70,
#DEL#            "number_of_outflows": 30,
#DEL#            "inflow_amount": 7000.00,
#DEL#            "outflow_amount": 7500.00,
#DEL#        }
#DEL#
#DEL#    else:
#
#    sample_report_data = {}
##TBD#    sample_report_data['case_state']=processing_status.get('case_state','')
#        
#j    ## New will generate or load
#    try: sample_report_data=INTERFACE_generate_get_report(case_id)
#    except: pass
#    
#    report_data=sample_report_data
#    return {"data": report_data}


def get_case_processing_status(case_id):
    """
        >> Called from m api FE_case_view
        - Retrieves the processing status
        - use new FSM
        - watch target variables (check front-end TODAY!)
        TODO:
        [ ] migrate estimated_time + variable mapping upstream to interface_get_case_status

    """

    status_data={}
    cdict=interface_get_case_status(case_id)
    
    logging.info("[debug] raw case ["+str(case_id)+"] data: "+str(cdict))
    
    # Return None emtpy
    if not cdict:
        return {"data": status_data}
    
    # 


    processing_status={}
    case_state={}


    # Initialize the status_data dictionary
    status_data = {
        "case_id": case_id,
        "is_case_started": False,
        "is_case_running": False,
        "is_case_ready_to_query": False,
        "last_state": cdict['state'],
        "case_status_word": "inactive",
        "case_files": [],  # You need to define how to get these
        "estimated_case_running_time_remaining_m": None,  # Define logic to calculate this
        "age_of_last_active_m": None,  # Define logic to calculate this
        "has_job_ever_finished": False,
        "job_page_count": 0,  # You need to define how to get this
    }

    #** Ideally these descriptive mappings happen in case_analytics
    # Update the status_data based on case_state and processing_status
    current_state = cdict['state']
    if current_state != 'INIT':
        status_data['is_case_started'] = True

    if current_state == 'PROCESSING':
        status_data['is_case_running'] = True
        status_data['case_status_word'] = "active"

    if current_state == 'DONE':
        status_data['has_job_ever_finished'] = True
        status_data['is_case_ready_to_query'] = True
        status_data['case_status_word'] = "completed"

    # Additional logic for calculating other fields like 'estimated_case_running_time_remaining_m', 'age_of_last_active_m', etc.
    
    ## Time remaining
    expected_total_processing_time = 5*60 #5 minutes also is sim_case

    # Calculate the estimated remaining processing time
    status_data['estimated_case_running_time_remaining_m'] = 0

    if 'metadata' in case_state:
        if case_state['metadata']['processing_start_time']:
            elapsed_time = time.time() - case_state['metadata']['processing_start_time']
            remaining_time = max(expected_total_processing_time - elapsed_time, 0)
            status_data['estimated_case_running_time_remaining_m'] = int(remaining_time / 60)  # convert to minutes

    status_data['case_state']=processing_status.get('case_state','')

    return {"data": status_data}


def get_sample():
    # FE sample target Jan 13, 2024 [ ] add test.
    api_sample=json.loads("""{
  "status": "ok",
  "data": {
    "case_id": "65858e0c198ceb69d5058fc3",
    "is_case_started": true,
    "is_case_running": false,
    "is_case_ready_to_query": true,
    "last_state": "Ready",
    "case_status_word": "completed",
    "case_files": [],
    "estimated_case_running_time_remaining_m": 0,
    "age_of_last_active_m": null,
    "has_job_ever_finished": true,
    "job_page_count": 0
  } """)
    return api_sample


def dev_check_update_to_new_backend():
    # Local test
    #** All logic moved to case_analytics
    #[ ] add test
    case_id="65858e0c198ceb69d5058fc3"
    
    if False: #ORG
        data0=get_case_processing_status_ORG(case_id)
        print ("TARGET: "+str(get_sample()))
        print ("NOW: "+str(data0))
        
    ## New
    data0=get_case_processing_status(case_id)
    print ("NOW: "+str(data0))

    return



if __name__=='__main__':
    branches=['dev_check_update_to_new_backend']
    for b in branches:
        globals()[b]()






