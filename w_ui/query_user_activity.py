import os
import sys
import time
import codecs
import json
import re
import psutil

import pandas as pd
import textwrap

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")

from w_storage.ystorage.ystorage_handler import Storage_Helper


#0v1# JC  Oct 18, 2023  Setup


"""
    QUERY USER ACTIVITY
"""

# Adjust display options to show the entire DataFrame
pd.set_option('display.max_columns', None)
pd.set_option('display.expand_frame_repr', False)
pd.set_option('max_colwidth', 150)


Storage=Storage_Helper(storage_dir=LOCAL_PATH+"../w_datasets")
Storage.init_db('kb_ask')

def dev1():
    #? where does w_chatbot save responses?
    #> kb_ask/kb_ask.py
    # meta{}
    # id is run id or random
    
    records=[]
    for run_id in Storage.iter_database('kb_ask'):
        meta=Storage.db_get(run_id,'run',name='kb_ask')
        records+=[meta]
        # ['run_id', 'question', 'case_id', 'rating', 'cypher', 'llm_query_make_cypher', 'data_response', 'human_readible', 'llm_query_make_readable', 'run_time', 'response', 'the_date']
#        print (meta.keys())
        
    df=pd.DataFrame(records)
    df['the_date']=pd.to_datetime(df['the_date'])

    df=df.sort_values('the_date', ascending=False)

    skip_cols=['run_id','rating','df','multimodal']

    df = df.drop(columns=['run_id', 'rating'])
    df = df.drop(columns=['llm_query_make_cypher', 'llm_query_make_readable'])
    df = df.drop(columns=['data_response'])
    df = df.drop(columns=['human_readible'])
    
    print (df.head(25))

    return


if __name__=='__main__':
    branches=['dev1']
    for b in branches:
        globals()[b]()
        




"""
"""
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
