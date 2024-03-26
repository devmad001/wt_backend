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

from sqlalchemy import create_engine, Column, Integer, String, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

import psutil
from abc import ABC, abstractmethod
from queue import Queue

from w_storage.ystorage.ystorage_handler import Storage_Helper

from get_logger import setup_logging
logging=setup_logging()

Storage=Storage_Helper(storage_dir=LOCAL_PATH+"../w_datasets/pipeline")
Storage.init_db('jobs')
Storage.init_db('job_logs')

#from algs_iagent import alg_get_case_files

## (std just like database_admin.py using)
from z_apiengine.database import SessionLocal
from z_apiengine.database import Base
from z_apiengine.database import engine


#0v2# JC  Dec 10, 2023  Migrate to mega_job
#0v1# JC  Nov 24, 2023  Init


"""
    SUPPORT CLASSES FOR MANAMGING JOBS
    
    DEFINE JOB:  A request to process a case
    - machine facing, distributed support, 

"""


#########################################
#  JOB DATABASE
#########################################
# SQLAlchemy setup for MySQL


class JobModel(Base):
    __tablename__ = 'jobs'
    
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    case_id= Column(String(255))
    status = Column(String(50))
    data = Column(JSON)  # Adding a JSON field
    # Add other relevant fields as needed

    def to_dict(self):
        return {key: value for key, value in self.__dict__.items() if not key.startswith('_')}
        

# Update with your MySQL database credentials
Base.metadata.create_all(engine)


#########################################
#  JOB
# Abstract Job class
class Job(ABC):
    def __init__(self, id='', name='',case_id='',data={},status="PENDING"):
        self.id = id
        self.name = name
        self.case_id= case_id
        self.status = status
        self.data=data

#    @abstractmethod
    def run(self):
        pass

#########################################
# Job State Machine
class JobStateMachine:
    def __init__(self, job):
        self.job = job
        self.states = ["RUNNING", "PENDING", "DONE", "ERROR","REQUESTED"]
        self.current_state = "PENDING"

    def update_state(self, new_state):
        if new_state in self.states:
            self.current_state = new_state
            self.job.status = new_state
            self.update_job_status_in_db(new_state)

    def update_job_status_in_db(self, new_state):
        with SessionLocal() as db:
            job_record = db.query(JobModel).filter(JobModel.id == self.job.id).first()
            if job_record:
                job_record.status = new_state
                db.commit()
                db.refresh(job_record)

#########################################
# Job Queue
class JobQueue:
    def __init__(self):
        self.queue = Queue()

    def add_job(self, job):
        self.queue.put(job)

    def get_next_job(self):
        return self.queue.get()


def dev_job_query():
    ## 

    job_data = {"key1": "value1", "key2": "value2"}
    new_job = JobModel(id=1, name="Sample Job", status="PENDING", data=job_data)
    session.add(new_job)
    session.commit()

    #And when you query the job, you can access the data field like a regular dictionary:
    job = session.query(JobModel).filter_by(id=1).first()
    if job:
        print(job.data)  # This will print the dictionary
        print(job.data["key1"])  # Accessing a specific value in the dictionary

    return


def dev1():
    print ("TEST DB (recall other sqlachemy code)")
    #> remove redefine Job table

    return

 
def ADMIN_drop_job_table_recreate():
    ########## ADMIN recreate table new fields (no data so ok)
    print ("Recreating job model...")
    if True:
        # Drop the table
        chhar=hardcop
        JobModel.__table__.drop(engine)
    
        # Recreate the table
        Base.metadata.create_all(engine)
        
    return


if __name__=='__main__':
    branches=['ADMIN_drop_job_table_recreate']
    branches=['dev1']

    for b in branches:
        globals()[b]()



"""
"""
