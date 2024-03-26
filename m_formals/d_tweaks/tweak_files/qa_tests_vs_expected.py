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

from kb_ai.schemas.SCHEMA_kbai import gold_schema_definition
from kb_ai.schemas.SCHEMA_graph import GRAPH_SCHEMA, GRAPH_INDEXES #*informally controlled?
from kb_ask.dev_kb_ask import get_graph_schema_str

from a_agent.sim_wt import wt_main_pipeline



from get_logger import setup_logging
logging=setup_logging()

#0v1# JC  Sep 29, 2023  Init


def test_expected():
    ## (case X)||(statement Y) @given page=[3] expect 9 transactions!
    ## Hard code samples for now
    
    b=[]
    b+=['standard']
    b+=['at_464_numbers_needs_gpt4']
    b+=['chase_hidden_transaction_needs_gpt4']
    b+=['dont_split_check_paid_line_item']

    if 'standard' in b:
        ##1/   page2transactions test standard:
        dd={}
        dd['expect_meta_count_transactions']=9
        dd['case_id']='case_schoolkids'
        dd['options']={}
        dd['options']['only_pages']=[3]
        dd['options']['allow_cache']=True
        dd['manual_skip_caps']=['start_KBAI_processing_pipeline']
        meta=wt_main_pipeline(case_id=dd['case_id'],options=dd['options'],manual_skip_caps=dd['manual_skip_caps'])
        if not meta['count_transactions']==dd['expect_meta_count_transactions']:
            print ("[main_pipeline meta]: "+str(meta))
            print ("[challenge meta] transactions touched: "+str(meta.get('count_transactions','')))
            raise Exception("Expected 9 transactions, got "+str(meta['count_transactions']))
    
    if 'at_464_numbers_needs_gpt4' in b:
        ##2/   page2transactions: gpt-4 on large page
        dd={}
        dd['expect_meta_count_transactions']=76
        dd['case_id']='case_schoolkids'
        dd['options']={}
        dd['options']['only_pages']=[10]
        dd['options']['allow_cache']=True
        dd['manual_skip_caps']=['start_KBAI_processing_pipeline']
        meta=wt_main_pipeline(case_id=dd['case_id'],options=dd['options'],manual_skip_caps=dd['manual_skip_caps'])
        if not meta['count_transactions']==dd['expect_meta_count_transactions']:
            print ("[main_pipeline meta]: "+str(meta))
            print ("[challenge meta] transactions touched: "+str(meta.get('count_transactions','')))
            raise Exception("Expected 76 transactions, got "+str(meta['count_transactions']))
    
    if 'chase_hidden_transaction_needs_gpt4' in b:
        ##3/  CHASE 1 hidden transaction by itself in section requires gpt-4 once count expected trans
        dd={}
        dd['expect_meta_count_transactions']=11  #NOT 10!!!
        dd['case_id']='case_o2_case_single'
        dd['options']={}
        dd['options']['only_pages']=[2]
        dd['options']['allow_cache']=True
        dd['manual_skip_caps']=['start_KBAI_processing_pipeline']
        meta=wt_main_pipeline(case_id=dd['case_id'],options=dd['options'],manual_skip_caps=dd['manual_skip_caps'])
        if not meta['count_transactions']==dd['expect_meta_count_transactions']:
            print ("[main_pipeline meta]: "+str(meta))
            print ("[challenge meta] transactions touched: "+str(meta.get('count_transactions','')))
            raise Exception("Expected 11 transactions, got "+str(meta['count_transactions']))
        
    ## Case test don't split Checks Paid on line item
    if 'dont_split_check_paid_line_item' in b:
        dd={}
        dd['expect_meta_count_transactions']=3  #NOT 10!!!
        dd['case_id']='case_o2_case_single'
        dd['options']={}
        dd['options']['only_pages']=[1]
        dd['options']['allow_cache']=True
        dd['manual_skip_caps']=['start_KBAI_processing_pipeline']
        meta=wt_main_pipeline(case_id=dd['case_id'],options=dd['options'],manual_skip_caps=dd['manual_skip_caps'])
        if not meta['count_transactions']==dd['expect_meta_count_transactions']:
            print ("[main_pipeline meta]: "+str(meta))
            print ("[challenge meta] transactions touched: "+str(meta.get('count_transactions','')))
            raise Exception("Expected 11 transactions, got "+str(meta['count_transactions']))


    logging.info("Done test expected...passed!")
    return

if __name__=='__main__':
    branches=['dev1']
    branches=['check_graph_schema']
    branches=['test_expected']

    for b in branches:
        globals()[b]()
