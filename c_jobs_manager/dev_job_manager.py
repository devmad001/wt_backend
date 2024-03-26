import os
import sys
import codecs
import json
import re
import time
import threading

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")

from w_storage.ystorage.ystorage_handler import Storage_Helper

from get_logger import setup_logging
logging=setup_logging()

from entry_workflows_jobs import entry_get_ujob_status
from entry_workflows_jobs import create_new_job
from entry_workflows_jobs import iter_jobs
from entry_workflows_jobs import add_job_to_queue

from jobs_manager import JobsManager


#0v1# JC  Nov 27, 2023  Init **informal



"""
    TESTS FOR JOB MANAGER
   
    jobs_model
        -> jobs_manager
            -> entry_workflow_jobs
                -> test_job_manager

"""



def test_create_new_job():
    Job=create_new_job(id='test_job_1',name='test_job',data={})
    if not Job.id: raise Exception('no job id')
    return Job

def test_get_ujob_status():
    #ujob== original sqlite
    case_id='MarnerHoldingsB'
    job_status=entry_get_ujob_status(case_id)
    if not job_status['job_id']: raise Exception('no job_id')
    return

def test_is_case_id_in_job_queue(case_id):
    JM=JobsManager()
    if JM.is_case_id_in_job_queue(case_id):
        print ('case_id in job queue')
    else:
        print ('case_id not in job queue')
        
    return

# ^^^ above has basic test
###################################

def test_CHECK_job_status():
    c=0
    for Job in iter_jobs():
        c+=1
        #Job.check_job_status()
    print ("Job count in db: "+str(c))
    return

def test_add_job_to_db():
    Job=create_new_job(id='test_job_1',name='test_job',data={})
    add_job_to_queue(Job)
    return


def test_SET_job_status():
    return
def test_spawn_job_in_background():
    return
def test_check_jobs_in_background():
    return
def test_get_system_resources():
    return


def dev1():
    #== dev == in-development functions (not tests)

    case_id='MarnerHoldingsB'
    
    b=[]
    b+=['put mock job in db']

    if 'put mock job in db' in b:
        pass
    
    return


def test_run_test_scripts():
    ## General (unofficial tests)
    
    b=[]
    
    if 'ok tested' in b:
        test_create_new_job()
        test_get_ujob_status()

    ## Continued run
    #test_CHECK_job_status()
    #test_add_job_to_db()
    
    ## JC Dec 10
    #** see ADMIN_mega_job
    case_id='simulated_case_request_case_1'
    test_is_case_id_in_job_queue(case_id)

    return



if __name__=='__main__':
    branches=['test_run_test_scripts']
    for b in branches:
        globals()[b]()




"""
"""
