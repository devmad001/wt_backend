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
    FIXED QUERIES
    - development area?
    - cypher_playground + various exists
    - this is a bit more formal
    - tied to audits?
    - tied to test?
    - external interface to db?
    
    QUERY REFERENCE (see also):
    - (lots)
    
    NOTES:
    - cache in sqlite (see mindstate.py)

"""

## ECHO TODO:
print (" [ ]  TODO:  add latitude + longitude to transaction meta")


## Cache instance
datasets_dir=LOCAL_PATH+"../../w_datasets"
if not os.path.exists(datasets_dir):
    raise Exception("Missing datasets dir: "+datasets_dir)
Storage=Storage_Helper(storage_dir=datasets_dir)
Storage.init_db('cache_transactions')


## Local query

def local_query2jsonl(stmt):
    jsonl=[]
    jsonl,df,tx,meta=Neo.run_stmt_to_normalized(stmt)
    return jsonl

def FIXED_get_all_transactions(case_id=''):
    # where case_id=case_id
    stmt="""
    MATCH (t:Transaction)
    WHERE
        t.case_id='{case_id}'
    RETURN t
    """.format(case_id=case_id)
    jsonl=local_query2jsonl(stmt)
    
    tts={}
    ## Re-index at transaction id
    for j in jsonl:
        id=j['t']['id']
        tts[id]=j['t']
    return tts

def add_transaction_fields(tts):
    for id in tts:
        tt=tts[id]
        
        ### VARIOUS
        
        ## Hyperlink
        tt['hyperlink_url']=alg_generate_transaction_hyperlink(tt)

        ## Node image (check):
        #node_image=''

        tts[id]=tt

    return tts

def dev1():
    # 2526 in 1.0s  (same on subsequent)
    
    start_time=time.time()
    case_id='65a8168eb3ac164610ea5bc2' ## Big new age
    
    ## GET BASE
    tts=FIXED_get_all_transactions(case_id=case_id)
    
    ## ADD MARKUPS
    tts=add_transaction_fields(tts)
    
    
    run_time=time.time()-start_time

    print ("GOT COUNT: "+str(len(tts))+" in "+str(run_time)+" seconds")
    for id in tts:
        print ("GOT sample: "+str(tts[id]))
        break
    
   # statement_id=['t']['statement_id']
    
    """
    {'t': {'is_credit': True, 'transaction_date': '2020-11-02', 'filename_page_num': 2, 'account_number': '334049185630', 'is_cash_involved': True, 'transaction_amount': 245.75, 'section': 'Cash transactions', 'transaction_method': 'other', 'label': 'Transaction', 'statement_id': '65a8168eb3ac164610ea5bc2-2020-11-01-334049185630-72d85b81-c416-4ffd-950c-f0c1fd62f251.pdf', 'transaction_type': 'deposit', 'transaction_description': 'MERCHANT BNKCD DES:DEPOSIT ID:323242463996 INDN:PLANET SMOOTHIE 19109 CO', 'algList': ['create_ERS'], 'account_id': '65a8168eb3ac164610ea5bc2-334049185630', 'filename': '72d85b81-c416-4ffd-950c-f0c1fd62f251.pdf', 'case_id': '65a8168eb3ac164610ea5bc2', 'versions_metadata': '{"transaction_method_id": "llm_markup-transaction_type_method_goals-", "transaction_type": "llm_markup-transaction_type_method_goals-", "is_cash_involved": "llm_markup-transaction_type_method_goals-", "transaction_method": "llm_markup-transaction_type_method_goals-"}', 'id': 'ec7dc18580087519dbce4e665f11e405bc88919aa2ede1f137389979421ace5b', 'transaction_method_id': '323242463996'}}
    """

    return

def load_transactions_from_cache(case_id,kind=''):
    global Storage
    AGE_EXPIRY=24*60*60 ## 1 day

    id=case_id
    if kind:
        id=id+kind

    tts={}
    meta={}
    dd=Storage.db_get(id,'tts',name='cache_transactions')
    if dd:
        tts=dd['tts']
        meta['age']=time.time()-dd['the_time']
        logging.info("load_transactions_from_cache age: "+str(meta['age']))
        
    ## Expiry
    if meta['age']>AGE_EXPIRY:
        tts={}
        meta['age']=0

    return tts,meta

def add_transactions_to_cache(case_id,tts,kind=''):
    global Storage

    ## Prepare record
    #- date
    ## Add to cache
    #[ ] check serializeable
    dd={}
    dd['id']=case_id+kind
    dd['kind']=kind
    dd['case_id']=case_id
    dd['tts']=tts
    dd['the_time']=time.time()
    
    Storage.db_put(case_id,'tts',dd,name='cache_transactions')

    return

def interface_preload_cache_transactions(case_id,kind=''):
    ## Cache
    #   [ ] age/expire?
    # PERFORMANCE
    # [A]  Initial query, markup, store ==  1.5s (at 2.5k transactions)
    #    - 2.5k tts 1.0s, +(hyperlinks & storage) +0.35 = 1.5s total
    # [B]  Reload from cache == 0.024s

    tts={}
    meta={}
    meta['used_cache']=False

    start_time=time.time()
    
    ## TRY CACHE LOAD
    tts,load_meta=load_transactions_from_cache(case_id,kind=kind)
    meta.update(load_meta) #'age'
    
    if not tts:
        
        ############################################################
        ## GET BASE
        tts=FIXED_get_all_transactions(case_id=case_id)
        ## ADD MARKUPS
        tts=add_transaction_fields(tts)
        ############################################################
        
        ## CACHE
        #- see mem for smart query cache
        add_transactions_to_cache(case_id,tts,kind='')

    else:
        meta['used_cache']=True
    
    meta['count']=len(tts)
    meta['run_time']=time.time()-start_time

    logging.info("interface_preload_cache_transactions: "+str(meta))

    return tts,meta


def call_preload_cache_transactions():
    ## Preload all transactions, add fields, cache, ready
     
    start_time=time.time()
    case_id='65a8168eb3ac164610ea5bc2' ## Big new age
    
    interface_preload_cache_transactions(case_id)

    return

def auto_join_transaction_meta(case_id,given_tts,kind='standard',filter_keep=[]):
    ##
    #- given some partial transactions, extend data using fixed extended transaction query
    #[ ] tbd: inner filter if want clean output

    assume_given_tts_kind='list'

    if assume_given_tts_kind=='list' and not isinstance(given_tts,list):
        raise Exception("auto_join_transaction_meta: given_tts must be list")
    elif assume_given_tts_kind=='dict' and not isinstance(given_tts,dict):
        raise Exception("auto_join_transaction_meta: given_tts must be dict")

    tts={}

    # **given_tts may require field mapping ie: Transaction_Latitude -> Latitude
    assume_transaction_id='id'
    
    ## Load at case_id
    tts_extended,meta=interface_preload_cache_transactions(case_id,kind=kind)
    
    if False:
        print ("> loaded: "+str(meta))
        for id in tts_extended:
            print ("AT ID: "+str(id))
            print ("LOADED: "+str(tts_extended[id]))
            break
    
    ## Join at id
    if assume_given_tts_kind=='list':
        for tt in given_tts:
            id=tt[assume_transaction_id]
            tte=tts_extended.get(id,{})
            if tte:
                for k in tte:
                    if filter_keep and not k in filter_keep: continue
                    if not k in tt: ## Update but don't overwrite
                        tt[k]=tte[k]
    elif assume_given_tts_kind=='dict':
        for id in given_tts:
            tt=given_tts[id]
            tte=tts_extended.get(id,{})
            if tte:
                for k in tte:
                    if filter_keep and not k in filter_keep: continue
                    if not k in tt: ## Update but don't overwrite
                        tt[k]=tte[k]
    else:
        raise Exception("auto_join_transaction_meta: given_tts kind not supported: "+str(assume_given_tts_kind))

    return given_tts


def call_auto_join_transaction_meta():
    ## Preload all transactions, add fields, cache, ready
     
    start_time=time.time()
    case_id='65a8168eb3ac164610ea5bc2' ## Big new age
    
    ## Build indexed at id
    given_tts={}
    dd={}
    dd['id']='ec7dc18580087519dbce4e665f11e405bc88919aa2ede1f137389979421ace5b'
    given_tts['ec7dc18580087519dbce4e665f11e405bc88919aa2ede1f137389979421ace5b']=dd

    ## Build as list
    given_tts=[]
    given_tts.append(dd)


    tts=auto_join_transaction_meta(case_id,given_tts,kind='standard',filter_keep=['hyperlink_url'])

    print ("EXTENDED: "+str(tts))
    
    print (">> break apart for general use.  add 'kind' so can do multiple kinds of joins")

    return



if __name__=='__main__':

    branches=['dev1']
    branches=['dev2']
    branches=['call_preload_cache_transactions']
    branches=['call_auto_join_transaction_meta']


    for b in branches:
        globals()[b]()
    










