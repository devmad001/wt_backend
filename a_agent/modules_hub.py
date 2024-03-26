import os
import sys
import codecs
import json
import re

import configparser as ConfigParser

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")

#from a_agent.iagent import Smart_Agent

## Main pipeline (base extraction)
#from w_pipeline.run_pipeline import interface_run_pipeline
#from kb_ai.interface_kbai import interface_run_all_trigger_questions_KB_AI
#from w_ui.sim_user import interface_dump_excel
#

## IMAGE PDF OCR:
from w_pdf.pdf_images import interface_ocr_image_pdf_if_required

## MAIN PIPELINE:
from w_pipeline.run_pipeline import interface_run_pipeline

## KB UPDATE PIPELINE:
from kb_ai.call_kbai import interface_call_kb_auto_update

from get_logger import setup_logging
logging=setup_logging()

#0v1# JC  Sep 22, 2023  Init

Config = ConfigParser.ConfigParser()
Config.read(LOCAL_PATH+"../w_settings.ini")

BASE_STORAGE_DIR=Config.get('files','base_storage_rel_dir')
BASE_STORAGE_DIR=LOCAL_PATH+"../"+BASE_STORAGE_DIR


"""
    MODULES HUB
    - import various modules for single place import and usage
    - keep light
    - easy background launching option?

"""

def TASK_call_KB_update_pipeline(case_id,force_update_all=False):
    outputs,meta=interface_call_kb_auto_update(case_id,force_update_all=force_update_all)
    total_tokens_used=meta.get('total_tokens_used',0)
    return outputs,meta

def TASK_move_processing_files_back_to_storage(case_id):
    ## If bad conversion, move back to storage
    #- watch for loops!
    #- check if already running!
    return

def SUBTASK_restore_partial_running_job(case_id):
    
    #[1]  IF, files in ./processing
    #[2]  IF, job is not currently running (besides this)
    #[3]  Move original files back to main and remove processing
    #[ ] validate not running though because could be a 2nd call in background.
    
    ### Assume not running
    is_run_using_existing_files=False

    ## Check processing directory (Hard code?)
    #- see process_pdfimage (w_pdf) since it deals with directories
    
    files_restored=[]

    hardcode_source_case_processing_directory=BASE_STORAGE_DIR+"/"+case_id+"/processing"
    hardcode_target_case_directory=BASE_STORAGE_DIR+"/"+case_id
    
    ## Move files (but delete downsampled)
    if os.path.isdir(hardcode_source_case_processing_directory):
        for full_file_path in os.listdir(hardcode_source_case_processing_directory):
            file_path=os.path.basename(full_file_path)
            full_file_path=hardcode_source_case_processing_directory+"/"+full_file_path
            
            if '_downsampled' in file_path:
                os.remove(full_file_path)
    
            elif file_path.lower().endswith(".pdf"):
                logging.info("[TASK] restore_partial_running_job: "+str(full_file_path))
                full_target_filename=hardcode_target_case_directory+"/"+file_path
                
                if os.path.exists(full_target_filename):
                    pass #Exists so remove active
                    os.remove(full_file_path)
                else:
                    os.rename(full_file_path,full_target_filename)
                    
                files_restored.append(full_target_filename)
               
            else:
                pass
                #logging.info("[TASK] restore_partial_running_job: "+str(full_file_path))
                #os.remove(full_file_path)
    return files_restored

def TASK_convert_raw_image_pdfs_to_text(case_id,force_ocr=False):
    global BASE_STORAGE_DIR
    ## Centralize
    # code?
    meta={}
    
    logging.info("[PRE-TASK START] Check if active files being processed (or may have failed)")
    files_restored=SUBTASK_restore_partial_running_job(case_id)
    if files_restored:
        logging.info("[PRE-TASK] restore_partial_running_job: "+str(len(files_restored))+" files restored")

    logging.info("[TASK START] convert_raw_image_pdfs_to_text @w_pdf")

    STORAGE_DIR=BASE_STORAGE_DIR+"/"+case_id

    count_processed=0
    ### Iter pdf files
    
    if os.path.isdir(STORAGE_DIR):
        for full_filename in os.listdir(STORAGE_DIR):
            filename=os.path.basename(full_filename)
            if full_filename.lower().endswith(".pdf"):
                logging.info("[TASK] check convert_raw_image_pdfs_to_text @w_pdf: "+str(full_filename))
    
                is_processed,is_an_image_pdf,meta=interface_ocr_image_pdf_if_required(STORAGE_DIR,filename, force=force_ocr)
    
                if not is_an_image_pdf:
                    pass
                elif is_processed:
                    count_processed+=1
                else:
                    if meta.get('is_already_processing',False):
                        logging.warning("[WARNINING: already files enqueued for processing!]")
                    else:
                        logging.warning("[WARNING not processed]")
    else:
        logging.warning("[no files in case storage]: "+str(STORAGE_DIR))
        #raise Exception("[no files in case storage]: "+str(STORAGE_DIR))

    ### If image pdf, convert to text pdf
    logging.info("[TASK] convert_raw_image_pdfs_to_text @w_pdf: "+str(count_processed)+" pdfs processed")

    return meta


def TASK_run_main_pipeline(job,Agent,options):
    ## Called from sim_wt
    #- consider branching via iagent or sim_user
    meta=interface_run_pipeline(job=job,Agent=Agent, options=options)
    return meta

def TASK_dump_excel(case_id=''):
    #@ sim_user
    #from w_ui.sim_user import interface_dump_excel
    return

def dev1():
    b=['TASK_convert_raw_image_pdfs_to_text']
    case_id='case_chase_dev_1'

    for i in b:
        print ("[info] calling: "+str(i))
        globals()[i](case_id)

    return

if __name__=='__main__':
    branches=['dev1']

    for b in branches:
        globals()[b]()


"""
"""
