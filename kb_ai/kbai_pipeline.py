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

from schemas.SCHEMA_kbai import gold_schema_definition
from w_storage.gstorage.gneo4j import Neo


#0v1# JC  Sep 14, 2023  Init

"""
DRAFT!!  See call_kbai!
    KB AI Pipeline
"""

def dev1():
    print ("SEE: call_kbai")
    print ("USIN case_id: case_3")
    print ("USIN PDF: SGM BOA statement december 2021.pdf")

    print ("HARDCODE OK")

    top_goal='apply llm_record_transform to update/augment KB'
    hard_goal_example="Identify the Entity where the withdrawal was directed. Provide its details."

    print ("[init] kb_helper")

    Kagent=KB_Agent()

    print ("Given question:")
    print ("{internal questions or dynamic externals}")

    question='Extract where this withdrawl went.  What is the Entity details?'

    print ("A kb_query()")

    print ("[agent] what data do I need?")
    print ("[agent] do cypher query")

    print ("Current schema is: xxx")
    print ("Raw data is: yyy")

    print ("[agent] if no data response, consider recommending what nodes/rels to add to KB")

    print ("A kb_update() is required")

    print ("What is the target schema: yyy?  Assume data is augmented")
    print ("Current records is: rrr (input data records)")
    print ("                    mmm (input meta -- or can fetch real-tim but ie/ doc_stats:is_BOA")

    records={}
    rmeta={}

    schema_versin='1' #active_schema_version'  #Could just always be 1 but support for dynamic + easy update

    print (" ----- BEGIN PROMPT ENGINEERING + EXECUTION CYCLES")

    LLM={}
    print ("- easy injectible prompt stuffs")
    print ("PROMPT EXECUTION IS DYNAMIC CYCLE and prompt may be entirely rewritten")

    print ("[ ] JON:  add all_transactions to sample to highlight how now incomplete list")

    records_updated={}
    output_misc={}

    print ("Push update records (including known schema) to cypher -- ideally write concrete for now cause prone to errors")

    return


if __name__=='__main__':
    branches=['dev1']
    branches=['dev2_higher_layer']
    for b in branches:
        globals()[b]()

"""
"""
