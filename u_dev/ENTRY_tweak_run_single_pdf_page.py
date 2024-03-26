import os
import sys
import codecs
import json
import re
import datetime
import uuid

from fastapi import FastAPI

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")

sys.path.insert(0,LOCAL_PATH+"../..")


#from w_chatbot.wt_brains import Bot_Interface
from w_storage.ystorage.ystorage_handler import Storage_Helper

from a_agent.sim_wt import wt_main_pipeline

from get_logger import setup_logging
logging=setup_logging()


Storage=Storage_Helper(storage_dir=LOCAL_PATH+"../w_datasets")
Storage.init_db('feedback')

        
#0v1# JC Nov 23, 2023  Setup

"""
    TWEAK easy way to run one page though processing for debug
"""

def ENTRY_tweak_run_single_pdf_page():
    print ("ENTRY_tweak_run_single_pdf_page")
    
    ## SPECIFICS:

    ## See report_tweaks.py
    #[x] added section heading
    page_url='https://core.epventures.co/api/v1/case/MarnerHoldings/pdf/2021-06June-statement-0823.pdf?page=1&key=798669380686ea0bfad31c5e69805b0c42f4edbcd556bb5bf226dde92e00d30a'

    #[x] thinks withdrawl section is deposit??
    # ^ it was not expecting all OCR'd
    page_url='https://core.epventures.co/api/v1/case/MarnerHoldings/pdf/2021-06June-statement-0823.pdf?page=9&key=798669380686ea0bfad31c5e69805b0c42f4edbcd556bb5bf226dde92e00d30a'
    
    #[x] resolved
    page_url='http://127.0.0.1:8008/api/v1/case/MarnerHoldingsJune/pdf/2021-06June-statement-0823.pdf?page=1&key=14b3f30104701f2ffd565d0efbcfa86e997f65e35cdf6e3c9867973603532a89'
    
    ##  Other withdrawl $25,222.25
    page_url="http://127.0.0.1:8008/api/v1/case/MarnerHoldingsB/pdf/2021-06June-statement-0823.pdf?page=12&key=938bf45baae2c97dbd5747808ddd2b8702153ad6261b072d8cdd171c9535b14e"
    


    ## CONTROLS
    
    ## BRANCH "1"
    b=[]
    b=['rerun_entire_case']

    ## BRANCH "2"
    ## BOTH FOR SINGLE PAGE!!!k
    b=['check_extraction_alg_on_single_page']
    b+=['only do specific page']
    
    
    
    if 'check_extraction_alg_on_single_page' in b or 'rerun_entire_case' in b:

        dd={}
        dd['filename']=''
        dd['page']=''

        dd['page_url']=page_url
        
        ### AUTO
        dd['case_id']=re.sub(r'.*\/case\/(.*)\/pdf.*',r'\1',dd['page_url'])
        dd['filename']=re.sub(r'.*pdf\/(.*)\?page.*','\\1',dd['page_url'])
        dd['page']=re.sub(r'.*page=(.*)\&key.*','\\1',dd['page_url'])
        

        ## Recall u_dev/dev_challenges has sample entry
        if False:
            case_id="MarnerHoldings"

            #    local_admin_remove_case_from_kb(case_id=case_id)
            meta=wt_main_pipeline(case_id=case_id,options=options,manual_skip_caps=['start_KBAI_processing_pipeline'])
            print ("[challenge meta] transactions touched: "+str(meta.get('count_transactions','')))
            manual_skip_caps=['start_main_processing_pipeline']
            meta=wt_main_pipeline(case_id=case_id,options=options,manual_skip_caps=manual_skip_caps)
            
        ### SETTINGS FOR EXTRACTION
        print ("[debug] running extraction on page: "+str(dd['page']))
#D        print (">> "+str(dd))

        options={}
        
        if 'rerun_entire_case' in b:
            options['db_commit']=True  #Default so not really needed
            stop=may_add_double_transactions

        if 'only do specific page' in b:
            options['only_pages']=[dd['page']] #array of ints!
            options['db_commit']=False

        meta=wt_main_pipeline(case_id=dd['case_id'],options=options,manual_skip_caps=['start_KBAI_processing_pipeline'])
        
        ### SETTINGS TO REMOVE AND REDO ENTIRE CASE (or even case or transaction i suppose)



    return
    
if __name__=='__main__':
    branches=['ENTRY_tweak_run_single_pdf_page']
    for b in branches:
        globals()[b]()


""
