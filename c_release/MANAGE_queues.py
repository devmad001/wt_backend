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


from c_jobs_manager.jobs_manager import JobsManager
from MANAGE_exe import easy_process_pdf_case


#0v1# JC Dec 29, 2023



"""
    TOP QUEUE MANAGER
    - have most of the capabilities already
    - ensure test coverage and ease of use / requeue
    
    See also:
    - FE_simulate_user_flow.py
    - dev_finaware_services.py
    - 

"""


def ask_job_manager_what_it_knows():
    #/c_jobs_manager/*
    #    test_job_manager.py
    #    jobs_manager.py -> JobsManager

    JM=JobsManager()
    
    jobs=JM.query_jobs(query={})
    statuses={}
    last_error_job={}
    for job in jobs:
        print ("> "+str(job.__dict__))
        # Increment
        statuses[job.status]=statuses.get(job.status,0)+1
        if job.status=='ERROR':
            last_error_job=job.__dict__
    
    print ("[jobs count] "+str(len(jobs)))
    print ("[status count] "+str(statuses))
    print ("[last error job]: "+str(last_error_job))

    return


def alg_list_of_active_cases():

    print ("[A]  FE cases statuses")

    print ("[B]  BE did it run to completion?")


    # did it finish?

    return

def VIEW_execution_log(case_id=''):
    #[x] added formal API endpoint::
    # http://127.0.0.1:8008/api/v1/case/657904fc20668da6f77cd64a/execution_log
    if False:
        from a_agent.interface_manager import Manager_Interface
        MI=Manager_Interface()
        filename,log_content=MI.dump_latest_log(case_id)
    if False:
        # command_services.py -> get_process_state_html(case_id)
        pass
    if False:
        #@app.route('/case/<case_id>/process_status')
        #def process_status(case_id):
        pass
    return


def dev1():
    case_id='658ef4cb4646edcae34b8083'
    case_id='658ef2ee4646edcae34b8021'
#20 random pdf#    case_id='6588ac33e5200c683d6d9425' # Had server-side
    
    b=[]
    b+=['ask what it knows']
    b=[]
    b+=['run case queue']


    if 'ask what it knows' in b:
        ask_job_manager_what_it_knows()

    #alg_list_of_active_cases()
    #VIEW_execution_log(case_id=case_id)
    #local_rerun_case(case_id=case_id)
    
    if 'run case queue' in b:
        print ("RUNNING: "+str(case_id))
        easy_process_pdf_case(case_id=case_id,force_remove_knowledge=True)

    return


def realtime_debug():
    case_id='658ef2ee4646edcae34b8021'

    remote_log_file='/w_datasets/pipeline_exe_logs/'
    """
        66 pages
         exe1_658ef2ee4646edcae34b8021_2023_12_29_16_27.log

    """

    return


if __name__ == "__main__":
    #dev1()
    dev1()


"""
JON CHECK RUNNING:
{'_sa_instance_state': <sqlalchemy.orm.state.InstanceState object at 0x0000022458A69DE0>, 'data': None, 'id': 88, 'case_id': '658ef2ee4646edcae34b8021', 'status': 'RUNNING', 'name': None}

"""