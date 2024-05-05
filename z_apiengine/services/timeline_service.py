import os
import sys
import codecs
import time
import json
import re

from urllib.parse import quote


from fastapi import FastAPI

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")

sys.path.insert(0,LOCAL_PATH+"../..")
from w_storage.gstorage.gneo4j import Neo
from a_custom.alg_classify_debit_credit import resolve_debit_credit_main_account_v2
from a_custom.alg_classify_transaction_color import alg_map_transaction_to_color
from a_custom.alg_classify_transaction_color import dump_color_palette


from alg_generate_pdf_hyperlink import alg_generate_transaction_hyperlink

from w_mindstate.mindstate import get_dashboard_data

from x_modules.k_checks.check_view_validation import interface_load_case_checks

from check_service import DEMO_merge_check_data


from get_logger import setup_logging
logging=setup_logging()


        
#0v5# JC  Feb  3, 2024  Load matched checks from db
#0v4# JC  Jan 28, 2024  Demo sample for include check images
#0v3# JC  Jan 16, 2024  Remove dynamic timeline colors (cause FE team fixed to green/red)
#0v2# JC  Jan  4, 2024  Extend mapping when column headings are dynamic
#0v1# JC  Oct 26, 2023  Setup



"""
TIMELINE SERVICE
-

{checks integration notes}
- see /x_modules/k_checks
- checks matched to transaction_id, loaded from db and merged at transaction_id for FE
[ ] ideally, blend check data into graph db

"""


#from project_root.app.models.timeline import Timeline

"""
OPTION 1/  ORG TIMELINE VIEW:
SEE:  run_objs.py
-> Mindstate()
-> get timeline
-> get_priority_keys()
-> format date etc.

OPTION 2/  QUERY CYPHER DIRECTLY
- (option 3 is use a_query.queryset1.py etc)

"""

"""
SAMPLE DATA USED AT TIMELINE  (circle version)

[A]  Timeline expected data variables:
transaction_date
transaction_amount
transaction_description
locate
value

[B]  Full good timeline data:
transaction_date	"2021-06-09 00:00:00"
filename	"2021-06June-statement-0823.pdf"
is_wire_transfer	true
transaction_method	"wire_transfer"
sender_entity_name	""
account_number	"000000539360823"
transaction_description	"Orig CO Name:Rp Shopify …Inc Trn: 1601378480Tc¢c"
is_credit	true
transaction_method_id	"091000011378480"
section	"DEPOSITS AND ADDITIONS"
label	"Transaction"
transaction_type	"deposit"
filename_page_num	2
is_cash_involved	""
statement_id	"MarnerHoldingsB-2021-05-…June-statement-0823.pdf"
transaction_amount	37466.58
case_id	"MarnerHoldingsB"
value	1
color	"#007d51"
locate	"http://127.0.0.1:8008/ap…TOWSEX1GO|1601378480Tc¢c"

[C]  partial "bad" timeline data:
Deposit_Date	"2020-02-20 00:00:00"
Deposit_Amount	3092.58
case_id	"65858e0c198ceb69d5058fc3"
value	-1
color	"#FF6F00"
locate	""
"""


def local_cypher_transactions(case_id=''):
    stmt="""
    MATCH (t:Transaction)
    WHERE t.case_id='"""+str(case_id)+"""'
    return t
    """
    jsonl,df,tx,meta=Neo.run_stmt_to_normalized(stmt)
    records=[]
    for record in jsonl:
        records.append(record['t'])
    return records


    """
    SAMPLE TRANSACTION:
     {'is_credit': True, 'transaction_date': '2016-07-15', 'filename_page_num': 1, 'account_number': '000000821739112', 'transaction_amount': 12.0, 'section': 'TRANSACTION DETAIL', 'label': 'Transaction', 'transaction_method': 'other', 'statement_id': 'chase_3_66_5ktransfer--000000821739112-Chase Statements 3 12.pdf', 'transaction_type': 'reversal', 'transaction_description': 'Service Fee Reversal', 'algList': ['create_ERS'], 'account_id': 'chase_3_66_5ktransfer-000000821739112', 'filename': 'Chase Statements 3 12.pdf', 'amount_sign': '+', 'case_id': 'chase_3_66_5ktransfer', 'versions_metadata': '{"transaction_type": "llm_markup-transaction_type_method_goals-", "transaction_method_id": "llm_markup-transaction_type_method_goals-", "transaction_method": "llm_markup-transaction_type_method_goals-"}', 'id': 'bf8d54bc04c4ba35f1fa74873fb69a08664342a8b126e5b572c64dbf60b89424', 'transaction_method_id': 'unknown'}
    """

def local_format_timeline_records(records,skip_bad_dates=True):
    ## debit/credit vs main account  +1 credit, -1 debit
    ## colors
    ## text wrapping?
    
    ASSUME_DISABLE_TIMELINE_COLORS_CAUSE_FIXED=True  #Jan 16, 2024
    
    all_transactions=[]
    for record in records:
        all_transactions.append(record)
        
    ## Color palette (type -> color for upper green and lower red)
    if ASSUME_DISABLE_TIMELINE_COLORS_CAUSE_FIXED:
        cmap_red={}
        cmap_green={}
    else:
        cmap_red,cmap_green=dump_color_palette(records=all_transactions,class_field='transaction_type')

    list_unique_debit=[]
    list_unique_credit=[]

    kept_records=[]
    for record in records:
        keep_it=True
        
        ## Categorize colors by...
        record_transaction_type=record.get('transaction_type','')
        
        if not 'is_credit' in record:
            # Choose more popular debits but shouldn't be an issue
            is_credit=False
            is_debit=True
        elif record['is_credit']:
            is_credit=True
            is_debit=False
        else:
            is_credit=False
            is_debit=True
        
        ## Map to value for d3 interpretation
        if is_credit:
            record['value']=1
        elif is_debit:
            record['value']=-1
        else:
            raise Exception("NO DEBIT OR CREDIT: "+str(record))
            record['value']=1
            
        if is_credit:
            #common green# record['color']=cmap_green.get(record_transaction_type,'#43A047') #Else green  (error)
            record['color']=cmap_green.get(record_transaction_type,'#66BB6A') #Else green  (error)
        else:
            record['color']=cmap_red.get(record_transaction_type,'#FF6F00') #Else orange (error)

        
        #[3]#  DATE FORMATTING
        if skip_bad_dates and record.get('transaction_date',''):
            if not re.search(r'^\d\d\d\d\-\d',str(record['transaction_date'])):
                #print ("BAD RAW DATE: "+str(record['transaction_date']))
                if len(str(record['transaction_date']).strip()):
                    logging.warning("[timeline] BAD DATE skip viz: "+str(record['transaction_date']))
                keep_it=False
            
            
        #[4]#  TRANSACTION HYPERLINK
        #(similar to excel recall hosted pdf)
        #i)   on server?
        #ii)  build url 
        record['locate']=alg_generate_transaction_hyperlink(record)
        
        if keep_it:

            ### *** REMOVE UNWANTED FIELDS (ie for now put in this records iter but should have ONE anyways)
            record=local_remove_unused_timeline_fields(record)

            kept_records.append(record)
        
    return kept_records


#######################################################
### REMOVE UNUSED TIMELINE (D3/chart) fields
#- reduces size of payload
#? transaction_method_id??

TIMELINE_FIELDS_TO_REMOVE=['is_cash_involved','algList','filename_page_num','account_number','transaction_method','label','versions_metadata','statement_id','account_id','transaction_method_id','filename']
TIMELINE_FIELDS_TO_REMOVE+=['is_wire_transfer','sender_entity_name','amount_sign']
TIMELINE_FIELDS_TO_REMOVE+=['is_credit','type','color']  #Remove last few until needed watch id!

def local_remove_unused_timeline_fields(record):
    global TIMELINE_FIELDS_TO_REMOVE
    return {k: v for k, v in record.items() if k not in TIMELINE_FIELDS_TO_REMOVE}


def local_patch_clean_to_common_transaction_keys(records):
    ## cypher may return ie:  Transaction_is_credit instead of is_credit
    if not records: return

    #> to patch resolve just redefine duplicate data at very end
    for record in records:
        more_record={}
        for k in record.keys():
            if re.search(r'^Transaction_',k):
                new_k=k.replace("Transaction_","")
                if not new_k in record:
                    more_record[new_k]=record[k]
        record.update(more_record)
        
    ## Patch 2:  Extended mapping
    known_keys=records[0].keys()

    #transaction_date
    mapkeys={}
    if not 'transaction_date' in known_keys:
        mapkeys['transaction_date']=find_key_like(known_keys,'Date')
    #transaction_amount
    if not 'transaction_amount' in known_keys:
        mapkeys['transaction_amount']=find_key_like(known_keys,'Amount')
    #transaction_description
    if not 'transaction_description' in known_keys:
        mapkeys['transaction_description']=find_key_like(known_keys,'Description')
    
    if not 'section' in known_keys:
        mapkeys['section']=find_key_like(known_keys,'Section')

    #locate
    #value
    
    for new_key,old_key in mapkeys.items():
        if old_key:
            for record in records:
                record[new_key]=record[old_key]
                #del record[old_key]
    return
    
def find_key_like(known_keys,key_like):
    #[ ] optional \bDate
    for k in known_keys:
        if re.search(key_like,k,re.IGNORECASE):
            return k
    return None


def get_service_dynamic_timeline_data(case_id):
    ## Use barchart as a model (but did clean timeline earlier I believe (at least titles and things))
    
    ## *** BEWARE:  Hard to fully classify dynamic columns!
    
    data={}
    data['records']=[]
    if case_id:
        ## Get from mindbody though also needs multimodal the_dashboard
        Dashboard,multimodal=get_dashboard_data(case_id)
        
        if not 'timeline' in multimodal['multimodal']:
            logging.warning("[timeline_service at get_service_dynamic_timeline_data] NO TIMELINE DATA: "+str(multimodal))
            records=[]
        else:
            records=multimodal['multimodal']['timeline']
        
        #######################################
        ## Patch add case_id
        for record in records:
            record['case_id']=case_id
#            print ("SAMPLE REORD: "+str(record))
            #print ("SAMPLE REORD: "+str(record))
        #######################################
            
        ## Patch since columns dynamicaly generated by LLM, so easy resolve to expected where possible
        local_patch_clean_to_common_transaction_keys(records)

        ### Demo include check images
        #! Include before removing transaction id etc.
        records=dev_include_check_images(case_id,records)
        
        ## Format records per official timeline (colors, hyperlinks, etc.)
        # enforce some needed
        #( also removed unwanted fields)
        records=local_format_timeline_records(records,skip_bad_dates=False) #no skip cause dynamic
        
        data['records']=records

    return data


def get_service_timeline_data(case_id):
    print ("[timeline_service.py get timeline data...")
    logging.info("[info at service_timeline_data]")

    data={}
    data['records']=[]
    if case_id:
        ## QUERY
        records=local_cypher_transactions(case_id=case_id)
        
        ## FORMAT
        #( also removed unwanted fields)
        records=local_format_timeline_records(records)

        ### Demo include check images
        records=dev_include_check_images(case_id,records)
        
        data['records']=records
        ## transaction_date, transaction_amount, transaction_type, transaction_description
        
    logging.info("[debug][5] remove -- done get data")
    return data


def dev1():
    case_id='ColinFCB1'
    for record in local_cypher_transactions(case_id=case_id):
        print ("> "+str(record))
    return


def dev_dynamic_timeline_data():
    case_id='case_atm_location'
    case_id='65a8168eb3ac164610ea5bc2'# force_checks_meta_filena
    case_id='case_December 2021 Skyview Capital Bank Statement'

    #data=get_service_timeline_data(case_id=case_id)
    data=get_service_dynamic_timeline_data(case_id=case_id)
    matches=0

#    print ("> "+str(data))
#    print ("KEYS: "+str(data['records'].keys()))
    for record in data['records']:
        if 'check_image' in str(record):
            print ("---------------")
            print ("> "+str(record))
            matches+=1
            a=okk
    return

    
from hardcode_demo_check import get_hardcoded_check_demo
def HARDCODED_check_info_for_demo():
    # DB load is 0.2s
    return
def dev_include_check_images(case_id,records):
    if case_id=='65a8168eb3ac164610ea5bc2':
        start_time=time.time()
        if False:
            print ("[ ] check merge delay!")
            ## Got validated checks
            # Load checks response at 0.18s, 0.23s
            validated=interface_load_case_checks(case_id)
        else:
            validated=get_hardcoded_check_demo()

        print ("[debug] load case checks time: "+str(time.time()-start_time))
        start_time=time.time()
        # Merge checks at: 0.002s
        records,merge_count=DEMO_merge_check_data(case_id,validated,records)
        print ("[debug] merge check data time: "+str(time.time()-start_time))
    return records

def test_check_images():
    ## Local test for now
    case_id='65a8168eb3ac164610ea5bc2'
    print ("CHECK IMAGE FOR CASE: "+str(case_id))

    data=get_service_dynamic_timeline_data(case_id=case_id)
    records=data['records']
    validated= interface_load_case_checks(case_id)

    DEMO_merge_check_data(case_id,validated,records,verbose=True)


    return



if __name__=='__main__':
    branches=['dev1']
    branches=['dev_dynamic_timeline_data']
    branches=['test_check_images']

    for b in branches:
        globals()[b]()

"""
raw multimodal timeline
 {'records': [{'transaction_date': '2021-08-20 00:00:00', 'account_number': '000000651770569', 'transaction_method': 'zelle', 'is_credit': False, 'label': 'Transaction', 'transaction_description': 'Zelle Payment To Melissa Fw Jpm686601797 | 500.00', 'statement_id': 'case_atm_location-2021-07-31-000000651770569-07A210E6-B60D-46B6-9D40-9B3239237F05-list.pdf', 'transaction_method_id': 'Jpm686601797', 'filename_page_num': 3, 'filename': '07A210E6-B60D-46B6-9D40-9B3239237F05-list.pdf', 'section': 'Total Electronic Withdrawals', 'transaction_type': 'withdrawal', 'is_wire_transfer': True, 'transaction_amount': 500.0}, {'transaction_date': '2021-08-25 00:00:00', 'account_number': '000000651770569', 'transaction_method': 'zelle', 'is_credit': False, 'label': 'Transaction', 'transaction_description': 'Zelle Payment To Luzby Andrade 12454300327 | 35.00', 'statement_id': 'case_atm_location-2021-07-31-000000651770569-07A210E6-B60D-46B6-9D40-9B3239237F05-list.pdf', 'transaction_method_id': '12454300327', 'filename_page_num': 3, 'filename': '07A210E6-B60D-46B6-9D40-9B3239237F05-list.pdf', 'section': 'Total Electronic Withdrawals', 'transaction_type': 'withdrawal', 'is_wire_transfer': True, 'transaction_amount': 35.0}, {'transaction_date': '2021-08-25 00:00:

     
    {'records': [{'is_credit': False, 'filename_page_num': 3, 'transaction_date': '2021-08-20', 'account_number': '000000651770569', 'transaction_amount': 500.0, 'section': 'Total Electronic Withdrawals', 'label': 'Transaction', 'transaction_method': 'zelle', 'statement_id': 'case_atm_location-2021-07-31-000000651770569-07A210E6-B60D-46B6-9D40-9B3239237F05-list.pdf', 'transaction_type': 'withdrawal', 'transaction_description': 'Zelle Payment To Melissa Fw Jpm686601797 | 500.00', 'algList': ['create_ERS'], 'account_id': 'case_atm_location-000000651770569', 'filename': '07A210E6-B60D-46B6-9D40-9B3239237F05-list.pdf', 'is_wire_transfer': True, 'case_id': 'case_atm_location', 'versions_metadata': '{"transaction_method": "llm_markup-transaction_type_method_goals-", "transaction_method_id": "llm_markup-transaction_type_method_goals-", "transaction_type": "llm_markup-transaction_type_method_goals-", "is_wire_transfer": "llm_markup-transaction_type_method_goals-"}', 'id': '774890b4652cf34d37230c8e265e348cac41e9b88054818ba60738f21615cdf7', 'transaction_method_id': 'Jpm686601797', 'value': -1, 'color': '#ff0600', 'locate': 'http://127.0.0.1:8008/api/v1/case/case_atm_location/pdf/07A210E6-B60D-46B6-9D40-9B3239237F05-list.pdf?page=3&key=c7fcd5728e8f03dec152b17f740f993be32b51a0d261a63bd40c0ff00d424a55'}, {'is_credit': False, 'filename_page_num': 3, 'transaction_date': '2021-08-25', 'account_number': '000000651770569', 'transaction_amount': 35.0, 'section': 'Total Electronic Withdrawals', 'label': 'Transaction', 'transaction_method': 'zelle', 'statement_id': 'case_atm_location-2021-07-31-000000651770569-07A210E6-B60D-46B6-9D40-9B3239237F05-list.pdf', 'transaction_type': 'withdrawal', 'transaction_description': 'Zelle Payment To 

 
"""

"""
project_root/
│
├── app/
│   ├── main.py            # FastAPI initialization and application instance
│   ├── api/
│   │   ├── v1/            # Versioning your API is a good practice
│   │   │   ├── router.py  # Collects all the routers from the different modules
│   │   │   ├── case.py
│   │   │   ├── timeline.py
│   │   │   └── ...
│   ├── models/
│   │   ├── __init__.py    # Imports all ORM models for easy access
│   │   ├── case.py
│   │   ├── timeline.py
│   │   └── ...
│   ├── services/          # Business logic here
│   │   ├── case_service.py
│   │   ├── timeline_service.py
│   │   └── ...
│   └── database.py        # Database connection and session management
│
└── ...

"""
