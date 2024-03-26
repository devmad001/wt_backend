import os, sys
import time
import requests
import re


LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")


from z_apiengine.database import SessionLocal

from w_utils import get_base_endpoint
from w_utils import get_ws_endpoint
from c_release.MANAGE_exe import easy_process_pdf_case


#0v2# JC Jan 15, 2023  Cont
#0v1# JC Dec 13, 2023  Config



"""
    ** OLD DEVELOPMENT NOTES
    INCLUDE FUNCTION FOR ANY ODD EXCEPTION
    
    INCREMENTAL ADJUSTMENTS
    - possibly elsewhere but having formal tests will help
    - keep detailed notes and have gpt create plan for later

"""


def issue_chase_summary_sections_bad_as_transactions():
    ## TIP ON CODE ADJUSTMENTS:
    #- schema_statement_kinds: CHASE -> if you see CHECKING SUMMARY, add a bullet description of fix
    
    ## ISSUE:
    #- CHASE CHECKING SUMMARY entries are being recorded as transactions
    # http://127.0.0.1:8008/api/v1/case/6578e48c20668da6f77cd052/pdf/19ec7d6b-ae01-4c17-ad1a-41262f6f32e3.pdf?page=141&key=c5ba49b75b2be40740aba8408b1aa71bfabbd75ff1214c67dbf68f5df5c7d292
    #- Transaction Detail   (but pulls from below!)
    #- Date?  Makes it up?
    #- Description:  Beginning balance
    case_view="http://127.0.0.1:5173/case/6578e48c20668da6f77cd052/run"
    
    """
    THOUGHTS:
    2)- No transactions like: "^Beginning balance" or ^
    CHASE IS PULLING ALL THESE AMOUNTS  but no date??!
    - pulls checking summary.  
    - NOT GOOD!
    http://127.0.0.1:8008/api/v1/case/6578e48c20668da6f77cd052/pdf/19ec7d6b-ae01-4c17-ad1a-41262f6f32e3.pdf?page=141&key=c5ba49b75b2be40740aba8408b1aa71bfabbd75ff1214c67dbf68f5df5c7d292

    """
    
    ## Setup basic check (but need better easy test cases)
    # u_dev/dev_challenges
    # save pdf to chase_bad_pulling_summary
    
    
    ## APPROACH:
    #- 
    #- if 'CHECKING SUMMARY' on page, explicitly say to ignore.  Add to chase schema fix logic at:
    #-   schema_statement_kinds.py
    # C:\scripts-23\watchtower\CASE_FILES_STORAGE\storage\chase_bad_pulling_summary_1page
    case_id="chase_bad_pulling_summary_1pageB"
    case_id="chase_bad_pulling_summary_1page" #<--
    local_process_pdf_case(case_id)
    
    """
     
    ## Chase CHECKING SUMMARY not in proper place which leads to Ending Balance etc showing up
    multib=['- CHECKING SUMMARY items are NOT transactions. Ignore summary items like: Beginning Balance, Deposits and Additions, Other Withdrawls, Ending Balance, Interest Paid this Period, etc']
    CHASE['bullets']+=[(r'CHECKING SUMMARY',multib)]
    """
    
    return

def issue_infinite_loop_on_kb_markup():
    """
    this case:
    case_id='6579bfd30c64027a3b9f2d3c'
    
    Involves this transaction description:
    
    'CHECKS PAID | \n\nCHEGCK DATE AMOUNT CHECK DATE AMOUNT \nNUMBER PAID NUMBER PAID \n3043 ~ 2020/03/18 $100.00 5980 ~ Q3/27 4,000.00 \n3048 * ~ 2020/03/13 25.00 5961 ~ 2020/03/26 1,337.65 \n5638 * A 2020/03/16 5,000.00 5862 A Q3/27 10,000.00 \n5855 * ~ 2020/03/17 120.00 5983 ~ 2020/03/31 3,803.00 \n5987 * A 2020/03/23 201.00 5964 A 2020/04/02 3,491.85 \n5958 A 2020/03/20 123.89 5965 2020/04/13 61.47 \n5959 Â» 2020/04/08 55.00 5968 ~ 2020/04/10 107.70 \nTotal Checks Paid $28,526.56', 'section': 'CHECKS PAID', 'id': '1'}, {'transaction_description': 'CHECKS PAID | \n\nCHEGCK DATE AMOUNT CHECK DATE AMOUNT \nNUMBER PAID NUMBER PAID \n3043 ~ 2020/03/18 $100.00 5980 ~ Q3/27 4,000.00 \n3048 * ~ 2020/03/13 25.00 5961 ~ 2020/03/26 1,337.65 \n5638 * A 2020/03/16 5,000.00 5862 A Q3/27 10,000.00 \n5855 * ~ 2020/03/17 120.00 5983 ~ 2020/03/31 3,803.00 \n5987 * A 2020/03/23 201.00 5964 A 2020/04/02 3,491.85 \n5958 A 2020/03/20 123.89 5965 2020/04/13 61.47 \n5959 Â» 2020/04/08 55.00 5968 ~ 2020/04/10 107.70 \nTotal Checks Paid $28,526.56', 'section': 'CHECKS PAID', 'id': '2'}, {'transaction_description': 'CHECKS PAID | \n\nCHEGCK DATE AMOUNT CHECK DATE AMOUNT \nNUMBER PAID NUMBER PAID \n3043 ~ 2020/03/18 $100.00 5980 ~ Q3/27 4,000.00 \n3048 * ~ 2020/03/13 25.00 5961 ~ 2020/03/26 1,337.65 \n5638 * A 2020/03/16 5,000.00 5862 A Q3/27 10,000.00 \n5855 * ~ 2020/03/17 120.00 5983 ~ 2020/03/31 3,803.00 \n5987 * A 2020/03/23 201.00 5964 A 2020/04/02 3,491.85 \n5958 A 2020/03/20 123.89 5965 2020/04/13 61.47 \n5959 Â» 2020/04/08 55.00 5968 ~ 2020/04/10 107.70 \nTotal Checks Paid $28,526.56', 'section': 'CHECKS PAID', 'id': '3'}, {'transaction_description': 'CHECKS PAID | \n\nCHEGCK DATE AMOUNT CHECK DATE AMOUNT \nNUMBER PAID NUMBER PAID \n3043 ~ 2020/03/18 $100.00 5980 ~ Q3/27 4,000.00 \n3048 * ~ 2020/03/13 25.00 5961 ~ 2020/03/26 1,337.65 \n5638 * A 2020/03/16 5,000.00 5862 A Q3/27 10,000.00 \n5855 * ~ 2020/03/17 120.00 5983 ~ 2020/03/31 3
            
    Comments:
    - appears the entire checks paid section ends up in description
    - recall MANY checks on page should use gpt-4 because things complicated
    - ? add check if multiple amounts or keywords in description then REGJECT llm_page2transaction and rerun with better gpt OR extra prompting?
    
    """
    
    """
    WHERE?  maybe page 88 or 89
    d  on \nohe  of  your  previous  statemants. \nÂ»  An  image  of  this  check  may  be  available  for  you  to  view  on  Chase.com. \nPage  1ot  4 \nSB1187285-F1 \n85\n \n"}, 'input_filename': '62eac7ab-388c-4ff0-802e-65e96fedbd29.pdf', 'input_page_number': 88, 'ptr': {'case_id': '6579bfd30c64027a3b9f2d3c', 'chunk_id': '6579bfd30c64027a3b9f2d3c-page-62eac7ab-388c-4ff0-802e-65e96fedbd29.pdf-88', 'page_num': 88, 'filename': '62eac7ab-388c-4ff0-802e-65e96fedbd29.pdf', 'block_update': ['opening_balance', 'closing_balance'], 'bank_name': 'JPMorgan Chase Bank, N.A', 'bank_address': 'P O Box 182051, Columbus, OH 43218-2051', 'statement_id': '6579bfd30c64027a3b9f2d3c-2020-03-13-000001962070404-62eac7ab-388c-4ff0-802e-65e96fedbd29.pdf', 'account_number': '000001962070404', 'account_holder_name': 'The Grayson Family Living Trust', 'account_holder_address': '302 Paradise Dr, Tiburon CA 94920-2536', 'statement_page_number': 1, 'statement_period': 'March 13, 2020 through April 13, 2020', 'statement_date': '2020-03-13', 'opening_balance': 89784.36, 'closing_balance': 86345.61}, 'allow_cache': True, 'db_commit': True, 'doc_dict': {}}
    """
    
    """
    JON APPROACH:
    - CHECKS PAID section is a SUMMARY!!
    
    >> adjustment is in schema_statement_kinds.py
    - add to CHASE['bullets']  

    """

    return


def colin_72dpi_missing_period():
    ## JON:
    #- rerunning the query on gpt-4 it even skipped the amount entirely
    #- doing OCR on my laptop did NOT miss the period!

    #- JON SUGGESTION:  no second OCR on 72dpi.  Can I see the OMNIPAGE?
    
    """
     {'format': 'PDF 1.6', 'title': '', 'author': '', 'subject': '', 'keywords': '', 'creator': 'OmniPage CSDK 18', 'producer': 'OmniPage 18', 'creationDate': "D:20230828120728-08'00'", 'modDate': '', 'trapped': '', 'encryption': None}
    """

    print ("gpt-4 leaves amount empty because not makes sense.")
    print ("**better to focus upstream and NOT do double ocr on 72dpi")
    
#    from w_llm.llm_interfaces import LazyLoadLLM
#    LLMSMARTEST=LazyLoadLLM.get_instance(model_name='gpt-4')
#    transactions=LLMSMARTEST.prompt(pp,json_validate=True,try_cache=False)
#    print ("T: "+str(transactions))

    
    #NO DOUBLE OCR IF <72DPI
    #enforce numbers REQUIRE CENTS FIX!
    
    # Page 69
    # (from dec_jon_pdf)
    from b_extract.p2t_test_sets.auto_create_test_sets import pdf2subpages
        
    if True:
        input_filename="C:/scripts-23/watchtower/DEMO_SET/colin_for_dec_21/Wells Fargo JWM Raw.pdf"
        output_filename='C:/scripts-23/watchtower/DEMO_SET/colin_for_dec_21/Wells Fargo JWM Raw 69.pdf'
        
        #pdf2subpages(input_filename=input_filename, output_filename=output_filename, keep_pages=[99])
        pdf2subpages(input_filename, output_filename, keep_pages=[69])

    return

def year_is_likely():
    #** jon fixed via
    # July 8,2021 m Page 3 of 5
    year=alg_get_page_year(not2028)
    print ("YEAR: "+str(year))

    return

def issue_a_transaction_date_beyond_today():
    #**jon fixed by more flexible page year
    ## Also happened on colin
    
#https://core.epventures.co/api/v1/case/657f172f9a57063d991dd88b/pdf/6fcac963-a70f-4edc-a386-5d8b98ef0832.pdf?page=151&key=800e70fb9829c74a3fbefdc1553cf2f9a2936cba4bc95b5824d0a6bfeb49569d
#https://watchdev.epventures.co/fin-aware/dashboard?case_id=657f172f9a57063d991dd88b


    # http://127.0.0.1:8008/api/v1/case/6578e48c20668da6f77cd052/pdf/19ec7d6b-ae01-4c17-ad1a-41262f6f32e3.pdf?page=141&key=c5ba49b75b2be40740aba8408b1aa71bfabbd75ff1214c67dbf68f5df5c7d292
    #1)- transaction date cannot be beyond today.
    return


##############################
# OPEN ITEMS BELOW
##############################


def timeline_node_view_no_fit_on_screen():
    # http://127.0.0.1:5173/case/chase_bad_pulling_summary_1pageB/run
    return



##############################
# MOSTLY FIXED BELOW
##############################

def entity_list_in_response():
    #[x] fixed at data source list -> string of key values ,
    return

def pipeline_frozen():
    #[ ] also added more info on thread wait
    #** colin did run on remote server so maybe ok.
    # colin 142 pager.  
    # case_id='6579bf870c64027a3b9f2cfe'
    # rerun with verbose multi-thread to look for exceptions
    return

def dev_bad_page():
    # wells fargo p117 not doing column right
    
    """
        Please retrieve details about the transactions from the following bank statement page.
    If you cannot find the information from this text then return "".  Do not make things up. Always return your response as a valid json (no single quotes).
    - Include any section heads (ie/ Transaction history, ATM & DEBIT CARD WITHDRAWLS, CASH TRANSACTIONS, ELECTRONIC WITHDRAWALS, etc)
    - Format the transaction_date as yyyy-mm-dd
    - The transaction_description should include the address and be fully descriptive (it may be multi-line)
   - Note: "section":"Transaction history" is not valid. Infer the section from the likely headings: Deposits and Additions or Withdrawals and Subtractions
   - Note:  The year is likely: 2021 So, 04/20  -->  2021-04-20
    All the transactions should be included in a valid JSON list:

    {"all_transactions": [{"transaction_description": "full description", "transaction_amount": 123.45, "transaction_date": "2021-01-01", "section": "Cash transactions"}]}

    Bank Statement Page:
    =====================


(text char length: 3344)
[d3]  full_prompt: September 8, 2021 ■ Page 2 of 6
Overdraft Protection
Your account is linked to the following for Overdraft Protection:
■ Credit Card - XXXX-XXXXXX-X0686
Transaction history
Check    Deposits/      Withdrawals/    Ending daily
Date     Number Description      Additions       Subtractions    balance
8/9      Purchase authorized on 08/06 Global Domains Int 760-6023000     10.00
CA S581218299361686 Card 4656
8/9      Purchase authorized on 08/06 Primrose Woodstock 770-9249881     307.00
GA S461218452323829 Card 4656
8/9      American Express ACH Pmt 210809 W3470 Jonathan W Mikula         1,987.47
8/9      American Express ACH Pmt 210809 W6080 Jonathan W Mikula         2,500.00        91,088.71
8/10     Vacasa LLC Payment 210809 540426 Jonathan W     5,469.31        96,558.02
8/11     Bill Pay Albert Smith Recurring No Account Number on 08-11      150.00
8/11     ^ 374 Madison Falls Ho Payment 080921 00374 0471570830          553.00          95,855.02
8/12     Common Sense Pub EDI Pymnts 0000659902 Jonathan William         4,944.65
Mikul
8/12     Bill Pay State Farm Credit Card on-Line Xxxxxxxxxxx54136 on     336.24
08-12
8/12     Bill Pay Pennymac Loan Services on-Line xxxxx66083 on 08-12     1,200.00
8/12     Bill Pay Cenlar FSB on-Line xxxxx75584 on 08-12         1,900.00        97,363.43
8/13     IRS Treas 310 Childctc 081321 xxxxxxxxxx00928 Mikula, Jonathan          300.00
W & J
8/13     WT F50813692676000 Scotiabank Inver /Org=Invekta Factorante     32,865.00
Sapi DE Cv Srf# F50813692676000 Trn#210813119391 Rfb#
8/13     Wire Trans Svc Charge - Sequence: 210813119391 Srf#     16.00
F50813692676000 Trn#210813119391 Rfb#
8/13     375 Check       9,100.00       121,412.43
8/16     Mobile Deposit : Ref Number :612150238465       0.01
8/16     Mobile Deposit : Ref Number :912150239156       0.01
8/16     Mobile Deposit : Ref Number :112150239847       0.01
8/16     Mobile Deposit : Ref Number :112150239887       0.01
8/16     Mobile Deposit : Ref Number :212150240231       0.01
8/16     Mobile Deposit : Ref Number :712150238862       38.00
8/16     Mobile Deposit : Ref Number :612150238497       40.00
8/16     Mobile Deposit : Ref Number :312150240283       130.89
8/16     Purchase authorized on 08/13 Primrose Woodstock 770-9249881     307.00
GA S301225464358436 Card 4656
8/16     Bill Pay American Express - New Biz Gold on-Line        9,450.00       111,864.37
xxxxxxxxxx42005 on 08-16
8/17     WT Fed#00530 Scotiabank Inverla /Org=Invekta Factorante Sapi    32,865.00
DE Cv Srf# 2021081700358709 Trn#210817119017 Rfb#
xxxxx9893
8/17     Wire Trans Svc Charge - Sequence: 210817119017 Srf#     16.00
2021081700358709 Trn#210817119017 Rfb# xxxxx9893
8/17     Bill Pay American Express - New Biz Gold on-Line        8,750.00       135,963.37
xxxxxxxxxx42005 on 08-17
8/18     Bill Pay Cherokee County Water & Sewage A on-Line xxxxx70711    27.25
on 08-18
8/18     Bill Pay Nbsc - A Division of Synovus Ban on-Line       36.06
Xxxxxxxxxxx00001 on 08-18
8/18     Bill Pay Cobb Emc on-Line xxxx87003 on 08-18    227.00
8/18     Bill Pay Pennymac Loan Services on-Line xxxxx15074 on 08-18     1,200.00
8/18     Bill Pay Chase Card Services on-Line Xxxxxxxxxxx68061 on 08-18          5,814.53
8/18     Bill Pay American Express - New Biz Gold on-Line        7,480.00
xxxxxxxxxx42005 on 08-18
8/18     Coinbase Inc. 8889087930 210818 Nvh768Jb Jonathan William       9,500.00
Mikul
8/18     Coinbase Inc. 8889087930 210818 Qvsx9Ge7 Jonathan William       10,000.00      101,678.53
Mikul
[choose gpt-4 because complex page]
[page2t] trying model: gpt-4 at attempt #1 (try_cache: True)
[debug] recall, 5 retries if timeout...won't throw errror until all 5 gone
[debug] [A] started llm query [gpt-4]: 2023-12-18 21:46:50.559521 timeout: 204
"""

    return

def wire_transfer_bad_type():
    today="2024-01-15"
    url='https://core.epventures.co/api/v1/case/659457fca348734715059312/pdf/a89f69d2-e8c2-4ebd-babf-29b95f7c4f5b.pdf?page=3&key=f6d1548ebcfd8de636d7c17cb775b17d7e96c9be0bcbd697bb882fb9f1a53f21&highlight=195031.90|SEQ%3A2021120300174912%2F496437|DET%3A52775903712030491046|TRN%3A2021120300491046'
    
    return


if __name__ == "__main__":
    #issue_chase_summary_sections_bad_as_transactions()
    #colin_72dpi_missing_period()
    #dev_cents()
    year_is_likely()

    wire_transfer_bad_type()



"""
TODO:  unhashable entities?
nteger not the external str
INFO:     18.118.67.255:0 - "POST /api/v1/auth_handshake HTTP/1.0" 200 OK
INFO:     198.52.145.121:0 - "GET /api/v1/case/657a51719a57063d991dcd51/get_buttons?fin_session_id=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2NTcxYjg2YTg4MDYxNjEyYWEyZmM4YjciLCJlbWFpbCI6InNoaXZhbUBzaGl2YW1wYXRlbHMuY29tIiwiaWF0IjoxNzAyNzM4NzkyLCJleHAiOiIyMDIzLTEyLTE3VDAyOjU5OjUyLjAwMFoifQ.5a67fc1c57abb0c98aa69546d9728a9def1c997e4fd80f1602568eab0405eca5&user_id=6571b86a88061612aa2fc8b7 HTTP/1.0" 200 OK
RAW: [{'Transaction Transaction Date': '2021-12-10', 'Transaction Filename Page Num': 2, 'Transaction Account Number': '000000705265012', 'Transaction Transaction Description': 'Orig Co Name:Pay Plus Orig 1D:6452579291 Desc Date:211210 Co Entry Descr:Achtrans Sec:Ccd Trace#:101000695726320 Eed:211210 Ind Id:452579291 Ind Name:Zp Account 1 Ppsaccount Trn: 3445726320T¢', 'Transaction Section': 'Withdrawals And Debits', 'Transaction Filename': '7D889C63-C564-44D9-Aa87-B551E9062Fdc.Pdf', 'Entities': [{'role': 'RECEIVER', 'name': 'Zp Account 1 Ppsaccount', 'label': 'Entity', 'id': '657a51719a57063d991dcd51-452579291', 'type': 'individual', 'entity_id': '452579291'}], 'Transaction Transaction Amount': '42696.00'}]
RAW flat: [{'Transaction Transaction Date': '2021-12-10', 'Transaction Filename Page Num': 2, 'Transaction Account Number': '000000705265012', 'Transaction Transaction Description': 'Orig Co Name:Pay Plus Orig 1D:6452579291 Desc Date:211210 Co Entry Descr:Achtrans Sec:Ccd Trace#:101000695726320 Eed:211210 Ind Id:452579291 Ind Name:Zp Account 1 Ppsaccount Trn: 3445726320T¢', 'Transaction Section': 'Withdrawals And Debits', 'Transaction Filename': '7D889C63-C564-44D9-Aa87-B551E9062Fdc.Pdf', 'Entities': 'role:RECEIVER, name:Zp Account 1 Ppsaccount, label:Entity, id:657a51719a57063d991dcd51-452579291, type:individual, entity_id:452579291', 'Transaction Transaction Amount': '42696.00'}]
INFO:     198.52.145.121:0 - "GET /api/v1/case/657a51719a57063d991dcd51/square_data?fin_session_id=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2NTcxYjg2YTg4MDYxNjEyYWEyZmM4YjciLCJlbWFpbCI6InNoaXZhbUBzaGl2YW1wYXRlbHMuY29tIiwiaWF0IjoxNzAyNzM4NzkyLCJleHAiOiIyMDIzLTEyLTE3VDAyOjU5OjUyLjAwMFoifQ.5a67fc1c57abb0c98aa69546d9728a9def1c997e4fd80f1602568eab0405eca5&user_id=6571b86a88061612aa2fc8b7 HTTP/1.0" 200 OK
Got timeline request for width: 2280 and height: 615
INFO:     198.52.145.121:0 - "GET /api/v1/case/657a51719a57063d991dcd51/timeline_dynamic?user_id=6571b86a88061612aa2fc8b7&fin_session_id=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2NTcxYjg2YTg4MDYxNjEyYWEyZmM4YjciLCJlbWFpbCI6InNoaXZhbUBzaGl2YW1wYXRlbHMuY29tIiwiaWF0IjoxNzAyNzM4NzkyLCJleHAiOiIyMDIzLTEyLTE3VDAyOjU5OjUyLjAwMFoifQ.5a67fc1c57abb0c98aa69546d9728a9def1c997e4fd80f1602568eab0405eca5&maxWidth=2280&maxHeight=615 HTTP/1.0" 200 OK
**RECALL, you have the prepare html data etc but this is more stand-alone
HAS LAT: False form: Index(['Transaction_transaction_date', 'Name', 'Transaction_account_number',
       'Transaction_label', 'Transaction_statement_id',
       'Transaction_transaction_description', 'Transaction_section', 'Name',
       'Transaction_is_credit', 'Transaction_id', 'Entities',
       'Transaction_transaction_amount'],
      dtype='object')
[is_timelineable]: True at date col: Transaction_transaction_date
[todo] handle df within df
[todo] handle df within df
An error occurred while processing column 'Entities': unhashable type: 'list'
[barchart] candidate value: Transaction_transaction_amount can category: Entities
[debug]  CATEGORY COL: Entities from options: ['Transaction_transaction_date', 'Name', 'Transaction_account_number', 'Transaction_label', 'Transaction_statement_id', 'Transaction_transaction_description', 'Transaction_section', 'Name', 'Transaction_is_credit', 'Transaction_id', 'Entities', 'Transaction_transaction_amount']
IDICT: {'features': {'has_lat_lng': False, 'is_timelineable': True, 'is_barchartable': True}, 'column_names_map': {'latitude': None, 'longitude': None, 'timeline_date_col': 'Transaction_transaction_date', 'timeline_amount_col': 'Transaction_transaction_amount', 'barchart_category_col': 'Entities', 'barchart_value_col': 'Transaction_transaction_amount'}, 'show_decision': 'timeline_dynamic'}
[show decision]: timeline_dynamic


"""



