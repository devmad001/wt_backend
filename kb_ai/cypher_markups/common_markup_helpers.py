import os
import sys
import codecs
import copy
import json
import re
import threading  #future multi

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")
sys.path.insert(0,LOCAL_PATH+"../../")

from w_utils import util_get_modified_keys
from w_storage.gstorage.gneo4j import Neo

from get_logger import setup_logging
logging=setup_logging()

from schemas.SCHEMA_kbai import gold_schema_definition


#0v1# JC  Oct 18, 2023  Init


"""
    MIGRATE FROM markup PROCESSED_BY/ CLEAN into useable funcs
"""


def get_target_records(case_id,markup_goals=[]):
    ## where transaction but no PROCESSED_BY relation
    stmt="""
    MATCH (t:Transaction)
    WHERE NOT EXISTS((t)-[:PROCESSED_BY]->()) AND t.case_id = '"""+case_id+"""'
    RETURN t;
    """
    print ("> get target records: "+str(stmt))
    jsonl,df,tx,meta=Neo.run_stmt_to_normalized(stmt,tx='')
    return jsonl


def dev1():
    return

if __name__=='__main__':
    branches=['dev1']
    for b in branches:
        globals()[b]()

    print ("[ ] checklist:  changes should be reflected in expected schema")
    print ("[ ] checklist:  changes should have tests + clear metrics")
