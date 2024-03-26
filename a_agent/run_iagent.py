import os
import sys
import codecs
import json
import re

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")

from a_agent.iagent import Smart_Agent
from w_pipeline.run_pipeline import interface_run_pipeline
from get_logger import setup_logging
logging=setup_logging()

#0v1# JC  Sep 12, 2023  Integrate job scheduling


"""
** this is superseeded by wt_main_pipeline.
    CALL AGENT
    - steer towards various tasks
    - watch circular imports because pipeline USES agent as well

"""



def dev_call_agent_run_pipeline():
    Agent=Smart_Agent()
    job=Agent.get_next_job()

    print ("[dev_call_agent] next job: "+str(job))

    b=[]
    b+=['agent calls main run_pipeline']

    if 'agent calls main run_pipeline' in b:
        #* recall, Agent could be spawned within pipeline if not exists

        ## OK
        if False and job:
            logging.info("[info] Smart agent calling main pipeline...")
            ## If job send without agent
            interface_run_pipeline(job=job,Agent=None)

        if job:
            logging.info("[info] Smart agent calling main pipeline...")
            interface_run_pipeline(job=job,Agent=Agent)

    return

def interface_call_agent_handle_case_request(case_id='case_3'): #SGM BOA, 
    FORCE_RUN=True

    Agent=Smart_Agent()

    ## Create job (stored below)
    job,is_created=Agent.create_job_request_dict(case_id=case_id)

    if is_created:
        print ("JOB REQUEST CREATED: "+str(job))
        logging.info("[info] Smart agent calling main pipeline...")
        Agent.store_job_request(job)
        interface_run_pipeline(job=job,Agent=Agent)
    else:
        logging.info("Job status: "+str(job))

        if FORCE_RUN:
            interface_run_pipeline(job=job,Agent=Agent)
        else:
            logging.info("Not running cause job previously created")

    ## Refresh for latest status
    job=Agent.load_job(job['job_id']) 
    logging.info("Done do job status: "+str(job))
    return

def dev_general_job_checks():
    case_id='SGM BOA'

    Agent=Smart_Agent()
    job=Agent.load_job(case_id=case_id)

    print ("[debug] job status: "+str(job))

    return


if __name__=='__main__':
    branches=['dev_call_agent_run_pipeline']
    branches=['dev_general_job_checks']
    branches=['interface_call_agent_handle_case_request']

    for b in branches:
        globals()[b]()


"""
"""