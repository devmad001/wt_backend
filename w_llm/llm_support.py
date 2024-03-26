import time
import os
import sys
import codecs
import copy
import json
import re
import datetime
import hashlib
import random
import threading
import pandas as pd

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)

import langchain
from langchain.llms import OpenAI #pip install langchain
from langchain.chat_models import ChatOpenAI  #New ? timeout?

from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate, PromptTemplate
from langchain.prompts.chat import SystemMessage

import tiktoken #pip isntall tiktoken  https://github.com/openai/tiktoken

sys.path.insert(0,LOCAL_PATH+"..")

from get_logger import setup_logging
from w_admin.load_credentials import get_creds
from w_storage.ystorage.ystorage_handler import Storage_Helper

logging=setup_logging()


#0v1# JC  Jan 15, 2024  Stand-alone


"""
    STAND-ALONE SUPPORT FUNCTIONS FOR LLM
    -
"""

Storage=None

def num_tokens_from_string(string: str, encoding_name='cl100k_base') -> int:
    """Returns the number of tokens in a text string."""
    encoding = tiktoken.get_encoding(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens


def generate_hash(text):
    # Create a SHA-256 hash object
    sha256 = hashlib.sha256()
    # Update the hash object with the bytes-like object (text in bytes format)
    sha256.update(text.encode())
    # Return the hexadecimal representation of the hash
    return sha256.hexdigest()


def cache_llm(given,response,meta):
    global Storage

    # id? tokens used? time?
    if not Storage:
        Storage=Storage_Helper(storage_dir=LOCAL_PATH+"../w_datasets")
        Storage.init_db('cache_llm')

    hash_text=given+meta.get('library','')+meta.get('model_name','')
    hash_id=generate_hash(hash_text)

    record={}
    record['id']=hash_id
    record['given']=given
    record['response']=response
    record['the_date']=str(datetime.datetime.now())
    record['meta']=meta

    ## Filter out bad responses

    # if response ends with "..." don't store
    if (len(str(response))>10) and str(response)[-3:]=='...':
        logging.info("[debug] response ends with ... so NOT storing")
    else:
        Storage.db_put(record['id'],'record',record,name='cache_llm')

    return

def load_cache(given,meta):
    global Storage
    response=None
    if not Storage:
        Storage=Storage_Helper(storage_dir=LOCAL_PATH+"../w_datasets")
        Storage.init_db('cache_llm')
    hash_text=given+meta.get('library','')+meta.get('model_name','')
    hash_id=generate_hash(hash_text)
    dd=Storage.db_get(hash_id,'record',name='cache_llm')
    if dd:
        ## Don't load cropped response
        if isinstance(dd['response'],str) and dd['response'][-3:]=='...':
            logging.info("[debug] response ends with ... so NOT loading")
        else:
            response=dd['response']
    if response:
        logging.info("[info] Loaded cached llm response")
    return response

def remove_cache_entry(given,meta):
    global Storage
    response=None
    if not Storage:
        Storage=Storage_Helper(storage_dir=LOCAL_PATH+"../w_datasets")
        Storage.init_db('cache_llm')
    hash_text=given+meta.get('library','')+meta.get('model_name','')
    hash_id=generate_hash(hash_text)
    dd_removed=Storage.db_remove(hash_id,name='cache_llm')
    if dd_removed:
        try:
            logging.dev("[warning] could not remove cached llm: "+str(dd_removed)) #Dec 20 threaded
        except: pass

    return



def iter_cache():
    global Storage
    logging.info("[debug] cache takes 10s for 10k records")

    if not Storage:
        Storage=Storage_Helper(storage_dir=LOCAL_PATH+"../w_datasets")
        Storage.init_db('cache_llm')

    #record={}
    #record['id']=hash_id
    #record['given']=given
    ##record['response']=response
    #record['meta']=meta
    
    df=pd.DataFrame()
    start_time=time.time()
    records=[]
    for kk in Storage.iter_database('cache_llm'):
        dd=Storage.db_get(kk,'record',name='cache_llm')
#        print ("[debug] loaded: "+str(dd))
#        print ("[debug] loaded: "+str(dd.get('meta',{}).keys()))
        # : dict_keys(['model_name', 'library', 'tokens', 'runtime'])
        
        ## Create dataframe dump of db [ ] move to lib?
        # id,given,response  then from meta: model_name, library, tokens, runtime

        meta=dd.pop('meta',{})
        for kk in meta:
            dd[kk]=meta[kk]
            
        #if not 'the_date' in dd: dd['the_date']=Storage.db_get(kk,'the_date',name='cache_llm')
        dd['the_date']=Storage.db_get_the_date_obj(kk,name='cache_llm')

        records+=[dd]
        
        if len(records)>100: break

    df=pd.DataFrame(records)
    
    ## the_date started Nov 23...
        
    logging.info ("Loaded "+str(len(df))+" records in "+str(time.time()-start_time)+" seconds")
    logging.info ("COLS: "+str(df.columns))
    
    # print the footer of the data (the end rows)
    logging.info (df.tail(20))

    return


## OPENAI ACCOUNTS
# future options:  allow multi-threaded use (so consider locks on use)

class OPENAI_Accounts:
    def __init__(self):
        self.accounts=[]
        self.account_index=0
        self.account=None
        self.account_lock=threading.Lock()
        self.load_accounts()
        return
    
    def load_accounts():
        #/w_admin/openai.ini
        #- email, email2, email3...
        return


def dev_openai_accounts():
    OA=OPENAI_Accounts()
    return




if __name__=='__main__':
    branches=['play_chattemplate']
    branches=['dev_openai_accounts']

    for b in branches:
        globals()[b]()






