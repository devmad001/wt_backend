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

from w_llm.llm_interfaces import LazyLoadLLM
from alg_clean_transactions import adjust_transactions_top_level
from alg_easy_extracts import alg_get_page_year

from schema_statement_kinds import dev_get_bank_schema
from fix_page_artifacts import auto_clean_page_text

#from algs_extract import alg_json2dict

from get_logger import setup_logging
logging=setup_logging()


#0v1# JC  Jan 15, 2024  Migrate common functions from llm_page2transactions


"""
    COMMON FUNCTIONS FOR LLM PAGE 2 TRANSACTIONS
"""


## Global defs
Config = ConfigParser.ConfigParser()
Config.read(LOCAL_PATH+"../w_settings.ini")
SMARTEST_MODEL_NAME=Config.get('performance','smartest_llm_name')

BANKS_SCHEMA=dev_get_bank_schema()


def force_manual_page_fixes(page_text,year=''):
    ##[A]  AUTO EXTEND (include) Year
    ##[B]  APPLY regex from schema_statement_kinds
    global BANKS_SCHEMA

    ## Case FCB OCR has too many OCR errors to extract all check numbers so infer date and do auto swap where possible
    ## ASSUMPTION AT FCB
    #>> tt['test_case_id']='new_kind_first_citizens_bank'

    #[1])  Take year from statement header and place into check date
    """
    Statement Period: January 1, 2020 ~~ Thru January 31, 2020 Account Number : 001064017308
    Checks Paid From Your Account
    Check No. Date Amount Check No. Date Amount Check No. Date Amount
    041-17 445.61 140124 01-14 639.56 10138 01-16 2,351.94
    [ ] watch because first cell is missing check no so will miss adding this date as well
    """
    
    year=alg_get_page_year(page_text)

    logging.info("[generic year extract] as : "+str(year))
    
    ## 101# Chase Chase Statements 2_b.pdf (or distant page has no ref to year)
    #i)  use generic year extractor and apply to date expected format
    
    if re.search(r'\bCHASE',page_text) and year:
        #mm/dd --> yyyy/mm/dd
        page_text=re.sub(r'\b(\d\d\/\d\d)\b',year+"/"+r"\1",page_text)

    ## 102#  Chase year adjust
    if 'Checks Paid From Your Account' in page_text:
        year=alg_get_page_year(page_text)
        if year:
            ## Do double rather then look back
            
            page_text=re.sub(r' (\d\d)-(\d\d) '," "+str(year)+r'-\1-\2 ',page_text)
#            page_text=re.sub(r'(\d\d)-(\d\d) '," "+str(year)+r'-\1-\2 ',page_text)
            #BAD# page_text = re.sub(r'(?<= |\A)(\d\d)-(\d\d)(?=\D)', str(year) + r'-\1-\2', page_text)
    
    ##########################
    # APPLY resubs from schema_statement_kinds
    ##########################
    #- easy to tweak but ideally should never need to

    #[A]  Apply re.sub ie:     if 'CHASE' in text and ' - 18.82' -> '-18.82' pdf oddity
    for bank_kind in BANKS_SCHEMA['banks']:
        for re_sub in BANKS_SCHEMA['banks'][bank_kind].get('re_subs',[]):
            ## PAGE-LEVEL MATCH
            if re.search(re_sub[0],page_text): #ie/ CHASE
                before=copy.deepcopy(page_text)
                page_text=re.sub(re_sub[1],re_sub[2],page_text)
                
#D#                if not before==page_text:
#D#                    logging.info("MODIFIED PAGE FROM: "+str(before)+" to: "+str(page_text))
#D#                    a=okkk

    return page_text


###############################################

def local_epage2page_text(epage,bank_name=''):
    #0v2# Nov 22, 2023  If OCR force all, will resolve layout issues that pypdf2_tables had issue with
    
    ASSUME_OCR_DOCUMENT=True
    method='default'
    
    if ASSUME_OCR_DOCUMENT:
        method='default'
    else:
        ####> THESE EXCEPTIONS REQUIRED MAYBE IF NOT OCR
        #page_text=epage.get('pdfminer') #pypdf2_tables
        ## SOMETIMES NORMAL PDF2TEXT doesn't work.  Custom logic
        ### Logic branch for choosing pdf2txt method
        ## pdf2txt preference based on bank type
        if 'chase' in bank_name.lower():
            method='pdfminer'
        ## LOGIC: Checks paid is likely chase which does headers at start
        elif 'Checks Paid' in epage.get('pypdf2_tables'):
            logging.info("[request to use pdfminer cause _tables puts section headings at top of page]")
            method='pdfminer'

    logging.info("=====================================")
    logging.info("= SELECT PDF2text METHOD:  (default is pypdf2_tables) "+str(method))
    logging.info("=====================================")
    

    if method=='default':
        page_text=epage.get('pypdf2_tables') #pypdf2_tables
        print ("="*40)
        
        ## Watch 
#        try:
#            print ("[debug] pypdf2_tables: "+str(page_text))
#        except:
#            page_text=page_text.encode('utf-8', errors='replace').decode('utf-8')  #Hot encode if not already
#        

    elif method=='pdfminer':
        page_text=epage.get('pdfminer') #pypdf2_tables    POSSIBLE IS NONE!!!
        print ("="*40)
#        print ("[debug] pdfminer: "+str(page_text))
        ### LOCAL PATCH IF WANT TO DO pdfminer but can't -- do alternative hard coded
        if page_text is None:
            logging.warning("[warning] no page text foundn using pdfminer!!  Default to pypdf2_tables at: "+str(epage))
            logging.dev("[warning] no page text foundn using pdfminer!!  Default to pypdf2_tables at: "+str(epage))
        page_text=epage.get('pypdf2_tables') #pypdf2_tables

    else:
        raise Exception("[error] invalid method: "+str(method))
    
    ### AUTO CLEAN
    #MVED# page_text=auto_clean_page_text(page_text,method=method)
    
    return page_text


## Note:  neo4j will try to insert but may as well check if valid from start
def is_normal_valid_date(date_str, format="%Y-%m-%d"):
    try:
        datetime.strptime(date_str, format)
        return True
    except: #ValueError ** may be type error like float.  Have catch all
        return False
            
    
def estimate_number_of_transactions_on_page(page_text):
    ##[A] FARGO
    """
    12/10    Bill Pay Cobb Emc on-Line xxxx87002 on 12-10    46.00
    12/10    Bill Pay TDS Telecom on-Line xxxxx83692 on 12-10        89.59
    12/10    Bill Pay Card Services on-Line Xxxxxxxxxxx51678 on 12-10        100.00
    """
    pattern = r'^\s*\d\d\/\d\d[ ]+.*\d\.'   #12/10
    fargo_matching_rows=0
    chase_matching_rows=0
    for row in page_text.splitlines():
        cols_on_row=len(row.split())
        if re.search(pattern, row.strip(),flags=re.I):  #** match is only at beginning of line
            if cols_on_row>2: #Require more then 2 columns for transaction (otherwise likely summary)
                fargo_matching_rows+=1
                
    pattern = r'^\s*(\d{2,4}/\d{2}/\d{2,4})\s+.*\d'
    fargo_matching_rows=0
    for row in page_text.splitlines():
        cols_on_row=len(row.split())
        if re.search(pattern, row.strip(),flags=re.I):  #** match is only at beginning of line
            if cols_on_row>2: #Require more then 2 columns for transaction (otherwise likely summary)
                fargo_matching_rows+=1
                

    ##[B]  Chase
    ## (i)  count date at start
    chase_matching_rows=0
    if re.search(r'chase',page_text,flags=re.I):
        """
        12/10    Bill Pay Cobb Emc on-Line xxxx87002 on 12-10    46.00
        12/10    Bill Pay TDS Telecom on-Line xxxxx83692 on 12-10        89.59
        12/10    Bill Pay Card Services on-Line Xxxxxxxxxxx51678 on 12-10        100.00
        2023/12/10    Bill Pay Card Services on-Line Xxxxxxxxxxx51678 on 12-10        100.00
        """
        #pattern = r'^\s*\d{0,4}[/]{0,1}\d{1,2}/\d{1,2}\s+.*\d' 
        pattern = r'^\s*\d{0,4}[/]{0,1}\d{1,2}/\d{1,2}\s+.*\w'    #Sometimes rows like:  12/10  DESCRIPTION so still need to catch
        for row in page_text.splitlines():
            cols_on_row=len(row.split())
            if re.search(pattern, row.strip(),flags=re.I):  #** match is only at beginning of line
                logging.info("[debug chase estimate number of transactions] counted row match "+str(row.strip()))
                chase_matching_rows+=1
    ## (ii)  Look for mentioned phrases
    max_chase=max(len(re.findall(r'YOUR REF\:',page_text)),len(re.findall(r'Trn\:',page_text)),chase_matching_rows)

    
    ##[C] FirstCitizensBank with many checks
    #   01-14 323,233.00  <-- date then amount
    max_fcb=len(re.findall(r'\d\d-\d\d[\s ]+[\d\,]+\.\d\d',page_text))  ## COUNT DATES OR AMOUNTS
    
    ##[D] schoolkidz [ ]TODO misses extra dates
    """
        12/29/21 CHECKCARD  1228 ZIPRECRUITER, INC. 8557475493   CA
        24492151362717143566815 CKCD 7361 XXXXXXXXXXXX6164 XXXX
        XXXX XXXX 6164929912281129508 9.99
        Subtotal for card account # XXXX XXXX XXXX 6164 $ 8,075.80
        Total withdrawals and other debits - $ 643,763.82
        Checks
        Date Check # Bank reference Amount Date Check # Bank reference Amount
        12/13 92441 813004592720485 -693.36 12/01 93149* 813009292293542 -758.44
    """
    ## COUNT BOA Bank Reference numbers
    if 'Bank reference' in page_text:
        # 929912153726831  length 15
        boa_ref_counts=len(re.findall(r'\b[\d]{15}\b',page_text))
    else:
        boa_ref_counts=0
    
    estimated_transactions=max(fargo_matching_rows,max_chase,max_fcb,boa_ref_counts)

    logging.info("[estimated_transactions on page] "+str(estimated_transactions))
    return estimated_transactions


def alg_force_skip_page(page_text, skip_regexes=[]):
    ## See schema_statement_kinds (per bank lookups)
    reasons=[]
    skip_it=False
    for regex in skip_regexes:
        # or DOTALL
        if re.search(regex,page_text,flags=re.DOTALL|re.I):
            skip_it=True
            reasons+=['regex: '+str(regex)]
    return skip_it,",".join(reasons)



def split_complicated_pages(page_text):
    #> mix of checks (3 columns and withdrawls 1 column causes confusion)
    #> that one sample had 76 transactions!

    sub_pages=[]
    did_split=[]
    
    ## [A]  SPLIT AT Checks Paid section (Chase) because it's 3 columns
    #[ ] CHASE
    ### Look for HEADING of Checks Paid NOT line item.  Line item will have number on next line

    blobs=re.split(r'\nChecks Paid\n',page_text,flags=re.I)
    #ii) If looks like line item then skip
    if re.search(r'\nChecks Paid\n\d',page_text,flags=re.I):
        logging.info("[split_complicated_pages] looks like line item so skip")
        blobs=[page_text]

    if len(blobs)==1: #No split
        pass
    elif len(blobs)>2:
        raise Exception("[error] too many blobs: "+str(len(blobs)))
    elif len(blobs)==2:
        did_split+=['Checks Paid']
        sub_pages+=[blobs[0]]
        sub_pages+=["Checks Paid\n"+blobs[1]]
        logging.info("[split_complicated_pages] split at Checks Paid!")
        logging.info("[split page]="*40+"ONE: "+str(sub_pages[0]))
        print ("[split page]="*40+"TWO: "+str(sub_pages[1]))
    else:
        raise Exception("[error] no split at Checks Paid: "+str(len(blobs)))
    
    ## Default
    if not sub_pages:
        sub_pages+=[page_text]

    logging.info("[complicated page *may have split into: "+str(len(sub_pages))+" pages]")
    return sub_pages




def alg_insert_bullet_point(text, new_bullet):
    # 0v1# Ensure there's a newline at the end of the new bullet
    if not new_bullet.endswith('\n'):
        new_bullet += '\n'

    # Search for the last occurrence of a bullet point
    match = list(re.finditer(r'^[ ]*\-', text, re.MULTILINE))[-1]

    # Find the end of the line where the last bullet point is
    line_end = text.find('\n', match.start())

    # Insert the new bullet point after the line of the last occurrence
    updated_text = text[:line_end+1] + '   ' + new_bullet + text[line_end+1:]
    
    return updated_text

def dev_test_auto_clean():
    sample="""December 1, 2021 to December 31, 2021Your checking account"""
    out=auto_clean_page_text(sample)
    print ("GIVEN: "+str(sample))
    print ("CLEAN: "+str(out))
    
    return


if __name__=='__main__':
    branches=['dev_test_auto_clean']
    for b in branches:
        globals()[b]()

