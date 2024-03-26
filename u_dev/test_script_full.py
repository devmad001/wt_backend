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
from a_query.queryset1 import query_transaction_relations
from a_query.admin_query import admin_remove_case_from_kb

from get_logger import setup_logging
logging=setup_logging()


#0v2# JC  Feb  2, 2024  Migrate to gold test configs [ ] stand_alone_functional_tests.py

#0v1# JC  Oct 10, 2023  Init


"""
    FUNCTIONAL TEST SCRIPT

"""

HARD_TESTS={}

def local_test_a_run():
    ## Get original test parameters
    case_id='case_atm_location'

    b=['run_logic']

    b=['query_logic']
    b+=['test_logic']
    
    if 'run_logic' in b:
        ### NARROW RUN CAPABILITY:: Specific page in KB_AI only
        options={}
        manual_skip_caps=[]
    
        options['only_pages']=[2]
        manual_skip_caps=['start_main_processing_pipeline']
        meta=wt_main_pipeline(case_id=case_id,options=options,manual_skip_caps=manual_skip_caps)
    
    ### CHECK EXPECTED
    #- look at pdf and query transaction
    if 'query_logic' in b:
        for tt in query_transactions(case_id=case_id):
            
            ## Narrow
            
            if '51a8b2a41fdf4f9591c82a538d4f9bf52b1ec3926d11e8c541de60ea8798e13f'==tt['id']:
                ## Same transaction as below
                #[ ] check that transaction has Account receiver as cash!

                print ("transaction> "+str(tt))
                c=0
                for rr in query_transaction_relations(transaction_id=tt['id']):
                    if 'BankStatement' in str(rr): continue
                    if 'PROCESSED_BY' in str(rr): continue
                    c+=1
                    print ("rel #"+str(c)+" "+str(rr))

                okk=kkk

            if False or 'Canyon' in str(tt):
                print ("transaction> "+str(tt))
                c=0
                for rr in query_transaction_relations(transaction_id=tt['id']):
                    if 'BankStatement' in str(rr): continue
                    c+=1
                    print ("rel #"+str(c)+" "+str(rr))

        pass
    return


#mv m_formals#def test_atm_withdrawl_cash_location():
#mv m_formals#    global HARD_TESTS
#mv m_formals#    #[ ] actually a functional test so link to overall test entrypoints
#mv m_formals#
#mv m_formals#    ## Look at PROCESSED_BY
#mv m_formals#    ## How to re-run specific narrow branch
#mv m_formals#    # [ document this]
#mv m_formals#    #? um, part of call_kb -> cypher_markups -> markup_alg_cypher_PROCESED_BY
#mv m_formals#
#mv m_formals#    from kb_ai.cypher_markups.markup_alg_cypher_PROCESSED_BY import dev_interface_do_processed_by
#mv m_formals#    
#mv m_formals#    transaction=HARD_TESTS['test_atm_withdrawl_cash_location']['transaction']
#mv m_formals#    
#mv m_formals#    case_id=transaction['case_id']
#mv m_formals#    
#mv m_formals#    meta=dev_interface_do_processed_by(transaction,case_id)
#mv m_formals#    
#mv m_formals#    print ("[debug] meta: "+str(meta))
#mv m_formals#    
#mv m_formals#    # 34.18 <-- longitude of a processor
#mv m_formals#    found_processor_location=False
#mv m_formals#    for processor in meta.get('log_processors',[]):
#mv m_formals#        print ("RAW: "+str(processor))
#mv m_formals#        if '34.18' in str(processor):
#mv m_formals#            found_processor_location=True
#mv m_formals#            break
#mv m_formals#
#mv m_formals#    if not found_processor_location:
#mv m_formals#        raise Exception("test_atm_withdrawl_cash_location:  failed to find processor location")
#mv m_formals#    return



def test_atm_withdrawl_cash_account():
    global HARD_TESTS
    ## Look at cash is the target receiver account!
    
    # withdrawl: **below sample
    # 08/24 ATM Withdrawal 08/24 6400 Laurel Canyon B North Hollywo CA Card 7413 700.00

    ###? Easy import run specific KB_AI branch

    transaction=HARD_TESTS['test_atm_withdrawl_cash_location']['transaction']
    case_id=transaction['case_id']

    from kb_ai.call_kbai import dev_interface_call_kb_auto_update
    from kb_ai.call_kbai import get_algs_to_apply
    
    #> see: call_kbai -> get_algs_to_apply 
    algs_to_apply=['add_sender_receiver_nodes']
    
    dev_interface_call_kb_auto_update(case_id,algs_to_apply=algs_to_apply,force_update_all=True)

    print ("Expect to see withdrawl from atm $700 to cash")

    return




#test={}
#test['test_comment']='Expect longitude location 34.18 in this Processor node'
#test['transaction']={'filename_page_num': 2, 'transaction_date': '2021-08-24', 'account_number': '000000651770569', 'transaction_amount': 700.0, 'section': 'ATM & Debit Card Withdrawals', 'transaction_method': 'atm', 'statement_id': 'case_atm_location-2021-07-31-000000651770569-07A210E6-B60D-46B6-9D40-9B3239237F05-list.pdf', 'label': 'Transaction', 'transaction_type': 'withdrawal', 'transaction_description': 'ATM Withdrawal | August 24, 2021 | 6400 Laurel Canyon B North Hollywo CA | Card 7413 | $700.00', 'account_id': 'case_atm_location-000000651770569', 'filename': '07A210E6-B60D-46B6-9D40-9B3239237F05-list.pdf', 'case_id': 'case_atm_location', 'versions_metadata': '{"transaction_type": "llm_markup-transaction_type_method_goals-", "transaction_method_id": "llm_markup-transaction_type_method_goals-", "transaction_method": "llm_markup-transaction_type_method_goals-"}', 'id': '51a8b2a41fdf4f9591c82a538d4f9bf52b1ec3926d11e8c541de60ea8798e13f', 'transaction_method_id': 'unknown'}
#HARD_TESTS['test_atm_withdrawl_cash_location']=test
#

def dev1():
    ## branch:  [dict to output check]
    ## branch:  [query id to output check]
    test_atm_withdrawl_cash_location()
    return



if __name__=='__main__':
    branches=['dev1']
    branches=['local_test_a_run']
    branches=['test_atm_withdrawl_cash_account']
    branches=['test_atm_withdrawl_cash_location'] #[ ] real test

    for b in branches:
        globals()[b]()




"""
JON test single lookup for accounts schema
- if withdrawl and atm then give cash example
>>

SINGLE TRANSACTION:
{'filename_page_num': 2, 'transaction_date': '2021-08-24', 'account_number': '000000651770569', 'transaction_amount': 700.0, 'section': 'ATM & Debit Card Withdrawals', 'transaction_method': 'atm', 'statement_id': 'case_atm_location-2021-07-31-000000651770569-07A210E6-B60D-46B6-9D40-9B3239237F05-list.pdf', 'label': 'Transaction', 'transaction_type': 'withdrawal', 'transaction_description': 'ATM Withdrawal | August 24, 2021 | 6400 Laurel Canyon B North Hollywo CA | Card 7413 | $700.00', 'account_id': 'case_atm_location-000000651770569', 'filename': '07A210E6-B60D-46B6-9D40-9B3239237F05-list.pdf', 'case_id': 'case_atm_location', 'versions_metadata': '{"transaction_type": "llm_markup-transaction_type_method_goals-", "transaction_method_id": "llm_markup-transaction_type_method_goals-", "transaction_method": "llm_markup-transaction_type_method_goals-"}', 'transaction_method_id': 'unknown', 'id': '51a8b2a41fdf4f9591c82a538d4f9bf52b1ec3926d11e8c541de60ea8798e13f', 'sender_entity_type': 'individual', 'sender_entity_id': 'Card 7413', 'sender_entity_name': '6400 Laurel Canyon B North Hollywo CA', 'receiver_entity_type': 'main_account', 'receiver_entity_id': '', 'receiver_entity_name': ''}

^^^ receiver is??
"""
