import os
import sys
import codecs
import json
import re
from datetime import datetime

import configparser as ConfigParser

from sqlalchemy import create_engine, Column, Integer, String, Sequence, DateTime, MetaData
from sqlalchemy import ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.mysql import JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import declarative_base




LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")

        
#0v3#  JC Feb 16, 2024  pool connection recycle lower for avoiding stale connection error
#0v2#  JC Nov  8, 2023  Extend to Button management (table)
#0v1#  JC Oct 26, 2023  Setup

Config = ConfigParser.ConfigParser()

## OPEN AI
Config.read(LOCAL_PATH+"db_config.ini")
config={}
config['ip']=Config.get('mysql','ip')
config['username']=Config.get('mysql','username')
config['password']=Config.get('mysql','password')

dbname='wtengine'


DATABASE_URL = "mysql+mysqldb://"+config['username']+":"+config['password']+"@"+config['ip']+":3306/"+dbname
DATABASE_URL = "mysql+mysqldb://"+config['username']+":"+config['password']+"@"+config['ip']+"/"+dbname

#D1# print ("CONNECT: "+str(DATABASE_URL)) #! has pw!!

## Concretely define pool size (defaults to 5 and 10)
pool_recycle=3600*2  #Default 8 hours timeout so recycle every 2 hours
#; optional pool_pre_ping later if needed
engine = create_engine(DATABASE_URL, pool_size=10, max_overflow=20, pool_recycle=pool_recycle)


Base = declarative_base()

#############################

from database_models import *   #<-- import after base to avoid circular 

    
# Create the tables in the database
Base.metadata.create_all(bind=engine)

##########################################3
# DB session singleton pattern
##########################################3
#

## Local import:
#- import SessionLocal and create instance when needed
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class DatabaseManager:
    _session = None
    @classmethod
    def get_session(cls):
#        raise Exception("[db session instance moved to local requests]")
        if cls._session is None:
            cls._session = SessionLocal()
        return cls._session
database_session=DatabaseManager.get_session()
        
def log_mysql_exception():
    ## NOTES: Getting timeout on idle connection
    # sqlalchemy.exc.OperationalError: (MySQLdb.OperationalError) (4031, 'The client was disconnected by the server because of inactivity. See wait_timeout and interactive_timeout for configuring this behavior.')
    # Adjust the connection recycle time less then the wait/interactive time.
    #1)  Check the wait_timeout and interactive_timeout in the mysql server:
    #    mysql> show variables like 'wait_timeout';
    #    mysql> show variables like 'interactive_timeout';
    # DEFAULT: 28800 (8 hours)
    
    #2)  Adjust the connection pool recycle time to be less than the wait/interactive timeout
    #    engine = create_engine('mysql://scott:tiger@localhost/test', pool_recycle=3600)

    return

def dev1():
    return


if __name__=='__main__':
    branches=['dev1']
    for b in branches:
        globals()[b]()




"""

RECALL YOUR CURRENT ./z_apiengine/services/timeline_service.py

                            ^^^ essentially where button_services.py would live (ButtonManagementService)


    /database
        __init__.py
        database.py         # SessionLocal and engine setup
        models.py           # ORM models (Case)
    /services
        __init__.py
        case_management.py  # CaseManagementService and business logic
    /schemas
        __init__.py
        case_schemas.py     # Pydantic models (CaseCreate, CaseInDB)
    /api
        __init__.py
        main.py             # FastAPI endpoints using the service layer
    /scripts
        some_script.py      # 
        
"""