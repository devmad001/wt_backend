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

from MANAGE_queues import ask_job_manager_what_it_knows


#0v1# JC Dec 29, 2023



"""
    ADMIN "high-level"
    - (like the dec28.py but with more functions)

"""



def queue_of_active_cases():

    ##> 

    ##> FARGO 1-10
    ##> FARGO raw
    ##> BOA raw

    return

def links_to_actives():
    #list all cases:  https://core.epventures.co/api/v1/user/list_cases_statuses?user_id=6571b86a88061612aa2fc8b7&fin_session_id=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2NTcxYjg2YTg4MDYxNjEyYWEyZmM4YjciLCJlbWFpbCI6InNoaXZhbUBzaGl2YW1wYXRlbHMuY29tIiwiaWF0IjoxNzAzNzczMTI2LCJleHAiOiIyMDIzLTEyLTI5VDAyOjE4OjQ2LjAwMFoifQ.aa7c939826bd89dafb09a0e8bc1e18d1c6273e6eddea224746abcfba228564b0
    #excel:  https://core.epventures.co/api/v1/case/6588e375e5200c683d6d94b4/generate_excel
    return

def PM_tasks():
    todo=[]
    todo+=['letsencrypt_refresh_on_core_domains']
    todo+=['cases runnings states to check when normal or halt']
    todo+=['time estimation with extended factors']
    todo+=['has case completed flag so clear']

    return

def PM_reminders_to_check():
    rem=[]
    rem+=['case report output there?']

    return

def MANAGEMENT_of_feedback_tweaks():
    #> formalize_tweaks.py
    
    return

def ref_to_functions():
    #  admin_view_all_user_cases_page_status()
    #  ADMIN_remove_job_from_queue(case_id=case_id)
    #  interface_run_one_job_cycle()
    #  is_added=LOCAL_add_case_request_to_job_queue(case_id)
    #  dev_run_page2transaction_on_local_pdf_file():

    return





def jon_admin_functions():

    b=['check on true case processing status']
    b=['requeue failed case']
    b=['emergency manual adjustments']
    b=['check processing queue']
    b=['check a bad case']


    if 'check processing queue':
        ask_job_manager_what_it_knows()



#    if 'check a bad case':
#        #     # http://127.0.0.1:8008/api/v1/case/657904fc20668da6f77cd64a/execution_log
#    """
#        # http://127.0.0.1:8008/api/v1/case/657904fc20668da6f77cd64a/execution_log
#    > {'_sa_instance_state': <sqlalchemy.orm.state.InstanceState object at 0x000001E5CA5F72E0>, 'case_id': '658ef4cb4646edcae34b8083', 'status': 'ERROR', 'name': None, 'data': None, 'id': 89}
#        # http://127.0.0.1:8008/api/v1/case/658ef4cb4646edcae34b8083/execution_log
#        # https://core.epventures.co/api/v1/case/658ef4cb4646edcae34b8083/execution_log
#    """


    return




if __name__ == "__main__":
    jon_admin_functions()


"""
"""