import os, sys
import time
import requests

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi import Query

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")

from a_agent.sim_wt import get_job_state
from a_agent.sim_wt import wt_main_pipeline

from BE_proxy import BE_Proxy
from z_apiengine.database import SessionLocal
from z_apiengine.services.case_service import list_all_cases

from a_query.admin_query import admin_remove_case_from_kb



#0v1# JC Dec 29, 2023



"""
    EASY execution
    -
"""


def iter_FE_cases():
    # Direct db or case_service
    for case in list_all_cases():
        yield case
    return

def easy_process_pdf_case(case_id,force_remove_knowledge=True):
    ## Sync file local
    ## Run dev entrypoints
    #- dev_challenges is one approach

    options={}
    options['force_ocr']=True
    
    if force_remove_knowledge:
        print ("[challenge meta] force_remove_knowledge: "+str(case_id))
        admin_remove_case_from_kb(case_id=case_id)
    
    get_job_state(case_id=case_id) #WILL ALSO SYNC

    meta=wt_main_pipeline(case_id=case_id,options=options,manual_skip_caps=['start_KBAI_processing_pipeline'])
    print ("[challenge meta] transactions touched: "+str(meta.get('count_transactions','')))
    
    manual_skip_caps=['start_main_processing_pipeline']
    meta=wt_main_pipeline(case_id=case_id,options=options,manual_skip_caps=manual_skip_caps)

    return


def dev1():
    print ("See auto_sync_case_files...will do them all")
    a=okk

    BE=BE_Proxy()
#    BE.sync_case_files(case_id,case_files=case_files)
    
    for case in iter_FE_cases():
        case_dict=case.case_meta  #<-- meta is specific to FE storage
        case_id=case.case_id
        
        file_urls=case_dict.get('file_urls',[])

        if file_urls and '//' in str(file_urls): #'STRING' bad
            print ("OPTION: "+str(case_id)+" -> "+str(case_dict))
            
            if not BE.has_case_ever_been_processed(case_id):
                print ("[challenge meta] case never run: "+str(case_id))
                BE.sync_case_files(case_id,case_files=file_urls) #re-get
                
                print ("enqueue_files_from_sync")
                BE.enqueue_files_from_sync(case_id)

                print ("Local process pdf case")
                local_process_pdf_case(case_id)
                
    return


if __name__ == "__main__":
    dev1()



"""
"""