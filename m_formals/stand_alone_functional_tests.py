import os
import sys
import codecs
import json
import re
import time
import requests

import configparser as ConfigParser


LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")
sys.path.insert(0,LOCAL_PATH+"../../")

from get_logger import setup_logging
logging=setup_logging()




#0v1# JC  Feb  2, 2023  Setup


#### TODO:
#> bring in more u_dev/test_script_full.py
#> expose the test capability to generic test cases
#> integreate into full test stack


"""
    STAND-ALONE FUNCTIONAL TESTS
    STEP 1:  migrate from codebase to centraly here.
    STEP 2:  make as generic interface for flexible test cases

NOTES:
- test_atm-withdrawl_cash_location via u_dev/test_script_full.py

"""

"""
CAPABILITIES:
    
    PROCESSED_BY & location:
        from kb_ai.cypher_markups.markup_alg_cypher_PROCESSED_BY import dev_interface_do_processed_by

    ADD SENDER RECEIVER NODES
        - see test_script_full [ ]


"""

def load_test_transaction():
    HARD_TESTS={}
    test={}
    test['test_comment']='Expect longitude location 34.18 in this Processor node'
    test['transaction']={'filename_page_num': 2, 'transaction_date': '2021-08-24', 'account_number': '000000651770569', 'transaction_amount': 700.0, 'section': 'ATM & Debit Card Withdrawals', 'transaction_method': 'atm', 'statement_id': 'case_atm_location-2021-07-31-000000651770569-07A210E6-B60D-46B6-9D40-9B3239237F05-list.pdf', 'label': 'Transaction', 'transaction_type': 'withdrawal', 'transaction_description': 'ATM Withdrawal | August 24, 2021 | 6400 Laurel Canyon B North Hollywo CA | Card 7413 | $700.00', 'account_id': 'case_atm_location-000000651770569', 'filename': '07A210E6-B60D-46B6-9D40-9B3239237F05-list.pdf', 'case_id': 'case_atm_location', 'versions_metadata': '{"transaction_type": "llm_markup-transaction_type_method_goals-", "transaction_method_id": "llm_markup-transaction_type_method_goals-", "transaction_method": "llm_markup-transaction_type_method_goals-"}', 'id': '51a8b2a41fdf4f9591c82a538d4f9bf52b1ec3926d11e8c541de60ea8798e13f', 'transaction_method_id': 'unknown'}
    HARD_TESTS['test_atm_withdrawl_cash_location']=test
    return HARD_TESTS
 

def test_atm_withdrawl_cash_location(HARD_TESTS):
    #[ ] actually a functional test so link to overall test entrypoints

    ## Look at PROCESSED_BY
    ## How to re-run specific narrow branch
    # [ document this]
    #? um, part of call_kb -> cypher_markups -> markup_alg_cypher_PROCESED_BY

    from kb_ai.cypher_markups.markup_alg_cypher_PROCESSED_BY import dev_interface_do_processed_by
    
    transaction=HARD_TESTS['test_atm_withdrawl_cash_location']['transaction']
    
    case_id=transaction['case_id']
    
    meta=dev_interface_do_processed_by(transaction,case_id,commit=False)
    
    print ("[debug] meta: "+str(meta))
    
    # 34.18 <-- longitude of a processor
    found_processor_location=False
    for processor in meta.get('log_processors',[]):
        print ("RAW: "+str(processor))
        if '34.18' in str(processor):
            found_processor_location=True
            break

    if not found_processor_location:
        raise Exception("test_atm_withdrawl_cash_location:  failed to find processor location")
    return



def test_atm_withdrawl_cash_account(HARD_TESTS):
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
    
    dev_interface_call_kb_auto_update(case_id,algs_to_apply=algs_to_apply,force_update_all=True,commit=False,force_thread_count=1)

    print ("Expect to see withdrawl from atm $700 to cash")

    return

def TOINTEGRATE_test_ask_question():
    #[ ] via dev_50q
    b=[]
    
    if 'do_questions' in b:
        Bot=Bot_Interface()
        Bot.set_case_id(case_id)
        
        #q50+=["What is the beginning monthly balance?"]
        question="What is the beginning monthly balance and date?"
        local_ask_question(question,Bot)

    """
        answer,answer_dict=Bot.handle_bot_query(question)
    print ("[answer]: ",answer_dict)
    #  fp.write(df.to_string(index=False))
    if 'df' in answer_dict:
        print(answer_dict['df'].to_string(index=False))
        
    print ("[cypher]: "+str(answer_dict.get('cypher','')))
    print ("[asking]: ",question)
    print ("[answer]: ",answer)

    """

    return


###################################
#  KB MARKUP TEMPLATE FOR TESTS
###################################
def local_run_specific_page(case_id,page_ids,force_algs_to_apply=['add_sender_receiver_nodes']):
    ## Call direct kb_auto_update with forced algs to apply:
    from kb_ai.call_kbai import interface_call_kb_auto_update
    interface_call_kb_auto_update(case_id,force_update_all=True,force_algs_to_apply=force_algs_to_apply)
    return
    
def TEMPLATE_apply_various_alg_tests():
    #[ ] from dev_50q

    if False:
        page_ids=[2]
        page_ids=[]
        force_algs_to_apply=['logical_card_check_numbers']
        force_algs_to_apply=['transaction_type_method']

        ALL_ALGS_TO_APPLY=[]
        ALL_ALGS_TO_APPLY+=['transaction_type_method']
        ALL_ALGS_TO_APPLY+=['add_sender_receiver_nodes']
        ALL_ALGS_TO_APPLY+=['logical_card_check_numbers']
        ALL_ALGS_TO_APPLY+=['add_PROCESSED_BY']
        force_algs_to_apply=ALL_ALGS_TO_APPLY

        force_algs_to_apply=['transaction_type_method']

## REDO SEND/RECEIVE
#ok        print ("REMOVING ENTITIES AND ADDING THEM BACK IN!!!")
#ok        force_algs_to_apply=['add_sender_receiver_nodes']
#ok        admin_remove_entity_nodes(case_id=case_id)

        local_run_specific_page(case_id,page_ids=page_ids,force_algs_to_apply=force_algs_to_apply)
    return


def register_run_test_scripts():
    b=[]
    b+=['test_processed_by_location']
    b=['test_atm_withdrawl_cash_account']


    if 'test_processed_by_location' in b:
        HARD_TESTS=load_test_transaction()
        test_atm_withdrawl_cash_location(HARD_TESTS)
        
    if 'test_atm_withdrawl_cash_account' in b:
        HARD_TESTS=load_test_transaction()
        test_atm_withdrawl_cash_account(HARD_TESTS)
    
    return


def dev_test_calls():
    case_id='case_atm_location'
    print ("Run transaction type classifier on case: "+case_id)
    force_algs_to_apply=['transaction_type_method']
    commit=False
#    page_ids=[2]

    from kb_ai.call_kbai import interface_call_kb_auto_update
    interface_call_kb_auto_update(case_id,force_update_all=True,force_algs_to_apply=force_algs_to_apply,commit=commit,force_thread_count=1)

    return



if __name__=='__main__':

    branches=['register_run_test_scripts']
    branches=['dev_test_calls']

    for b in branches:
        globals()[b]()











