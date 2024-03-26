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

from a_query.cypher_helper import cypher_create_update_node
from a_query.cypher_helper import cypher_create_relationship

from get_logger import setup_logging
logging=setup_logging()

from schemas.SCHEMA_kbai import gold_schema_definition


#0v1# JC  Oct 18, 2023  Init


"""
    SIMILAR TO Applying logic
    - apply to existing KB (on already processed record)
    - see do_llm_markup for sample fow (esp on version tracking) 
    
    - see markup_alg_cypher
    - this routine can work on entire grpah OR a case_id
"""


def alg_is_valid_account_number(account_number):
    ## Manual algs for adjustements and post processing
    #(i) if account_number looks like:  '11756070502000000065'
    is_valid=True
    if account_number is None:
        is_valid=False
    elif len(account_number)==20:
        is_valid=False
    return is_valid


if __name__=='__main__':
    branches=['dev1']

    for b in branches:
        globals()[b]()





