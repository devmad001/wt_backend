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

from support_gold import local_process_case_remove_first
from support_gold import local_page2transaction
from support_gold import local_firstpage2fields
from support_gold import local_transaction_type_on_subgraph

from support_gold import url2testcase
from support_gold import case_id2text

from gold_test_configs import load_all_test_cases

from get_logger import setup_logging
logging=setup_logging()



#0v1# JC  Jan 18, 2023  Setup



"""
    GOLD FUNCTIONAL TESTS
    **see doc on emergent exceptions to closing the loop on functional tests

    - existing features
    - extending features
    - new features
    - tweaking features

TEST ARCHITECTURE:
- gold_test_configs.py for narrow focused tests
- stand_alone_functional_tests.py for broader functional tests and PENDING INTEGRATION (think funnel of brining in test frameworks)
[ ] need to formalize source data for test cases into directory structure (you have, need more
)
"""



def local_run_alg_on_test_case(tt):
    # (migrated from functional_test_page2transactions.py)) 
    
    ## Generic test prep
    #> url2testcase (mostly for page2transactions)
    #[ ] optionally move to page2t below
    if 'url' in tt['meta']:
        tt=url2testcase(tt)
        

    ## Run alg on test case
    test_results={}
    test_results['targets_found']=False
    test_results['notargets_found']=False
    

    ######################################
    #  page2transactions function test
    ######################################
    if tt['alg']=='page2transactions':
        ## Pre-check (again)
        if not 'full_path' in tt['meta']:
            raise Exception("No full_path in test case: "+str(tt))
        
        if not os.path.exists(tt['meta']['full_path']):
            raise Exception("File not found: "+str(tt['meta']['full_path']))

        transactions,meta=local_page2transaction(tt['meta']['full_path'],page_number=tt['meta'].get('page_number',1))
        
        ## Evaluate alg results vs expected tests
        for tr in transactions.get('all_transactions',[]):
        
            if tt['TARGET']:
                ## Assume single target amount to find
                if float(tr.get('transaction_amount',0))==float(tt['TARGET']['amount']): #12.0 sometimes
                    test_results['targets_found']=True

            ## Assume single target amount to NOT find
            if tt['NOTARGET']:
                if float(tr.get('transaction_amount',0))==float(tt['NOTARGET']['amount']):
                    test_results['notargets_found']=True

    ######################################
    #  firstpage2fields
    ######################################
    #- opening/closing balances.  User account, bank, dates, etc.
    elif tt['alg']=='firstpage2fields':
        ## Prepare for run
        page_text=case_id2text(tt['meta']['case_id'],tt['meta']['page'])
        fields_group=local_firstpage2fields(page_text)
        fields=fields_group[0]
        
        ### Evaluate results vs expected
        good_tests=0
        expected_good_tests=len(tt['TARGET'])

        test_results['targets_found']=False
        for target_field in tt['TARGET']:
            if target_field in fields:
                if fields[target_field]==tt['TARGET'][target_field]:
                    good_tests+=1
        if good_tests==expected_good_tests:
            test_results['targets_found']=True
        else:
            print ("[debug] bad results: "+str(fields))

    ######################################
    #  KB markup transaction_type
    ######################################
    #- expects subgraph or auto create if not found.
    elif tt['alg']=='kb_transaction_type':
        #> markup_goals=transaction_type_method_goals
        #> see: schema_transaction_type_method.py for tips on crafting prompt
        #> call_kbai
        ASSUME_SUBGRAPH=True
        
        if not ASSUME_SUBGRAPH:
            from gold_kb_test_cases import interface_create_test_transaction_subgraph
            interface_create_test_transaction_subgraph(tt['meta']['case_id'],tt['meta']['page_number'])

        ##> call standard function inteface
        # #[ ] check on response?? 
        results=local_transaction_type_on_subgraph(tt['meta']['case_id'])

#d2        print ("TEST RESULTS: "+str(test_results))
        
        ## Evaluate
        #>> expect ANDTEST_amount_type
        outputs=results[0][0]['output']['markup_output']
        if not 'ANDTEST_amount_type' in tt:
            raise Exception("No ANDTEST_amount_type in test case: "+str(tt))
        
        found=False
        for record in outputs:
            if record['transaction_amount']==tt['ANDTEST_amount_type'][0]:
                if record['transaction_type']==tt['ANDTEST_amount_type'][1]:
                    found=True
        # Validate
        if not found:
            print ("[debug] bad results expect: "+str(tt['ANDTEST_amount_type']))
            raise Exception("Test failed")

    else:
        raise Exception("Unknown alg: "+str(tt['alg']))
            
            
    ## Store results & alert results
    if tt['TARGET']:
        if test_results['targets_found']:
            logging.info("Test passed")
        else:
            logging.info("Test failed (target not found)")
            raise Exception("Test failed (target not found)")
    
    if tt['NOTARGET']:
        if not test_results['notargets_found']:
            logging.info("Test passed")
        else:
            logging.info("Test failed -- because no-targets found")
            raise Exception("Test failed -- because no-targets found!")

    return test_results



def run_existing_function_tests():
    ## > functionaLtest_page2transactions.py
    
    if 't1' in []:
        print ("> test p2t with no summary pulling")
        from pending_integration.functional_test_page2transactions import t1
        t1()
        
    from d_tweaks.tweak_developments import dev_jan15
    
    print ("New test setup...")
    dev_jan15()

    return


def load_test_suite(groups=[]):

    #name='boa_wire_transfers_odd'
    #tts=load_all_test_cases(name=name)
    
    ## Test suite and method
    tts=load_all_test_cases()

    return tts

def run_functional_tests():

    tts=load_test_suite()
    for tt in tts:
        print ("Running test case: "+str(tt['name']))
        print("test dict: "+str(tt))
        local_run_alg_on_test_case(tt)
        
    print ("[ ] register_run_test_scripts")
    from stand_alone_functional_tests import register_run_test_scripts
    register_run_test_scripts()

    return

def run_specific_functional_tests():
    name='marners_check_big_deposit'  #gpt-4 could take a while?!
    name='PJ_opening_balance'
    name='chase_3_page_consolidated'
    name='newage_check_check_not_total'
    name='check withdrawl flagged as deposit'
    name='skyview_checks_included'
    name='schoolkiz_checks_missing_bad_transaction_count'
    
    tts=load_all_test_cases(name=name)
    for tt in tts:
        if name==tt['name']:
            print ("Running test case:")
            print("test dict: "+str(tt))
            local_run_alg_on_test_case(tt)

    return




if __name__=='__main__':
    branches=['run_functional_tests']
    branches=['run_specific_functional_tests']

    for b in branches:
        globals()[b]()





