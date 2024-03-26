import os
import sys
import time
import codecs
import json
import re

from datetime import datetime


LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"

sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")
sys.path.insert(0,LOCAL_PATH+"../../")

from w_storage.ystorage.ystorage_handler import Storage_Helper

from w_storage.gstorage.gneo4j import Neo
from z_apiengine.services.alg_generate_pdf_hyperlink import alg_generate_transaction_hyperlink

from fixed_helper import local_query2jsonl
from fixed_helper import load_response_from_cache
from fixed_helper import add_response_to_cache

from fixed_query_transactions import interface_preload_cache_transactions

from fixed_definitions import COMPUTE_is_wire, COMPUTE_is_check_paid
        
from get_logger import setup_logging
logging=setup_logging()


#0v1# Jan 22, 2024


"""
    FIXED QUERY:  Transaction Tracker
    - expiry? cache?

    items+=['Total Transactions Counted']
    items+=['Deposits / Additions']
    items+=['Withdrawals']
    items+=['Checks Paid']
    items+=['Wires']

    NOTES:
    - see also case-level report
"""


def FIXED_query_transaction_tracker(case_id='',tts=[],expires=1*60*60):
    ## Query direct cypher or calculation, as defined?
    #; tts possible when testing
    
    meta={}
    start_time=time.time()

    ### LOAD DATA
    if not tts:
       tts,meta=interface_preload_cache_transactions(case_id=case_id,kind='standard',expires=expires)
    
    ## Define items
    items=[]
    items+=['Total Transactions Counted']
    # Count of all credits
    items+=['Deposits / Additions']
    # Count of all debits
    items+=['Withdrawals']
    # Count where check?
    #/ check_num? / mentions check?
    items+=['Checks Paid']
    # Count where wire?
    items+=['Wires']
    #/ mentions 'Wire'? transaction_type?  transaction_method=''

    ## SETUP DICT
    results={}
    results['count_transactions_total']=0
    results['count_deposits']=0
    results['count_withdrawls']=0
    results['count_checks_paid']=0
    results['count_wires']=0


    if tts:
         
        #items+=['Total Transactions Counted']
        results['count_transactions_total']=len(tts)
        
        ## LOCAL ITERATE
        for id in tts:
            tt=tts[id]
            if not 'is_credit' in tt:
#D1                [ ] TODO (added to list)
#D1                print ("NO CREDIT: "+str(tt))
#D1   #             raise Exception("NO CREDIT")
                continue
                
            if tt['is_credit']:
                results['count_deposits']+=1
            else:
                results['count_withdrawls']+=1
                
            results['count_checks_paid']+=COMPUTE_is_check_paid(tt)
            
            results['count_wires']+=COMPUTE_is_wire(tt)

    meta['runtime']=time.time()-start_time
    return results,meta




def dev_call_do_transaction_tracker():
    case_id='65a8168eb3ac164610ea5bc2' ## Big new age
    results,meta=FIXED_query_transaction_tracker(case_id=case_id)
    print ("Transaction Tracker Results:")
    print (results)
    print ("Transaction Tracker Meta:")
    print (meta)
    
    return



if __name__=='__main__':
    branches=['dev_tracker_query']
    branches=['dev_call_do_transaction_tracker']

    for b in branches:
        globals()[b]()
    
    
    
"""
transaction_methods by count:
1679

379 Other

206 Credit_Card

108 Online_Payment

79 Check

54 Debit_Card

10 Wire_Transfer

5 Book_Transfer

3 Zelle

2 Unknown

1 Cash

"""


"""
 [{'id': 'ec7dc18580087519dbce4e665f11e405bc88919aa2ede1f137389979421ace5b', 'is_credit': True, 'transaction_date': '2020-11-02', 'filename_page_num': 2, 'account_number': '334049185630', 'is_cash_involved': True, 'transaction_amount': 245.75, 'section': 'Cash transactions', 'transaction_method': 'other', 'label': 'Transaction', 'statement_id': '65a8168eb3ac164610ea5bc2-2020-11-01-334049185630-72d85b81-c416-4ffd-950c-f0c1fd62f251.pdf', 'transaction_type': 'deposit', 'transaction_description': 'MERCHANT BNKCD DES:DEPOSIT ID:323242463996 INDN:PLANET SMOOTHIE 19109 CO', 'algList': ['create_ERS'], 'account_id': '65a8168eb3ac164610ea5bc2-334049185630', 'filename': '72d85b81-c416-4ffd-950c-f0c1fd62f251.pdf', 'case_id': '65a8168eb3ac164610ea5bc2', 'versions_metadata': '{"transaction_method_id": "llm_markup-transaction_type_method_goals-", "transaction_type": "llm_markup-transaction_type_method_goals-", "is_cash_involved": "llm_markup-transaction_type_method_goals-", "transaction_method": "llm_markup-transaction_type_method_goals-"}', 'transaction_method_id': '323242463996', 'hyperlink_url': 'http://127.0.0.1:8008/api/v1/case/65a8168eb3ac164610ea5bc2/pdf/72d85b81-c416-4ffd-950c-f0c1fd62f251.pdf?page=2&key=d5c891217c4bb3f96f0b4e0fd2b2dc8568bc8a7b952e234f861ede8ab9035acb&highlight=245.75|ID%3A323242463996|INDN%3APLANET|DES%3ADEPOSIT'}]

 """






