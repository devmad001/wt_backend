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
    tt['ISDEBIT']={}
    tt['ISCREDIT']={}
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

    ## TD pdf2txt removing spaces in text -- likely requires forced OCR or another method
    #- also part of building out auto_audit system
    #- also part of adding local test file support
    tt=init_basic()
    print ("[ ] do formal test")
    tt['name']='TD_odd_pdf2txt' #<-- use in ENTRY_gold for calling specifically
    tt['alg']='pdf2txt' #<-- could define as page2text but more narrow better and sample audit entrypoint too
    tt['date']='20240228'
    tt['notes']+=['']

    tt['meta']['case_id']='65cd06669b6ff316a77a1d21'
    tt['meta']['test_single_path']='65cd06669b6ff316a77a1d21_sample_odd_pdf2txt.pdf'   #For ie/ single pdf input
#351#    tt['meta']['test_single_path']='65cd06669b6ff316a77a1d21_d0765e38-0724-475e-97fa-e27ffc31f484.pdf' #Trial full TD

#    tt['meta']['test_folder_path']=''   #For ie/ case folder (ie/ multiple pdfs or conversions")

    tts+=[tt]
    
    ## OCR mistaking commas & periods 227,293.46
    #> add test file here as part of auditing + refinement dev (see n_docs/*)
    print ("[ ] do formal test")
    tt=init_basic()
    tt['name']='silent_pipe_200_plus'
    tt['alg']='pdf2txt'
    tt['date']='20240304'
    tt['notes']+=['']

    tt['meta']['case_id']='65d11a8c04aa75114767637a'
    tt['meta']['test_single_path']='aac18e37-dc9e-4343-9c73-4cebbc08c043.pdf'
    tts+=[tt]
    
    
    ## Statement date bridges year - requires proper year inferral
    tt=init_basic()
    tt['name']='year_end_date_roll'
    tt['alg']='page2transactions'
    tt['date']='20240314'
    tt['notes']+=['Think failed on server but passed on local at retry']

    tt['meta']['case_id']='65d11d5f04aa751147676516'
    tt['meta']['test_single_path']='c9d328f4-4c9c-4f8f-b68f-48def8eb0c84.pdf'

    tt['meta']['url']="https://core.epventures.co/api/v1/case/65d11d5f04aa751147676516/pdf/c9d328f4-4c9c-4f8f-b68f-48def8eb0c84.pdf?page=1&key=34c17c0f6e75b60a63f9d291fc51912b6f76e3b9cba7577d43106959d8242844&highlight=52.08|Google%2AGoogle|authorized|Purchase"
    tt['TARGET']['date']='2021-01-04' # I think on server it popped up as 2020?? need statement window check
    tts+=[tt]
    
    print ("[ ] document parameters: test_single_path is single file")
    print ("[ ] document parameters: if input is url it will be pulled locally")


    tt=init_basic()
    tt['name']='hallucinates_123_main_st'
    tt['alg']='page2transactions'
    tt['date']='20240314'
    tt['notes']+=['123 Main St, Anytown hallucinates with gpt 3.5']
    
    tt['NOTARGET']['amount']=2018.48   # This is summary amount not transactinss (3.5 bad 4 good)

    tt['meta']['case_id']='65d65ae49be7358de5d1fb89'
#    tt['meta']['test_single_path']='c9d328f4-4c9c-4f8f-b68f-48def8eb0c84.pdf'
    tt['meta']['url']="https://core.epventures.co/api/v1/case/65d65ae49be7358de5d1fb89/pdf/883bbc4c-802a-4630-956e-6ae9c4f773a5.pdf?page=1&key=de6e883631917c100f4e2036ff06121f75caaa27af8b26be58cf6aa6151dc040&highlight=67.89|Anytown%2C|shopping|Purchase"
    tts+=[tt]


    ###### TEST SETUP two parts?
    tt=init_basic()
    tt['name']='james_bad_debit_credit_on_obvious'
    tt['alg']='page2transactions2creditdebit'
    tt['date']='20240315'
    tt['notes']+=['seems like standard page']
    
    tt['ISDEBIT']['amount']=150000.00

    tt['meta']['case_id']='65cbb7ac9b6ff316a779fac0'
    tt['meta']['url']="https://core.epventures.co/api/v1/case/65cbb7ac9b6ff316a779fac0/pdf/ba893e2c-6356-4b7a-8631-9b84b49f5922.pdf?page=105&key=a940753f7af65813c85b2a8e3ed846a492698b7b844fa9ac50012cf61ec178b9&highlight=150000.00|Confirmation%23|150%2C000.00|1186801186"

    tts+=[tt]

#    ## OK but does entire case!
#    tt=init_basic()
#    
#    tt['name']='james_bad_debit_credit_subgraphmaybe'
#    tt['notes']+=[]
#    tt['alg']='kb_transaction_type'
#    tt['date']='20240315'
#    tt['meta']['page_number']=105
#    tt['meta']['case_id']='65cbb7ac9b6ff316a779fac0'
#    #tt['ANDTEST_amount_type']=(0.55,'withdrawal') # for kb_transaction_type test kind only
#    tts+=[tt]
#    


    if False:
        #** double transaction BECAUSE statement duplicated
        tt=init_basic()
        tt['name']='james_double_transaction'
        tt['alg']='page2transactions'
        tt['date']='20240315'
        tt['notes']+=['double transaction but mentioned in summary']
        
        tt['TARGET']['amount']=69.52
        tt['meta']['case_id']='65d65ae49be7358de5d1fb89'
        tt['meta']['test_single_path']='883bbc4c-802a-4630-956e-6ae9c4f773a5_page9_double_trans.pdf'
    #    tt['meta']['url']="https://core.epventures.co/api/v1/case/65d65ae49be7358de5d1fb89/pdf/883bbc4c-802a-4630-956e-6ae9c4f773a5.pdf?page=9&key=de6e883631917c100f4e2036ff06121f75caaa27af8b26be58cf6aa6151dc040&highlight=69.52|Charge|Debit|DDA"
        tts+=[tt]
    
    tt=init_basic()
    tt['name']='blank_page_continues_chat'
    tt['alg']='page2transactions'
    tt['date']='20240315'
    tt['meta']['case_id']='65d65ae49be7358de5d1fb89'
    tt['meta']['test_single_path']='883bbc4c-802a-4630-956e-6ae9c4f773a5_blank_page.pdf'
    tts+=[tt]

    #[x] fixed
    tt=init_basic()
    tt['name']='ashford_year_in_advance'
    tt['alg']='page2transactions'
    tt['date']='20240318'
    tt['notes']+=['Bad year suggestion thinks posted date is wrong. also skips amounts']
    tt['TARGET']['amount']=19510.26
    tt['meta']['case_id']='65caaffb9b6ff316a779f525'
    tt['meta']['test_single_path']='M&T Victim Records__Reserve 2023__STMT__1 page1.pdf'
    tts+=[tt]


    ##
    # BAD OCR:

    #? tell to repair during extraction ie/ assumptions?
    #[]? ask to repair bad ocr via llm by few lines at a time specific to dates or numbers?

    # 02/08 26,363,086 Business to Business ACH Debit - TX Comptroller Tax Pymt 05059764/20207
    # 02/09 2,059,09 Business to Business ACH Debit - Wl Dept Revenue Taxpaymnt 220208
    # 02/10 20,00 Bill Pay Xueer Zhu on-Line No Account Number on 02-10
    # 02/08 41216777 Business to Business ACH Debit -Brex Inc. Payments 220206 Brexi7WrofdwOF
    # NTE*ZZZ*BrexCard Paymenf\
    # 02/10 11,69895  WT 220210-007857 Royal Bank of Canad /Bnf=Caytor Consulting Sri#
    # Gw0000004847 3699 Trn#220210007857 Rib# 4974

    #__this needs better OCR.
    tt=init_basic()
    tt['name']='bad comma period amount'
    tt['alg']='page2transactions'
    tt['date']='20240318'
    tt['notes']+=[]
#    tt['TARGET']['amount']=19510.26
    tt['meta']['case_id']='65d11a8c04aa75114767637a'
    tt['meta']['test_single_path']='aac18e37-dc9e-4343-9c73-4cebbc08c043_bad_large_amount.pdf'
    tts+=[tt]
    

    ###  New year extractor pickin up check numbers as year!  Do statement range anyways
    # https://core.epventures.co/api/v1/case/65960931c8fca0cb7b70e024/pdf/eda6493a-3b12-4884-a4b7-d9a29d8e83c1.pdf?page=12&key=dfd502fdeb8cba8e8f090163398642c86261ecc1d3afcda3115bb99c898c78d2&highlight=4836.00|Transaction%23%3A|5530488616|Transfer
    tt=init_basic()
    tt['name']='year is not check num'
    tt['alg']='page2transactions'
    tt['date']='20240318'
    tt['notes']+=['fix: alg_easy_extract.py -> alg_get_page_year()']

#    tt['TARGET']['amount']=19510.26
    tt['meta']['case_id']='65960931c8fca0cb7b70e024'
    tt['meta']['test_single_path']='eda6493a-3b12-4884-a4b7-d9a29d8e83c1_year_not_check.pdf'
    tts+=[tt]
    
    
    ##########################################################
    # FORMALIZE TEST CASES
    ##########################################################
    #> symptom, cause, fix
    #> local test files
    #> remote pdf view (highlight option maybe but put as meta)
    
    ## check withdrawl seen as deposit
    #- possibly bad credit/debit assignment?
    #- case is org Evan + data
    tt=init_basic()
    tt['name']='check not debit'
    tt['alg']='page2transactions'
    tt['date']='20240319'
    tt['notes']+=[]
#    tt['TARGET']['amount']=19510.26
    tt['meta']['case_id']='65960931c8fca0cb7b70e024'
    tt['meta']['test_single_path']='eda6493a-3b12-4884-a4b7-d9a29d8e83c1_check_not_debit.pdf'
    tt['meta']['online_url']='https://core.epventures.co/api/v1/case/65960931c8fca0cb7b70e024/pdf/eda6493a-3b12-4884-a4b7-d9a29d8e83c1.pdf?page=40&key=dfd502fdeb8cba8e8f090163398642c86261ecc1d3afcda3115bb99c898c78d2&highlight=601.91|232082'
    tts+=[tt]
    
    ## Bad check value -94.29 NOT -xxxx.xx
    tt['name']='bad ocr normal entry'
    tt['alg']='page2transactions'
    tt['date']='20240319'
    tt['TARGET']['amount']=-94.29
    tt['notes']+=[]
    tt['meta']['case_id']='65960931c8fca0cb7b70e024'
    tt['meta']['test_single_path']='eda6493a-3b12-4884-a4b7-d9a29d8e83c1_bad_amount_normal_transaction.pdf'
    tt['meta']['online_url']='https://core.epventures.co/api/v1/case/65960931c8fca0cb7b70e024/pdf/eda6493a-3b12-4884-a4b7-d9a29d8e83c1.pdf?page=2&key=dfd502fdeb8cba8e8f090163398642c86261ecc1d3afcda3115bb99c898c78d2&highlight=9429.00|2002|23'
    tts+=[tt]

    ## Affinity quick trial for hidden year.
    tt['name']='affinity date'
    tt['alg']='page2transactions'
    tt['date']='20240319'
    tt['notes']+=[]
    tt['meta']['case_id']='65f9a28a7a047045e56b4df1'
    tt['meta']['test_single_path']='daa9e835-2572-48a0-833e-df03a8fbd5e6_afinity.pdf'
    tt['meta']['online_url']='https://core.epventures.co/api/v1/case/65f9a28a7a047045e56b4df1/pdf/daa9e835-2572-48a0-833e-df03a8fbd5e6.pdf?page=85&key=5de2cba355d506eb83264f053d93098c749d77dedcbfa5546c69bc6baa5fbfef&highlight=143.70|Insurance|Web|Pay'
    tts+=[tt]

    tt['name']='reversal deposit'
    tt['alg']='page2transactions2creditdebit'
    tt['date']='20240320'
    tt['notes']+=[]
    tt['meta']['case_id']='65fa72717a047045e56b54bb'
    tt['meta']['test_single_path']='a2601df4-dea0-4a2b-9a09-67b948cb8ca2_reversal_should_be_deposit.pdf'
    tt['meta']['online_url']='https://core.epventures.co/api/v1/case/65fa72717a047045e56b54bb/pdf/a2601df4-dea0-4a2b-9a09-67b948cb8ca2.pdf?page=2&key=b2682c064bb90d24a70cb156745ff627e0f27bf67dc56cfd8b9c64518a48fa65&highlight=4213.77|Name%3AAmerican|Reversal%3A|Express'
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
