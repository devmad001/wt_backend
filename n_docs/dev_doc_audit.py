import os
import sys
import codecs
import json
import re
import time
import requests

import configparser as ConfigParser


LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")

from a_agent.RUN_sim_wt import call_normal_full_run

from get_logger import setup_logging
logging=setup_logging()



#0v1# JC  Mar  4, 2024  Setup


"""
    "DOCUMENT-LEVEL" AUDIT
    - To support multi-document type -- first attempt at classifier or router
        (see also, chain agents or similar)
    - leverage auto-auditor to help narrow common exceptions

    - review document for OCR quality, data integrity, and other issues
    - identify and log incidents for further review or resolution
    - route incidents to appropriate resolution paths
    

    FUNCTION:
    - review historical document data

    - Front-end OCR & pdf2txt & GPT-V modules drive a lot of downstream quality issues

    - audit_ocr_quality_report?
    - unseen bank statement type?


"""



def dev1():
    #### SPECIFIC CASE
    #[ ] optionally add as test case for OCR

    ## OCR challenge via periods as commas
    # 227,293.46
    case_id='65d11a8c04aa75114767637a' #{'name': 'Silent Pipe', 'size': '0', 'username': '65cc09229b6ff316a77a0549
            

    #### CALL RUN DIRECTLY
    print ("RUNNING CASE:")
    call_normal_full_run(case_id=case_id,b=[],options=[])
    

    #### CALL SUB-MODULE
    #> pdf2txt (assuming know file?)

    #[ ] add specific test?
    #> JC:  See gold_test_configs...
    #> put pdf into test folder
    #> walk through similar to TD...


    return




if __name__=='__main__':
    branches=['dev1']
    for b in branches:
        globals()[b]()





