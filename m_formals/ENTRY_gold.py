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
from support_gold import local_pdf2doc
from support_gold import local_is_transaction_credit

from support_gold import url2testcase
from support_gold import case_id2text

from gold_test_configs import load_all_test_cases

from get_logger import setup_logging
logging=setup_logging()



#0v2# JC  Mar 15, 2024  Add is_credit test
#0v1# JC  Jan 18, 2024  Setup



"""
**these tests are precursor to dynamic auditing

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


## FOLDERS  (keep within repo -- so can do git pull and have all files)
config_filename=LOCAL_PATH+"../w_settings.ini"
if not os.path.exists(config_filename):
    raise Exception("Config file not found: "+str(config_filename))

Config = ConfigParser.ConfigParser()
Config.read(config_filename)
BASE_STORAGE_DIR=Config.get('files','base_test_storage_rel_dir')

TARGET_TEST_FOLDER=LOCAL_PATH+BASE_STORAGE_DIR
#TARGET_TEST_FOLDER=LOCAL_PATH+"../CASE_FILES_STORAGE/tests"
SINGLE_TEST_FILE_FOLDER=TARGET_TEST_FOLDER+"/single_pdfs"

if not os.path.exists(TARGET_TEST_FOLDER): os.makedirs(TARGET_TEST_FOLDER)
if not os.path.exists(SINGLE_TEST_FILE_FOLDER): os.makedirs(SINGLE_TEST_FILE_FOLDER)


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
        if 'test_single_path' in tt['meta']:
            full_path=SINGLE_TEST_FILE_FOLDER+"/"+tt['meta']['test_single_path']
            tt['meta']['full_path']=full_path

        ## Pre-check (again)
        if not 'full_path' in tt['meta']:
            raise Exception("No full_path in test case: "+str(tt))
        
        if not os.path.exists(tt['meta']['full_path']):
            raise Exception("File not found: "+str(tt['meta']['full_path']))

        transactions,meta=local_page2transaction(tt['meta']['full_path'],page_number=tt['meta'].get('page_number',1))
        
        ## Evaluate alg results vs expected tests
        if transactions:
            for tr in transactions.get('all_transactions',[]):
            
                if tt['TARGET']:
                    ## AMOUNT target saught:
                    if 'amount' in tt['TARGET']:
                        if float(tr.get('transaction_amount',0))==float(tt['TARGET']['amount']): #12.0 sometimes
                            test_results['targets_found']=True
                    if 'date' in tt['TARGET']:
                        if tr.get('transaction_date','')==tt['TARGET']['date']:
                            test_results['targets_found']=True
    
                ## Assume single target amount to NOT find
                if tt['NOTARGET']:
                    if float(tr.get('transaction_amount',0))==float(tt['NOTARGET']['amount']):
                        test_results['notargets_found']=True
    ######################################
    #  page2transactions2creditdebit function test
    ######################################
    elif tt['alg']=='page2transactions2creditdebit':
        if 'test_single_path' in tt['meta']:
            full_path=SINGLE_TEST_FILE_FOLDER+"/"+tt['meta']['test_single_path']
            tt['meta']['full_path']=full_path
        ## Pre-check (again)
        if not 'full_path' in tt['meta']:
            raise Exception("No full_path in test case: "+str(tt))
        
        if not os.path.exists(tt['meta']['full_path']):
            raise Exception("File not found: "+str(tt['meta']['full_path']))

        transactions,meta=local_page2transaction(tt['meta']['full_path'],page_number=tt['meta'].get('page_number',1))
        
        ## Evaluate alg results vs expected tests
        c=0
        for tr in transactions.get('all_transactions',[]):
            c+=1
            tr['id']=c
            is_credit,tcredit,reasons=local_is_transaction_credit(tr)
            print ("[verbose] credit: "+str(is_credit)+" for : "+str(tr))

            if tt.get('ISDEBIT',''):
                if tr.get('transaction_amount',0)==tt['ISDEBIT']['amount'] and not is_credit:
                    test_results['targets_found']=True
                    print ("** GOOD DEBIT CLASSIFIED: "+str(tr))
            if tt.get('ISCREDIT',''):
                if tr.get('transaction_amount',0)==tt['ISCREDIT']['amount'] and is_credit:
                    test_results['targets_found']=True
                    print ("** GOOD CREDIT CLASSIFIED: "+str(tr))

    ######################################
    #  firstpage2fields
    ######################################
    #- opening/closing balances.  User account, bank, dates, etc.
    elif tt['alg']=='firstpage2fields':
        ## Prepare for run
        page_text=case_id2text(tt['meta']['case_id'],tt['meta']['page'])
        
        ## Run alg
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
            raise Exception("Test failed: "+str(tt))

    ######################################
    #  pdf2txt
    ######################################
    #- ie/ TD or various removes spaces in text -- requires OCR or different pdf2txt library
    elif tt['alg']=='pdf2txt':
        print ("[debug] pdf2txt: [1]  validate filename exists (or source/sync)")
        print ("[debug] pdf2txt: [2]  Load default pdf2txt")
        print ("[debug] pdf2txt: [3]  Run pdf2txt + check output format")
        print ("[debug] pdf2txt: [4]  **hook auto_audit system HERE for dev/validation [ ] draw this!!!! because good approach to integrated auto-audit and resolver")
        print ("[debug] pdf2txt: [5]  Evaluate outputs (use audit plugin logic where possible)")

        from m_autoaudit.audit_plugins.audit_plugins_main import alg_count_joined_words
        from m_autoaudit.audit_plugins.audit_plugins_main import alg_count_comma_period_amounts
                
        ## 1
        full_path=SINGLE_TEST_FILE_FOLDER+"/"+tt['meta']['test_single_path']
        if not os.path.exists(full_path):
            raise Exception("File not found: "+str(full_path))
            
        ## 2+3  Load pdf2txt wrapper similar to above
        #- see support_gold and used in case_id2text as well
        Doc=local_pdf2doc(full_path)
        epages=Doc.get_epages()
         
        # sample page_text grab
        page_text=''
        all_pages=[]
        for page_num in epages:
            #if not (page_num+1)==page_number: continue
            for method in epages[page_num]:
                if not method=='pypdf2_tables': continue
                print ("METHOD: "+str(method))
                page_text=epages[page_num][method]
                all_pages.append(page_text)
        blob=" ".join(all_pages)
        
        ## Audit hook
        #[ ] count occurrences of bad spaces (see audit_plugins setup)
        count_joined,count_words,joined_rate,samples=alg_count_joined_words(blob)
        
        print ("[debug] count_joined: "+str(count_joined)+", joined_rate: "+str(joined_rate)+' count_words : '+str(count_words))
        print ("[bad pdf2txt samples] "+str(samples))
        
        ## Audit hook 2 for amount
        count_bad_amounts=alg_count_comma_period_amounts(blob)
        
        print ("[debug] pdf2txt bad amounts count: "+str(count_bad_amounts))

        
        ## Test evaluation
        #[ ] follow test eval template?
        #if len(samples)>8: #Better for rate
        #    raise Exception("Test failed too many conjoined words: "+str(tt))
        if joined_rate>0.005:
            raise Exception("Test failed too many conjoined words: "+str(tt))
        
    else:
        raise Exception("Unknown alg: "+str(tt['alg'])+" at test: "+str(tt))
            
            
    ## Store results & alert results
    if tt['TARGET']:
        if test_results['targets_found']:
            logging.info("Test passed")
        else:
            logging.info("Test failed (target not found)")
            raise Exception("Test failed (target not found) at test: "+str(tt))
    
    if tt['NOTARGET']:
        if not test_results['notargets_found']:
            logging.info("Test passed")
        else:
            logging.info("Test failed -- because no-targets found")
            raise Exception("Test failed -- because no-targets found! at test: "+str(tt))

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
    ##
    name='marners_check_big_deposit'  #gpt-4 could take a while?!
    name='chase_3_page_consolidated'
    name='newage_check_check_not_total'
    name='check withdrawl flagged as deposit'
    name='skyview_checks_included'

    name='schoolkiz_checks_missing_bad_transaction_count' #Feb 28 fail??
    name='PJ_opening_balance'

    name='boa_wire_transfers_odd'

    name='TD_odd_pdf2txt'
    name='silent_pipe_200_plus' #Large check ocr

    name='year_end_date_roll'
    name='james_bad_debit_credit_on_obvious' #<-- page2t ok
    #2long#  name='james_bad_debit_credit_subgraphmaybe'
    name='blank_page_continues_chat' #No hallucination if direct call
    name='hallucinates_123_main_st'  #3.5 -> 4 fixed
    name='ashford_year_in_advance' #[x] fixed
    name='bad comma period amount'
    name='year is not check num' #
    name='check not debit'   #Fixed on subsequent
    name='bad ocr normal entry'

    name='affinity date'

    name='reversal deposit'


    
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





