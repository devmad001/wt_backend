import os,sys
import re
import json
import time
import copy
import codecs

import requests

from pathlib import Path
import shutil

import numpy as np

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"


sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../../")


from z_apiengine.database_models import LogEntryModel
from z_apiengine.database import SessionLocal




#0v1# JC  Feb  9, 2024  Usage




"""
    USE HUB LOGS
    - A


"""




def dev_create_sample_entries():
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
    
    log2hub(**log_entry_data)
    print ("Done dev sample entry creation")
    return


def dev1():
    
    ## Query for latest logs

    with SessionLocal() as db:
        #results=db.query(LogEntryModel).all()
        # Order by time_updated desc
        results=db.query(LogEntryModel).order_by(LogEntryModel.time_updated.desc()).all()
        print ("[debug] log entries count: "+str(len(results)))
        for r in results:
            print ("> "+str(r.__dict__))

    return



if __name__ == "__main__":
    dev1()





"""
REF SNAPSHOT:

class LogEntry(BaseModel):
    case_id: int
    job_id: int
    case_status: Optional[str] = None
    job_state: Optional[str] = None
    job_time_started: Optional[int] = None  # UNIX timestamp
    current_state: Optional[str] = None
    current_state_start_time: Optional[int] = None 
    state_transition_name: Optional[str] = None
    transition_timestamp: int
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



"""



