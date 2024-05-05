import os, sys
import time
import requests
import re


import configparser as ConfigParser

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)

sys.path.insert(0,LOCAL_PATH+"../../")
from z_apiengine.database import SessionLocal


#0v1# JC Mar  5, 2024  Setup



"""
    "GLOBAL QA REPORT"
    [ ] ok to move elsewhere
    - Now that auto_audit exists, can we use it to do a global QA report?
    - Run OCR quality check against all known documents? Cases?

"""

Config = ConfigParser.ConfigParser()
Config.read(LOCAL_PATH+"../../w_settings.ini")

BASE_STORAGE_DIR=Config.get('files','base_storage_rel_dir')
BASE_STORAGE_DIR=LOCAL_PATH+"../../"+BASE_STORAGE_DIR  ## BASE_STORAGE_DIR may be:  ../x/y


def iter_local_case_files():
    global BASE_STORAGE_DIR
    
    yield_only_ocrd=True

    #flag ocr done if file exists in org or org copoy
    
    # Iter over folders in BASE_STORAGE_DIR
    # For each folder, iter over files
    # If file is a pdf, check if OCR has been performed
    
    print ("[debug] walking: "+str(BASE_STORAGE_DIR))
    base_depth=0
    case_id=''
    for root, dirs, files in os.walk(BASE_STORAGE_DIR):
        depth=root.count(os.sep)
        if not base_depth:
            base_depth=depth
        depth=depth-base_depth
        
        ## CASE MAIN FOLDER
        if depth==1: #At case_id
            case_id=os.path.basename(root)

            ## Files in main case folder
            for file in files:
#D1                print ("[debug] file: "+str(file))
                
                full_filename=os.path.join(root, file)

                #If has been ocr'd there will be a copy
                #  - recall, org/file will be original file (possibly check for diff size)
                ocr_copy=root+"/ocr_copies/"+file
                
                is_ocr_done=False
                if os.path.exists(ocr_copy):
                    is_ocr_done=True
                    
                if is_ocr_done:
#D1                    print ("[debug] OCR done: "+str(full_filename))
                    if yield_only_ocrd:
                        yield case_id,full_filename
        
    
    return


def enter_run_on_known_cases():
    from w_pdf.pdf_extractor import AUDIT_does_pdf_require_advanced_ocr
    
    # iter via local files or stored data?
    # Run what?
    
    #> For every pdf file in every case IF OCR has been performed then check for quality
    filename=LOCAL_PATH+"ocr_quality_report_m5.csv"
    fp=open(filename,'w')
    
    seen={}
    for case_id,ocrd_filename in iter_local_case_files():
        print ("DO OCR quality ANALYSIS: "+str(ocrd_filename))
        recommend_ocr_higher_quality,meta=AUDIT_does_pdf_require_advanced_ocr(ocrd_filename)
        
        if meta:
            liner=str(meta['count_bad_separators'])+","+str(meta['rate_bad_separators'])+", "+case_id+", meta:,"+str(ocrd_filename)+",META: "+str(meta)
            print (liner)
            
            base_filename=os.path.basename(ocrd_filename)
            if not base_filename in seen:
                fp.write(liner+"\n")
            seen[base_filename]=True

    fp.close()
    print ("wrote: "+str(LOCAL_PATH+"ocr_quality_report_m5.csv"))

    ### JON SUMMARY NOTES run mar 5, 2024 on local dev cpu
    # 445 files total    (so 10 files is 1%)
    # 300 files zero separators
    # 90 files have 1
    # <17 have greater then 4
    #but top 12 have 12... 8 20...1 141!


    return



def dev1():
    enter_run_on_known_cases()

    return



if __name__ == "__main__":
    dev1()






"""

"""



