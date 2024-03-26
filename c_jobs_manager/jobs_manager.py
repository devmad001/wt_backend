import os
import sys
import codecs
import json
import re
import uuid
import time
import threading

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")

from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import threading
import time
import psutil
from abc import ABC, abstractmethod
from queue import Queue

from w_storage.ystorage.ystorage_handler import Storage_Helper

from get_logger import setup_logging
logging=setup_logging()

Storage=Storage_Helper(storage_dir=LOCAL_PATH+"../w_datasets/pipeline")
Storage.init_db('jobs')
Storage.init_db('job_logs')

from jobs_model import Job
from jobs_model import JobQueue
from jobs_model import JobModel

from z_apiengine.database import SessionLocal

#from algs_iagent import alg_get_case_files


#0v2# JC  Dec 10, 2023  Time to use it
#0v1# JC  Nov 24, 2023  Init

"""
    ** HIGH LEVEL (see cg for more details)
    FORMAL JOB MANAGER
    - see iagent for original support

    DESIGN:
    -  JOBS_MANAGER
       - TESTS
    -  JOB ABSTRACT CLASS
       - INPUTS, OUTPUTS, FILES, LOGS, STATUS, etc.
       - WATCH PARTIAL DATA
    -  JOB STATE MACHINE
        - RUNNING, WAITING, DONE, ERROR, etc.
        - RECOVERY
    -  JOB QUEUE
    -  JOB PROCESSOR:  THREADS, PROCESSES, etc.  (cpu possible)
"""


# Jobs Manager
class JobsManager:
    def __init__(self):
        self.job_queue = JobQueue()
#skeleton#        self.job_processor = JobProcessor(self.job_queue)
#skeleton#        self.external_monitor = ExternalJobMonitor()
        
    def delete_job(self,query):
        #** admin only!
        with SessionLocal() as db:
            db.query(JobModel).filter_by(**query).delete()
            db.commit()
        return

    def add_job(self, job_instance):
        if not isinstance(job_instance,JobModel):
            print ("[debug] job is: "+str(job_instance))
            raise Exception('Job must be a JobModel')
        #job_record = JobModel(id=job.id, name=job.name, status=job.status)
        
        with SessionLocal() as db:
            ## Commit to database
            db.add(job_instance)
            db.commit()
        
        ## Commit to queue object
        self.job_queue.add_job(job_instance)
        return 

    def update_job_status(self, job_id, status):
        if status not in ["RUNNING", "PENDING", "DONE", "ERROR", "REQUESTED"]:
            raise Exception('Invalid status: ' + str(status))
    
        with SessionLocal() as db:
            # Fetch the job instance from the database
            job_instance = db.query(JobModel).filter(JobModel.id == job_id).first()
            if job_instance is None:
                raise Exception('Job not found')
    
            # Update the status
            job_instance.status = status
    
            # Commit the changes to the database
            db.commit()
    
            # Optionally refresh the instance (if needed)
            # db.refresh(job_instance)
    
        return

    def start_processing(self):
        pass
#skeleton        threading.Thread(target=self.job_processor.process_jobs).start()
#skeleton        threading.Thread(target=self.external_monitor.start_monitoring).start()
        
    def init_job(self,id='',name='',data={}):
        if not id: id=str(uuid.uuid4())
        if not name: raise Exception('name required')
        return Job(id=id,name=name,data=data)
    
    def query_jobs(self,query={}):
        ## Iter jobs or specific filter
        jobs=[]
        with SessionLocal() as db:
            if query:
                #{'case_id':case_id,'status':status}
                jobs=db.query(JobModel).filter_by(**query).all()
            else:
                jobs=db.query(JobModel).all()
        return jobs
    
    def count_all_job_records(self):
        with SessionLocal() as db:
            return db.query(JobModel).count()
        
    def is_case_id_in_job_queue(self,case_id):
        with SessionLocal() as db:
            return db.query(JobModel).filter(JobModel.case_id==case_id).count()>0
        return


# Example usage
def dev1():
    check=kkk
    jobs_manager = JobsManager()

    # Example job
    class MyJob(Job):
        def __init__(self, id, name):
            super().__init__(id, name)

        def run(self):
            print(f"Running job {self.id}")
            # Job logic here

    # Add and start jobs
    for i in range(5):
        check=dev_only
        my_job = MyJob(i, f"Job{i}")
        jobs_manager.add_job(my_job)

    jobs_manager.start_processing()
    return


if __name__=='__main__':
    branches=['dev1']
    for b in branches:
        globals()[b]()



"""
"""
