import os
import sys
import codecs
import json
import re

from fastapi import FastAPI

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")

from get_logger import setup_logging
logging=setup_logging()

from call_kbai import call_kb_auto_solver_flow

#0v1# JC  Sep 19, 2023  Init

"""
    FORMAL INERFACE TO KB Q & MARKUP
    - ?run in background or threaded
    - auto run (via internal trigger questions?)
"""



def get_internal_trigger_questions():
    ## Similar to general Q&A but these questions have keyword triggers
    #- goal remains:  fill gap/update KB
    trigger_questions=[]
    trigger_questions+=['[transaction_type_method]']

    return trigger_questions


def interface_run_KB_AI(question,case_id):
    response=call_kb_auto_solver_flow(question,case_id)
    return response

def interface_run_all_trigger_questions_KB_AI(case_id):
    tquestions=get_internal_trigger_questions()

    for question in tquestions:
        response=interface_run_KB_AI(question,case_id)

    return

def dev1():
    ## Internal or external
    case_id='case_3'

    # Sample self-trigger
    b=['single_trigger']
    b=['all_trigger']

    if 'single_trigger' in b:
        logging.info("[running] interface_run_KB_AI")
        trigger_question='[transaction_type_method]'
        interface_run_KB_AI(trigger_question,case_id)

    if 'all_trigger' in b:
        interface_run_all_trigger_questions_KB_AI(case_id)

    return


if __name__=='__main__':
    branches=['dev1']
    for b in branches:
        globals()[b]()

"""
"""
