import os
import sys
import codecs
import json
import re
import time

#import threading
#import psutil

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")

from mega_job import practical_receive_run_request_put_to_job_queue
from mega_job import interface_run_one_job_cycle
from mega_job import interface_get_verbose_job_status
from mega_job import Mega_Jobber

from jobs_manager import JobsManager

from c_case_manager.case_analytics import interface_get_BE_cases_statuses


from get_logger import setup_logging
logging=setup_logging()



#0v3# JC  Feb  8, 2023  Validate standard flows
#0v2# JC  Jan 13, 2023  Admin report
#0v1# JC  Dec 10, 2023  Easy ADMIN


def local_iter_recent_jobs():
    JM=JobsManager()
    for Job in JM.query_jobs(query={}):
        yield Job
    return

# Example usage
def colin_run_reports_for_all_recent_cases():
    #* on server
    do_continue=False
    nextt='657f12dc9a57063d991dd7c2'
    for Job in local_iter_recent_jobs():
        case_id=Job.case_id
        if case_id==nextt: do_continue=True
        if not do_continue: continue
        print ("[case generating reports]: "+str(case_id))
        CALL_generate_all_reports(case_id)
        
    return

def ADMIN_remove_job_from_queue(case_id='',job_id=None):
    print ("Watch multiple case_id?!")

    if case_id:
        query={'case_id':case_id}
    elif job_id:
        query={'id':job_id}
    else:
        raise Exception("Must provide case_id or job_id")
        
    print ("[dev] deleting job (ADMIN req) IF exists: "+str(query))
    MJ=Mega_Jobber()
    MJ.Manager.delete_job(query=query)
    
    return


def LOCAL_add_case_request_to_job_queue(case_id):
    #** should be resolved by handle_one_job_cycle()
    is_added=practical_receive_run_request_put_to_job_queue(case_id)
    return is_added



def dev1():
    
    b=['dec10_add_sample_cases']
    b=['dec10_try_job_cycle']
    
    ## ECHO JOB STATUS?? -- see mega_job.py
    ## ADMIN or dev this is where we manually check the enqueue
    

    
             
    if 'dec10_try_job_cycle' in b:
        interface_run_one_job_cycle()  #<-- this is the main job cycle.
             
    if 'dec10_add_sample_cases' in b:

        #case_id='simulated_case_request_case_1'
        #ADMIN_remove_job_from_queue(case_id=case_id)

        case_id='65713fc888061612aa2fc3c6'  #<-- google storage. should sync and put to requested
        #...then on next job cycle...it should auto run if possible

        is_added=LOCAL_add_case_request_to_job_queue(case_id)
        
        print ("ADMIN mega job is case added? "+str(is_added)+" : "+str(case_id))


    return



def dev2_manual_remove():
    
    print ("DOING MANUAL")

    case_id='65713fc888061612aa2fc3c6'
    ADMIN_remove_job_from_queue(case_id=case_id)
    
    MJ=Mega_Jobber()
    
    for Job in MJ.iter_jobs():
        print ("JOB: "+str(Job))
    

    return


def ADMIN_report_jobs_and_cases():
    print ("* easy summary")
    
    #print ("The job queue has how many jobs ready: "+str(Mega_Jobber().Manager.count_jobs(query={'status':'ready'})))
    print ("The job queue has how many jobs ready: xxx")
    print ("The job queue has which cases active lately?")
    print ("The FE case status has what cases active lately?")
    
    ## JOBS
    print ("="*40)
    print ("JOBS (last 10):")
    jobs=[]
    for Job in local_iter_recent_jobs():
        jobs+=[Job.__dict__]
    #Last 10 jobs
    for Job in jobs[-10:]:
        print ("Job: "+str(Job))
    
    ## FE CASES
    print ("="*40)
    print ("FE-CASES:")
    for cdict in interface_get_BE_cases_statuses(limit=10):
        print ("FE case: "+str(cdict))


    return

def ADMIN_call_branches():
    case_id='65c4e4423af8480437d0b9b2'

    b=[]
    b+=['verbose_job_status']

    if 'verbose_job_status' in b:
        print ("[debug] verbose status for: "+str(case_id))
        vv,MG=interface_get_verbose_job_status(case_id)
        print ("DETAILS: "+str(vv))
        if not vv:
            print ("[warning] no job status for case: (?has it been queued?)"+str(case_id))
    


    return


if __name__=='__main__':
    branches=['dev1']
    branches=['dev2_manual_remove']
    branches=['ADMIN_report_jobs_and_cases']
    branches=['ADMIN_call_branches']

    for b in branches:
        globals()[b]()



"""

"""
