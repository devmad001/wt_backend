import os
import sys
import codecs
import json
from datetime import datetime
import re
import ast
import random

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")
sys.path.insert(0,LOCAL_PATH+"../../")

#from w_llm.llm_interfaces import LazyLoadLLM
#from alg_clean_transactions import adjust_transactions_top_level
#from schema_statement_kinds import dev_get_bank_schema
#from algs_extract import alg_json2dict

from w_pdf.pdf_extractor import alg_extract_pages_from_pdf
from w_pdf.pdf_process import interface_file2doc

from llm_page2transactions import llm_page2transactions

from get_logger import setup_logging
logging=setup_logging()


#0v2# JC  Feb  2, 2024  Yield actual page number (not offset)
#0v1# JC  Oct 13, 2023  Wells fargo has sections as headers.


"""
    CREATE TEST SETS
    - when adding various kinds of statements
    - Manual adjustments to base extractors need to be backwards compatible

"""


def pdf2subpages(input_pdf_filename,output_pdf_filename,keep_pages=[]):
    new_pdf_filename=alg_extract_pages_from_pdf(input_pdf_filename,output_pdf_filename,keep_pages=keep_pages)
    if not os.path.exists(new_pdf_filename):
        raise Exception("failed to create pdf file: "+new_pdf_filename)
    return

def pdf2epages(pdf_filename):
    ## Similar to main pipeline (but focusing in on unit test)
    
    ## Call and map
    print ("[ ] page_num value is wrong... want 8 but gives 9?")
    
    Doc=interface_file2doc(pdf_filename)
    epages=Doc.get_epages()
    
    c=-1
    for page_num in epages: #0...n-1
        for extraction_method in epages[page_num]:
            # pdfminer. pypdf2_tables
            content=epages[page_num][extraction_method]
#            print ("> "+str(extraction_method))
#            print ("CONTENT: "+str(content))
#            print ("")
            actual_page_num=page_num+1
            yield actual_page_num,extraction_method,content,epages[page_num]

    ## epage: per pdf_process is [0][extraction_method]=page_text
#    page_extractions=file_pages[filename_path]['epages'][page_number_index]
# extraction method

    return

def run_pdf2pdfpage2transactions_test(pdf_filename,target_page_num):
    ## Combine into one call (not as effecient but fine)
    print ("****NOT work maybe dup ocr or what??")
    print ("*processing full pdf to 1 pdf **ideally just processing 1 page pdf though")
    total_transactions=0
    meta={}

    count_processed=0
    counter=0
    for page_num,extraction_method,content,epage in pdf2epages(pdf_filename):
        counter+=1
        if not target_page_num==page_num: continue
        
#        if c>85 and c<92:
#            print (str(c)+" RAW: "+str(content))
#            print ("="*50)
#
        count_processed+=1

        all_transactions,meta=llm_page2transactions(epage=epage,bank_name='')
        total_transactions+=meta['transaction_count']
        
        print ("="*50+" at page!!")
#        break
        
    if not count_processed:
        print ("**warning no pages processed raw count: "+str(counter)+" looking for: "+str(page_num))

    meta={}
    return total_transactions,meta


def run_pdf_filename2transactions_test(pdf_filename,page_number=1):
    ## Assume only one page number

    total_transactions=0
    for page_num,extraction_method,content,epage in pdf2epages(pdf_filename):
        if not page_num==page_number:continue
        #        if extraction_method=='pdfminer': #** I think better one
        print ("[debug] run_pdf_filename2transactions_test page: "+str(page_num))
        
        ## Apply llm2page
        all_transactions,meta=llm_page2transactions(epage=epage,bank_name='')
        total_transactions+=meta['transaction_count']
        print ("="*50+" break at single page!!")
        break

    return all_transactions, meta

def run_page2transactions_test(pdf_filename):
    total_transactions=0
        
    for page_num,extraction_method,content,epage in pdf2epages(pdf_filename):
        #        if extraction_method=='pdfminer': #** I think better one
        
        ## Apply llm2page
        all_transactions,meta=llm_page2transactions(epage=epage,bank_name='')
        total_transactions+=meta['transaction_count']
        
        print ("="*50+" at page!!")
        break

    meta={}
    return total_transactions,meta

def load_test_set_configs():
    tts=[]

    ## Test/dev for now citizens bank
    tt={}
    tt['test_case_id']='new_kind_first_citizens_bank'
    tt['min_transaction_count']=37 #?

    tt['goals']=['validate page2transactions performance is stable']
    tt['goals']+=['3 columns of Checks Paid From Your Account']

    tt['raw_input_pdf_filename']=LOCAL_PATH+'../../w_ui/file_manager/storage/ColinTestCase/'+'Management-Properties-v-Brusko-Copy-of-First-Citizens-Bank-Checks-2020.pdf'
    tt['pages_to_keep']=[1]
    test_filename=tt['test_case_id']+"-"+os.path.basename(tt['raw_input_pdf_filename'])
    tt['target_filename']=LOCAL_PATH+"test_case_files/"+test_filename
    
    
    tts+=[tt]
    
    return tts


def test_run_page2transactions(tt):
    ## prepare test then set parameter, run test, test results
    
    ## Create test file
    if not os.path.exists(tt['target_filename']):
        logging.info("creating test file: "+tt['target_filename'])
        pdf2subpages(tt['raw_input_pdf_filename'],tt['target_filename'],keep_pages=tt['pages_to_keep'])
        
    ### RUN normal code
    total_transactions,meta=run_page2transactions_test(tt['target_filename'])
    
    if int(total_transactions)<int(tt['min_transaction_count']):
        raise Exception("Too few transactions -- likely missed multiple columns at: "+tt['target_filename'])
    else:
        print ("MIN: "+str(tt['min_transaction_count'])+"  ACTUAL: "+str(total_transactions))
        wadd=whattt

    return


def test_run_all_page2transactions():
    tts=load_test_set_configs()
    
    for tt in tts:
        test_run_page2transactions(tt)
    return

def test_blob_vs_p2t():
    
    ## AMAZON OUTPUT PAGE TEXT
    page_text="""
    
FirstCitizens Bank Central Bank Operations - DAC02 P.O. Box 27131 Raleigh, NC 27611-7131 IM 727 14617 MANAGEMENT PROPERTIES INC OPERATING ACCT Your Account(s) At A Glance 27286 VIA INDUSTRIA STE B TEMECULA CA 92590-3751 Checking Balance 204,755.45+ Statement Period: January 1 , 2020 Thru January 31, 2020 Account Number : 001064017308 Basic Business Checking Account Number : 001064017308 Enclosures In Statement: 0 N.ELMA MAIN ST. Beginning Balance 255,964.05+ Statement Period Days 31 3 Deposits 48,921.75+ Average Ledger Balance 242,593.00+ 0 Other Credits 0.00 37 Checks 96,927.02- 4 Other Debits 3,203.33- Monthly Service Charge 0.00 Ending Balance 204,755.45+ Deposits To Your Account Date Amount Date Amount Date Amount 01-07 151.20 01-07 48,619.35 01-28 151.20 Checks Paid From Your Account Check No. Date Amount Check No. Date Amount Check No. Date Amount 01-17 445.61 10124 01-14 639.56 10138 01-16 2,351.94 10059 01-06 2,567.64 10125 01-17 1,935.70 10139 01-15 1,543.30 10107* 01-06 9,494.07 10126 01-16 709.95 10140 01-17 2,576.12 10112* 01-09 3,000.00 10127 01-13 321.88 10141 01-24 4,596.27 10114* 01-07 350.00 10128 01-14 310.05 10143* 01-29 208.87 10116* 01-02 4,155.25 10130* 01-17 852.14 10144 01-28 270.60 10117 01-13 270.87 10131 01-17 12,900.69 10145 01-28 3,000.00 10118 01-09 151.20 10132 01-17 17,722.77 10147* 01-29 151.20 10119 01-06 3,275.75 10133 01-17 4,725.75 10148 01-31 311.42 10120 01-16 120.00 10134 01-17 393.50 10150* 01-30 173.39 10121 01-10 4,475.75 10135 01-17 1,903.22 10151 01-29 3,975.75 10122 01-17 120.00 10136 01-22 2,351.94 10123 01-30 299.12 10137 01-24 4,275.75 *Prior Check Number(s) Not Included or Out of Sequence. Other Debits From Your Account Date Description Amount 01-16 Irs Usataxpymt 7689 50.70 01-16 Irs Usataxpymt 8008 2,236.68 01-17 Employment Devel Edd Eftpmt 0768 910.95 01-31 Paper Statement Fee 5.00 Total 3,203.33 Direct Customer Inquiry Calls To UP FIRST CITIZENS DIRECT Telephone Banking At 1-888-323-4732. Page 1 of 8 FirstCitizens Bank Central Bank Operations - DAC02 P.O. Box 27131 Raleigh, NC 27611-7131 IM 727 14617 MANAGEMENT PROPERTIES INC OPERATING ACCT Your Account(s) At A Glance 27286 VIA INDUSTRIA STE B TEMECULA CA 92590-3751 Checking Balance 204,755.45+ Statement Period: January 1 , 2020 Thru January 31, 2020 Account Number : 001064017308 Basic Business Checking Account Number : 001064017308 Enclosures In Statement: 0 N.ELMA MAIN ST. Beginning Balance 255,964.05+ Statement Period Days 31 3 Deposits 48,921.75+ Average Ledger Balance 242,593.00+ 0 Other Credits 0.00 37 Checks 96,927.02- 4 Other Debits 3,203.33- Monthly Service Charge 0.00 Ending Balance 204,755.45+ Deposits To Your Account Date Amount Date Amount Date Amount 01-07 151.20 01-07 48,619.35 01-28 151.20 Checks Paid From Your Account Check No. Date Amount Check No. Date Amount Check No. Date Amount 01-17 445.61 10124 01-14 639.56 10138 01-16 2,351.94 10059 01-06 2,567.64 10125 01-17 1,935.70 10139 01-15 1,543.30 10107* 01-06 9,494.07 10126 01-16 709.95 10140 01-17 2,576.12 10112* 01-09 3,000.00 10127 01-13 321.88 10141 01-24 4,596.27 10114* 01-07 350.00 10128 01-14 310.05 10143* 01-29 208.87 10116* 01-02 4,155.25 10130* 01-17 852.14 10144 01-28 270.60 10117 01-13 270.87 10131 01-17 12,900.69 10145 01-28 3,000.00 10118 01-09 151.20 10132 01-17 17,722.77 10147* 01-29 151.20 10119 01-06 3,275.75 10133 01-17 4,725.75 10148 01-31 311.42 10120 01-16 120.00 10134 01-17 393.50 10150* 01-30 173.39 10121 01-10 4,475.75 10135 01-17 1,903.22 10151 01-29 3,975.75 10122 01-17 120.00 10136 01-22 2,351.94 10123 01-30 299.12 10137 01-24 4,275.75 *Prior Check Number(s) Not Included or Out of Sequence. Other Debits From Your Account Date Description Amount 01-16 Irs Usataxpymt 7689 50.70 01-16 Irs Usataxpymt 8008 2,236.68 01-17 Employment Devel Edd Eftpmt 0768 910.95 01-31 Paper Statement Fee 5.00 Total 3,203.33 Direct Customer Inquiry Calls To UP FIRST CITIZENS DIRECT Telephone Banking At 1-888-323-4732. Page 1 of 8
    """
    
    ## GOOGLE OUTPUT PAGE TEXT
    page_text="""
    First Citizens Bank
Central Bank Operations - DAC02
P.O. Box 27131
Raleigh, NC 27611-7131
14617
MANAGEMENT PROPERTIES INC
OPERATING ACCT
Date
01-07
27286 VIA INDUSTRIA STE B
TEMECULA CA 92590-3751
Statement Period: January 1, 2020 Thru January 31, 2020
Basic Business Checking
Account Number: 001064017308
N.EL MA
MAIN ST.
Beginning Balance
3 Deposits
0 Other Credits
37 Checks
4 Other Debits
Monthly Service Charge
Ending Balance
W
Deposits To Your Account
Amount
Date
151.20 | 01-07
01-17
10059 01-06
10107* 01-06
10112* 01-09
10114* 01-07
10116* 01-02
10117 01-13
10118 01-09
10119 01-06
10120 01-16
10121 01-10
10122 01-17
10123 01-30
*Prior Check Number(s) Not Included or Out of Sequence.
Amount
445.61
2,567.64
9,494.07
3,000.00
350.00
4,155.25
Date
01-16 Irs Usataxpymt
01-16 Irs Usataxpymt
Checks Paid From Your Account
Check No. Date
Check No. Date
270.87
151.20
3,275.75
120.00
4,475.75
120.00
299.12
255,964.05+
48,921.75+
0.00
***********7689
IM
727
96,927.02-
3,203.33-
0.00
***********
204,755.45+
Other Debits From Your Account
Description
**8008
01-17 Employment Devel Edd Eftpmt *****0768
01-31
Paper Statement Fee
Total
10124 01-14
10125 01-17
10126 01-16
10127 01-13
10128 01-14
10130* 01-17
10131 01-17
10132 01-17
10133 01-17
10134 01-17
10135 01-17
10136 01-22
10137 01-24
Direct Customer Inquiry Calls To
FIRST CITIZENS DIRECT
Telephone Banking At 1-888-323-4732.
Statement Period Days
Average Ledger Balance
Amount
48,619.35
Amount
639.56
1,935.70
709.95
321.88
310.05
852.14
12,900.69
17,722.77
4,725.75
393.50
1,903.22
2,351.94
4,275.75
|
Your Account(s) At A Glance
Checking
Balance
Account Number : 001064017308
Enclosures In Statement: 0
Date
01-28
Check No. Date
10138 01-16
10139 01-15
10140 01-17
10141
204,755.45+
01-24
10143* 01-29
10144
01-28
10145 01-28
10147* 01-29
10148 01-31
10150* 01-30
10151 01-29
31
242,593.00+
Amount
151.20
Amount
2,351.94
1,543.30
2,576.12
4,596.27
208.87
270.60
3,000.00
151.20
311.42
173.39
3,975.75
Amount
50.70
2,236.68
910.95
5.00
3,203.33
Page 1 of 8
"""

    total_transactions=0
    all_transactions,meta=llm_page2transactions(page_text=page_text)

    total_transactions+=meta['transaction_count']
    print ("="*50+" at page!!")
    
    return


if __name__=='__main__':
    branches=['dev1']
    branches=['test_blob_vs_p2t']
    branches=['test_run_all_page2transactions']
    for b in branches:
        globals()[b]()


"""
"""