import os
import sys
import codecs
import json
import copy
import re
import pandas as pd

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")

#from get_logger import setup_logging
#logging=setup_logging()

# Set the display options for pandas
pd.set_option('display.max_columns', None)  # This option displays all columns
pd.set_option('display.expand_frame_repr', False)  # This option ensures that the DataFrame is not broken into multiple lines
pd.set_option('display.max_rows', None)  # Optional: You might also want to see all rows


#0v1# JC  Oct  3, 2023  Init

"""
    Transform standard jsonl into a pandas dataframe
    - order columns
    - convert date to datetime
"""

def flatten_dict(d, parent_key='', sep='_'):
    """Function to flatten a nested dictionary."""
    items = {}
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.update(flatten_dict(v, new_key, sep=sep))
        else:
            items[new_key] = v
    return items
    
def resolve_if_nested(jsonl):
    #ie/ cypher return just n (node) then jsonl of nested dict
#    print ("given JSONL: "+str(jsonl))

    ### AUTO FIX WHERE POSSIBLY NESTED
    is_nested=True
    top_key_count=0
    for record in jsonl:
#must check#         if len(record.keys())>1: is_nested=False
        ## If key value is not dict then not nexted
        # [{'account_number': '000000373171278'}]
        top_key_count=max(top_key_count,len(record.keys()))
        if not isinstance(list(record.values())[0],dict):
            is_nested=False
    
    if is_nested:
        if top_key_count==1:
            ## Nested but only 1 key at top ie 'n'
            nested_key=list(jsonl[0].keys())[0]
            temp=[]
            for record in jsonl:
                temp+=[record[nested_key]]
            jsonl=temp
        else:
            # Flatten ie n_* e_* as headers
            temp=[]
            for record in jsonl:
                temp+=[flatten_dict(record)]
            jsonl=temp

    return jsonl

def graph_to_df(jsonl):
    meta={}
    ## Use with data table view OR timeline view
    jsonl=copy.deepcopy(jsonl)
    
    jsonl=resolve_if_nested(jsonl)
    
    #Column order
    #- date,x,y,z,amounts
    layout_method='timeline'
    
#D#    print ("[debug] working with raw data: "+str(jsonl))
    headers_unsorted=unique_keys = set(key for d in jsonl for key in d)
    
    ## Look for date
    date_keys=[]
    amount_keys=[]
    
    ## STANDARD LOOK
    for record in jsonl:
        ## Find date column
        if not date_keys:
            for key in record:
                if 'date' in key.lower():
                    # 2020-10-03 ideally
                    if re.search(r'[\d]{1,2}\-[\d]{1,2}\-[\d]{1,2}', str(record[key])):
                        date_keys=[key]+date_keys #to start cause best option
                    else:
                        date_keys+=[key] #To end, doesn't look like date but likely is
                        
        ## Find amount column
        if not amount_keys:
            for key in record:
                sdata=str(record[key])
                if 'total' in key.lower():
                    if re.search(r'\d',sdata):
                        amount_keys=[key]+amount_keys
                elif 'balance' in key.lower():
                    if re.search(r'\d',sdata):
                        amount_keys=[key]+amount_keys
                elif 'amount' in key.lower():
                    if re.search(r'\d',sdata):
                        amount_keys=[key]+amount_keys
    ## DEEPER LOOK
    if not date_keys:
        for record in jsonl:
            ## Look just for date (ignoring column heading)
            for key in record:
                if re.search(r'[\d]{1,2}\-[\d]{1,2}\-[\d]{1,2}', str(record[key])):
                    date_keys=[key]+date_keys
                    
    ## Assemble column headers based on date & amounts
    headers=[]
    
    #[ ] amount at end
    amount_col=''
    if amount_keys:
        amount_col=amount_keys[0]
        headers_unsorted.remove(amount_col)
    
    #[ ] date first
    if date_keys:
        headers+=[date_keys[0]]
        # Remove from unsorted
        headers_unsorted.remove(date_keys[0])
        
    ## Add normal headers
    for header in headers_unsorted:
        headers+=[header]
        
    ## Add end header
    if amount_col:
        headers+=[amount_col]
        
#D#    print ("[normalize headers]: "+str(headers))

    ### PANDAS DF
    
    # Convert list of dictionaries into a DataFrame
    df = pd.DataFrame(jsonl)
    
    # Reorder the DataFrame columns based on the headers list
    # For columns in headers that are not in the DataFrame, NaN values will be inserted
    df = df.reindex(columns=headers)
    
    # Fill empty
    df = df.fillna({col: '' for col in headers})
    
    ### CHECK FORMATS

    ## By default pandas should consider it as a date otherwise...
    # Convert 'transaction_date' to datetime
#    print ("[debug] date keys: "+str(date_keys))
    if date_keys:
        try: df[date_keys[0]] = pd.to_datetime(df[date_keys[0]])
        except: pass


    # Check DataFrame info to verify the data type of 'transaction_date'
    if False:
        print(df.info())
        
    return df,meta


def dev1():
    #(org internal_quesitons)
    from w_storage.gstorage.gneo4j import Neo
    case_id='case_o3_case_single'
    yes=devonly
    #
    stmt="""
    MATCH (s)-[:DEBIT_FROM]->(t:Transaction)
    WHERE exists(t.transaction_amount) AND exists(s.name)
        AND t.case_id='"""+case_id+"""'
    RETURN
        coalesce(s.name, s.id) AS sender_name,
        t.transaction_amount AS transaction_amount,
        t.transaction_date AS transaction_date
    ORDER BY
        transaction_date ASC;
    """
    
    print ("{running]: "+str(stmt))
    jsonl=[]
    for dd in Neo.run_stmt_to_data(stmt):
        print ("dd> "+str(dd))
        jsonl+=[dd]
        
    df,meta=graph_to_df(jsonl)
    
    print ("TABLE: "+str(df))

    return


if __name__=='__main__':
    branches=['dev1']

    for b in branches:
        globals()[b]()




"""

"""
