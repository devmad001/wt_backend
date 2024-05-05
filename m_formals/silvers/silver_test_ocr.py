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
sys.path.insert(0,LOCAL_PATH+"../../../")

from support_gold import local_ocr
from support_gold import local_pdf2doc

from m_autoaudit.audit_plugins.audit_plugins_main import alg_ocr_quality

from get_logger import setup_logging
logging=setup_logging()




#0v1# JC  Mar 20, 2024  Setup


"""
*silver is less about a specific case

    "Silver" level tests
    - not end-to-end-tests
    - not unit test

    Focus on single module or specific function
    - While this could be unittest, this is part performance evaluation and part pre-audit
    - Focus is silver standard set of test cases on what options work when

"""



########################################################
## FOLDERS  (keep within repo -- so can do git pull and have all files)
config_filename=LOCAL_PATH+"../../w_settings.ini"
if not os.path.exists(config_filename):
    raise Exception("Config file not found: "+str(config_filename))

Config = ConfigParser.ConfigParser()
Config.read(config_filename)
BASE_STORAGE_DIR=Config.get('files','base_test_storage_rel_dir')

TARGET_TEST_FOLDER=LOCAL_PATH+"../"+BASE_STORAGE_DIR
#TARGET_TEST_FOLDER=LOCAL_PATH+"../CASE_FILES_STORAGE/tests"
SINGLE_TEST_FILE_FOLDER=TARGET_TEST_FOLDER+"/single_pdfs"

if not os.path.exists(TARGET_TEST_FOLDER): os.makedirs(TARGET_TEST_FOLDER)
if not os.path.exists(SINGLE_TEST_FILE_FOLDER): os.makedirs(SINGLE_TEST_FILE_FOLDER)



def call_silver_ocr_test():
    # (setup similar to gold_test_configs.py
    # 

    tts=[]
    
    if False:
        tt['notes']=['no effect when upsampling']
        tt['meta']['test_single_path']='aac18e37-dc9e-4343-9c73-4cebbc08c043_page_162_silent_pipe_bad_ocr_decimals.pdf'
        tt['TEST_NOT_HAVE']='4000'
        if '120,00' in epages[index][method]: raise Exception("Test should not have: 120,00")
        if '891817' in epages[index][method]: raise Exception("Test should not have: 891817")
        

    ####################################################################################
    #  Affinity strange OCR requires 400 dpi
    if False:
        tt={}
        tt['meta']={}
        tt['name']='ocr 75 vs 300'
        tt['date']='20240320'
        #tt['meta']['case_id']='65d11a8c04aa75114767637a'

        #** this seems to work locally but not sure not on server or ensure this is original file.
        tt['meta']['test_single_path']='affinity_page_85_odd_date_on_ocr.pdf'
        tt['TEST_HAVE']='07/01/23'
        """
        BAD OUTPUT IS:
        = « Date F Date T P 5‘ Affll’llty® 012 071 /3 2
        n Federal Credit Unio
        GOOD OUTPUT IS: 
        ....07/01/23...
        """
    #    TARGET_UPSAMPLE=0
    #    meta=local_ocr(input_pdf,output_pdf,upsample=0)
    #    meta=local_ocr(input_pdf,output_pdf,upsample=150) #Prints as better view not \n??
        #meta=local_ocr(input_pdf,output_pdf,upsample=300)
        """ @300 NO!
        --> e Date T P
        §A\ Affll‘llty® z 07 1 /3 2
        n Federal Credit Unio
        NAZIRAH BEY
        """
    
        #meta=local_ocr(input_pdf,output_pdf,upsample=400)
        """ @400: works best for dates, not for name
         B o Date From Date To Page
        5‘\ Afflnlty® 07/01/23 | 07/31/23
        n Federal Credit Unio
        NAZIRAH BEY
        """
    
        #meta=local_ocr(input_pdf,output_pdf,upsample=600)  #Works
        """ @600:
        Date To Page A& Affinity -
        Federal Credit Unio 07/31/23
        NAZIRAH BEY
        """
    
        meta=local_ocr(input_pdf,output_pdf,upsample=800)
        """ @800 not great
        --> ?} f f- o . Date From Date To Page T A ll‘llty 07/01/23 | 07/31/23 | 2of5
        Federal Credit Union
        NAZIRAH BEY
        Affinity Cash Back Debit - 812126921
        """
    ####################################################################################
    
    
        
    ####################################################################################
    #  Normal poor ocr bad amount
    #>> jon conclusion:  any kind of alert on quality, do azure ocr.
    #>> no effect upscaling 72 -> 300+

    tt={}
    tt['meta']={}
    tt['name']='rnd poor ocr'
    tt['date']='20240323'
    #tt['meta']['case_id']='65d11a8c04aa75114767637a'

    if True:
        #** this seems to work locally but not sure not on server or ensure this is original file.
        tt['meta']['test_single_path']='65e743696c750f81c06e5160_af37f200-4f01-4c01-9364-75e9e8bb3be4_bad_amount_ocr.pdf'
#        tt['TEST_HAVE']='07/01/23'
    ####################################################################################

    ####################################################################################
    #  Mike test case
    #- he did textract, gptv

    tt={}
    tt['meta']={}
    tt['name']='test case textract etc'
    tt['date']='20240325'
    #tt['meta']['case_id']='65d11a8c04aa75114767637a'

    if True:
        #** this seems to work locally but not sure not on server or ensure this is original file.
        tt['meta']['test_single_path']='TEST_CASE_1_PAGE_ORG_IMAGE_Management-Properties-v-Brusko-Copy-of-First-Citizens-Bank-Checks-2020_OCR (2).pdf'
#        tt['TEST_HAVE']='07/01/23'
    ####################################################################################
    
    ## DO direct
    input_pdf=SINGLE_TEST_FILE_FOLDER+"/"+tt['meta']['test_single_path']
    if not os.path.exists(input_pdf):
        raise Exception("Input file not found: "+str(input_pdf))
        
    output_pdf=SINGLE_TEST_FILE_FOLDER+"/"+tt['meta']['test_single_path']+".out.pdf"
    
    TARGET_UPSAMPLE=400 #same
    TARGET_UPSAMPLE=800 #same
    TARGET_UPSAMPLE=300
    TARGET_UPSAMPLE=0 #2 bad counts
    print ("JC:  beware 300 drops check number entirely...better to just keep normal)")
    print ("====================================")
    meta=local_ocr(input_pdf,output_pdf,upsample=TARGET_UPSAMPLE)
        
    
    print ("!!!! INCLUDE ocr quality number test!!!")

    print ("META: "+str(meta))
#
#    if not os.path.exists(output_pdf):
#        meta=local_ocr(input_pdf,output_pdf)
    Doc=local_pdf2doc(output_pdf)
    
    epages=Doc.get_epages()
    for index in epages:
        print ("PAGE: "+str(index)+"-"*30)
        for method in epages[index]:
            if not method=='pypdf2_tables': continue
            print ("PAGE: "+str(index)+"-"*30+" method: "+str(method))

            blob=epages[index][method]
            print ("--> "+blob)
            
            ocr_reliability,recommend_ocr_higher_quality,meta=alg_ocr_quality(blob)
            bad_separators=meta['count_bad_separators']

            print ("OCR RELIABILITY: "+str(ocr_reliability))
            print ("RECOMMEND HIGHER QUALITY: "+str(recommend_ocr_higher_quality))
            print ("META: "+str(meta))
            print ("Bad separators (if>1 for one page say redo!): "+str(bad_separators))

            if 'TEST_NOT_HAVE' in tt:
                #4000
                if tt['TEST_NOT_HAVE'] in epages[index][method]:
                    raise Exception("Test should not have: "+str(tt['TEST_NOT_HAVE']))
            if 'TEST_HAVE' in tt:
                #4000
                if tt['TEST_HAVE'] in epages[index][method]:
                    raise Exception("Test should not have: "+str(tt['TEST_NOT_HAVE']))
                

    return


if __name__=='__main__':
    branches=['call_silver_ocr_test']

    for b in branches:
        globals()[b]()
