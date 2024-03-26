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
from z_apiengine.database import Base
from z_apiengine.database import engine

from z_apiengine.database import SessionLocal


#0v2# JC  Jan 24, 2024  TBD  (unused)
#0v1# JC  Nov 28, 2023  Init


"""
    AUTHENTICATION TOKEN STORE
"""

#########################################
#  AUTH DATABASE
#########################################
class AuthModel(Base):
    __tablename__ = 'auth'
    
    # token session key lenth
    token=Column(String(255), primary_key=True)

    # user id
    user_id=Column(String(255))

    # cases list [optional fks?]
    cases=Column(JSON)
    
    data=Column(JSON)  # Adding a JSON field
    
    created_date=Column(String(255))
    last_accessed_date=Column(String(255))
    
    ## MISC (or combine into data field)
#    last_accessed_ip=Column(String(255))
#    last_accessed_user_agent=Column(String(255))
#    last_accessed_url=Column(String(255))
#    last_accessed_method=Column(String(255))
    

# Update with your MySQL database credentials
Base.metadata.create_all(engine)


def dev1():
    return


if __name__=='__main__':
    branches=['dev1']
    for b in branches:
        globals()[b]()



"""
"""
