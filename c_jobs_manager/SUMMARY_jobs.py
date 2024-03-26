import os
import sys
import codecs
import json
import re
import uuid
import time
import threading

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")


from mega_job import Mega_Jobber
from jobs_manager import JobsManager    

from mega_job import interface_run_one_job_cycle
from mega_job import practical_fetch_next_case_from_FE_if_never_ran_before
from mega_job import practically_run_a_case_if_possible


from get_logger import setup_logging
logging=setup_logging()




#0v1# JC  Feb  8, 2024  Init

"""
    SUMMARIZE CASE + JOB QUEUE STATUS
    - this will evolve into proper user-facing view/api control

"""



def SUMMARIZE_queue():
    # <> all cases or case specific?
    guide=[]

    cases=[]
#    cases+=["65c4e4423af8480437d0b9b2"]  #Jons' test
    cases+=["65b81d67d82c1db065bc4a97"]

    Mega=Mega_Jobber()
    JM=JobsManager()

    branch=['case_specific']
    branch=['queue_specific']

    if 'case_specific' in branch:
        ## Normal class usage
        print ("[info] ============== CASE DETAILS")
        for case_id in cases:
    
            print ("[info] -- SUMMARY FOR CASE: "+str(case_id))
    
            ## Larger job manager
            verbose_state_of_case=Mega.get_verbose_state_of_case(case_id)
            print ("[info] verbose state of BACKGROUND case: "+str(verbose_state_of_case))
    
            ## Direct job manager
            is_case_in_queue=JM.is_case_id_in_job_queue(case_id)

            print ("[info] is case id: "+str(case_id)+" in DB job queue: "+str(is_case_in_queue))
            if is_case_in_queue:
                note='Case is in queue. I thought the queue would be auto processed'
                if not note in guide:
                    guide+=[note]


    if 'queue_specific' in branch:

        print ("[info] ============== QUEUE DETAILS")
        next_case_id=Mega.get_next_priority_case_id_to_run()
        countr={}
        if not next_case_id:
            print ("[info] warning, no next priority case to run!")
        else:
            print ("[info] next case_id to run: "+str(next_case_id))

        print ("[info] ============== JOB QUEUE DETAILS?")
        for Job in Mega.iter_jobs():
            print ("> "+str(Job.__dict__))
            try: countr[str(Job.status)]+=1
            except: countr[str(Job.status)]=1
        print ("^done job queue details: "+str(countr))

    
    """ TBD
     vv,MG=interface_get_verbose_job_status(case_id)
    """
    print ("GENERIC GUIDES: ")
    for note in guide:
        print ("> "+str(note))

    return



def NOCOMMIT_run_job_cycle():
    print ("[debug] NOCOMMIT, running job cycle check")
    commit=False
    #mega_job::
    interface_run_one_job_cycle(commit=commit)

    return

def COMMIT_practical_fetch_if_can():
    commit=True
    #mega_job::
    practical_fetch_next_case_from_FE_if_never_ran_before(commit=commit, verbose=True)
    return


def COMMIT_run_a_case_if_can():
    commit=True
    flag_started,info=practically_run_a_case_if_possible(commit=commit)
    print ("STARTED: "+str(flag_started))
    print ("INFO: "+str(info))

    return



def SUMMARY_jobdb():
    #? iter jobs but non requested?

    case_id="65b81d67d82c1db065bc4a97"
    case_id='65b94869cb281abf7748cea3'

    Mega=Mega_Jobber()

    ## Job in queue but not listed here??
    for Job in Mega.iter_jobs():
        print ("> "+str(Job.__dict__))

    #JM=JobsManager()
    #is_case_in_queue=Mega.Manager.JM.is_case_id_in_job_queue(case_id)
    is_case_in_queue=Mega.Manager.is_case_id_in_job_queue(case_id)
    print ("IS CASE IN JOB QUEUE (queue includes DONE queue): "+str(is_case_in_queue)+" for: "+str(case_id))
    print ("status done but did it start??")

    return


def normal_check_normal_run():
    print ("==== DEV enqueue something, run something")
    COMMIT_practical_fetch_if_can()
    COMMIT_run_a_case_if_can()

    return
"""
DEBUG NOTES:
    - what calls add_case_id_run_request_to_job_queue??
    - view front-end case status?

"""



if __name__=='__main__':
    branches=['NOCOMMIT_run_job_cycle']

    branches=['COMMIT_practical_fetch_if_can']
    branches=['COMMIT_run_a_case_if_can']

    branches=['normal_check_normal_run']
    branches=['SUMMARY_jobdb']
    branches=['SUMMARIZE_queue']


    for b in branches:
        globals()[b]()


