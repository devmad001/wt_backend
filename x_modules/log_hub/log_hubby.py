import os,sys
import re
import json
import time
import copy
import codecs
from datetime import datetime

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import JSON  # Use JSONB if using PostgreSQL
from pathlib import Path


LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"

sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../../")

from z_apiengine.database_models import LogEntryModel
from z_apiengine.database import SessionLocal

from get_logger import setup_logging
logging=setup_logging()






#0v1# JC  Feb  6, 2024  Init


"""
    CENTRAL LOG HUB SYSTEM
    - db supported centralized logs
    - begin with background job processing



NOTES:
- log to single file until firm on attributes to collect
- recall, sqlite have it but not for longer term distributed setup


"""

"""
This a detailed tracker for monitoring the lifecycle and transitions of jobs within cases.

Field Insights
case_id: Unique identifier for each case, linking all related jobs.
job_id: Specific identifier for tracking a job's journey within its case.
case_status: Describes the overarching phase of the case, like "active" or "closed".
job_state: Captures the job's immediate status, such as "running" or "completed".
job_time_started: Timestamp for when the job originally kicked off, setting the stage for duration calculations.
current_state: Zooms in on the job's exact activity at the moment, like "processing".
current_state_start_time: Pinpoints when the job entered its current phase, useful for timing analysis.
state_transition_name: Names the specific shift or milestone the job is passing through, for clarity on its progression.
transition_timestamp: The exact moment a transition was recorded, maintaining a chronological log.
time_updated: Timestamp for the most recent update to this log entry, ensuring freshness.
meta: A flexible space for all additional, contextual details that don't fit neatly elsewhere but are vital for a full understanding.

"""


"""
USAGE NOTES:
- meta {}
    - machine name?


"""




class LogEntry(BaseModel):
    case_id: str
    job_id: Optional[str] = None
    case_status: Optional[str] = None
    job_state: Optional[str] = None
    job_time_started: Optional[int] = None  # UNIX timestamp
    current_state: Optional[str] = None
    current_state_start_time: Optional[int] = None 
    state_transition_name: Optional[str] = None
    transition_timestamp: Optional[int]=None
    time_updated: int 
    token_a: Optional[int]=0
    token_b: Optional[int]=0
    meta: Optional[Dict[str, Any]] = Field(default_factory=dict)

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "case_id": 123,
                "job_id": 456,
                "case_status": "active",
                "job_state": "running",
                "job_time_started": 1617983106,
                "current_state": "processing",
                "current_state_start_time": 1617983106,
                "state_transition_name": "processing_to_completed",
                "transition_timestamp": 1617983106,
                "time_updated": 1617983106,
                "token_a": 333,
                "token_b": 33,
                "meta": {
                    "cpu_usage": 75.0,
                    "memory_usage": 1600.0,
                    "additional_info": "Any other relevant information"
                }
            }
        }


## Interface to log
def log2hub(**log_entry_kwargs):
    ## General logging handler
    #- exception to avoid breaking the main process

    #    logging.info("[log2hub] log ok: "+str(log_entry.dict())
    
    try:
        ## Default values
        log_entry_kwargs['time_updated'] = int(time.time())
        
        ## Validate with LogEntry
        log_entry = LogEntry(**log_entry_kwargs)
    
    
        ## Map to model
        log_entry_model = LogEntryModel(**log_entry.dict())
    
        
        ## Save to db
        with SessionLocal() as db:
            db.add(log_entry_model)
            db.commit()
            db.refresh(log_entry_model)
            logging.info("[debug] saved log entry")
    except Exception as e:
        logging.error("[log2hub] error: "+str(e))
        return False
    
    return True


def dev1():
    

    print (">> log_hubby ")


    # Example usage
    log_entry_data = {
        "case_id": 123,
        "job_id": 456,
        "case_status": "active",
        "job_state": "running",
        "job_time_started": 1617983106,
        "current_state": "processing",
        "current_state_start_time": 1617983106,
        "state_transition_name": "processing_to_completed",
        "transition_timestamp": 1617983200,  # A new UNIX timestamp
        "time_updated": 1617983200,
        "token_a": 1,
        "token_b": 1,
        "meta": {
            "cpu_usage": 80.0,
            "memory_usage": 2000.0,
            "notes": "Transition to completed state"
        }
    }
    

    ## Step through usage
    log_entry = LogEntry(**log_entry_data)
    print ("[debug] log ok: "+str(log_entry))

    log_entry_model = LogEntryModel(**log_entry.dict())
    print ("[debug] log ok: "+str(log_entry_model))
    

    print ("[done dev check log_hobby]")

    return




if __name__ == "__main__":
    dev1()




"""

"""



