import os
import sys
import codecs
import json
import re
import pandas as pd

from fastapi import FastAPI

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")

sys.path.insert(0,LOCAL_PATH+"../..")
from w_storage.gstorage.gneo4j import Neo

from w_mindstate.mindstate import get_dashboard_data
from kb_ask.kb_answer_multimodal import prepare_barchart_data

from service_test_data.chart_case_data_v1 import get_barchart_data_sample


from get_logger import setup_logging
logging=setup_logging()


        
#0v1# JC Nov 13, 2023  Setup



"""
    BARCHART SERVICE
"""

#from project_root.app.models.timeline import Timeline

"""

"""

def local_get_category_column(data):
    # Transform data[0] dict record to dataframe 1 row
    df=pd.DataFrame(data[0],index=[0])
    col_cat,col_value,is_barchartable=prepare_barchart_data(df)
    return col_cat

def reformat_given(data,col_value,col_cat):
    # List of all possible transaction types
    #all_types = ["withdrawal", "deposit", "other", "refund", "fee", "reversal"]
    logging.info("[debug] barchart value column: "+str(col_value)+" and category column: "+str(col_cat))
    

    # Extract unique transaction types and sort them by col_value in descending order
    try:
      all_types = sorted(set(item[col_cat] for item in data), key=lambda x: -sum(item[col_value] for item in data if item[col_cat] == x))
    except Exception as e:
        logging.info("[barchart_service.py could not find all types]: "+str(data))
        logging.info("[ERROR]: "+str(e))
        all_types = []


    # Initialize an empty list for the target format
    target_format = []

    # Create a dictionary with default counts for each type
    for transaction_type in all_types:
        transaction_dict = {"stacks": transaction_type}
        for t_type in all_types:
            transaction_dict[t_type] = 0
        target_format.append(transaction_dict)

    # Update counts for each given transaction type
    for item in data:
        if item.get(col_cat,'') and item.get(col_value,''):
            given_type = item[col_cat]
            count = item[col_value]
            # Find the corresponding dictionary and update the count
            for transaction_dict in target_format:
                if transaction_dict["stacks"] == given_type:
                    transaction_dict[given_type] = count
                    break

    return target_format

    
def dev_local_format_barchart():
    ## From df to d3 barchart

    GIVEN= [
      {
        "Count_of_Transactions": 48,
        "Transaction_Type": "withdrawal"
      },
      {
        "Count_of_Transactions": 22,
        "Transaction_Type": "deposit"
      },
      {
        "Count_of_Transactions": 13,
        "Transaction_Type": ""
      },
      {
        "Count_of_Transactions": 7,
        "Transaction_Type": "other"
      },
      {
        "Count_of_Transactions": 1,
        "Transaction_Type": "refund"
      },
      {
        "Count_of_Transactions": 1,
        "Transaction_Type": "fee"
      },
      {
        "Count_of_Transactions": 1,
        "Transaction_Type": "reversal"
      }
    ]

    TARGET_FORMAT=[  {"stacks":"A","Type_1":123,"Type_2":0,"Type_3":0,"Type_4":0},
   {"stacks":"B","Type_1":0,"Type_2":107,"Type_3":0,"Type_4":0},
   {"stacks":"C","Type_1":0,"Type_2":0,"Type_3":123,"Type_4":0},
   {"stacks":"D","Type_1":0,"Type_2":0,"Type_3":0,"Type_4":203}
]
    col_value='Count_of_Transactions'
    cat_value='Transaction_Type'

    got=reformat_given(GIVEN,col_value,cat_value)

    print ("GOT: "+str(got))
    return

def auto_subset_data(data,col_value, col_cat, keep_top=15):
    #Given jsonl transform to df
    count_of_unique_categories=0

    df=pd.DataFrame(data)
    
    if col_cat and col_cat in df.columns:
        count_of_unique_categories=len(df[col_cat].unique())
    
    if count_of_unique_categories>keep_top:
        logging.info("[barchart_service.py auto subset data]: "+str(count_of_unique_categories))

        ## Auto subset
        df=df.sort_values(by=[col_value],ascending=False)
        
        ## Keep top 10
        #- check proportion that kept? [ ]
        df=df.iloc[:keep_top]
        data=df.to_dict('records')
    
    return data


def get_service_barchart_data(case_id='case_atm_location'):
    logging.info("[barchart data at case]: "+str(case_id))
    if case_id=='case_chart_data_v1': return get_barchart_data_sample(case_id)
    
    records_list=[]

    ## Get from mindbody though also needs multimodal the_dashboard
    Dashboard,multimodal=get_dashboard_data(case_id)
    
    ## Barchart data in multimodal
    
    if 'dev check data' in []:
        print ("FO: "+str(multimodal['multimodal']['barchart']))
        print ("FO: "+str(multimodal['multimodal'].keys()))
        print ("idict: "+str(multimodal['multimodal']['idict']))

    timeline_view_type=multimodal['multimodal']['timeline_view_type']
    timeline_view_url=multimodal['multimodal']['timeline_view_url']
    
    ## Assume barchart chosen and get relevant column dimensions
    idict=multimodal['multimodal']['idict']
    
    print ("NAMES: "+str(idict))
    
    x_axis_title=''

    if 'column_names_map' in idict:
        col_cat=idict['column_names_map']['barchart_category_col']
        col_value=idict['column_names_map']['barchart_value_col']

        x_axis_title=col_cat
        
        ## Transform barchart df data into d3 friendly format
    
        GIVEN_JSONL=multimodal['multimodal']['barchart']     # (usually like above)
        logging.info("[RAW GIVEN_JSONL]: "+str(GIVEN_JSONL))
        #if not GIVEN_JSONL: print ("RAWRAW DUMP: "+str(multimodal['multimodal']))
        
        if GIVEN_JSONL:
            ## Exception check possible that column header renamed to ease user experience
            if col_cat not in GIVEN_JSONL[0].keys():
                logging.info("[barchart_service.py col_value not in data[0].keys()]: "+str(GIVEN_JSONL[0].keys()))
                ## Recalculate special
                col_cat=local_get_category_column(GIVEN_JSONL)
                
            ## Auto subset (ie/ 30+ bars too many)
            GIVEN_JSONL=auto_subset_data(GIVEN_JSONL,col_value,col_cat)
                
            ## Translate jsonl to d3 friendly format
            d3_barchart_records=reformat_given(GIVEN_JSONL,col_value,col_cat)
            
        
            ## Validate vs expected [ ]
            logging.info("[debug] raw d3 barchart: "+str(d3_barchart_records))
            
            ## Auto do title etc.
            
            records_list=d3_barchart_records
    else:
        logging.info("[get barchart data but no column names map expected at: "+str(idict))
        
    #(recall, data['data'] appended at router normalize)
    return records_list,x_axis_title


if __name__=='__main__':
    branches=['dev_local_format_barchart']
    branches=['get_service_barchart_data']

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