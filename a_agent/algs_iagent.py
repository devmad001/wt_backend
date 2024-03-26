import os
import sys
import codecs
import json
import re

import configparser as ConfigParser

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")

from get_logger import setup_logging
logging=setup_logging()

from interface_sync_google import interface_sync_case_storage_to_processing_storage


#0v2# JC  Dec 13, 2023  Move google file sync down to alg level (keep missing at higher)
#0v1# JC  Sep 12, 2023  Setup


"""
"""

Config = ConfigParser.ConfigParser()
Config.read(LOCAL_PATH+"../w_settings.ini")

BASE_STORAGE_DIR=Config.get('files','base_storage_rel_dir')
BASE_STORAGE_DIR=LOCAL_PATH+"../"+BASE_STORAGE_DIR  ## BASE_STORAGE_DIR may be:  ../x/y


def alg_get_case_files(case_id,auto_sync=True):
    global BASE_STORAGE_DIR
    
    logging.info("[alg_get_case_files] assumes already sync'd from cloud!")

    case_filenames=[]
    case_path_filenames=[]

    ## Remove bad chars [ ]
    case_directory=BASE_STORAGE_DIR+"/"+case_id+"/"
    
    if not os.path.exists(case_directory):
        if auto_sync:
            logging.info("[alg_get_case_files] no local so assume pull from cloud system: "+str(case_directory))
            interface_sync_case_storage_to_processing_storage(case_id)

    if not os.path.exists(case_directory):
        raise Exception("Case directory does not exist: "+case_directory+" ensure run get_job_state(case_id) for google sync")

    is_good_directory=True
    if '..' in case_id: is_good_directory=False
    if '/' in case_id: is_good_directory=False

    if is_good_directory:
        if os.path.exists(case_directory):
            for filename in os.listdir(case_directory):
                if re.search(r'\.pdf$',filename,flags=re.I):
                    case_filenames.append(filename)
                    case_path_filenames.append((case_directory+filename,filename))

    return case_path_filenames,case_filenames,case_directory


if __name__=='__main__':
    branches=['dev_call_agent']
    for b in branches:
        globals()[b]()


"""
"""