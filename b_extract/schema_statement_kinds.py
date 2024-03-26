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

from get_logger import setup_logging
logging=setup_logging()


#0v2# JC  Oct 31, 2023  Skip request check image pages (Chase)
#0v1# JC  Oct 13, 2023  Wells fargo has sections as headers.

"""
    CAPTURE VARIATIONS BETWEEN STATEMENT KINDS
"""


def dev_get_bank_schema():
    ## Note differences (may not suggest them all)
    
    ### BANK KIND
    #                                      only first page
    kindregexes=[]
    kindregexes=[('first_citizens_bank',[r'FirstCitizensBank',r'FIRST CITIZENS DIRECT'])]
    kindregexes=[('wells_fargo',[r'Wells Fargo',r'Wells Fargo'])]
    

    ### BANK KIND NUANCES
    banks_schema={}
    banks_schema['version']=1
    banks_schema['banks']={}
    
    FC={}
    CHASE={}
    BOA={}
    WELLSFARGO={}
    
    CHASE['bullets']=[]

    ###############################################
    ##    SECTIONS
    ###############################################
    #[ ] see llm_page2transactions -> suggest headings
    
    ###  first_citizens_bank  SECTIONS
    FC['section_headings']=['Deposits To Your Account','Checks Paid From Your Account','Other Debits From Your Account']
    
    ###  chase sections
    CHASE['section_headings']=['ATM & DEBIT CARD WITHDRAWLS','CASH TRANSACTIONS','ELECTRONIC WITHDRAWALS']
    CHASE['section_headings']+=['FEES','OTHER WITHDRAWALS'] #jNov23# could be 1 line and easily missed
    
    ###  BOA
    BOA['section_headings']=['Transaction Detail','Deposits and other credits','Deposits and other credits','Withdrawals and other debits','Checks']

    WELLSFARGO['section_headings']=['Transaction history','Withdrawals/Subtractions','Fees','Checks','Deposits/ Additions']

    
    ###############################################
    ##    SAMPLES
    ###############################################
    #** FCB really the only one with samples
    #** include 3 samples that match bullet
    #ONE#  FC['samples']=[(r'Checks Paid From Your Account',[{'transaction_description':'Check No. 10490','transaction_amount':'2253.09','transaction_date':'2022-12-13','section':'Checks Paid'}])]

    ss=[]
    #FC['bullets']=[(r'Check No\..*Check No\..*Check No\.',['- NOTE:  There are three columns of check transactions (Check No. mm-dd amount). So this line is 3 transactions: 84322 02-29 3,443.11 115432* 01-29 1,400.30 00332 02-13 443.50'])]
    
    ## D2: Requires these specifics EVEN with dividers and other suggestsions!
    ss+=[{'transaction_description':'Check No. 84322','transaction_amount':'3,443.11','transaction_date':'2020-02-29','section':'Checks Paid'}]
#Too many    ss+=[{'transaction_description':'Check No. 115432','transaction_amount':'1,400.30','transaction_date':'2020-01-29','section':'Checks Paid'}]
#Too many    ss+=[{'transaction_description':'Check No. 00332','transaction_amount':'443.50','transaction_date':'2020-02-13','section':'Checks Paid'}]
    FC['samples']=[(r'Checks Paid From Your Account',ss)]
    
    BOA['samples']=[(r'Bank reference',[{'transaction_description':'Check No. 10490','transaction_amount':'2253.09','transaction_date':'2022-12-13','section':'Checks Paid'}])]

    ###############################################
    ##    ENFORCE SMARTEST GPT IF...
    #- ie/ if common complicated or important page like first page etc.
    ###############################################


    ###############################################
    ##    BULLETS
    ###############################################
    #>  Give bullet point suggestions on LLM
    
    #[1]#  Not required but Check area:  3 columns,
    #**has a difficult time!
    multib=[]
    multib+=['- NOTE:  There are three columns under "Checks Paid From Your Account": (Check No. yyyy-mm-dd amount). So, for example, this line is 3 transactions per line: 84322 2020-02-29 3,443.11 115432 2020-01-29 1,400.30 00332 2020-02-13 443.50 --> {"transaction_description":"Check No. 84322","transaction_amount":"3,443.11","transaction_date":"2020-02-29","section":"Checks Paid"},{"transaction_description":"Check No. 115432","transaction_amount":"1,400.30","transaction_date":"2020-01-29","section":"Checks Paid"},{"transaction_description":"Check No. 00332","transaction_amount":"443.50","transaction_date":"2020-02-13","section":"Checks Paid"}']
    multib+=['- Ensure that all transactions listed under "Checks Paid From Your Account" are included, capturing each check number, date, and amount accurately.']
    
    ## !! Difficult because sample is missing Check No. in cell 1,1,
#too much?#    multib+=['- If the check number is missing, enter "Unknown"']

    #[ ] matcher option at Check Paid From Your Account ie/ if 1 or 2 columns?

    FC['bullets']=[(r'Check No\..*Check No\..*Check No\.',multib)]


    ## Chase (ie/ chase_4_a page 24 pulling in transactions from summary table so say skip!)
    multib=['- Ignore summary sections like: SERVICE CHARGE SUMMARY or DAILY ENDING BALANCE or CHECKING SUMMARY']
    CHASE['bullets']+=[(r'SUMMARY',multib)]

    multib=['- Fees are generally sender_entity_name="main_account"']
    CHASE['bullets']+=[(r'\bfee\b',multib)]
    
    ## Chase CHECKING SUMMARY not in proper place which leads to Ending Balance etc showing up
    #(Dec 13, 2023)
    #Jan 31 worse to NOT explain that it's a SECTION # multib=['- CHECKING SUMMARY items are NOT transactions. Ignore summary items like: Beginning Balance, Deposits and Additions, Other Withdrawls, Ending Balance, Interest Paid this Period, etc']
    multib=['- The "CHECKING SUMMARY" section items are NOT transactions. Ignore summary items like: Beginning Balance, Deposits and Additions, Other Withdrawls, Ending Balance, Interest Paid this Period, etc']
    #** optionally add more
    CHASE['bullets']+=[(r'CHECKING SUMMARY',multib)]
    
    ##  Chase CHECKS PAID causing problems with multiple columns while it's not even supposed to be 
    #(Dec 14, 2023)
    #  input_filename='C:/scripts-23/watchtower/CASE_FILES_STORAGE/storage/6579bfd30c64027a3b9f2d3c/62eac7ab-388c-4ff0-802e-65e96fedbd29.pdf'
    multib=['- CHECKS PAID items are NOT transactions. They are a summary of the checks (which are in the transaction detail section. Ignore these columns of check summary data which usually ends with: Total Checks Paid.']
    CHASE['bullets']+=[(r'CHECKS PAID',multib)]
    
    ## Wells fargo do explicit non sections:
    #Not section:  'Summary of checks written'
    WELLSFARGO['bullets']=[]

    ## WELLS needs to ignore summary sections cause things entries are picked up as transactions so be verbose
    #weak    WELLSFARGO['bullets']+=[(r'Activity summary',["- Ignore the entire 'Activity summary' section: (they are not transactions)"])]
    WELLSFARGO['bullets']+=[(r'Activity summary',["- Ignore the entire 'Activity summary' area these are summaries not transactions.  Ignore: Deposits/Additions, Withdrawals/Subtractions, Ending daily balance."])]
    WELLSFARGO['bullets']+=[(r'Statement period activity summary',["- Ignore the entire summary section: Statement period activity summary (they are not transactions)"])]
    WELLSFARGO['bullets']+=[(r'Summary of checks',["- Ignore the entire summary section: Summary of checks written (they are not transactions)"])]
    WELLSFARGO['bullets']+=[(r'Monthly service fee summary',["- Ignore the entire summary section: Monthly service fee summary (They are not transactions)"])]
    WELLSFARGO['bullets']+=[(r'ee summary',["- Ignore the entire summary section: Fee summary (They are not transactions)"])]
    

    ## Note: BOA is Account summary on first page (Not Activity)
    BOA['bullets']=[]
    
    #*Account summary is an image in some cases so can't apply this so duplicate or use separate
    BOA['bullets']+=[(r'Account summary',["- Ignore the entire 'Account summary' area these are summaries not transactions.  Ignore: Beginning balance, Deposits and other credits, Checks, Service fees, Withdrawals and other debits, Ending balance, etc."])]
    BOA['bullets']+=[(r'Your Business Fundamentals',["- This first page of the statement has a summary section IGNORE the summary lines: Beginning balance on.., Deposits and other credits, Checks, Service fees, Withdrawals and other debits, Ending balance, etc (they are NOT transactions)."])] #* Jan 8, 2024 works when VERY explicit.
    
    ##> 
    # Feb 2, 2024
    #- missing double column checks?
    #Date Check # Bank reference Amount Date Check # Bank reference Amount
    #[ ] not needed after clarified that Checks was a section but keep anyways
    BOA['bullets']+=[(r'Bank reference Amount Date',["- The Checks section has TWO COLUMNS of check transactions."])]


    ## Transaction history may have odd column alignment so be firm on how many
    #BAD DISTRACTS AND THINKS transaction history is a section    WELLSFARGO['bullets']+=[(r'Transaction history',["- the Transaction history table has 6 columns: Date, Check Number, Description, Deposits/Additions, Withdrawals/Subtractions, Ending daily balance."])]


    
    ###############################################
    ##    SKIP ENTIRE PAGES
    ###############################################
    #- if known filler text
    #- why?  to increase throughput
    #?? all banks or specific.
    #- assume dotall!
    #- see llm_page2t

    skip_entire_page_regex=[]
    skip_entire_page_regex+=['FOLLOW THESE EASY STEPS TO BALANCE YOUR CHEKCING']                #first_citizens_bank
    skip_entire_page_regex+=['In Case of Errors or Questions About Your Electronic Transfers']  #first_citizens_bank
    #10 checks but 4 too# skip_entire_page_regex+=['Chk#.*Chk#.*Chk#.*Chk#.*Chk#.*Chk#.*Chk#.*Chk#.*Chk#.*Chk#']      #fcb full check page
    skip_entire_page_regex+=['Chk#.*Chk#.*Chk#.*Chk#']      #fcb full check page
    skip_entire_page_regex+=['Important Changes to Certain Provisions']
    skip_entire_page_regex+=['Disclosure of Business Account and Miscellaneous Service Fees']
    skip_entire_page_regex+=['Property Management Lockbox']
    skip_entire_page_regex+=['Worksheet to balance your account'] #Wells fargo
    
    #[B]
    # Chase has Substitute or image documents (see Chase Statements 2.pdf)
    skip_entire_page_regex+=['request for an image']
    
    #[C]  M&T (Hogan)
    #- how to balance your account:
    skip_entire_page_regex+=['Any deposils and other oredits shown on this statement which you have not already entered']
    
    banks_schema['skip_entire_page_regex']=skip_entire_page_regex

    ######################################################
    ##    SKIP ENTIRE PAGES FROM TRANSACTION PROCESSING
    ######################################################
    #> specificaly don't do llm_page2transactions if match here ie/ known title pages etc.
    
    ## Ok to blend banks for now because high savings on skip
    
    ## Wells Fargo.  Keep high level demo really for now
    se=[]
    se+=[['You and Wells Fargo','Account options']]  #Multiple required for match
    banks_schema['skip_entire_transaction_page_regex']=se

    
    ###############################################
    ##    BANK PAGE-WIDE re.sub
    ###############################################
    # *ideally not but pick up strange happenings
    # ** beware:  use r'' with \1
    chase_resubs=[]
    #            page like         item like      fix
    chase_resubs+=[('CHASE',r' - ([\d]+\.\d\d )',r' -\1 ')]  #chase)')] #- 18.81 -> -18.81 *possibly confuses column lookups
    CHASE['re_subs']=chase_resubs
    
    ###############################################
    ##    SKIP SECTIONS (don't allow transactions from sections)
    #- CHECKING SUMMARY:  duplicates or summary
    #- CHECKS PAID:  duplicates or summary
    #- applies to llm_page2transaction
    #- also check against transaction_description in case grabs it
    ###############################################
    #? remove all summary?
    #CHASE['skip_sections']=[r'CHECKING SUMMARY',r'CHECKS PAID',r'ITEM FEE SUMMARY']
    # CHECKS PAID:  I thought they where duplicate with some chase?  But ie/ Chase Statements 4.pdf you see a long list of CHECKS PAID (page 22 ie), whereby only included once.
    #:: [ ] yes, but sometimes just names it that  Total Electronic Withdrawals was being picked up in case_atm_location (showing as duplicate from some random entry odd)
    CHASE['skip_sections']=[r'CHECKING SUMMARY',r'ITEM FEE SUMMARY',r'DAILY ENDING BALANCE',r'SERVICE CHARGE SUMMARY']

    WELLSFARGO['skip_sections']=['Summary of checks written','Activity summary','Statement period activity summary']
    WELLSFARGO['skip_sections']+=['Monthly service fee summary']
    
    ## Explicit remove transactions with filter

    ###############################################
    ##    STORE
    ###############################################
    #
    banks_schema['banks']['first_citizens_bank']=FC
    banks_schema['banks']['bank_of_america']=BOA
    banks_schema['banks']['chase']=CHASE
    banks_schema['banks']['wells_fargo']=WELLSFARGO
    
    
    banks_schema['bank_kind_regexes']=kindregexes
    

    return banks_schema



if __name__=='__main__':
    branches=['dev1']
    for b in branches:
        globals()[b]()
