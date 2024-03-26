import os
import sys
import codecs
import json
import re

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")

from pypher import __, Pypher
from w_storage.gstorage.gneo4j import Neo

from get_logger import setup_logging
logging=setup_logging()


#0v1# JC  Oct 13, 2023  Init
#0v1# JC  Oct 11, 2023  Init


"""
   **NOTES ONLY
    QA REPORT
    - how many transactions?
    - total amounts?
    - anything missing?
    - ? tie into runtime estimation?
    
    OTHER THOUGHTS
    print ("[QA REPORT FOR ONE CASE]")
    print ("a)  General stats")
    print ("b)  Check for obvious/common errors")
    print ("c)  Q50 score (how well did it do?)")
    
    
"""



def run_qa_report(case_id):
    #* mostly queries exist
    report=[]

    return

def count_transactions():
    stmt="""
        MATCH (n:Transaction {case_id: '""" + str(case_id) + """'})
        RETURN
            count(n) as count
    """
    return

def check_missing_transaction_amounts():
    stmt="""
        MATCH (n:Transaction {case_id: '""" + str(case_id) + """'})
        RETURN
            n.transaction_date as date,
            n.transaction_amount as amount,
            n.transaction_description as description
        ORDER BY n.transaction_date ASC
    """
    return

def list_ongoing_challenges():
    challenges=[]
    challenges+=['runtime?']
    return


def dev_call_run_qa_report():
    case_id='case_atm_location'
    run_qa_report(case_id)

    return


if __name__=='__main__':
    branches=['run_qa_report']
    for b in branches:
        globals()[b]()


"""
"""
