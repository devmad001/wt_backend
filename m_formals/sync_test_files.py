import os, sys
import time
import requests
import re

import configparser as ConfigParser

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")


from get_logger import setup_logging
logging=setup_logging()

from gold_test_configs import load_all_test_cases


#0v1# JC Feb 28, 2023  Sync urls & files for local functional tests


"""
    SYNC TEST FILES


"""

## FOLDERS  (keep within repo -- so can do git pull and have all files)
config_filename=LOCAL_PATH+"../w_settings.ini"
if not os.path.exists(config_filename):
    raise Exception("Config file not found: "+str(config_filename))

Config = ConfigParser.ConfigParser()
Config.read(config_filename)
BASE_STORAGE_DIR=Config.get('files','base_test_storage_rel_dir')

TARGET_TEST_FOLDER=LOCAL_PATH+"../"+BASE_STORAGE_DIR
#TARGET_TEST_FOLDER=LOCAL_PATH+"../CASE_FILES_STORAGE/tests"
SINGLE_TEST_FILE_FOLDER=TARGET_TEST_FOLDER+"/single_pdfs"

if not os.path.exists(TARGET_TEST_FOLDER): os.makedirs(TARGET_TEST_FOLDER)
if not os.path.exists(SINGLE_TEST_FILE_FOLDER): os.makedirs(SINGLE_TEST_FILE_FOLDER)

    
"""
    TODO:  DESIGN NOTES:
    - see support_gold.py because that essentially sets that up
    - just need to formalize so files cached in local repo

"""

def test_config_to_local_files():
    #? not sure on prepare full case setup runner or create custom test_case_id

    return


def dev_sync_all_files_locally():
    # pdf page or full docs to local REPO
    #- single pages, full docs, case folders, etc.
    
    ## ITER TEST CASES
    #- put as stand-alone function so can quickly grab local pdf given tt (test config)
    
    for tt in load_all_test_cases():
        logging.info("Syncing test case: "+str(tt))
        
        ## Expect full path (required for all?)
        tt=['meta']['full_path']

        #print(tt)


    return



if __name__ == "__main__":
    dev_sync_all_files_locally()






"""
"""


