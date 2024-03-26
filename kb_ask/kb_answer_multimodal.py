import os
import sys
import time
import codecs
import datetime
import copy
import json
import re
import uuid
import pandas as pd

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")

from w_storage.gstorage.gneo4j import Neo
from w_storage.ystorage.ystorage_handler import Storage_Helper

## More unconventional 'ideal' queries or approaches
#from ideal_answer import Ideal_Answer


from get_logger import setup_logging
logging=setup_logging()

Storage=Storage_Helper(storage_dir=LOCAL_PATH+"../w_datasets")
Storage.init_db('kb_ask')


#0v1# JC  Nov 11, 2023  Setup

"""
    MORE ELABORATE HANDLING OF MULTI-MODAL RESPONSE KINDS

"""

def prepare_map_data(df):
    #[ ] have some already so keep optional for now
    # Initialize variables
    latitude_col = None
    longitude_col = None
    has_lat_lng = False
    
    # Function to check if a column can be converted to float

    def can_convert_to_float(df, column):
        # Create a copy of the DataFrame to avoid modifying the original one
        df_copy = df.copy()
    
        # Convert the column to numeric, coercing errors to NaN, and then fill NaN with 0
        df_copy[column] = pd.to_numeric(df_copy[column], errors='coerce').fillna(0)
    
        # Check if the column is now of float type
        #if df_copy[column].dtype == float or df_copy[column].dtype == int:
        if df_copy[column].dtype == float:
            return True
        else:
            print("NOT FLOAT: " + str(df_copy[column]))
            return False

    
    # Search for latitude and longitude columns
    
    if not df is None:
        for col in df.columns:
            col_lower = col.lower()
            if 'lat' in col_lower or 'latitude' in col_lower:
                if can_convert_to_float(df,col):
                    latitude_col = col
            elif 'lng' in col_lower or 'longitude' in col_lower:
                if can_convert_to_float(df,col):
                    longitude_col = col
        
        # Check if both latitude and longitude columns are found
        if latitude_col is not None and longitude_col is not None:
            has_lat_lng = True
        
        # (Optional) Convert the latitude and longitude columns to float if they are not already
        if has_lat_lng:
            df[latitude_col] = pd.to_numeric(df[latitude_col], errors='coerce') #if '' to Nan
            #df[latitude_col] = df[latitude_col].astype(float)
            #df[longitude_col] = df[longitude_col].astype(float)
            df[longitude_col] = pd.to_numeric(df[longitude_col], errors='coerce') #if '' to Nan
        
        print ("HAS LAT: "+str(has_lat_lng)+" form: "+str(df.columns))
    return df,has_lat_lng,latitude_col,longitude_col


def can_convert_to_datetime(df, column):
    # Check if the column's data type is likely to contain dates
    #>> too flexible:            pd.to_datetime(df[column])
    #[ ] todo:  possible for 1 of 2000 has bad date and will flag as bad date.
    can_convert=True
    reasons=[]
    
    ## Could be dtype or another df?
    try:
        if df[column].dtype.kind not in ['O', 'M']:
            reasons+=['Not object or datetime']
    except:
        can_convert=False

    if can_convert:
        if df[column].dtype.kind not in ['O', 'M']:
            # If the data type is not object (string-like) or datetime, return False
            reasons+=['Not object or datetime']
            can_convert=False
    
        if can_convert:
            
            try:
                pd.to_datetime(df[column])  #In except not caught?
                can_convert=True #already true
            except:
                ### Exception
                ## Possible one bad date can stop them all so do percentage
                # Step 1: Convert the date column, coercing errors to NaT
                try:
                    temp= pd.to_datetime(df['date_column'], errors='coerce')

                    # Step 2: Calculate the percentage of valid datetime entries
                    valid_percentage = temp.notna().mean() * 100
                    if valid_percentage>50:
                        can_convert=True
                    else:
                        reasons+=['Less than 50% valid datetime: '+str(valid_percentage)]
                        can_convert=False
                except:
                    reasons+=['Cannot coerce to datetime at column: '+str(column)]
                    can_convert=False
    if not can_convert:
        pass
#        print ("[debug] cannot convert to datetime: "+str(column)+" because: "+str(reasons))
    return can_convert
        
def prepare_timeline_data(df):
    # Initialize variables
    date_col = None
    amount_col = None
    is_timelineable = False
    reasons=[]

    # Priority list for amount column
    amount_priorities = ['amount', 'value', 'price', 'cost', 'total', 'balance',
                         'balance_amount', 'balance_value', 'balance_total', 
                         'balance_cost', 'balance_price', 'count']

    # Search for a date column
    if df is not None:
        for col in df.columns:
            if col in ['transaction_date']:
                date_col=col

        if not date_col:
            for col in df.columns:
                if True:
                    print ("[date col]: "+str(col)+" has value: "+str(df[col].values))
                if can_convert_to_datetime(df, col):
                    date_col = col
                    break
        if not date_col:
            reasons+=['No date col found']
            print ("[debug1] no date found")
            #a=eeee
    
        # Search for an amount column with priority
        for priority in amount_priorities:
            for col in df.columns:
                if priority in col.lower() and is_numeric(df,col):
                    amount_col = col
                    break
            if amount_col is not None:
                break
        if not amount_col:
            reasons+=['No amount col found']
    
        # Check if both date and amount columns are found
        if date_col is not None and amount_col is not None:
            is_timelineable = True
            logging.info("[is_timelineable]: "+str(is_timelineable)+" at date col: "+str(date_col))
    else:
        reasons+=['Not timelineable: no df']
        
    ## Verbose reasons
    for r in reasons:
        print ("[not timelineable] reason: "+str(r))
    if reasons:
        print ("[not timelineable] columns: "+str(list(df.columns)))

    return date_col, amount_col, is_timelineable


def is_numeric(df, column):
    #> boolean is NOT numeric
    
    # Check if the column is numeric
    is_numeric_type = pd.api.types.is_numeric_dtype(df[column])
    
    # Check if the column is not a boolean type
    is_not_bool = not pd.api.types.is_bool_dtype(df[column])

    # Return True if it is numeric and not boolean, otherwise False
    return is_numeric_type and is_not_bool

def allow_category_col(candidate):
    allow=True
    not_category=['Longitude','Latitude','lat','lng']
    for nc in not_category:
        if re.search(r'\b'+nc+r'\b',candidate,re.IGNORECASE):
            allow=False
    return allow

def prepare_barchart_data(df):
    # Initialize variables
    category_col = None
    value_col = None
    is_barchartable = False
    
    if df is None:
        return category_col, value_col, is_barchartable

    # Priority list for value column
    value_priorities = ['count', 'amount', 'freq', 'value', 'price', 'cost', 'total', 'balance',
                        'balance_amount', 'balance_value', 'balance_total', 
                        'balance_cost', 'balance_price', 'transactions']

    # Search for a value column with priority
    ## [VALUE LOGIC A]
    for priority in value_priorities:
        for col in df.columns:
#            print ("NUMERIC: "+str(col)+": "+str(is_numeric(df,col)))

            if priority in col.lower() and is_numeric(df,col):
                value_col = col
                break
        if value_col is not None:
            break
    ## [VALUE LOGIC B]
    #:: if even numeric then assume value
    if not value_col:
        for col in df.columns:
            if is_numeric(df,col):
                value_col = col
                break

    # Search for a category column
    #[logic 1] We want a column with a limited number of distinct values, but not unique for each row

    # Assuming df is a pandas DataFrame

    for col in df.columns:
        try:
            # Ensure the column is not of an object type that might cause unexpected behavior

            ## df in df!!
            if isinstance(df[col],list):
                print ("[todo] handle list within df")
            elif isinstance(df[col],pd.DataFrame):
                print ("[todo] handle df within df")

            elif df[col].dtype == 'object' or df[col].dtype == 'category':
                unique_count = df[col].nunique()
                total_rows = len(df)
    
                # Explicitly cast to integers to avoid any ambiguity
                unique_count = int(unique_count)
                total_rows = int(total_rows)
    
                # Robust comparison
                if 1 < unique_count < total_rows / 2:
                    if allow_category_col(col):
                        category_col = col
                        break
        except Exception as e:
            print(f"An error occurred while processing column '{col}': {e}")
            #^possibly a df itself
            # Optionally, handle the error or continue to the next column
            continue


    #[logic 2]  If only two columns then assume category and value?
    if not category_col and value_col:
#        if len(df.columns)<4: #Why 4?  when 2 or 3 maybe?
        for col in df.columns:
            if not allow_category_col(col): continue
            
            # Not the value col
            if col!=value_col:  #Not the value col
                # Not just numeric
                if not is_numeric(df,col) and not can_convert_to_datetime(df, col):
                    category_col=col
                    ## Not just unique value categories (ie/ repeated -- unless just 1?)
                    #if df[col].nunique() != len(df[col]):
                    #    category_col=col
    #[logic 3]:  type or group or category or xxx
    if not category_col:
        for col in df.columns:
            if not allow_category_col(col): continue
            for sname in ['type','group','category']:
                if sname in col.lower():
                    category_col=col
                    break
    #[logic 4]  If only two columns and not category then yes def cat
#        if len(df.columns)<4: #Why 4?  when 2 or 3 maybe?
    if len(df.columns)==2 and not category_col and value_col:
        for col in df.columns:
            if not allow_category_col(col): continue
            # Not the value col
            if col!=value_col:  #Not the value col
                category_col=col

    logging.info("[barchart] candidate value: "+str(value_col)+" can category: "+str(category_col))
    # Check if both category and value columns are found
    if category_col is not None and value_col is not None:
        is_barchartable = True

    print ("[debug]  CATEGORY COL: "+str(category_col)+" from options: "+str(list(df.columns)))
    return category_col, value_col, is_barchartable

## Used elsewhere so enforce schema
def control_load_decision(name):
    #** see abstract_FE since decision is mapped to FE Component names
    if not name in ['timeline','timeline_dynamic','map','barchart']:
        raise Exception("Invalid show_decision: "+str(name))
    return name

def prepare_multimodal_insight_dict(multimodal, question=None, case_id=None, meta={},force_show_decision=''):
    print ("**RECALL, you have the prepare html data etc but this is more stand-alone")
    # meta['multimodal']==multimodal

    ## Apply logic below
    
    ## CHECK MULTIMODAL RECORDS
    #- expose features
    idict={}
    idict['features']={}
    idict['features']['has_lat_lng']=None
    idict['features']['is_timelineable']=None
    idict['features']['is_barchartable']=None
    
    idict['column_names_map']={}
    
    df=multimodal['df']
    
    #### MAP DATA
    # Does df column have column name \blat\b,\blng\b,latitude or longitude (case insensitive) AND is float (or string that looks like float)
    df,idict['features']['has_lat_lng'],lat_col,lng_col=prepare_map_data(df)
    idict['column_names_map']['latitude']=lat_col
    idict['column_names_map']['longitude']=lng_col
    

    #### TIMELINE DATA
    # Is there a date, amount and suppose transaction info
    idict['column_names_map']['timeline_date_col'], idict['column_names_map']['timeline_amount_col'], idict['features']['is_timelineable']=prepare_timeline_data(df)
    if not idict['features']['is_timelineable']:
        print ("[debug] NOT timelineable!")
    

    #### BARCHART DATA
    category_col, value_col, idict['features']['is_barchartable']=prepare_barchart_data(df)
    idict['column_names_map']['barchart_category_col']=category_col
    idict['column_names_map']['barchart_value_col']=value_col
    

    #################################
    ## DECIDE ON WHAT TO SHOW
    show_options=['timeline','map','barchart']
    
    idict['show_decision']=''
    
    ## Mostly for debug but allow forcing decision (ie/ barchart possible as well?)
    if force_show_decision: #
        idict['show_decision']=control_load_decision(force_show_decision)
    elif idict['features']['has_lat_lng']:
        idict['show_decision']=control_load_decision('map')
    elif idict['features']['is_timelineable']:
        idict['show_decision']=control_load_decision('timeline_dynamic')
    elif idict['features']['is_barchartable']:
        idict['show_decision']=control_load_decision('barchart')
    else:
        pass

    logging.info("IDICT: "+str(idict))
    logging.info("[show decision]: "+str(idict['show_decision']))

    return idict



def dev1():
    ### Recall:
    #- "square" view component
    #LOGIC:  defaults to html table view of response data


    ####
    #- "timeline" large view component

    timeline_views=['timeline','map','barchart']
    #LOGIC:  if map data (latitude/longitude) then map
    #LOGIC:  if dates + amounts (I guess if transaction) then timeline
    #LOGIC:  if values then barchart
    
    # Flexible answer form (variations on a chart, pre-defined Q50 etc)

    
    return


def dev_local_qna():
    from kb_ask.kb_ask import AI_handle_kb_question
    ##> Try some questions and refine the multimodal responses

    case_id='chase_3_66_5ktransfer'
    question='Show me all transactions including date and amount'


    text_response,meta,Agent=AI_handle_kb_question(question,case_id=case_id)
    
    ## META KEYS:
    #RE META KEYS: dict_keys(['run_id', 'question', 'case_id', 'rating', 'cypher', 'llm_query_make_cypher', 'data_response', 'df', 'data_response_token_length', 'human_readible', 'llm_query_make_readable', 'run_time', 'multimodal', 'response', 'the_date'])
    
    ## META['multimodal'].keys()
    # RE META multi: dict_keys(['human_readible', 'jsonl', 'df', 'df_filtered', 'chatbot', 'barchart', 'timeline', 'html', 'map'])

    
    if False:
        print ("RE: "+str(text_response))
        print ("RE META: "+str(meta))
        print ("RE META KEYS: "+str(meta.keys()))
        print ("RE META multi: "+str(meta['multimodal']))
        print ("RE META multi: "+str(meta['multimodal'].keys()))
        print ("(for question: "+str(question)+")")


    idict=prepare_multimodal_insight_dict(meta['multimodal'],question=question,case_id=case_id,meta=meta)




    return





if __name__=='__main__':
    branches=['dev1']
    branches=['dev_local_qna']

    for b in branches:
        globals()[b]()




