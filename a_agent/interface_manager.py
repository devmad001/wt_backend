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

from a_agent.iagent import Smart_Agent

## Main pipeline (base extraction)

from sim_wt import wt_main_pipeline
from sim_wt import get_job_state


from w_utils import am_i_on_server
from z_server.mod_execute.mod_execute import The_Execute_Command
from z_server.mod_execute.mod_execute import is_process_running_linux
from z_server.mod_execute.mod_execute import is_script_running_with_arg

from get_logger import setup_logging

logging=setup_logging()


#0v2# JC  Dec 10 2023  Tie into mega_job + FE
#0v1# JC  Oct  5 2023  Init


"""
   TOP-LEVEL INTERFACE FOR MANAGING EXECUTION
"""

LOG_DIRECTORY=LOCAL_PATH+"../w_datasets/pipeline_exe_logs"

ON_SERVER=am_i_on_server()


#def is_background_case_processor_running():
#        if is_script_running_with_arg('execute_wt.py',case_id):
#    return

def is_background_case_processor_running():
    EXE=The_Execute_Command()
    pname='execute_wt.py'
    if EXE.is_running(pname,verbose=True):
        return True
    return False

def request_spawn_pipeline_process(case_id,method):
    global LOG_DIRECTORY
    print ("[debug] request spawn pipeline process for: "+str(case_id))
    
    #job id? tbd since could make new one
    #    print ("SEE:  execute_wt.py" and dev_auto_server for spawning
            
    Exe=The_Execute_Command()
    #?check if running:   if pname and self.Exe.is_running(pname,verbose=False):
    
    
    ## CREATE LOG FILE
    log_name=''
    # Get the current date and time
    now = datetime.datetime.now()

    # Format the current date and time as a string 'yyyy_mm_dd_hh_mm'
    date_time_string = now.strftime("%Y_%m_%d_%H_%M")

    fname=method+"_"+case_id+"_"+date_time_string+".log"
    
    if not os.path.isdir(LOG_DIRECTORY): raise Exception("No log dir")
    log_filename=LOG_DIRECTORY+"/"+fname
    
    exe_dir=LOCAL_PATH+"../z_server"
    
    run_cmd='cd '+exe_dir+' && python execute_wt.py '+case_id+' '+method+" > "+log_filename+" 2>&1 &"
    cmd='cd '+exe_dir+' && python execute_wt.py '+case_id+' '+method
    
    if not ON_SERVER:
        print ("ON SERVER: "+str(ON_SERVER))
        Exe.execute(run_cmd,visible=True,background=True)

    else:
    
        ## Last check if script is running
        if is_script_running_with_arg('execute_wt.py',case_id):
            logging.info("Script already running: "+str(case_id))

        else:
    
            ## linux wrap spawn in nohup
            cmd_full="nohup bash -c '"+cmd+"' > "+log_filename+" 2>&1 &"

            ## Linux shell cmd
            print ("[dev] ready to spawn: "+str(cmd))
            print ("[dev] ready to spawn: "+str(cmd_full))
    
    
            subprocess.Popen(cmd_full, shell=True)
    return
    

class Manager_Interface:
    # "interface" meaning -- helper support for API
    
    def __init__(self):
        self.Agent=Smart_Agent() #<-- code side manager
        return
    
    def is_the_server_ok(self):
        return
    
    def is_background_case_processor_running(self):
        return is_background_case_processor_running()
    
    def start_long_running_job_process_in_background(self,case_id):
        logging.info("start_long_running_job_process_in_background> "+str(case_id))
        request_spawn_pipeline_process(case_id,'exe1')  #_dummy')
        return
    
    def which_cases_are_running(self,verbose=False):
        ## Check for background running jobs?

        #ie/ don't start the same case multiple times
        active_cases=[]
        
        print ("[debug] ON SERVER: "+str(ON_SERVER))

        if ON_SERVER:
            ## Define running:  Started within last 10 minutes?
            jobs=self.Agent.get_all_jobs_sorted()
            print ("[debug] jobs total count: "+str(len(jobs)))

            for job in jobs:
                #**had to check further
                    
                if not 'last_active' in job:
                    if 'state' in job and 'create_run_job' in job['state']:  #If long OCR may not look active
                        try: age=time.time()-job['state']['create_run_job']['time']
                        except: continue
                    else:
                        continue #Old

                else:
                    age=time.time()-job['last_active']

                if (age/60/60)>3: continue # more then 3 hours

                print ("[debug] job age option: "+str(age))

                print ("[job running candidate]: "+str(job))
                
                case_id=job['case_id']
                ## Check if still running
                if is_script_running_with_arg('execute_wt.py',case_id):
                    active_cases+=[case_id]
        return active_cases
    
    def get_job_specific_details(self,case_id):
        states=self.Agent.get_case_states(case_id) #<-- may file if google sync or local files not exist
        return states
    
    def what_was_the_last_case_and_state(self):
        #(recall RUN_sim_wt.py)
        rr={}
        
        ## Job and case
        jobs=self.Agent.get_all_jobs_sorted()
        if jobs:
            newest_job=jobs[0]
            case_id=newest_job['case_id']
            rr['newest_case_id']=case_id
            
            ## 3/  Get states of newest job
            states=self.Agent.get_case_states(case_id,job=newest_job)

            if states:
                min_age_key = min(states, key=lambda k: states[k]['age'])
                min_age_value=states[min_age_key]['age']
                rr['newest_last_ran_age']=min_age_value
                rr['newest_last_ran_state']=min_age_key
                rr['job_id']=newest_job['job_id']
        return rr
    
    def what_is_the_last_state_of_case(self,case_id):
        ## Case 2 job
        rr={}
        rr['case_id']=case_id
        newest_job=self.Agent.case2job(case_id)
        if newest_job:
            states=self.Agent.get_case_states(case_id,job=newest_job)
            min_age_key = min(states, key=lambda k: states[k]['age'])
            min_age_value=states[min_age_key]['age']
            rr['newest_last_ran_age']=min_age_value
            rr['newest_last_ran_state']=min_age_key
            rr['job_id']=newest_job['job_id']
            rr['pages_count']=newest_job.get('pages_count',0)
        return rr
    
    def has_case_been_processed_ever(self,case_id, verbose=False):
        #> has been processed sometime
        #> has been processed and last state is end
        reasons=[]
        
        last_state_is_processed_done=False
        has_been_processed=False
        
        ## [A]  OVERALL STATES
        #  {'create_run_job': {'age': 1021}, 'ocr_conversion': {'age': 1020}, 'start_main_processing_pipeline': {'age': 2907}, 'running_KBAI_processing_pipeline': {'age': 1021}, 'end_KBAI_processing_pipeline': {'age': 1021}, 'end_main_processing_pipeline': {'age': 1021}, 'wt_main_pipeline_finished': {'age': 1021}, 'start_KBAI_processing_pipeline': {'age': 1020}}
        states=self.Agent.get_case_states(case_id)
        logging.info("[debug] CASE STATES: "+str(states))
        

        ## [B]  LAST STATE
        rr= self.what_is_the_last_state_of_case(case_id)
        if verbose:
            print ("[last state of case debug]: "+str(rr))
            print ("[last state of case debug]: "+str(rr))

        
        ## [1]  if last active state is end then definitionly done at some point
        if rr.get('newest_last_ran_state','')=='end_KBAI_processing_pipeline':
            last_state_is_processed_done=True #<-- reprocessed?
        elif rr.get('newest_last_ran_state','')=='wt_main_pipeline_finished':
            last_state_is_processed_done=True #<-- reprocessed?
            

        ## [2] if hsa ever finished
        if 'end_main_processing_pipeline' in states:
            has_been_processed=True
            reasons+=['has end_main_processing_pipeline']
        elif 'end_KBAI_processing_pipeline' in states:
            has_been_processed=True
            reasons+=['has end_KBAI_processing_pipeline']
        elif 'wt_main_pipeline_finished' in states:
            has_been_processed=True
            reasons+=['has wt_main_pipeline_finished']
            
        if has_been_processed and not last_state_is_processed_done:
            logging.info("[debug] case has been processed in the past but last state is: "+str(rr.get('newest_last_ran_state','')))

        logging.info("[debug] has been processed ever: "+str(has_been_processed)+" because: "+str(reasons))
        return has_been_processed
        
    
    def get_verbose_state_of_case(self,case_id):
        ## Clean interface for FE
        vs={}
        vs['case_id']=case_id
        vs['is_done_processing']=False

        rr=self.what_is_the_last_state_of_case(case_id)
        if rr.get('newest_last_ran_state','')=='end_KBAI_processing_pipeline':
            vs['is_done_processing']=True
            
        vs['pages_count']=rr.get('pages_count',0)
        
        times=self.estimate_run_times(case_id)
        vs['estimated_runtime']=times['total_estimated_on_page_count_m']
        
        rjob=self.get_job_specific_details(case_id)
        if 'create_run_job' in rjob:
            # Not sure if refreshes if already exists
            vs['minutes_since_started']=rjob['create_run_job']['age']/60
        elif 'start_main_processing_pipeline' in rjob:
           vs['minutes_since_started']=rjob['start_main_processing_pipeline']['age']/60
        else:
            print ("[debug] no start_main_processing_pipeline: "+str(rjob))
            vs['minutes_since_started']=0
        
        ## For now don't assume failed etc.  Just do general case
        if 'is_done_processing' in vs and vs['is_done_processing']:
            vs['percent_complete']=100
        else:
            try: vs['percent_complete']=int(100*(vs['minutes_since_started'])/vs['estimated_runtime'])
            except: vs['percent_complete']=0
            vs['percent_complete']=min(99,vs['percent_complete'])
        
        ## For FE
        remaining_minutes=times['total_estimated_remaining_on_page_count_m']
        
        ## METHOD 2 for time remining
        remaining_minutes2=vs['minutes_since_started']-vs['estimated_runtime']
        
        ## TbD
        vs['remaining_minutes']=max(1,remaining_minutes,remaining_minutes2)

        return vs
    
    def estimate_run_times(self,case_id):
        ### MAIN AREAS:
        ##:  OCR CONVERSION
        ##:  MAIN PAGE TO TRANSACTIONS
        ##:  KB MARKUP
        
        ## INFORMAL LOGGING:
        # 142 pages (fairly hard) OCR in 800s = 5.6s per page
        
        already_done=None #Unknown

        newest_job=self.Agent.case2job(case_id)
        total_pages_of_all_files=newest_job.get('pages_count',0)
        active_process_main_page=newest_job.get('page_active',0)
        
        total_pages=total_pages_of_all_files

        total_time=0
        total_time=total_time+(total_pages*30)  # OCR
        total_time=total_time+(total_pages*122) # MAIN PAGE
        total_time=total_time+(total_pages*100) # KB
        
        total_time_remaining=total_time-(active_process_main_page*122)
        
        times={}
        times['total_estimated_on_page_count_m']=total_time/60 #Minutes
        times['total_estimated_remaining_on_page_count_m']=total_time_remaining/60 #Minutes

        return times
    
    def dump_latest_log(self,case_id):
        global LOG_DIRECTORY
        filename,log_content=load_newest_file_content(LOG_DIRECTORY,case_id)
        fname=os.path.basename(filename)
        return fname,log_content


def load_newest_file_content(directory, keyword):
    # Create a search pattern with the given keyword
    search_pattern = os.path.join(directory, f"*{keyword}*")
    
    # Get a list of all files in the directory that contain the keyword in their name
    files = glob.glob(search_pattern)
    
    # If no matching files, return None or handle appropriately
    if not files:
        print(f"No files found with keyword: {keyword}")
        return '',''
    
    # Find the newest file based on modification time
    newest_file = max(files, key=os.path.getmtime)
    
    with open(newest_file, 'rb') as file:
        content_bytes = file.read()
        content = content_bytes.decode('utf-8', errors='replace')
        print(f"Loaded content from newest file: {newest_file}")
        return newest_file, content


def dev1():
    case_id='demo_a'

    MI=Manager_Interface()
    rr=MI.what_was_the_last_case_and_state()
    rr=MI.what_is_the_last_state_of_case(case_id)
    
    print ("case state> "+str(rr))

    rr=MI.estimate_run_times(case_id)
    print ("case runtimes> "+str(rr))
    
    return


def auto_background_spawn():
    case_id='demo_a'
    MI=Manager_Interface()
    MI.start_long_running_job_process_in_background(case_id)
    print ("[done] should have spawned")
    return

def dump_calog():
    case_id='demo_a'
    WI=Manager_Interface()
    fname,log_content=WI.dump_latest_log(case_id)
    print ("GOT: "+str(fname))
    print ("LOG: "+str(log_content))
    return

def dev_what_is_running():
    MI=Manager_Interface()
    cases=MI.which_cases_are_running()
    print ("RUNNING: "+str(cases))
    return

def dev_background_running():
    print ("IS IT: "+str(is_background_case_processor_running()))
    return

if __name__=='__main__':
    branches=['auto_background_spawn']
    branches=['dump_calog']
    branches=['dev_what_is_running']

    branches=['dev1']
    branches=['dev_background_running']

    for b in branches:
        globals()[b]()


"""
"""
