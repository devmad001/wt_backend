import os
import sys
import time
import codecs
import json
import re

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")

from pypher import __, Pypher
from w_storage.gstorage.gneo4j import Neo

from a_agent.RUN_sim_wt import call_normal_full_run
from a_agent.sim_wt import wt_main_pipeline

from a_query.queryset1 import query_statements
from a_query.queryset1 import query_transaction
from a_query.queryset1 import query_transactions
from a_query.admin_query import admin_remove_case_from_kb

from get_logger import setup_logging
logging=setup_logging()


#0v1# JC  Oct  7, 2023  Init



"""
    JON DEV SPECIFIC CHALLANGES
    
    jon_accounts:
    - validate MainAccount account behaviour
    - validate PhysicalCash account behaviour
    
    - schema sync + enforced validation ie/ tests etc.
    - other top-level nodes?  Or watch entity vs account handling
    
    CLEAR DISTINCTION YES.
    what about bank as facilitator of transaction?
    - transfer methods: zelle, wire, check, cash, atm, etc.
    - transfer types: deposit, withdraw, transfer, etc.
    
    SourceEntity: ____
    SourceBank: ____
    DestinationBank
    DestinationEntity..
    
    [PROCESSED_BY]
    
    BE CONSISTENT IN WHERE TO FIND DATA.
    ??     [:ORIGINATED_FROM] -> SourceBank AAA
    ?? vs: Transaction.source_bank=AAA
    
    JON CONCLUSION
    - should be consistent but if duplicate data then also fine because don't have to tell the queryer.
    
    - [ PROCESSED_BY ] at the transfer method type since want info.
    - ?Handling of main account and cash account since they need to be forced entitites not assumed from just looking at transaction info
    
    FOLLOW ON ACCOUNT TYPES (yes probably)
    - loan account, credit card accounts, debit card 'entity'
    

"""

"""
TASK:
    > audit validate current schema additions match gold including examples and possible real data audit. ie/ do it. audit data.
     ^^ possibly as part of insert is immediate query and check (can turn off level 2 running later.)
    
"""


def dev1():
    print ("[ ] audit current schema + management including possible immediate query of what is inserted")
    print ("[ ] Sort out main account and cash account handling")
    print ("[ ] [PROCESSED_BY] relation  (but recall keeping simple is good")

    return

    
def dev_schema_check():
    print ("> dev_challenges for full run or page only...")
    
    case_id='demo_a'
    case_id='case_o1_case_single'
    case_id='case_atm_location'
    
    b=['main then kb','all']
    b=['all']

    if 'all' in b:
#        admin_remove_case_from_kb(case_id=case_id)

        options={}
        manual_skip_caps=[]
        meta=wt_main_pipeline(case_id=case_id,options=options)

    elif 'main then kb' in b:
#        admin_remove_case_from_kb(case_id=case_id)

        ## MAIN
        manual_skip_caps=['start_KBAI_processing_pipeline']
        options={}
        meta=wt_main_pipeline(case_id=case_id,options=options,manual_skip_caps=manual_skip_caps)
    
        ## KBA
        options={}
        manual_skip_caps=['start_main_processing_pipeline']
        meta=wt_main_pipeline(case_id=case_id,options=options,manual_skip_caps=manual_skip_caps)

    return


def jon_include_basic_tests_here_to_integrate_or_at_least_notes():
    #q_va
    print ("Recall page to expected")

    manual_skip_caps=['start_main_processing_pipeline']
    options={}
    
    case_id='case_atm_location'
    options['only_pages']=[1]
    options['only_pages']=[2]

    meta=wt_main_pipeline(case_id=case_id,options=options,manual_skip_caps=manual_skip_caps)

    return    


def jon_notices_odds():
    no_location_found_esri="GIVEN CANDIDATE: ATM Withdrawal | August 24, 2021 | 6400 Laurel Canyon B North Hollywo CA | Card 7413 | $700.00"
    return

if __name__=='__main__':
    branches=['dev_schema_check']
    branches=['jon_include_basic_tests_here_to_integrate_or_at_least_notes']

    for b in branches:
        globals()[b]()




"""
"""
