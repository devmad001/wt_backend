import os
import sys
import time
import codecs
import json
import re

from datetime import datetime


LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"

sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")
sys.path.insert(0,LOCAL_PATH+"../../")

from w_storage.ystorage.ystorage_handler import Storage_Helper

from w_storage.gstorage.gneo4j import Neo
from z_apiengine.services.alg_generate_pdf_hyperlink import alg_generate_transaction_hyperlink
        
from get_logger import setup_logging
logging=setup_logging()


#0v1# Jan 22, 2024


"""
    HELP FIXED QUERIES
    - cache
    - query
"""


## Cache instance
datasets_dir=LOCAL_PATH+"../../w_datasets"
if not os.path.exists(datasets_dir):
    raise Exception("Missing datasets dir: "+datasets_dir)
CacheStorage=Storage_Helper(storage_dir=datasets_dir)
CacheStorage.init_db('cache_transactions')



## Local query

def local_query2jsonl(stmt):
    jsonl=[]
    jsonl,df,tx,meta=Neo.run_stmt_to_normalized(stmt)
    return jsonl


def load_response_from_cache(case_id,kind='',expires=24*60*60):
    global CacheStorage

    id=case_id
    if kind:
        id=case_id+kind
    else:
        id=case_id

    tts={}
    meta={}
    dd=CacheStorage.db_get(id,'tts',name='cache_transactions')
    if dd:
        tts=dd['tts']
        meta['age']=time.time()-dd['the_time']
        logging.info("load_transactions_from_cache age: "+str(meta['age']))
        
    ## Expiry
    if tts and expires:
        if meta['age']>expires:
            tts={}
            meta['age']=0

    return tts,meta

def add_response_to_cache(case_id,tts,kind=''):
    global CacheStorage
    
    if kind:
        id=case_id+kind
    else:
        id=case_id

    ## Prepare record
    #- date
    ## Add to cache
    #[ ] check serializeable
    dd={}
    dd['id']=id
    dd['kind']=kind
    dd['case_id']=case_id
    dd['tts']=tts
    dd['the_time']=time.time()
    
    CacheStorage.db_put(id,'tts',dd,name='cache_transactions')
    

    return


if __name__=='__main__':

    branches=['dev1']

    for b in branches:
        globals()[b]()
    










