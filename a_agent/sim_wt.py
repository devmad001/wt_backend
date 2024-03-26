import os
import sys
import codecs
import json
import datetime
import re

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")

from a_agent.iagent import Smart_Agent
from interface_sync_google import interface_sync_case_storage_to_processing_storage

## Main pipeline (base extraction)

from modules_hub import TASK_convert_raw_image_pdfs_to_text
from modules_hub import TASK_run_main_pipeline
from modules_hub import TASK_call_KB_update_pipeline
from modules_hub import TASK_dump_excel

from get_logger import setup_logging

logging=setup_logging()


#0v2# JC  Dec 10, 2023  Tie into front end + file sync
#0v1# JC  Sep 19, 2023  Init

FILENAME_RUN_LOG=LOCAL_PATH+"../w_datasets/run_logs/run_logs.jsonl"

"""
    FORMAL MAIN ENTRYPOINT
    - optionally allows for various piece-wise executions (just add test for any changes)
    - see run_iagent.py for sample interface_handling case requests

"""

## Ideally move to file but for larger assumptions:
GLOBAL_PIPELINE_CONFIG={}
GLOBAL_PIPELINE_CONFIG['force_ocr']=True
logging.info("[debug]  GLOBAL pipeline force ocr: "+str(GLOBAL_PIPELINE_CONFIG['force_ocr']))


def get_standard_job_needs(options={}):
    global GLOBAL_PIPELINE_CONFIG
    caps={}
    caps['download_cloud_case_files']=False

    caps['create_run_job']=False

    caps['upload_files']=False

    caps['ocr_conversion']=False

    caps['start_main_processing_pipeline']=False
    caps['check_files_main_processing_done']=False

    caps['start_KBAI_processing_pipeline']=False
    caps['check_KBAI_processing_done']=False

    caps['dump_excel']=False
    caps['dump_dev_status']=False

    caps['QA_Online']=False
    caps['full_ux_online']=False  # Core API service UI

    #TODO#    caps['pdf_viewer_cached']=False

    ## Control top options
    if options.get('force_ocr',False) or GLOBAL_PIPELINE_CONFIG.get('force_ocr',False):
        caps['ocr_conversion_force']=True
    logging.info("[force_ocr] state: "+str(caps['ocr_conversion_force']))
    
    return caps


def wt_main_pipeline(case_id='',manual_skip_caps=[],options={}):
    ## options={}  #mostly dev options like running for specific document + page #
    
    if options:
        logging.info("[wt_main_pipeline] options: "+str(options))

    if not case_id: raise ValueError("case_id required")
    meta={}

    caps=get_standard_job_needs(options=options)

    ### TOP JOB
    Agent=Smart_Agent()
    job={}  # controlled dict

    #### MANUAL SKIP CAPS
    for skip_caps in manual_skip_caps:
        skip=caps.pop(skip_caps,'')
        if not skip:
            logging.warning("[skip_caps] not found: "+str(skip_caps))

    if 'create_run_job' in caps:
        ########### JOB MANAGEMENT 0v2
        logging.info ("*** SETUP JOB ***")
        if 'create_run_job' in caps:
            job,is_created=Agent.create_job_request_dict(case_id=case_id)
            """
                run_iagent -> handle case request
                run_iagent -> call run pipeline
                run_iagent -> check on job
                job=Agent.get_next_job()
            """
            logging.info("[got job]: "+str(job))

        job=Agent.note_job_status(job,'create_run_job')

    #### Auto pop if completed in past
    # [ ] watch cause KBAI checks' itself (via field versions + flags)

    ASSUME_ALWAYS_SYNC_FILES=True
    logging.info ("[sync cloud files to local] Technically should already be done")
    interface_sync_case_storage_to_processing_storage(case_id=case_id)

    job_state=get_job_state(case_id=case_id)

    ## ocr_conversion:  always run cause may have more files dropped in
    ## main_pipeline:   incremental files added.  Have own tracking in mega -> chunk
    ## KBAI:            have own tracking via field version or node AlgList
    #status,age_hours=Agent.get_state_status(job['job_id'],'ocr_conversion')
    #status,age_hours=Agent.get_state_status(job['job_id'],'end_main_processing_pipeline')
    

    if 'ocr_conversion' in caps:
        ########### OCR 0v1
        ocr_meta=TASK_convert_raw_image_pdfs_to_text(case_id,force_ocr=caps.get('ocr_conversion_force',False))
        meta.update(ocr_meta)
        job=Agent.note_job_status(job,'ocr_conversion')

    if job and 'start_main_processing_pipeline' in caps or 'check_files_main_processing_pipeline' in caps:
        ## [ ] move to modules_hub and decide on run_iagent or sim_user there!
        job=Agent.note_job_status(job,'start_main_processing_pipeline')
        print ("{recall} main processing is on a page-by-page basis & tracked with mega + chunks")

        ## w_pipeline/run_pipeline.py
        #- main transaction + page extracts
        pipe_meta=TASK_run_main_pipeline(job=job,Agent=Agent, options=options)
        meta.update(pipe_meta)

        job=Agent.note_job_status(job,'end_main_processing_pipeline')

    if job and 'start_KBAI_processing_pipeline' in caps:
        job=Agent.note_job_status(job,'start_KBAI_processing_pipeline')

        outputs,kb_meta=TASK_call_KB_update_pipeline(case_id,force_update_all=options.get('force_update_all',False))
        total_tokens_used=kb_meta.get('total_tokens_used',0)
        meta.update(kb_meta)
        logging.info("[done KBAI] for: "+str(meta))
        job=Agent.note_job_status(job,'end_KBAI_processing_pipeline')


    job=Agent.note_job_status(job,'wt_main_pipeline_finished')

    """
        logging.info ("*** > dump to excel          ***")
    if 'dump_excel' in caps:
        target_filename,case_filename=TASK_dump_excel(case_id=case_id)

    logging.info ("*** SYSTEM ONLINE FOR Q&A    ***")
    if 'QA_Online' in caps:
        logging.info ("> PING BASE HANDLER")
        logging.info ("> PING API HUB")
        logging.info ("> PING UX WIDGET SUPPORT")
    """
    
    meta['job_state']=get_job_state(case_id=case_id,write_log=True)
    return meta


def get_job_state(case_id='case_schoolkids',write_log=True):
    global FILENAME_RUN_LOG
    
    
    ## Move to algs_iagent -> alg_get_case_files (lower down at get_case_states)
#MVED    ## Job state may depend on having remove files from google storage
#MVED    logging.info("[sync cloud files to local] **move optionally but fine here for now for latest")
#MVED    #* see a_agent/algs_iagent)
#MVED    interface_sync_case_storage_to_processing_storage(case_id=case_id)

    ## QUERY FOR UP-TO-DATE ALL STATES + META

    Agent=Smart_Agent()
    all_states=Agent.get_case_states(case_id)
    if not all_states: return None

    # Sort the dictionary by age in ascending order
    sorted_data = {k: v for k, v in sorted(all_states.items(), key=lambda item: item[1]['age'])}
    
    # Get the newest state and its age
    newest_state = next(iter(sorted_data.keys()))
    newest_age_seconds = sorted_data[newest_state]['age']
    
    # Convert the newest age to minutes
    newest_age_minutes = newest_age_seconds / 60.0

    c=0
    for state in sorted_data:
        c++1
        print("age #"+str(c)+f"State {state} is {sorted_data[state]['age']:.2f} seconds.")

    print ()
    print(f"Newest state {newest_state} is {newest_age_minutes:.2f} minutes.")
    
    print ("> "+str(all_states))
    

    ## LOCAL COUNT RUNTIMES
    runtimes={}
    
    try:
        runtimes['kbai']=(all_states['start_KBAI_processing_pipeline']['age']- all_states['end_KBAI_processing_pipeline']['age'])//60

        runtimes['pipeline']=(all_states['start_main_processing_pipeline']['age']- all_states['end_main_processing_pipeline']['age'])//60
    
    except: pass

    ## end estimation
    #* note: is not a good estimate cause not all states are in yet
    #runtimes['full_pipeline']=(all_states['create_run_job']['age']- all_states['end_main_processing_pipeline']['age'])//60
    
    print ("[dev runtimes (minutes)]: "+str(runtimes))
    
    ## LOG
    if write_log:
        run={}
        run['runtime']=runtimes
        run['all_states']=all_states
        run['date']=str(datetime.datetime.now())
        with open(FILENAME_RUN_LOG,'a') as f:
            f.write(json.dumps(run)+"\n")

    return sorted_data


def dev1():
    # C:\scripts-23\watchtower\CASE_FILES_GOOGLE_SYNC
    case_id='65725b0050560b89044dca99'
    return


if __name__=='__main__':

    branches=['get_job_state']
    branches=['dev_sept22']
    branches=['dev1']

    for b in branches:
        globals()[b]()



"""
"""