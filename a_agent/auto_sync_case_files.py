import os
import sys
import codecs
import json
import re

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"

sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")
sys.path.insert(0,LOCAL_PATH+"../..")

from get_logger import setup_logging
logging=setup_logging()

from c_release.BE_proxy import BE_Proxy

from z_apiengine.services.case_service import list_all_cases

        
#0v1# JC Dec  8, 2023  Automate various processes


"""
    SUITE OF AUTOMATION TOOLS
    - easy patches, auto processes, auto reports, syncs, updates, etc.
    - *easier to do once in a script than many times everywhere
"""


def iter_FE_cases():
    # Direct db or case_service
    for case in list_all_cases():
        yield case
    return

def run_auto_sync_case_files(case_id):
    did_sync=False
    BE=BE_Proxy()
    for case in iter_FE_cases():
        if not case_id==case.case_id: continue
        print ("[debug] case found: "+str(case_id))
        case_id=case.case_id
        case_dict=case.case_meta
        file_urls=case_dict.get('file_urls',[])
        print ("[debug] case_dict: "+str(case_dict))
        print ("[debug] file urls: "+str(file_urls))
        
        if file_urls and '//' in str(file_urls): #'STRING' bad
            print ("OPTION: "+str(case_id)+" -> "+str(case_dict))
            
            did_sync=True # assume True
            if not BE.does_processing_dir_exist(case_id):
                print ("(1) sync case files from google")
                BE.sync_case_files(case_id,case_files=file_urls) #re-get
                print ("(2) 'enqueue' files into BE processing dir")
                BE.enqueue_files_from_sync(case_id)
            else:
                print ("[debug] case dir exists: "+str(case_id))
    return did_sync

def run_auto_sync_ALL_case_files():
    ## Maybe redudant but gets the point across
    #>> see PROCESS_auto
    BE=BE_Proxy()

    for case in iter_FE_cases():

        case_id=case.case_id
        case_dict=case.case_meta
        file_urls=case_dict.get('file_urls',[])
        
        if file_urls and '//' in str(file_urls): #'STRING' bad
            print ("OPTION: "+str(case_id)+" -> "+str(case_dict))
            
            if not BE.does_processing_dir_exist(case_id):
                print ("(1) sync case files from google")
                BE.sync_case_files(case_id,case_files=file_urls) #re-get
                print ("(2) 'enqueue' files into BE processing dir")
                BE.enqueue_files_from_sync(case_id)
        
    return



def test_run_auto_sync_case_files():
    case_id="65725b0050560b89044dca99"
    case_id="65a057c36c33e2599cce71d7"

    run_auto_sync_case_files(case_id)

    return

if __name__=='__main__':
    branches=['test_run_auto_sync_case_files']
    branches=['run_auto_sync_case_files']
    branches=['run_auto_sync_ALL_case_files']

    branches=['test_run_auto_sync_case_files']

    for b in branches:
        globals()[b]()





