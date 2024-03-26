import os
import sys
import codecs
import json
import re

from fastapi import FastAPI

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")

sys.path.insert(0,LOCAL_PATH+"../..")

from w_mindstate.mindstate import Mindstate
from service_test_data.chart_case_data_v1 import get_square_data_sample
from get_logger import setup_logging
logging=setup_logging()


        
#0v4# JC Jan 28, 2024  Remove transaction id (in data now because timeline needs it)
#0v3# JC Dec 16, 2023  Clean data table headings + normalize list to value field
#0v2# JC Nov 24, 2023  Separate out raw data view
#0v1# JC Nov  2, 2023  Setup


"""
    SQUARE SERVICE
    
    > multimodal.* is set in kb_answer_multimodal.py
    > multimodal> recall kb_answer_multimodal -> idict show_decision, AND columns to plot first
    
    > kb_ask/multimodal.py  -> MultiModel_Response()get_multimodal_response
        > barchart, timeline, html, map
            >   kb_answer.py -> answers=QA_Session_Answers().dump_answers(dd['df'],dd['df_filtered'])
                >  dd['html'], html_data <<NEW =self.dump_for_html_table_view(df=df_friendly)
                    > pretty_html_table.py build_table(df) ** IS A LIBRARY!
        
"""


## Don't view transaction id in data table view
SPECIAL_EXCLUDE_KEYS_DATA_TABLE=['id','transaction id','amount sign']



def local_load_multimodal(case_id):
    ## Can access via api or module
    Mind=Mindstate()
    sesh,session_id,is_created=Mind.start_or_load_session(case_id=case_id)
    answer_dict=Mind.get_field(session_id,'last_answer_meta')
    return Mind,session_id,answer_dict


## VERSION v0 (original is html blob)
def get_service_square_data_html(case_id):
     ## Load from cache (mind state)
    Mind,session_id,answer_dict=local_load_multimodal(case_id)
    try: html=answer_dict.get('multimodal',{}).get('html','')
    except: html=''
    if not html:
        html="" #"- at session_id: "+str(session_id)
    return html


"""
https://core.epventures.co/api/v1/case/657a51719a57063d991dcd51/square_data?fin_session_id=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2NTcxYjg2YTg4MDYxNjEyYWEyZmM4YjciLCJlbWFpbCI6InNoaXZhbUBzaGl2YW1wYXRlbHMuY29tIiwiaWF0IjoxNzAyNjQ5NzUzLCJleHAiOiIyMDIzLTEyLTE2VDAyOjE1OjUzLjAwMFoifQ.3256118dccb64b9710bb4429d31412e11175c040c72811990084a4ea1cae2773&user_id=6571b86a88061612aa2fc8b7
"""
"""
 [{'Transaction Transaction Date': '2021-12-10', 'Transaction Filename Page Num': 2, 'Transaction Account Number': '000000705265012', 'Transaction Transaction Description': 'Orig Co Name:Pay Plus Orig 1D:6452579291 Desc Date:211210 Co Entry Descr:Achtrans Sec:Ccd Trace#:101000695726320 Eed:211210 Ind Id:452579291 Ind Name:Zp Account 1 Ppsaccount Trn: 3445726320T¢', 'Transaction Section': 'Withdrawals And Debits', 'Transaction Filename': '7D889C63-C564-44D9-Aa87-B551E9062Fdc.Pdf', 'Entities': [{'role': 'RECEIVER', 'name': 'Zp Account 1 Ppsaccount', 'label': 'Entity', 'id': '657a51719a57063d991dcd51-452579291', 'type': 'individual', 'entity_id': '452579291'}], 'Transaction Transaction Amount': '42696.00'}]

"""

## Flatten data model to k-v  [ ] move upstream
#Flatten the List of Dictionaries: We'll iterate through each dictionary in the list and flatten it.
#Normalize 'Entities' Field: When the 'Entities' field is encountered, and it's a list, we'll format it according to your specifications.
#String Formatting: For the 'Entities' list, if its length is 1, we'll use a simple comma-separated format. If it's longer, we'll use a format that separates each item by a pipe (|) symbol and each key-value pair by a comma.
#
def flatten_data(data):
    flattened_data = []

    for item in data:
        flattened_item = {}
        for key, value in item.items():
            
            if isinstance(value, list):
                # Format the Entities list into a string
                if len(value) == 1:
                    flattened_item[key] = ', '.join([f"{k}:{v}" for k, v in value[0].items()])
                else:
                    flattened_item[key] = ' | '.join([', '.join([f"{k}:{v}" for k, v in entity.items()]) for entity in value])
            else:
                flattened_item[key] = value
        flattened_data.append(flattened_item)

    return flattened_data


def local_no_lists_as_values(html_data):
    # 
    html_data=flatten_data(html_data)
    return html_data

def local_clean_headers(data):
    def clean_key(key):
        parts = key.split()
        if len(parts) > 1 and parts[0] == parts[1]:
            return ' '.join(parts[1:])
        return key

    cleaned_data = []
    for item in data:
        cleaned_item = {clean_key(key): value for key, value in item.items()}
        cleaned_data.append(cleaned_item)

    return cleaned_data

def local_remove_headers(data):
    global SPECIAL_EXCLUDE_KEYS_DATA_TABLE
    #[ ] ideally move this upstream

    # Process each item in the data to remove excluded headers
    cleaned_data = []
    for item in data:
        # Create a new dictionary for each item, excluding the keys in exclude_keys
        cleaned_item = {key: value for key, value in item.items() if key.lower() not in SPECIAL_EXCLUDE_KEYS_DATA_TABLE}
        cleaned_data.append(cleaned_item)

    return cleaned_data            

## VERSION v1: is json list of records (from df (see source description above))
def get_service_square_data_records(case_id):
     ## Load from cache (mind state)
    if case_id=='case_chart_data_v1': return get_square_data_sample(case_id)

    Mind,session_id,answer_dict=local_load_multimodal(case_id)
    try:
        html_data=answer_dict.get('multimodal',{}).get('html_data','')
    except:
        html_data=''
    if not html_data:
        html_data={}

    ## Tweak output no list in field value
    html_data=local_no_lists_as_values(html_data)
    html_data=local_clean_headers(html_data)
    
    html_data=local_remove_headers(html_data)


    return html_data

def dev1():
    print ("*if can't find proper dict, recall its' cached sso test_question_to_cache.py for load")

    case_id='MarnerHoldingsB'

    Mind,session_id,answer_dict=local_load_multimodal(case_id)

    print (">> answer_dict: "+str(answer_dict['multimodal'].keys()))
    print ("^^for case id: "+str(case_id))
    
    square_data=answer_dict.get('multimodal',{}).get('html_data','')
    
    print ("SQUARE DATA: "+str(square_data))

    return


if __name__=='__main__':
    branches=['dev1']
    for b in branches:
        globals()[b]()


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
