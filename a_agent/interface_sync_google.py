import os
import sys
import codecs
import json
import datetime
import re

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")

from auto_sync_case_files import run_auto_sync_case_files

from get_logger import setup_logging

logging=setup_logging()


#0v1# JC  Dec 10, 2023  Init





## LOCAL
def interface_sync_case_storage_to_processing_storage(case_id):
    
    logging.info("[SYNC CASE FILES CLOUD TO LOCAL]...")
    try:
        did_sync=run_auto_sync_case_files(case_id)
    except Exception as e:
        logging.error("[interface_sync_case_storage_to_processing_storage] ERROR: "+str(e))

        did_sync=run_auto_sync_case_files(case_id) #<-- rerun to throw traceback
        did_sync=False

    logging.info("[interface_sync_case_storage_to_processing_storage] did_sync: "+str(did_sync))

    return


def dev1():
    case_id='65725b0050560b89044dca99'
    interface_sync_case_storage_to_processing_storage(case_id)
    return

if __name__=='__main__':
    branches=['dev1']

    for b in branches:
        globals()[b]()



"""
"""