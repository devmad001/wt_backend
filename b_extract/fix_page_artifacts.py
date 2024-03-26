import os
import sys
import copy
import codecs
import json
from datetime import datetime
import re
import ast
import random

import configparser as ConfigParser

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")

#from algs_extract import alg_json2dict

from get_logger import setup_logging
logging=setup_logging()


#0v1# JC  Jan 26, 2024  SETUP


"""
    PAGE TEXT CLEANING
    - artifacts from pdf2txt converter or OCR or misc
    - ideally should be done in the pdf2txt converter but sometimes not possible
    
    ADD TESTS TO:  wcodebase/m_formals/ENTRY_gold.py
    - I've avoided doing these customizations, so most assumptions contained here

"""

MONEY_PATTERN = r'(\$?\d{1,3}(?:,\d{3})*\.\d{2})' #Too specific?

def auto_clean_page_text(page_text,method='pdfminer'):
    global MONEY_PATTERN

    ## Remove known odd artifacts from page text due to pdf conversion or similar
    # - these are NOT required but ultimately helps
    # > possibly move to another area
    #** see schema_statement_kinds for generalized regex
    
    #### [1]
    if method=='pdfminer':
        ## Add space after date
        #ie/ December 1, 2021 to December 31, 2021Your checking account
        page_text=re.sub(r' ([0-9]{1,2}, [0-9]{4})([A-Za-z])',r' \1 \2',page_text)

        ##Page 5 of 10Withdrawals and other debits - continued
        page_text=re.sub(r'([0-9]{1,3} of [0-9]{1,3})([A-Za-z])',r'\1 \2',page_text)

    #### [2]
    ## Case FCB OCR has too many OCR errors to extract all check numbers so infer date and do auto swap where possible
    ## ASSUMPTION AT FCB
    #>> tt['test_case_id']='new_kind_first_citizens_bank'
    # Take year from statement header and place into check date
    """
    Statement Period: January 1, 2020 ~~ Thru January 31, 2020 Account Number : 001064017308
    Checks Paid From Your Account
    Check No. Date Amount Check No. Date Amount Check No. Date Amount
    041-17 445.61 140124 01-14 639.56 10138 01-16 2,351.94
    [ ] watch because first cell is missing check no so will miss adding this date as well
    """
    
    #### [3]
    #     FCB  (First Citizens Bank) Font causes issue with ie 7.50 -> 7  .50 or 7 .50
    #Oct 25#  Cases where OCR or font or known limitation assuption in page content.
    #> logic:  since never see decimal without leading \d, do a replace across all seen pages
    ## SAMPLES:
    #    2,567 .64 10125 2020-01-17 1,935.70 10139 2020-01-15 1,543.30
    # 10107* 2020-01-06 9,494 .07 10126 20

    page_text=re.sub(r'(\d)[\s ]+(\.\d\d)',r'\1\2',page_text)
    
    #### [4]
    #[ ] still misses:  Ending Balance 204, 755. 45+
    
    #### [5]
    #[ ] FCB manual still can't parse 3 column Checks!
    #[ ] optionally move these to statement type custom
    #** extra hard because in the sample of Colin missing Check No. in first cell!!
    page_text=re.sub(r'Date Amount Check No','Date Amount | Check No',page_text)
    
    #### [6]
    #[4] OCR may miss space before dollar sign.  Enforce space before ALL dollar signs that look like numbers
    #ie  ID:St-G2O8N4V4Q1L0              Ind Name:Marner Holdings Inc Trn: 1528254113Tc$19,066.24
    # Regular expression to add space before dollar sign if not already present and followed by a digit
    page_text = re.sub(r'(?<!\s)\$(\s{0,3}\d)', r' $\1', page_text)
    
    #### MORE FORMAL SETUP (Jan 2024)
    page_text=extended_auto_clean_page_text(page_text,method=method)

    ##### [7]
    #*optionally use MONEY_PATTERN - 2,331.44 -> -2,331.44
#    print ("GIVEN::: "+str(page_text))
    page_text=re.sub(r'( \-)[ ]+'+MONEY_PATTERN,r'\1\2',page_text)
#    print ("GOOTO::: "+str(page_text))

    return page_text


def extended_auto_clean_page_text(page_text,method='pdfminer'):
    ### Clean formal reasons along with support tests
    
    #[100]  pdf tables joining amount with description even if try via ocr
    #1650059214Tc36,964.36
    # DEFINE:  if >=10k then add space to left of comma to right of non digit
    # COMMENTS: gpt-4 sometimes resolves space being there...

    #page_text=re.sub(r'(\d{5,})\,(\d{2})',r'\1 ,\2',page_text)
    page_text=re.sub(r'(\D)([\d]{1,3}\,[\d]{3}\.\d\d\b)',r'\1 \2',page_text) #>10 <100
    page_text=re.sub(r'(\D)([\d]{1,3}\,[\d]{1,3}\,[\d]{3}\.\d\d\b)',r'\1 \2',page_text) #>=100k

    return page_text


def dev_test_auto_clean():
    # !!!! moved to test_fix_page_artifacts.py

    ## TEST AT SPECIFIC LEVEL OR PAGE? OR BOTH?
    #>> basic for now is fine.

    #[x] 
    sample="""December 1, 2021 to December 31, 2021Your checking account"""
    out=auto_clean_page_text(sample)
    print ("GIVEN: "+str(sample))
    print ("CLEAN: "+str(out))
    if '2021Your' in out: raise Exception('failed')

    #[100]
    sample="""R8A6V7T8T9R3              Ind Name:Marner Holdings Inc Trn: 1650059214Tc36,964.36"""
    out=auto_clean_page_text(sample)
    print ("GIVEN: "+str(sample))
    print ("CLEAN: "+str(out))
    if 'c36' in out: raise Exception('failed')

    sample="""R8A6V7T8T9R3              Ind Name:Marner Holdings Inc Trn: 1650059214Tc136,964.36"""
    out=auto_clean_page_text(sample)
    print ("GIVEN: "+str(sample))
    print ("CLEAN: "+str(out))
    if 'c136' in out: raise Exception('failed')
    
    ## Help extractor for common but strange values:
    #a)  Space after negative on numbers:    - 2,331.44 -> -2,331.44
    sample=' - 2,331.44'
    out=auto_clean_page_text(sample)
    print ("GIVEN: "+str(sample))
    print ("CLEAN: "+str(out))
    if '- ' in out: raise Exception('failed')
#tbd    sample=' - $2,331.44'
#tbd    out=auto_clean_page_text(sample)
#tbd    if '- ' in out: raise Exception('failed')
    
    return


if __name__=='__main__':
    branches=['dev_test_auto_clean']
    for b in branches:
        globals()[b]()

