import os
import sys
import codecs
import json
import re
import time
import threading

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")

from w_storage.ystorage.ystorage_handler import Storage_Helper
from z_server.mod_execute.performance import Performance_Tracker
from z_server.mod_execute.mod_execute import is_script_running_with_arg

from get_logger import setup_logging
logging=setup_logging()


#0v1# JC  Jan 13, 2024  Init



"""
    HAS JOB STATUS
    - easy imports (stand-alone)
    
    *Refine as needed but for now -- FE pulls DONE status from BE
    - also option for BE to push.

"""


def ALG_machine_has_resources():
    print ("[debug] doing 10s sample of system resources, wait...")

    Perf=Performance_Tracker()

    has_resources=True
    reasons=[]
    stats={}

    ## RAM CHECK
    if has_resources:
        stats['ram']=Perf.get_ram_used()
        if stats['ram']>80:
            has_resourced=False
            reasons+=['high_ram']

    ## CPU CHECK
    #  10s cpu survey
    samples=3
    while samples:
        samples-=1
        stats['cpu']=Perf.get_cpu_used(interval=3)
        if stats['cpu']>60:
            has_resources=False
            reasons+=['high_cpu']

    if not has_resources:
        print ("[debug] machine not has resources: "+str(reasons))
    print ("[debug] machine resource stats: "+str(stats)+" is resources available: "+str(has_resources))

    return has_resources

def ALG_has_case_ever_finished_without_error(case_id):
    logging.dev("[TODO]: remove circular + do state properly (cache?) but, only for PROCESSING state now")
    #[ ] def refresh_single_running_job_status(case_id,job_dict=None,is_a_case_running=False):

    ## OPTIONS:
    #- NOT rely on case manager because job (BE focused)
    #>
    #x) ask smart agent if have seen kbai
    #? or maybe if done but error
    ## Smart_Agent talks directly with backend pipeline status

    from a_agent.iagent import Smart_Agent #Circular

    Agent=Smart_Agent()
    has_finished=Agent.dev_has_case_finished_ever(case_id)
    return has_finished


def ALG_is_case_job_running_now(case_id):
    is_running=False
    if is_script_running_with_arg('execute_wt.py',case_id):
        is_running=True
    return is_running


def dev1():
    #
    case_id='659f1c966c33e2599cce6d1c'
    case_id='65a83597b3ac164610ea5f75'
    case_id='65a7ce0bac045a667c77c7b5'
    case_id='65a8422cb3ac164610ea602b'
    case_id='65a847d0b3ac164610ea617b'
    case_id='65a88333b3ac164610ea63a3'
    
    print ("GIVEN CASE: "+str(case_id))
    has_finished=ALG_has_case_ever_finished_without_error(case_id)
    
    print ('has_finished: '+str(has_finished))


    
    ## Last check if script is running
    if is_script_running_with_arg('execute_wt.py',case_id):
        print ("IS RUNNING ALREADY")
    else:
        print ("IS not active run")


    return 



if __name__=='__main__':
    branches=['dev1']
    for b in branches:
        globals()[b]()




"""
"""
