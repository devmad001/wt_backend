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
from a_agent.iagent import Smart_Agent

from jobs_manager import JobsManager

from get_logger import setup_logging
logging=setup_logging()



#0v2# JC  Dec 10, 2023  See lean mega_job.py
#0v1# JC  Nov 24, 2023  Init



"""
    **see lean mega_job.py
    WORKFLOWS FOR JOB MANAGEMENT
    
    jobs_model
        -> jobs_manager
            -> entry_workflow_jobs
                -> test_job_manager

"""


def create_new_job(id='',name='',data={}):
    Manager=JobsManager()
    Job=Manager.init_job(id=id,name=name,data=data)
    return Job

def iter_jobs():
    Manager=JobsManager()
    for Job in Manager.query_jobs(query={}):
        yield Job
    return

def add_job_to_queue(Job):
    ## Check job?
    Manager=JobsManager()
    Manager.add_job(Job)
    return

######################################
#  BELOW ARE SKELETON WORKFLOWS
######################################

def dev_create_new_job():
    # Define a custom job class
    Job=J
    class MyCustomJob(Job):
        def __init__(self, id, name, data):
            super().__init__(id, name)
            self.data = data
    
        def run(self):
            print(f"Running job {self.id}")
            # Add job logic here
    return


def create_new_job_to_run():
    # Create and add a new job
    new_job_data = {"example_key": "example_value"}
    new_job = MyCustomJob(id=1, name="ExampleJob", data=new_job_data)
    jobs_manager.add_job(new_job)
    
    # Start processing jobs
    jobs_manager.start_processing()

    return

def check_status_of_job():
    # Function to check job status
    def check_job_status(job_id):
        job = session.query(JobModel).filter(JobModel.id == job_id).first()
        if job:
            return job.status
        else:
            return "Job not found"
    
    # Example usage
    status = check_job_status(1)
    print(f"Status of job 1: {status}")
    return
    
def restart_failed_job():
    #    To restart a failed job, you would first check if it failed and then re-add it to the job queue.
    
    # Function to restart a failed job
    def restart_failed_job(job_id):
        job = session.query(JobModel).filter(JobModel.id == job_id).first()
        if job and job.status == "ERROR":
            print(f"Restarting job {job_id}")
            # Assuming the job data is still valid, recreate and requeue the job
            restarted_job = MyCustomJob(id=job_id, name=job.name, data=job.data)
            jobs_manager.add_job(restarted_job)
    
    # Example usage
    restart_failed_job(1)
    return

def validate_job_ran_correctly():
    # To validate that a job ran successfully, you would check if its status is "DONE" after its expected completion time.
    # Function to validate job success
    def validate_job_success(job_id):
        status = check_job_status(job_id)
        if status == "DONE":
            print(f"Job {job_id} ran successfully.")
        else:
            print(f"Job {job_id} did not run successfully. Current status: {status}")
    
    # Example usage (after an appropriate delay to allow job processing)
    validate_job_success(1)
    return

def update_job_data():
    #Sometimes you might need to update the data associated with a job, either before it starts or after it finishes.
    
    # Function to update job data
    def update_job_data(job_id, new_data):
        job = session.query(JobModel).filter(JobModel.id == job_id).first()
        if job:
            job.data = new_data
            session.commit()
            print(f"Updated data for job {job_id}")
        else:
            print("Job not found")
    
    # Example usage
    new_data = {"updated_key": "updated_value"}
    update_job_data(1, new_data)
    return

def pause_and_resume_job():
    #In some systems, you might want the ability to pause and resume jobs. This requires additional logic in the job's run method to handle pausing.
    # Assuming a global flag for simplicity
    pause_job_flag = False
    
    class MyCustomJob(Job):
        # ... existing methods ...
    
        def run(self):
            while pause_job_flag:
                time.sleep(1)  # Pause the job
            # Job logic here
    return

def cancel_job():
    #Cancel a job that's either in the queue or currently running.
    # Function to cancel a job
    def cancel_job(job_id):
        # Logic to remove job from the queue or stop it if it's running
        pass  # Implementation depends on the job's design
    
    return

def listing_all_jobs():
    #Sometimes you might want to list all jobs with their statuses.
    
    # Function to list all jobs
    def list_all_jobs():
        jobs = session.query(JobModel).all()
        for job in jobs:
            print(f"Job ID: {job.id}, Name: {job.name}, Status: {job.status}")
    
    # Example usage
    list_all_jobs()
    return

def handling_job_dependencies():
    #In more complex scenarios, jobs might have dependencies on the completion of other jobs.
    
    # Function to check dependencies and queue job
    def queue_job_with_dependency(job, dependency_job_id):
        dependency_job = session.query(JobModel).filter(JobModel.id == dependency_job_id).first()
        if dependency_job and dependency_job.status == "DONE":
            jobs_manager.add_job(job)
        else:
            print(f"Dependency for job {job.id} not met yet")
    
    # Example usage
    dependent_job = MyCustomJob(id=2, name="DependentJob", data={"key": "value"})
    queue_job_with_dependency(dependent_job, 1)  # Assuming job 1 is the dependency
    
    return
    

def dev1():
    workflows=[]
    workflows+=['sync job status with sqlite']
    workflows+=['create new job to run']
    workflows+=['check status of job']
    workflows+=['restart failed job']
    workflows+=['validate job ran correctly']
    workflows+=['update job data']
    workflows+=['puase and resume job']
    workflows+=['cancel job']
    workflows+=['list all jobs']
    workflows+=['handle job dependencies'] #Run after, push updates, tbd.

    workflows+=['push job to external system (receive from central system']
    workflows+=['']

    return


def entry_get_ujob_status(case_id):
    ## Where ujob is original job setup

    print ("Check existing jobs setup")
    
    case_id='MarnerHoldingsB'

    Agent=Smart_Agent()
    
    job=Agent.case2job(case_id)

    return job


def dev2():
    print ("Check existing jobs setup")
    
    case_id='MarnerHoldingsB'
    job=entry_get_ujob_status(case_id)
    
    print ("HIGH LEVEL STATE MACHINES")

    """
    - let system run as-is??
    - START:  put into queue (to ensure fully processed even on error)
    - MONITOR PROGRESS
    - AUTO RESTART/RETRY
    - REPORT
    - RESOURCE_LOGGING  (should have most stats already)
    - RESOURCE_ESTIMATION

    """

    return


def dev3():
    ## Capability requirements

    reqs=[]
    reqs+=['enqueue job for processing in mysql database']  # Must ensure completition attempt
    reqs+=['check status']                                  # Done, Error, Running, Queued...
    reqs+=['set status of job']
    reqs+=['spawn job from Job Manager side']               # Start from zero
    
    ## Extra fancies
    reqs+=['completion broadcast']
    reqs+=['parallel support']
    reqs+=['mock runs']
    

    return


def interface_case_done_processing(case_id):
    ## Job perspective
    #>> same method!
    
    if True or 'one way' in []:
        Agent=Smart_Agent()
        job1=Agent.case2job(case_id)
        print ("J1: "+str(job1))
        
        print ("FINISHED EVER: "+str(Agent.dev_has_case_finished_ever(case_id)))
        
        
#    if True or 'another way' in []:
#        job2=entry_get_ujob_status(case_id)
#        print ("J2: "+str(job2))

    """
    J2: {'case_id': '6587008b36850ea066e5843c', 'version': 1, 'job_id': '6587008b36850ea066e5843c-1', 'base_dir': 'c:\\scripts-23\\watchtower\\wcodebase\\a_agent/../../CASE_FILES_STORAGE/storage/6587008b36850ea066e5843c/', 'filenames': ['8f4d0124-8464-4bfa-abc7-84688f750c1e.pdf'], 'path_filenames': [('c:\\scripts-23\\watchtower\\wcodebase\\a_agent/../../CASE_FILES_STORAGE/storage/6587008b36850ea066e5843c/8f4d0124-8464-4bfa-abc7-84688f750c1e.pdf', '8f4d0124-8464-4bfa-abc7-84688f750c1e.pdf')], 'state': {'create_run_job': {'time': 1704232484}, 'ocr_conversion': {'time': 1704232488}, 'start_main_processing_pipeline': {'time': 1704230343}, 'running_KBAI_processing_pipeline': {'time': 1704230343}, 'end_KBAI_processing_pipeline': {'time': 1704232483}, 'end_main_processing_pipeline': {'time': 1704232483}, 'wt_main_pipeline_finished': {'time': 1704232483}, 'start_KBAI_processing_pipeline': {'time': 1704232488}}, 'next_actions': [], 'pages_count': 195, 'last_active': 1704230343}
"""
    return


def dev_call_processing():
    case_id='6596f6efc8fca0cb7b70e219'
    interface_case_done_processing(case_id)
    return

def dev_feb17_check_alt_servers_and_queue():
    """
        Cases being processed on alt servers
        - did they finish?
        - collection of bad?
        - auto rerun or patch?
        
        CMDS:
        - finaware_dev server::
        - edit all vi $(ls -l | grep 'Feb' | awk '{print $9}')
        
        STOPPED due to nan into cypher query causing errors opening/closing balance
        "exe1_65ca54869b6ff316a779e6d5_2024_02_12_17_26.log" 
        
        STOPPED AT DPI:  fixed previously
        "exe1_65caaffb9b6ff316a779f525_2024_02_12_23_57.log" 46L, 3433B written  
        "exe1_65cd01899b6ff316a77a1988_2024_02_14_18_10.log" 135L, 13839B written   
        
        NORMAL SERVER::
            FEB 17
        vi $(ls -l | grep 'Feb 17' | awk '{print $9}')
        
        CSV::8
        65d07b4a69409d8064dd477a/
        exe1_65d07c6d2648b25bc55e3faf_2024_02_17_09_32.log
        /2a81dd75-2ce4-435e-b12c-3e16baadb7f5.csv'
        2d3f0c4a-7348-41c7-9985-f981ad182128.csv'
        17335e47-7333-45e7-83f2-da17aaeeab75.csv
        '65d1090504aa7511476750ab'
        '65d1097a04aa751147675411'
        65d1099604aa7511476757a9

        xls::1
        15d7726e-de39-4f02-9166-b1fc9c247e47.xls'

 >>>>       max wait time:
            '65d11a8c04aa75114767637a'
                raise Exception(f"Max wait time of {max_wait_time} seconds exceeded. Exiting wait loop.")
                Exception: Max wait time of 7200 seconds exceeded. Exiting wait loop.


GOOD FOR MANUAL RERUN:

        65d11a8c04aa75114767637a
        65ca54869b6ff316a779e6d5
        65caaffb9b6ff316a779f525
        65cd01899b6ff316a77a1988
        
CHECK ON RERUN DONE:
37a timeout again
988 was dpi now timeout.  <-- now ok. on retry


        
    """
    return

if __name__=='__main__':
    branches=['dev1']
    branches=['dev2']
    branches=['dev_call_processing']

    for b in branches:
        globals()[b]()



"""
"""






