import os
import sys
import codecs
import json
import re

from fastapi import FastAPI

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")

sys.path.insert(0,LOCAL_PATH+"../..")

from c_macros.fixed_queries.fixed_query_transaction_tracker import FIXED_query_transaction_tracker

from get_logger import setup_logging
logging=setup_logging()


        
#0v1#  JC  Jan 23, 2023  Setup



"""
    GENERAL SERVICES
    FIXED QUERIES
    - "canned" queries or services that are not user-specific
    
    FIXED_query_transaction_tracker:
    - Given case_id, return high-level counts like #transactions, #wires, etc.
    
    
"""



async def FIXED_transaction_tracker(case_id='',expires=1*60*60):
    results,meta=FIXED_query_transaction_tracker(case_id=case_id,expires=expires)    
    return results


def dev1():
    return


if __name__=='__main__':
    branches=['dev1']
    for b in branches:
        globals()[b]()


"""
"""