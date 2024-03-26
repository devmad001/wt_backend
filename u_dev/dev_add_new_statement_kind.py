import os
import sys
import time
import codecs
import json
import re

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")

from pypher import __, Pypher
from w_storage.gstorage.gneo4j import Neo

from a_agent.RUN_sim_wt import call_normal_full_run
from a_agent.sim_wt import wt_main_pipeline

from a_query.queryset1 import query_statements
from a_query.queryset1 import query_transaction
from a_query.queryset1 import query_transactions
from a_query.admin_query import admin_remove_case_from_kb

from get_logger import setup_logging
logging=setup_logging()


#0v2# JC  Oct 25, 2023  Required upgrade to tesseract. retry
#                         - see integrated test via: /w_pdf/ocr_development/test_ocr.py
#                         - downsample pdf (1200 to 400 now processes 100 pager in 22m (not 60m conversion only))

#0v1# JC  Oct 19, 2023  Init


"""
    ENTRY AND NOTES FOR ADDING NEW STATEMENT KIND:
    FirstCitizensBank
    
    - detailed notes on exceptions and concerns to note
"""


def dev_manually_validate_new_statement_kind():
    options=[]
    options+=['run one page']
    options+=['run till fail']
    options+=['run run validation self qa']
    
    ## Case
    #- 100 pages (was image pdf)
    #- 

    case_id='ColinTestCase'
    
    """
    ISSUE 1:  fails at date format insert in neo
        raise Neo4jError.hydrate(**metadata)
        neo4j.exceptions.CypherSyntaxError: {code: Neo.ClientError.Statement.SyntaxError} {message: Invalid value for DayOfMonth (valid values 1 - 28/31): 41}
        
        TRANSACTIONS
{'all_transactions': [{'transaction_description': 'Beginning Balance', 'transaction_amount': 293677.26, 'transaction_date': '2020-03-41', 'section': ''}, {'transaction_description': 'Deposits To Your Account | Date Amount Date Amount Date Amount | 03-14 16.18 03-12 50409.51 03-27 2800.00 | 03-14 920.214 03-27 4541.20', 'transaction_amount': '', 'transaction_date': '', 'section': 'Deposits'}, {'transaction_description': 'Checks Paid From Your Account | Check No. Date Amount Check No. Date Amount Check No. Date Amount | 10480 63-04 328.73 40201" 03-1410 1407.86 10214 03-17 193 | 10481 03-05 85.00 40202 03-10 920.24 40215 063-20 4865. | 140182 063-04 473.25 40203 03-17 639.56 40216 03-23 4541.20 | 10483 03-02 235.94 140204 03-16 275.58 40217 063-20 3476.50 | 10484 03-02 2/0.60 10205 03-23 852.414 10218 03-25 4665.25 | 10186* 03-06 423.15 140206 03-16 373.93 40219 03-31 328.73 | 10487 03-16 1976.01 40207 03-413 2204.43 40220 03-31 208.87 | 10194" 03-144 699.39 40208 03-412 1346.24 402241 03-27 3000.00 | 10495 03-602 4175.25 40209 03-413 2576.12 140223” 03-30 2660.00 | 10496 03-06 300.00 40210 03-23 484.00 140225* 03-31 4534.32 | 140197 063-1411 252.83 4021414 063-412 4675.75 40226 03-31 2576.13 | 10498 03-09 4725.75 40212 03-417 3241.00 | 10499 03-17 420.00 40213 03-417 4425.75 | “Prior Gheck Number(s) Not Included or Out of Sequence.', 'transaction_amount': '', 'transaction_date': '', 'section': 'Checks'}]}
[found 3 transactions]
[debug gneo4j] 3 nodes were created.
LINKING_LINKING:
            MATCH (bs:BankStatement {id: 'ColinTestCase-2020-03-41-001064017308-Management-Properties-v-Brusko-Copy-of-First-Citizens-Bank-Checks-2020.pdf'}), (t:Transaction {id: '8cda0d8dad1623572c405cd15105149d1d161eb898192756b0127a98e56cc3bb'})
            MERGE (bs)-[r:HAS_TRANSACTION]->(t)
            ON CREATE SET r.transaction_date = date('2020-03-41')

JC THOUGHTS:  check date formats during extraction... if problem, use better gpt4 immeidately (may also be other problems).
--> llm_page2transactions.py -> validate_transactions -> look at dates

JC FIRST ADJUSTMENT:
- if on 3rd try then boost to gpt-4 model.

#2 adjustment.  Check for FirstCitizensBank where could be 3 coluns
>> add schema for multiple bank suggestions.


>> continue at run specific trial on page 1
    """

    return

def run_local_trial():
    if True:
        case_id='ColinTestCase'
        case_id='ColinTestCase1Page'
        case_id='ColinFCB1'

        if case_id=='ColinTestCase':
            print ("**beware possible cashe on pdf2txt cause thinks starts w 4")

        options={}
        options['only_pages']=[1]
        options['only_pages']=[]

        manual_skip_caps=['start_KBAI_processing_pipeline']
        manual_skip_caps=[]

        meta=wt_main_pipeline(case_id=case_id,options=options,manual_skip_caps=manual_skip_caps)

    return

def dev_attempt_2_new_ocr_on_FCB():
    return


if __name__=='__main__':
    branches=['dev_manually_validate_new_statement_kind']
    branches=['dev_attempt_2_new_oocr_on_FCB']
    branches=['run_local_trial']

    for b in branches:
        globals()[b]()




"""
Use JPM unique idenfiier on transaction?
 "receiver_id": "951) 2242099 Jpm696293969",


//  sample BOA withdrawls
            "section": "Withdrawals and other debits",			
WIRE TYPE:WIRE OUT DATE:211201 TIME:1724 ET\nTRN:2021120100554721 SERVICE REF:527479\nBNF:PAYCHEX, INC ID:512068399 BNF\nBK:JPMORGAN CHAS E BANK, N. ID:0002 PMT\nDET:21C1F14252DW2T361607-81 06 NewNet903712010554721			
AMERIFLEX LLC    DES:PPDFUNDING\nID:00000003841974  INDN:NewNet Secure\nTransact  CO ID:1223639401 PPD902535029125818			


// BOA lots of wire transfers
A lot of weird transactions					
	see:		file:///C:/scripts-23/watchtower/Watchtower%20Solutions%20AI/Bank%20Statements%20-%20for%20Beta%20Testing/Dec%2031%202021%20NST%20BOA%20Bank%20Statement.pdf		



"""
