import os
import sys
import codecs
import time
import json
import re
import glob
import datetime
import subprocess

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")

from iagent import Smart_Agent

#from sim_wt import get_job_state
#from w_utils import am_i_on_server
#from z_server.mod_execute.mod_execute import is_process_running_linux
#from z_server.mod_execute.mod_execute import is_script_running_with_arg

from get_logger import setup_logging

logging=setup_logging()


#0v1# JC  Dec 27 2023  Init


"""
   STAND-ALONE ESTIMATED THROUGHPUT
   - be clear on how its' estimated/calculated

"""


def dev_estimated_throughput(case_id=''):

    ## Factors
    factors=[]
    factors+=['existing_queue_size'] #Count or sum estimation
    factors+=['computer_resources']
    factors+=['past_estimations']
    factors+=['hard_coded_equation']  #Base on per-page?
    factors+=['case_state_position']  #Inner state
    factors+=['pipeline_config']      #Number of threads

    ## Real-time query update
    #- historical data (always over/under?)
    
    ## Get at case status request
    #- or standalone
    
    ## Existing estimations

    return


## Ideally move job methods to job class but keep in agent for now
def jalg_processing_time(job_state):
    
    runtime_seconds=0
    start_times=0
    end_times=0

    # Extract start and end timestamps
    try:
        start_times = [job_state['state'].get(key, {}).get('time', None) for key in ['create_run_job', 'start_main_processing_pipeline']]
        end_times = [job_state['state'].get(key, {}).get('time', None) for key in ['end_KBAI_processing_pipeline', 'wt_main_pipeline_finished']]
    except:
        pass
    
    # Check if any timestamp is None (indicating a missing key)
    if not start_times or not end_times:
        print("Error: One or more keys not found in the job state.")
    else:
        # Calculate runtime
        try:
            start_time = min(filter(None, start_times))
            end_time = max(filter(None, end_times))
            runtime_seconds = end_time - start_time
        except:
            pass

    return runtime_seconds


def dev_check_past_throughputs():
    #>> Logged at pipeline level run_pipeline.py -> Agent.note_job_status

    ## At Job status level
    
    #> sqlite stored in local file system
    Agent=Smart_Agent()
    
    for Job in Agent.get_all_jobs_sorted():
        print ("JOB: "+str(Job))
        rt={}
        rt['runtime_job']=jalg_processing_time(Job)
        rt['ocr_time']=jalg_get_ocr_time(Job)
        rt['pages_count']=Job.get('pages_count',-1)
        rt['runtime_per_page']=rt['runtime_job']/rt['pages_count']
        print ("RUNTIME: "+str(rt))
        print ("RUNTIME PER PAGE: "+str(rt['runtime_per_page']))
        print ("OCR TIME: "+str(rt['ocr_time']))
        print ("OCR TIME PER PAGE: "+str(rt['ocr_time']/rt['pages_count']))

    print ("[info] done check throughputs")
    return


def jalg_get_ocr_time(job_state):
    runtime_seconds=0
    start_time=0
    end_time=0
    
    try:
        start_time = job_state['state'].get('ocr_conversion', {}).get('time', 0)
        end_time = job_state['state'].get('start_main_processing_pipeline', {}).get('time', 0)
    except:
        pass
    
    if not start_time or not end_time:
        print("Error: One or more keys not found in the job state.")
    else:
        try:
            runtime_seconds = end_time - start_time
        except:
            pass

    return runtime_seconds

def dev_gather_specific_metrics():
    ## Given system
    p2t_threads=8        #8 as of dec 20 (w_settings.ini)
    kb_markup_threads=14 #14 as of dec 20
    
    ## Target metrics
    runtime_entire=0
    runtime_ocr=0
    runtime_p2t=0
    runtime_kbai=0
    
    ## Iter job and calculate
    
    ##
    # job=Agent.note_job_status(job,'running_KBAI_processing_pipeline')
    #> initial pdf to text
    
    #'end_KBAI_processing_pipeline') #
    
#1#    #'start_main_processing_pipeline': {'time': 1703128972}
    #'running_KBAI_processing_pipeline': {'time': 1703128972}

#2#    #'create_run_job': {'time': 1703128976}
    #'end_main_processing_pipeline': {'time': 1703128976}

#3#    #'ocr_conversion': {'time': 1703128979}
#4#    #'start_KBAI_processing_pipeline': {'time': 1703128979}

    #'end_KBAI_processing_pipeline': {'time': 1703128981}
#5#    #'wt_main_pipeline_finished': {'time': 1703128981}

    return



def alg_throughput_estimation(version=2,ocr_needed=False,page_count=0):
    ## ESTIMATE OVERALL
    estimation=0

    ocr_needed=False
    
    ## Stats taken from runtimes_log.csv at 2023-12-27

    time_per_page_large=12.7
    time_per_page_small=33
    time_extra_per_page_ocr=30
    
    ## ESTIMATE REMAINING
    #> based on pipeline position
    
    return estimation


def alg_estimate_remaining_time(case_id=''):
    remaining_time=0
    return remaining_time


def test_estimation():
    ocr_needed=True
    page_count=6
    
    entire_time=alg_throughput_estimation(ocr_needed=ocr_needed,page_count=page_count)
    remaining_time=alg_estimate_remaining_time(case_id='')
    
    return

def dev_note_existing_estimators():
    #
      
    #/a_agent/interface_manager.py
    #> get_verbose_state_of_case
    
    return


if __name__=='__main__':
    branches=['dev_estimated_throughput']
    branches=['dev_check_past_throughputs']

    branches=['alg_throughput_estimation']
    branches=['test_estimation']

    for b in branches:
        globals()[b]()



"""
 {'case_id': 'case_2021-June-Statement_Business-Reserves-5635', 'version': 1, 'job_id': 'case_2021-June-Statement_Business-Reserves-5635-1', 'base_dir': 'c:/scripts-23/watchtower/wcodebase/a_agent/../w_ui/file_manager/storage/case_2021-June-Statement_Business-Reserves-5635/', 'filenames': ['2021-June-Statement_Business-Reserves-5635.pdf'], 'path_filenames': [('c:/scripts-23/watchtower/wcodebase/a_agent/../w_ui/file_manager/storage/case_2021-June-Statement_Business-Reserves-5635/2021-June-Statement_Business-Reserves-5635.pdf', '2021-June-Statement_Business-Reserves-5635.pdf')], 'state': {'create_run_job': {'time': 1697161573}, 'ocr_conversion': {'time': 1697161577}, 'start_main_processing_pipeline': {'time': 1697161444}, 'running_KBAI_processing_pipeline': {'time': 1697161553, 'meta': {'progress': 1.0}}, 'end_KBAI_processing_pipeline': {'time': 1697161894}, 'end_main_processing_pipeline': {'time': 1697161561}, 'wt_main_pipeline_finished': {'time': 1697161894}, 'start_KBAI_processing_pipeline': {'time': 1697161577}}, 'next_actions': [], 'pages_count': 2, 'page_active': 2, 'last_active': 1697161444}
 
job_state = {
    'create_run_job': {'time': 1703128976},
    'ocr_conversion': {'time': 1703128979},
    'start_main_processing_pipeline': {'time': 1703128972},
    'running_KBAI_processing_pipeline': {'time': 1703128972},
    'end_KBAI_processing_pipeline': {'time': 1703128981},
    'end_main_processing_pipeline': {'time': 1703128976},
    'wt_main_pipeline_finished': {'time': 1703128981},
    'start_KBAI_processing_pipeline': {'time': 1703128979}
}
"""







