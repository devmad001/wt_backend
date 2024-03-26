import os
import sys
import time
import codecs
import json
import re
import psutil

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")

from a_agent.iagent import Smart_Agent

#0v1# JC  Sep 11, 2023  Setup


"""
    SIMULATE USER WORKFLOWS
    - [ ] add tests:  used for UX status in api_helper.py
"""


def dev1():
    b=[]
    b+=['upload_files']
    b+=['call_process']
    b+=['dump_excel']
    b=['upload_files']
    b=['call_process']
    b=['check_if_finished']
    b=['dump_excel']

    story_name='Process BOA pdf to excel output.'

    ppaths=[]
    ppaths+=['Upload one BOA pdf file to a case id']

    ppaths+=['Process via extractor']
    ppaths+=['Excel data merge and output']

    case_id='case_schoolkids'

    demo={}
    demo['case_id']=case_id
    demo['filenames']=['Schoolkidz December 2021 statement.pdf']

    print ("[info] doing demo flow: "+str(demo))


    if 'upload_files' in b:
        pass
    print ("==== UPLOAD CASE FILES =================")
    print ("[dev] start file listener: cd ~/w_ui/file_manager/pyfiledrop.py")
    print("[info] Listening on http://0.0.0.0:8081/case/"+case_id+"/upload")

    if 'call_process' in b:
        print ("==== START PROCESS 'JOB' ===============")
        from a_agent.run_iagent import dev_call_agent_handle_case_request
        dev_call_agent_handle_case_request(case_id=case_id)

    if 'check_if_finished' in b:
        ## job:    'completed_on': 1694556769.4598532,  (define in dict when done)
        job=interface_get_job_dict(case_id=case_id)
        print ("JOB STATUS: "+str(job))

        if job.get('last_active',0):
            print ("[info] job last active: "+str(time.time()-job['last_active'])+"s ago.")
        if 'completed_on' in job:
            print ("[info] job completed on: "+str(job['completed_on']))
            print ("** ready to dump excel")

    if 'dump_excel' in b:
        target_filename,case_filename=interface_dump_excel(case_id=case_id)

        print ("REPORT AT: "+str(target_filename))
        print ("REPORT name: "+str(case_filename))

    return

def interface_get_job_dict(case_id=''):
    Agent=Smart_Agent()
    job=Agent.load_job(case_id=case_id)
    return job

def interface_dump_excel(case_id=''):
    from excel_manager.dev_ereport import dev_generate_excel_report_oct14
    
    print ("[info] generating report for: "+str(case_id))
    target_filename,case_filename=dev_generate_excel_report_oct14(case_id=case_id)
    return target_filename,case_filename

def interface_run_pipeline_in_background(case_id=''):
    from handle_background_requests import call_run_pipeline_background
    #case_id='case_schoolkids'
    is_started=False
    if case_id:
        is_started,meta=call_run_pipeline_background(case_id)
    return is_started,{}

def interface_get_job_status(case_id=''):
    #** COMBINE WITH a_agent/interface_manager
    #** yes, another status dict but make user facing 
    #[ ] also see sim_wt get_job_state but essentially the same as here.
    """
     {'case_id': 'case_atm_location', 'version': 1, 'job_id': 'case_atm_location-1', 'base_dir': 'c:/scripts-23/watchtower/wcodebase/a_agent/../w_ui/file_manager/storage/case_atm_location/', 'filenames': ['07A210E6-B60D-46B6-9D40-9B3239237F05-list.pdf'], 'path_filenames': [('c:/scripts-23/watchtower/wcodebase/a_agent/../w_ui/file_manager/storage/case_atm_location/07A210E6-B60D-46B6-9D40-9B3239237F05-list.pdf', '07A210E6-B60D-46B6-9D40-9B3239237F05-list.pdf')], 'state': {'create_run_job': {'time': 1697230325}, 'ocr_conversion': {'time': 1697230325}, 'start_main_processing_pipeline': {'time': 1697230325}, 'running_KBAI_processing_pipeline': {'time': 1697230439, 'meta': {'progress': 1.0}}, 'end_KBAI_processing_pipeline': {'time': 1697231081}, 'end_main_processing_pipeline': {'time': 1697230439}, 'start_KBAI_processing_pipeline': {'time': 1697230439}, 'wt_main_pipeline_finished': {'time': 1697231081}}, 'next_actions': [], 'pages_count': 4, 'page_active': 1, 'last_active': 1697230325}
    """
    
    job=interface_get_job_dict(case_id=case_id)
    print ("JOB: "+str(job))
    
    ## Patch from earlier if job.state is str migrate to now time.
    if isinstance(job.get('state',{}),str):
        print ("[patch migrate job state from str to dict]")
        temp=job['state']
        job['state']={}
        job['state'][temp]=time.time()
    
    ss={}
    if job:

        Agent=Smart_Agent()

        ##
        ss['is_case_running_in_background']=False
        
        ## LOGIC:
        #> running if:
        # ii) job start time > job completed_on
        ss['is_job_running']=False
        print ("[raw get_job_status]: "+str(job['state']))
        if job['state'].get('start_main_processing_pipeline',{'time':0})['time'] > job['state'].get('wt_main_pipeline_finished',{'time':0})['time']:
            ss['is_job_running']=True
        
        ##[A]
        ss['has_job_ever_finished']=False
        if not job['state'].get('wt_main_pipeline_finished',{'time':0})['time']==0:
            ss['has_job_ever_finished']=True
            
        ##[B]
        # last active state?
        all_states=Agent.get_case_states(case_id)
        if all_states:
            # Sort the dictionary by age in ascending order
            sorted_data = {k: v for k, v in sorted(all_states.items(), key=lambda item: item[1]['age'])}
            
            # Get the newest state and its age
            newest_state = next(iter(sorted_data.keys()))
            newest_age_seconds = sorted_data[newest_state]['age']
            
            # Convert the newest age to minutes
            newest_age_minutes = newest_age_seconds / 60.
        else:
            newest_age_minutes=-1
            
        ss['age_of_last_active_m']=newest_age_minutes
        try: ss['age_since_started_m']=(time.time()-job['state']['start_main_processing_pipeline']['time'])/60.
        except:
            ss['age_since_started_m']=-1
            pass
            ss['age_since_started_m']=-1
        ss['job_raw_page_count']=job.get('pages_count',0)
        
        tot_time_m=calculate_estimated_processing_time(ss)
        remaining_time_m=tot_time_m-ss.get('age_since_started_m',0)
        ss['estimated_time_remaining']=max(remaining_time_m,0)

    """
    {'is_case_running_in_background': False, 'is_job_running': False, 'has_job_ever_finished': True, 'age_of_last_active_m': 2510.15, 'age_since_started_m': 2522.7591921448707, 'job_raw_page_count': 4, 'estimated_time_remaining': 0}
    """
    return ss

def calculate_estimated_processing_time(job_status):
    #0v1# Nov 15, 2023  Really just estimate
    tot_time_m=(job_status.get('job_raw_page_count',0)*250)/60.
    return tot_time_m

def dev_background():
    print ("Sample import and run in background...")
    from handle_background_requests import call_run_pipeline_background
    case_id='case_schoolkids'
    is_started,meta=call_run_pipeline_background(case_id)

    print ("[dev background] started: "+str(is_started))

    return

def dev2():
    case_id='case_atm_location'
    ss=interface_get_job_status(case_id=case_id)
    print ("BASE: "+str(ss))

    return


if __name__=='__main__':
    branches=['dev1']
    branches=['dev_background']
    branches=['dev2']
    for b in branches:
        globals()[b]()
        




"""
"""
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
