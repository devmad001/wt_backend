import os
import sys
import codecs
import time
import json
import re

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")

from a_agent.sim_wt import wt_main_pipeline
from a_agent.sim_wt import get_job_state
from a_agent.RUN_sim_wt import MAIN_ENTRYPOINT_CASE_processing_pipeline

from get_logger import setup_logging

logging=setup_logging()


#0v2# JC  Dec 10 2023  Cont (from interface_manager.py from mega_job.py from EXECUTION_HUB.py)
#0v1# JC  Oct  5 2023  Init

### START MAIN PROCESSING OF JOB IN BACKGROUND PROCESS
#- this is run in thread -- expects to be spawned as background!

## Expect outputs to be logged but also standard logging out

def execute_in_background_case_id(case_id, method):
    start_time=time.time()

    if method=='exe1':
        MAIN_ENTRYPOINT_CASE_processing_pipeline(case_id)
        pass
    elif method=='exe_dummy':
        print ("[debug] not running full pipeline but could: "+str(case_id))

    end_time=time.time()-start_time
    logging.info("execute in background runtime: "+str(end_time))

    return


if len(sys.argv) != 3:
    print("Usage: python run_background.py <case_id> <state1>")
    sys.exit(1)

# Capture arguments
case_id = sys.argv[1]
method = sys.argv[2]

execute_in_background_case_id(case_id, method)

