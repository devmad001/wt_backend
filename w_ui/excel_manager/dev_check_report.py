import os
import sys
import codecs
import json
import re
from collections import OrderedDict

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"

sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")
sys.path.insert(0,LOCAL_PATH+"../../") 


from openpyxl.styles import Font  #external import but fine for style
from exceltemplate.excel_wrap import Excel_Wrap
#from exceltemplate.excel_markup import do_markup


from z_apiengine.database import SessionLocal
from z_apiengine.database_models import Check

from z_apiengine.services.timeline_service import get_service_timeline_data
from z_apiengine.services.check_service import DEMO_merge_check_data
from x_modules.k_checks.check_view_validation import interface_load_case_checks
from x_modules.k_checks.check_view_validation import interface_load_all_checks


#0v1# JC  Feb 16, 2024  Base


"""
    CHECK DATA FOR EXCEL TAB REPORT
    - /x_modules/k_checks/check_view_validation
    -  ^ interface to pass  to front-end via transaction socket message

"""

"""
    PLANNED APPROACH
    *assume gives decent data
    1)  Load check data via case transactions (see check_matcher)
    2)  Load check data directly too (on cases where check does not match transactions)

"""


#** via timeline_service.py as part of DEMO!
def test_check_images():
    ## Local test for now
    case_id='65a8168eb3ac164610ea5bc2'
    print ("CHECK IMAGE FOR CASE: "+str(case_id))
    data=get_service_timeline_data(case_id=case_id)
    records=data['records']
    validated= interface_load_case_checks(case_id)
    DEMO_merge_check_data(case_id,validated,records,verbose=True)
    return


def dev_iterate_check_records():

    ## NOTES:
    #- recall validated (checks) is transaction_id indexed for fast lookup
    #    ^ but needs to be re-indexed here
    
    case_id='65caaffb9b6ff316a779f525'

    print ("CHECK IMAGE FOR CASE: "+str(case_id))

    ## 1)  LOAD PRE-MATCHED CHECK DATA
    #- a bit odd because want to get transaction matches AND original check data
    data=get_service_timeline_data(case_id=case_id)
    records=data['records']
    validated_pre_matched= interface_load_case_checks(case_id)
    base_data_with_matched_checks,status_check_identifiers=DEMO_merge_check_data(case_id,validated_pre_matched,records,verbose=True)
    
    ## Reindex base transaction data based on check_identifier
    trd={}
    for r in base_data_with_matched_checks:
        ## Transaction record so check identifier at...
        if 'check_info' in r:
            trd[r['check_info']['check_identifier']]=r
            
    ## 2)  Iterate over all checks
    print ("Load all checks again..")
    count_matched=0
    count_unmatched=0
    for check in interface_load_all_checks(case_id):
        meta=json.loads(check['meta'])
#        print ("AT: "+str(check))
        check_identifier=check['check_identifier']
        
        if check_identifier in trd:
            count_matched+=1
            pass
        else:
            count_unmatched+=1
#            print ("NO MATCH: "+str(check_identifier))
#            print (">> "+str(check))
#            print ("META: "+str(meta))
#            print ("TRD: "+str(trd))


#    print ("TRD: "+str(trd))
    print ("FOUND matched with transactions: "+str(len(trd)))
    print ("FOUND unmatched: "+str(count_unmatched))
    print ("FOUND matched: "+str(count_matched))
    print ("Percent matched (~18%): "+str(count_matched/(count_matched+count_unmatched)))
            
    
    ## Iterate
    
    return


def get_sample_check_values(case_id='65caaffb9b6ff316a779f525',verbose=False):

    headings=[]
    records=[]
    meta={}

    ## RAW CHECK INFO
    with SessionLocal() as db:
        checks = db.query(Check).options(Check.query_without_image_bytes()).filter(Check.case_id == case_id).all()
        
        for check in checks:

#D1            print ("RAW: "+str(check.__dict__))
#D1            print ("url: "+str(check.generate_check_image_url()))
            
            ## RAW META
            meta = json.loads(check.meta)
#D1            print ("META: "+str(meta))

            record=OrderedDict()

            record['Check Number']=meta['check-number']
            record['Check Date']=meta['check-date']
            record['Check Amount']=meta['check-amount']

            record['Payor']=meta['payer_name']
            record['Payee']=meta['pay-to-order']

            record['Bank Name']=meta['bank-name']
            record['Account Number']=meta['account_number']

            record['Memo']=meta['check-memo']
            
            record['Pay-to-order']=meta['pay-to-order']

            record['Image URL']=check.generate_check_image_url()

            #Posting Date
            #Bank #
            #Research Seq
            #Account #
            #Dollar Amount
            #Check/Serial Store #
            #Tran Code
            #RTABA
            #DB/CR
            
            if not headings:
                headings=list(record.keys())
                print ("[info] check HEADINGS: "+str(headings))

            if verbose:
                print ("RECORD: "+str(record))
            
            records+=[record]
            
        
    ## WHAT ABOUT FULL TRANSACTION MATCH OPTION?

    return headings,records,meta




if __name__=='__main__':
    branches=['dev_iterate_check_records']
    branches=['dev_sample_values']

    for b in branches:
        globals()[b]()
        




"""

{'_sa_instance_state': <sqlalchemy.orm.state.InstanceState object at 0x000001EF61614E80>, 'transaction_id': '', 'id': 169, 'pdf_filename': 'M&T Victim Records__Operating 2017__CR__2017 02__020317-$2,335.00.pdf', 'payor_name': '', 'account_num': '', 'created': datetime.datetime(2024, 2, 13, 8, 19, 26), 'case_id': '65caaffb9b6ff316a779f525', 'check_id': '973', 'check_identifier': 'M&T Victim Records__Operating 2017__CR__2017 02__020317-$2,335.00.pdf_973_2_0_0', 'check_image_filename': 'M&T Victim Records__Operating 2017__CR__2017 02__020317-$2,335.00_check_2_0_0.jpg', 'payee_name': '', 'meta': '{"check-name-address": "YAMIN SHEN / Vain Z hong 1778 OLD WATERBURY ROAD CHESHIRE, CT 06410-1347", "pay-to-order": "Total Asset Managers Ashford Parles", "check-amount": "244", "bank-name": "BANK OF AMERICA", "check-number": "973", "check-memo": "11-3 Kent et, Ashford, CT06278", "check-date": "1/27 2007", "check-amount-words": "Two hundred forty four A /100- Dot", "account_number": "000029289888\\u2448 0073", "payer_name": "YAMIN SHEN", "payer_address": "/ Vain Z hong 1778 OLD WATERBURY ROAD CHESHIRE, CT 06410-1347"}', 'state': 'created'}


    id = Column(Integer, primary_key=True)
    check_identifier = Column(String(255), unique=True, nullable=False,index=True)

    case_id = Column(String(255), index=True)  # 
    transaction_id = Column(String(255), index=True,nullable=True)  # 

    check_id = Column(String(255))  # 
    pdf_filename = Column(String(255),nullable=True)  #
    check_image_filename = Column(String(255),nullable=True)  

    payor_name = Column(String(255),nullable=True)  # Name of the payor, initially empty
    payee_name = Column(String(255),nullable=True)  # Name of the payee, initially empty
    account_num = Column(String(255),nullable=True)  # Possible query param

    image_bytes = Column(LargeBinary(length=2 * 1024 * 1024)) #(mysql no Medium)

    meta = Column(JSON)  # Storing additional metadata as JSON. Use JSON for non-PostgreSQL databases

    created = Column(DateTime, default=datetime.utcnow)
    state = Column(String(255),nullable=True)  # Status of the check record, initially 'created'


"""
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
