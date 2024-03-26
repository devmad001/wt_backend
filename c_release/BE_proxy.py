import os, sys
import time
import requests
import shutil

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi import Query

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")

## Direct endpoint calls rather then library imports
#from starlette.testclient import TestClient
# client = TestClient(app)

from get_logger import setup_logging
logging=setup_logging()

from z_apiengine.services.case_service import get_case_meta

from z_apiengine.services.external_interfaces.google_storage_interface import sync_google_storage_files_local

from z_apiengine.services.case_BE_service import get_case_processing_status
from z_apiengine.services.case_BE_service import get_case_report
from c_case_manager.case_analytics import interface_get_case_status


## Hard code case dir for mv from sync to processing
STORAGE_SYNC_BASE_DIR=LOCAL_PATH+"../../CASE_FILES_GOOGLE_SYNC"
STORAGE_BASE_DIR=LOCAL_PATH+"../../CASE_FILES_STORAGE/storage"

## VALIDATE FILES
if not os.path.exists(STORAGE_SYNC_BASE_DIR):
    raise Exception(f"Storage base dir does not exist: {STORAGE_SYNC_BASE_DIR}")
if not os.path.exists(STORAGE_BASE_DIR):
    raise Exception(f"Storage base dir does not exist: {STORAGE_BASE_DIR}")


#0v2# JC Jan 13, 2024  Extend parts to new Case db view
#0v1# JC Dec  6, 2023


"""
    BACK-END "clean" PROXY
    - allow debug mode
"""

##############################################################
# INTERFACES:
#- use real endpoint where possible  (though circular imports)
#- use api services then
##############################################################

## REF:
#- recall abstract_FE looks at init_data and Dashboard broadcast etc.


class BE_Proxy:
    ## BACKEND PROXY
    #- interface with local db
    #- interface with job processing queue
    #- allow for debug mode to test status changes
    def __init__(self):
        pass
        
    def get_case_details(self,case_id):
        return get_case_meta(case_id)

    def get_BE_case_processing_status(self,case_id):
        #** Note:  BE to FE requires cache + state validation to simplify
        #- adds a layer but easier to control mapping of variables
        return get_case_processing_status(case_id)

    def get_case_report(self,case_id):
        return get_case_report(case_id)
    
    def sync_case_files(self,case_id,case_files):
        #[ ] updated needed to both prod + staging
        files_synced=sync_google_storage_files_local(case_id,case_files)
        if not len(case_files) == len(files_synced):
            raise Exception("Failed to sync all files")
        return
    
    def has_case_ever_been_processed(self,case_id):
        ## OPTIONS:
        #i) check for dir (this but bad assumption) - AND -
        #ii) check if case is DONE or ERROR on Case side
        #iii) check if job processing state has entry for kbai

        has_been_processed=False
        
        #(ii)
        cdict=interface_get_case_status(case_id)
        if cdict['state'] in ['DONE','ERROR']:
            has_been_processed=True

        #(i) - AND -  logic  at end as well
        expected_dir=STORAGE_BASE_DIR+"/"+case_id
        if not os.path.exists(expected_dir): return has_been_processed

        return has_been_processed
    
    def does_processing_dir_exist(self,case_id):
        is_exists=False
        expected_dir=STORAGE_BASE_DIR+"/"+case_id
        if os.path.exists(expected_dir):
            is_exists=True
        return is_exists

    def enqueue_files_from_sync(self,case_id):
        source_dir=STORAGE_SYNC_BASE_DIR+"/"+case_id
        target_dir=STORAGE_BASE_DIR+"/"+case_id

        if not os.path.exists(source_dir):
            logging.warning("Source sync dir does not exist: "+str(source_dir))

        if not os.path.exists(target_dir):
            os.mkdir(target_dir)
            
        for f in os.listdir(source_dir):
            shutil.move(source_dir+"/"+f,target_dir+"/"+f)
            logging.info("Moved file: "+str(f))
        
        return
        


def workflow_get_process_case(case_id):
    ## For view friendly testing see above.  This is pure functional
    
    case_id='6570af77949fdfbf2c5810e8'
    
    ## Precheck passed values

    #[1]#  Accept case details posted or sync files for ready

    #[2]#  Proxy submit for processing

    #[3]#  Check/test case processing status
    
    #[4]#  Get case report


    return



def dev_BE_proxy():
    
    print ("OBVS from perspective of BE")
    print ("** require formalization between BE <> FE processing")
    

    b=[]
    b+=['sync_files']
    b=[]
    b+=['dev_set_state']
    
    case_id='6570af77949fdfbf2c5810e8'
    
    BE=BE_Proxy()

    CASE=CASE_Proxy(case_id)
    
    case_dict=BE.get_case_details(case_id)
    
    if 'sync_files' in b:
        case_files=case_dict['file_urls']
        BE.sync_case_files(case_id,case_files)

    if 'dev_set_state' in b:
        raw_state_dict=CASE.set_state_key('state_phrase','Processing...')
        print ("Updated state. raw state is: "+str(raw_state_dict))

    return



if __name__ == "__main__":
    dev_BE_proxy()
