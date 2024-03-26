import os
import sys
import codecs
import json
import re
import time

#import threading
#import psutil

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")


#from w_storage.ystorage.ystorage_handler import Storage_Helper

from get_logger import setup_logging
logging=setup_logging()


#0v1# JC  Dec 10, 2023  To-the-point runner


## RECALL:
#> FE Cases state managed for view (keep separate -- loosely coupled)
#> Job Queue managed for ensuring jobs finish
#> a_agent/interface_manager -> traditional running but tied to backend sqlite job

## THIS IS SINGLE


## SINGLE PURPOSE RUNNER
#- recall a lot of factors into spawning job but keep obvious

## EXTRA NOTES:
#- distributed would be nice...
#- breakout of ocr would be nice...



def EXECUTE_KNOWN_CASE(case_id,top_options={}):
    print ("[execute_case] case_id: %s" % case_id)]")
    print ("> assume have resources")
    print ("> assume job is being tracked in job queue")
    print (">     ^so will resolve or retry any failures")
    
    return

def info_list_cases():
    #> cases from local /storage  (org enqueue way)
    #> cases from FE requests
    #> cases from Google Storage files
    #> cases from Job queue
    return


def recall_existing_entrypoints():
    
    # JON TRIALS:
    # udev/dev_challenges.py --> a_agent.py RUN_sim_wt.py
    # udev/jon_accounts -> wt_main_pipeline @ a_agent.sim_wt
    
    # u_entrypoints/ENTRY_tweak_run_single_pdf_page.py -> wt_main_pipeline

    # a_agent/interface_manager.py -> request_spawn_pipeline_process
    #     > pipeline_exe_logs/*
    #     > exe1_*  as way to see if running
    #     > done per sqlite but not tied to FE requests
    #     > estimate runtime
    #                 Manager_Interface: which_cases_are_running?
    
    ## Recall new requirement to sync remote google to local !!
    #- did somewhere but tie into wt_execute.py exe1 which does full thing
    #- 

    return



def preview_full_run_entrypoint():
    print ("NOW: this -> mega_job -> interface_manager -> wt_execute -> pipeline??")
    
    print ("[ ] add google sync to execution pipeline req")
    #(further down pipeline is fine even if not checking..jsut make
    # stand-alone logic so can be called from anywhere)
    
    # execute_wt.py ->     MAIN_ENTRYPOINT_CASE_processing_pipeline(case_id)
    
    # a_agent.RUN_sim_wt MAIN_ENTRYPOINT_CASE_processing_pipeline(case_id)
    
    #  -> from sim_wt import wt_main_pipeline
     

    return


def dev1():

    return


if __name__=='__main__':
    branches=['preview_full_run_entrypoint']

    for b in branches:
        globals()[b]()







"""


"""
