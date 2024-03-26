import os
import sys
import codecs
import json
import re
import time
import unittest

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")

from get_logger import setup_logging
logging=setup_logging()

## JOB SPECIFIC
#from entry_workflows_jobs import entry_get_ujob_status
#from entry_workflows_jobs import create_new_job
#from entry_workflows_jobs import iter_jobs
#from entry_workflows_jobs import add_job_to_queue
#from jobs_manager import JobsManager

from c_case_manager.case_analytics import interface_get_user_cases_statuses
from mega_job import interface_run_one_job_cycle

from mega_job import practically_run_a_case_if_possible
from mega_job import practical_fetch_next_case_from_FE_if_never_ran_before


## CASES SPECIFIC
#- ideally unit test at job but want to check more fragile integration area



#0v1# JC  Jan 11, 2024  Init



"""
    TESTS FOR JOB MANAGER
    - also check integration with Case manager + case state manager
"""


"""
ARCHITECTURE

c_case_manager/
- front-end facing queue system for INIT -> PROCESSING -> DONE
- includes case status, db for processing times + meta

c_jobs_manager/
- responsible for spawning background jobs (checking resource ok)
- "queue", fallbacks, retries, "backend" for case manager

NORMAL FLOW:
-> User uploads pdf + creates case details  (state: DETAILS_POSTED)
-> Recall, FSM manages tracking case state changes
-> backend (this c_jobs_manager) if sees a case is ready, move to PROCESSING, starts background
-> When job completes, update state to DONE

"""



class TestExternalCaseStatus(unittest.TestCase):
    def setUp(self):
        self.case_id='test_case_123'
        #self.username='test_user_123'
        self.username='6571b86a88061612aa2fc8b7'  ## shivam debug *hard coded for now - mock later
        pass
        
    def test_user_cases_statuses(self):
        cdicts=interface_get_user_cases_statuses(self.username)
        self.assertTrue(len(cdicts)>0)
        
        return

class TestJobEnrypoints(unittest.TestCase):
    ## Regular modules accessible
    def setUp(self):
        pass
        
    def test_main_cron_runner(self):
        mega=interface_run_one_job_cycle(commit=False)  #Passes if no exceptions
        return

class TestJobStateChanges(unittest.TestCase):
    def setUp(self):
        pass

    def test_done_processing_signal_to_FE_cases(self):
        #** feature not there.  For now, FE polls BE on processing jobs.
        pass



def dev1():

    ## Develop integrated tests
    
    print ("Front-end case status: ")
    
    print ("Back-end job status: ")

    print ("Specific checks of job infrastructure")
    
    print ("Echo integration or normal flow test with case (dummy/simulated) ")
    
    print ("? exceptions like fatal fail of job etc, must update front or retry (this built in really)..")


    return


def dev2():
    a=beware_called_by_wtest
    
    b=[]
    b+=['test pull next job from FE']
    
    if 'do non commit job cycle' in b:
        # locally here as part of test integration
        mega=interface_run_one_job_cycle(commit=False)
        
    if 'do non commit direct FE job fetch' in b:
        print ("dev run what case though?")
        practically_run_a_case_if_possible(commit=False)

    if 'test pull next job from FE' in b:
        print ("Fetch from FE, if never ran before, and put to job queue")
        actions=practical_fetch_next_case_from_FE_if_never_ran_before(verbose=True,commit=True)
        for action in actions:
            print ("Action: ",action)

    #[1]# CASE TO JOB VIA:

    # FE "queue" -> job queue
    ##########################
    #def practical_fetch_next_case_from_FE_if_never_ran_before(commit=True):

    #  practical_receive_run_request_put_to_job_queue(case_id):
    
    #[2]# JOB TO RUN VIA:
    # practically_run_a_case_if_possible(commit=False)

    return



if __name__=='__main__':
    unittest.main()
#    dev2()




"""
"""










