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

from log_hubby import log2hub



#0v1# JC  Feb  6, 2024  Init


"""
    CENTRAL LOG HUB SYSTEM
    - db supported centralized logs
    - begin with background job processing

"""


"""
NOTES:
- log to single file until firm on attributes to collect
- recall, sqlite have it but not for longer term distributed setup

"""


class LogEntry(BaseModel):

    case_id: Optional[int] = Field(None, description="Unique identifier for the case")
    job_id: Optional[int] = Field(None, description="Unique identifier for the job")
    
    # Case and Job statuses
    case_status: Optional[str] = Field(None, description="Current status of the case (start, queue, run, end)")
    job_state: Optional[str] = Field(None, description="Current state of the job")
    
    # Resource usage metrics
    cpu_usage: Optional[float] = Field(None, description="CPU usage percentage")
    memory_usage: Optional[float] = Field(None, description="Memory usage in MB")
    
    # Timing information
    time_started: Optional[datetime] = Field(None, description="Timestamp when the job started")
    time_queued: Optional[datetime] = Field(None, description="Timestamp when the job was queued")
    time_ended: Optional[datetime] = Field(None, description="Timestamp when the job ended")
    time_updated: Optional[datetime] = Field(None, description="Timestamp when the job status was last updated")
    estimated_time_remaining: Optional[str] = Field(None, description="Estimated time remaining for the job to complete")
    
    # Error handling
    error_stack_trace: Optional[str] = Field(None, description="Stack trace in case of an error")
    
    # Additional fields for questions, answers, extractions, and audits
    questions_and_answers: Optional[List[str]] = Field(None, description="List of questions and their corresponding answers")
    extractions: Optional[List[str]] = Field(None, description="List of data extractions or audits")

    class Config:
        schema_extra = {
            "example": {
                "case_id": 123,
                "job_id": 456,
                "case_status": "start",
                "job_state": "running",
                
                "meta": {
                    "cpu_usage": 50.0,
                    "memory_usage": 1024.0,
                    "error_stack_trace": ""
                }
            }
        }


def dev2():
    
    ## Recall GOAL:

    #- track ongoing job processing status
    #> core indexes (case_id, job_id)
    #> absolute metrics:  state, job_start_time, job_duration_s, estimated_remaining_s, state_start_time
    #> absolute metrics:  comment


    ## MISC:
    # Possible examples:
    #- state_transition='ocr_done_main_begins'?  **just call it "state"
    


    return


def save_log_entry():
    return


def dev1():
    
    #1)  Log CASE status (start, queue, run, end)
    #2)  Log JOB  status (state, metrics like cpu/mme?, estimated time remaining?)
    #3)  Log all Questions and Answers
    #4)  Log all extractions or basic audits?
    
    ## Start with Job status logs
    #> case_id index, job_id index.

    #> job_id, state, cpu, mem, time, time_remaining, time_elapsed, time_estimated, time_completed, time_started, time_queued, time_ended, time_updated, time_created, time_modified, time_deleted, time_recovered, time_rejected, time_failed, time_retried, time_skipped, time_paused, time_resumed, time_stopped, time_canceled, time_aborted, time_terminated
    
    ## Estimated time remaining?  **logging estimated time helps refine time estimator.
    
    ## On error log stack trace to db for visibility.
    

    # CURRENT_STATE="running"

    return


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
    
#    log2hub(**log_entry_data)
#    print ("Done dev sample entry creation")

    ## CREATE SAMPLE REAL MOCK
    
    log2hub(case_id='123')

    return




if __name__ == "__main__":
#    dev1()
#    dev2()
    dev_create_sample_entries()




"""

"""



