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

from support_gold import url2testcase

from get_logger import setup_logging
logging=setup_logging()




#0v1# JC  Jan 18, 2023  Setup



"""
    SPECIFIC TEST DICTS
    - be clear on inputs/targets/outputs

"""




"""
    PAGE TO TRANSACTION TEST CASES
    - use as part of development + register as 'functiona' tests
    
    NOTES:
    - see also functiona_test_page2transactions

"""

def init_basic():
    tt={}
    tt['notes']=[]
    tt['NOTARGET']={}
    tt['TARGET']={}
    tt['meta']={}
    tt['alg']='page2transactions'  #Default but other integrated tests like ocr?
    return tt


def load_all_test_cases(name=''):
    ## Slowly formalize function tests
    print ("** meta is generally the input parameters to the test function")
    tts=[]

    ## BOA beginning balance.
    tt=init_basic()
    tt['name']='BOA beginning balance'
    tt['alg']='page2transactions'
    tt['date']='20240109'
    tt['notes']+=['Fails (Jan 9) -- no transactions just unseen Account Summary']
    tt['NOTARGET']['amount']=64007.17
    tt['meta']['url']='chrome-extension://efaidnbmnnnibpcajpcglclefindmkaj/https://core.epventures.co/api/v1/case/6596f679c8fca0cb7b70e1fb/pdf/b584defb-db9a-42da-b612-f5a5dc9b47c2.pdf?page=74&key=75add40ae552468997b3bf96fa895406a75b8ab0936bfc5eaf6a0bef12a24663&highlight=64007.17|Beginning|balance|July'
    tts+=[tt]
    
    ## misc credit/debit
    tt=init_basic()
    tt['name']='misc credit/debit'
    tt['alg']='page2transactions'
    tt['date']='20240109'
    tt['notes']+=["[ ] need to verify when this fails -- what are the test cases? mis credit/debit or others"]
    tt['meta']['full_path']="C:/scripts-23/watchtower/CASE_FILES_STORAGE/tests/exceptions1/wells_fargo_table_compact_needs_custom_p2t.pdf"
    tt['TARGET']['amount']=36.06   #I believe that's the column had issues
    tt['NOTARGET']['amount']=135963.37 #Daily ending balance
#[ ] add back once generic tests    tts+=[tt]
    
    ## BOA wire transfers
    tt=init_basic()
    tt['name']='boa_wire_transfers_odd'
    tt['alg']='page2transactions'
    tt['date']='20240115'
    tt['notes']+=["all seen as withdrawls but deposits maybe didn't finish?"]
    tt['meta']['url']='https://core.epventures.co/api/v1/case/659457fca348734715059312/pdf/a89f69d2-e8c2-4ebd-babf-29b95f7c4f5b.pdf?page=3&key=f6d1548ebcfd8de636d7c17cb775b17d7e96c9be0bcbd697bb882fb9f1a53f21&highlight=195031.90|SEQ%3A2021120300174912%2F496437|DET%3A52775903712030491046|TRN%3A2021120300491046'
    tts+=[tt]

    ## MARNERS Has amount combined with transaction maybe needs ocr??
    tt=init_basic()
    tt['name']='marners_check_big_deposit'
    tt['alg']='page2transactions'
    tt['date']='20240126'
    tt['notes']+=["check big deposit beside small"]
    tt['meta']['url']="http://127.0.0.1:8008/api/v1/case/MarnerHoldingsB/pdf/2021-06June-statement-0823.pdf?page=3&key=938bf45baae2c97dbd5747808ddd2b8702153ad6261b072d8cdd171c9535b14e&highlight=36,964.36"
    tt['TARGET']['amount']=36964.36 # Marner Holdings Inc Trn: 1650059214Tc36,964.36
    tts+=[tt]
    
    ## PJ plumbers had odd opening balance but seems good now
    #[ ] upgrade to use shared pdf (easier then depending on local file)
    tt=init_basic()
    tt['name']='PJ_opening_balance'
    tt['alg']='firstpage2fields'
    tt['date']='20240129'
    tt['notes']+=["check opening balance but seems mostly good now"]
    tt['meta']['case_id']='case_bank state 2'  #<-- assumes exists on local maching [ ] setup test cases globally
    tt['meta']['page']=1
    tt['TARGET']['opening_balance']=167391.65
    tt['TARGET']['closing_balance']=134397.19
    tts+=[tt]
    
    ## Pickup up 444 in balance?
    # [ ] dealing with consolidated vs checking vs savings
    # [ ] this has all transaction dates as same?
    # [ ] was picking up 444 of balance?
    #[test p2t is correct]
    tt=init_basic()
    tt['name']='chase_3_page_consolidated'
    tt['alg']='page2transactions'
    tt['date']='20240131'
    tt['notes']+=[]
    tt['meta']['url']="https://core.epventures.co/api/v1/case/659ee02b6c33e2599cce68e2/pdf/4f17c252-925a-47a0-b65f-d42324774e75.pdf?page=2&key=cd7b2d32bc0375816ad7493673e8b3ab749304217eb5ffe111d806110f49cb6b&highlight=50000.00|50000.00"
    tt['meta']['case_id']='65a8168eb3ac164610ea5bc2'
    tt['NOTARGET']['amount']=3613.23  # no electronic withdrawal summary!
    
    tts+=[tt]

    ## General coverage with 3.5 to gpt-4 differences
    tt=init_basic()
    tt['name']='newage_check_check_not_total'
    tt['notes']+=['continues to find 10 with gpt 3.5T (expects 15) but finds 15 with gpt-4']
    tt['alg']='page2transactions'
    tt['date']='20240201'
    tt['meta']['case_id']='659ee02b6c33e2599cce68e2'
    tt['meta']['url']="chrome-extension://efaidnbmnnnibpcajpcglclefindmkaj/https://core.epventures.co/api/v1/case/65a8168eb3ac164610ea5bc2/pdf/72d85b81-c416-4ffd-950c-f0c1fd62f251.pdf?page=194&key=d5c891217c4bb3f96f0b4e0fd2b2dc8568bc8a7b952e234f861ede8ab9035acb&highlight=900.00|231545"
    tt['NOTARGET']['amount']=8888.89  #Last total checks not a transaction -- fixed before but ok
    tt['TARGET']['amount']=260.00  #First check missing?  (gpt 3.5T),  passes gpt 4
    tts+=[tt]



    #OK [ ] but may want a different ANDTEST?
    ### KB focused tests
    ## gold_KB_test_cases -> create subgraph for testing
    ## call kb markup via alg
    ###################################################
    #[x] in-dev setup test for KB algorithm (+ test case pdf + test case KB)
    ###################################################
    ## Check withdrawl being flagged as transaction type deposit: (shows up on graph etc.)
    #> assume subgraph exists

    #. run subgraph creation from gold_kb_test_cases import interface_create_test_transaction_subgraph
    # FIX:  schema_transactioN_type_method.py -> only_use_these_fields add sign...
    
    tt=init_basic()
    
    tt['name']='check withdrawl flagged as deposit'
    tt['notes']+=['amount sign is negative on checks']
    tt['alg']='kb_transaction_type'
    tt['date']='20240202'
    tt['meta']['page_number']=194
    tt['meta']['case_id']='test_default_65a8168eb3ac164610ea5bc2_194' #!! PAGE TOO
    tt['ANDTEST_amount_type']=(0.55,'withdrawal') # for kb_transaction_type test kind only
    #    tt['meta']['url']="https://core.epventures.co/api/v1/case/65a8168eb3ac164610ea5bc2/pdf/72d85b81-c416-4ffd-950c-f0c1fd62f251.pdf?page=194&key=d5c891217c4bb3f96f0b4e0fd2b2dc8568bc8a7b952e234f861ede8ab9035acb&highlight=1000.00|235087%2A"
    
    #    tt['TARGET']['amount']=260.00  #First check missing?  (gpt 3.5T),  passes gpt 4
    tts+=[tt]
    

    ## Check missing? [ ] can remove from test cases really but ok
    #er\CASE_FILES_STORAGE\storage\case_December 2021 Skyview Capital Bank Statement
    tt=init_basic()
    tt['name']='skyview_checks_included'
    tt['notes']+=['Case is only on PENT for now']
    tt['alg']='page2transactions'
    tt['date']='20240202'
    tt['meta']['case_id']='case_December 2021 Skyview Capital Bank Statement'
    #** IF NO URL (ie/ local on PENT) must include full path
    tt['meta']['page_number']=8
    tt['meta']['full_path']="C:/scripts-23/watchtower/CASE_FILES_STORAGE/storage/case_December 2021 Skyview Capital Bank Statement/December 2021 Skyview Capital Bank Statement.pdf"
    tt['TARGET']['amount']=2807.42
    tts+=[tt]
    

    ## Checks missing below big section
    #- missed the check section that has header in text:  Check # Bank reference
    #   [ ] so add to schema kinds to look for Checks as section bullet point
    # DOUBLE check heading.  Date Check # Bank reference Amount Date Check # Bank reference Amount
    #[x] added to kinds
    tt=init_basic()
    tt['name']='schoolkiz_checks_missing_bad_transaction_count'
    tt['notes']+=['elevates to gpt-4 which does fine.  Page should be flagged as complex']
    tt['alg']='page2transactions'
    tt['date']='20240202'
    tt['meta']['case_id']='case_schoolkids'
    tt['meta']['page_number']=9
    tt['meta']['full_path']="C:/scripts-23/watchtower/CASE_FILES_STORAGE/storage/case_schoolkids/Schoolkidz-December-2021-statement.pdf"
    tt['TARGET']['amount']=1375.36  #Check within two column check section
    tts+=[tt]


    ###################################
    ## Filter to name specific
    if name:
        keepers=[]
        for tt in tts:
            if name==tt.get('name',''):
                print ("YES: "+str(tt))
                keepers+=[tt]
        tts=keepers
        if not tt:
            raise Exception("No test cases found for name: %s"%name)


    return tts
    
print ("[ ] integrate test_script_full.py here")


def notes_on_creating_KB_graph_test_cases():
    options=[]
    options+=['[A]  enforce specific nodes from known case and run alg on them']
    options+=['[B]  create test case from known case page and run alg on them']

    return




if __name__=='__main__':
    branches=['dev1']
    for b in branches:
        globals()[b]()
