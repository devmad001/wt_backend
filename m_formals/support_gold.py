import os, sys
import time
import requests
import re

import configparser as ConfigParser

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")


from z_apiengine.database import SessionLocal

from w_utils import get_base_endpoint
from w_utils import get_ws_endpoint

from a_agent.algs_iagent import alg_get_case_files
from w_pdf.pdf_process import interface_file2doc  #epages

from c_release.MANAGE_exe import easy_process_pdf_case
from b_extract.p2t_test_sets.auto_create_test_sets import run_pdf_filename2transactions_test
from w_pdf.ocr_model import interface_pdfocr
from a_custom.smart_extract import local_extract_first_page_style_data

from kb_ai.call_kbai import interface_call_kb_auto_update
from kb_ai.cypher_markups.markup_alg_cypher_EASY_CREDIT_DEBIT import is_transaction_credit

from w_pdf.ocr_model import interface_pdfocr

from get_logger import setup_logging
logging=setup_logging()


#0v2# JC Jan 29, 2023  Extend for more system gold sub-function test
#0v1# JC Jan 15, 2023  Setup

"""
    SUPPORT GOLD (functional tests) TESTS
    - page2transactions, ocr, statement first-page, etc.

"""



## Temp storage
config_filename=LOCAL_PATH+"../w_settings.ini"
if not os.path.exists(config_filename):
    raise Exception("Config file not found: "+str(config_filename))

Config = ConfigParser.ConfigParser()
Config.read(config_filename)
BASE_STORAGE_DIR=Config.get('files','base_test_storage_rel_dir')

TEMP_DIR=LOCAL_PATH+"../"+BASE_STORAGE_DIR
if not os.path.exists(TEMP_DIR):
    os.makedirs(TEMP_DIR)


"""
    DEBUG HELPER
    - common methods for targeted case processing
    
    NOTES:
    - see also functiona_test_page2transactions
    [ ] see also jon_dev or dev_challenges for common functions?
    [ ] see also: from c_release.MANAGE_exe import easy_process_pdf_case

"""

def local_ocr(input_pdf,output_pdf,downsample=300,jobs=2,upsample=150):
    return interface_pdfocr(input_pdf,output_pdf,downsample=downsample,jobs=jobs,upsample=upsample)

def local_process_case_remove_first(case_id):
    #[ ] see dev_challenges
    return 

def local_page2transaction(pdf_filename,page_number=0):
    ## Recall
    all_transactions,meta=run_pdf_filename2transactions_test(pdf_filename,page_number=page_number)
    return all_transactions,meta

def local_pdf2ocr2txt(pdf_filename):
    doc=None
    ocr_output_filename=pdf_filename.replace('.pdf','_ocr.pdf')
    if not os.path.exists(ocr_output_filename):
        print ("Running OCR: "+str(pdf_filename)+" --> "+str(ocr_output_filename))
        meta=interface_pdfocr(pdf_filename,ocr_output_filename,jobs=0)
        print ("OCR META: "+str(meta))
    doc=local_pdf2doc(ocr_output_filename)
    return doc

def local_firstpage2fields(page_text):
    ## Recall
    page_fields=local_extract_first_page_style_data(page_text)
    return page_fields

def local_transaction_type_on_subgraph(case_id):
    #> assumes subgraph (for narrow test)
    force_algs_to_apply=['transaction_type_method']
    commit=False

    response=interface_call_kb_auto_update(case_id,force_update_all=True,force_algs_to_apply=force_algs_to_apply,commit=commit,force_thread_count=1)

    return response

def local_is_transaction_credit(tt):
    #**this is part of markup section but too many assumptions?
    tcredit={} #DICT
    is_credit,tcredit,reasons=is_transaction_credit(tt)
    return is_credit,tcredit,reasons

###################################################################################
#^above are core system functions (to test)



### BELOW ARE SUPPORT

def url2testcase(tt):
    #0v1# (sourced from functional_test_page2transactions.py)

    global TEMP_DIR
    #[x] support for per page but need full file.
    #[ ] full multi page support
    
    ### NORMALIZE FILENAME
    if 'filename' in tt['meta']:
        if not os.path.exists(tt['meta']['filename']):
            ## Look for file pattern
            filename=tt['meta']['filename']
            filename=re.sub(r'.*\tests',r'',filename)  #Assume bad escape
            alt_filename=TEMP_DIR+"/"+filename
            if not os.path.exists(alt_filename):
                raise Exception("File not found: "+str(tt['meta']['filename']))
            tt['meta']['full_path']=alt_filename
        else:
            tt['meta']['full_path']=tt['meta']['filename']

    ### NORMALIZE URL
    if 'url' in tt['meta']:
        #url='chrome-extension://efaidnbmnnnibpcajpcglclefindmkaj/https://core.epventures.co/api/v1/case/6596f679c8fca0cb7b70e1fb/pdf/b584defb-db9a-42da-b612-f5a5dc9b47c2.pdf?page=74&key=75add40ae552468997b3bf96fa895406a75b8ab0936bfc5eaf6a0bef12a24663&highlight=64007.17|Beginning|balance|July'
        tt['meta']['url']=re.sub(r'.*\/https',r'https',tt['meta']['url'])
        url=tt['meta']['url']
        
        if url:
            ## Extract various
            tt['meta']['case_id']=re.findall('case/(.*?)/',url)[0]
            tt['meta']['page']=re.findall('page=(.*?)&',url)[0]
            tt['meta']['filename']=re.findall('pdf/(.*?).pdf',url)[0]+'.pdf'
    
        ## Check givens
        # If page is not integer raise
        try:
            tt['meta']['page']=int(tt['meta']['page'])
        except:
            tt['meta']['page']=0
        
        ## Hard path
        tt['meta']['file_directory']=TEMP_DIR+"/"+tt['meta']['case_id']+'/'
        if not os.path.exists(tt['meta']['file_directory']):
            os.makedirs(tt['meta']['file_directory'])
        tt['meta']['full_path']=tt['meta']['file_directory']+tt['meta']['filename']
        
        ## Download if not exists
        if not os.path.exists(tt['meta']['full_path']):
            r=requests.get(url)
            with open(tt['meta']['full_path'], 'wb') as f:
                f.write(r.content)

    ##
    #tt['meta']['amount=re.findall('highlight=(.*?)\|',url)[0]
    #tt['meta']amount=float(amount.replace(',',''))

    return tt

def case_id2text(case_id,page_number):
    ## Assume fetch file or case or pdf then convert
    ASSUME_USE_ONE_FILE=True
    
    ### GET CASE FILES
    full_path=None
    ff=alg_get_case_files(case_id)

    print ("DEBUG: "+str(ff))
    print ("DEBUG: "+str(len(ff)))

    case_path_filenames=ff[0]
    case_filenames=ff[1]
    case_directory=ff[2]

    for full_case_filename_path,case_filename in ff[0]:
        break
            
    print ("USE FILE: "+str(full_case_filename_path))

    ### CONVERT CASE FILE PAGE TO TEXT
    Doc=local_pdf2doc(full_case_filename_path)
    epages=Doc.get_epages()
    
    page_text=''
    for page_num in epages:
        if not (page_num+1)==page_number: continue
        for method in epages[page_num]:
            if not method=='pypdf2_tables': continue
            print ("METHOD: "+str(method))
            page_text=epages[page_num][method]
            if page_text:break
        if page_text:break
    
    return page_text



#from w_pdf.pdf_process import interface_file2doc
def local_pdf2doc(pdf_filename):
    doc=interface_file2doc(pdf_filename)
    return doc


def dev_gold_system_entrypoints():

    ## Try some support functions
    
    ## Maybe needs ocr??
    #-> check get text vs ocr get text

    tt={}
    tt['meta']={}


    
    b=[]
    b=['test local pdf2doc','try_ocr']
    b=['try llm statement balance']
    
    ## Auto select case / url for specific dev of feature
    
    # if any overlap
    if ['test local pdf2doc','try_ocr'] in b:
        tt['meta']['url']="http://127.0.0.1:8008/api/v1/case/MarnerHoldingsB/pdf/2021-06June-statement-0823.pdf?page=3&key=938bf45baae2c97dbd5747808ddd2b8702153ad6261b072d8cdd171c9535b14e&highlight=36,964.36"
        pass
    elif 'try llm statement balance' in b:
        #[ ] optionally via pdf
        tt['meta']['case_id']='case_bank state 3'  #<-- pent local [ ] build test cases
        tt['meta']['case_id']='case_bank state 2'
        tt['meta']['page']=1

    else:
        tt['meta']['url']="http://127.0.0.1:8008/api/v1/case/MarnerHoldingsB/pdf/2021-06June-statement-0823.pdf?page=3&key=938bf45baae2c97dbd5747808ddd2b8702153ad6261b072d8cdd171c9535b14e&highlight=36,964.36"
        
    
    ## AUTO PREPARE TEST CASE  (ie/ local files + conversion)
    tt=url2testcase(tt)

    print ("READY: "+str(tt))
    
    if 'test local pdf2doc' in b:
        doc=local_pdf2doc(tt['meta']['full_path'])
        
        print ("GOT DOC: "+str(doc))
        
        epages=doc.get_epages()
        for index in epages:
            print ("[debug] epage: "+str(epages[index]))
            
    if 'try ocr' in b:
        doc=local_pdf2ocr2txt(tt['meta']['full_path'])

        epages=doc.get_epages()
        for index in epages:
            print ("[debug] epage: "+str(epages[index]))
        #!! The specified amount "$36,964.36" is not present in the new OCR-processed text snippet. ​
        

    if 'try llm statement balance' in b:
        # Given case id, call inner get statement balance on raw pdf  (may need text epage)
        print ("RECALL MAIN run_pipeline is entrypoint but what about direct?")
        print ("[ ] document this?")
        print (" a_custom/smart_extract.py -> local_extract_first_page_style_data ")
        #*recall using standard pdf_tables method i believe
        page_text=case_id2text(tt['meta']['case_id'],tt['meta']['page'])

        print ("READ PAGE TEXT: "+str(page_text))
        
        fields=local_firstpage2fields(page_text)

        print ("FIELDS: "+str(fields))
        
        ## Test at bank state 2
        if not fields['opening_balance']==167391.65: raise Exception("Opening balance bad")
        if not fields['closing_balance']==134397.19: raise Exception("Closing balance bad")
        
        ## Test assertion at bank state 3
        if not fields['opening_balance']==162555.77: raise Exception("Opening balance bad")
        if not fields['closing_balance']==167391.65: raise Exception("Closing balance bad")

        """
        ## Add this to model extension logic
        
        ## Require file...
        so the problem is:  consolidated balances.  accounts tracking

        evan case has bad number read:
        https://watchdev.epventures.co/fin-aware/dashboard?case_id=65a82cc9b3ac164610ea5e64
        - opening balance of debig 16255.77??
        looks like:  

        HOWEVER what is bank state 3 because im seeing
        beginning 162,555.77
        ending: 167,391.65
        but excel shows debig 16,255.77 and 146,300.00

        """




    if False:
        file_pages[fname]['epages']=Doc.get_epages()
        print ("[debug] file pages: "+str(Doc.count_pages()))
        total_pages+=Doc.count_pages()

    return



if __name__ == "__main__":
    dev_gold_system_entrypoints()




"""
    **RECALL.

        ## Assumes 1 page
        if True:
            from b_extract.p2t_test_sets.auto_create_test_sets import run_page2transactions_test
            run_page2transactions_test(output_filename)


        ## Deals with 1 page from full doc (but a bit hacky)
        if False:
            from b_extract.p2t_test_sets.auto_create_test_sets import run_pdf2pdfpage2transactions_test
        
            filename='C:/scripts-23/watchtower/CASE_FILES_STORAGE/storage/6579bfd30c64027a3b9f2d3c/62eac7ab-388c-4ff0-802e-65e96fedbd29.pdf'

            run_pdf2pdfpage2transactions_test(filename,88)


"""


