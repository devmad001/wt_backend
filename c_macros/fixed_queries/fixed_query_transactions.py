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

from fixed_helper import local_query2jsonl
from fixed_helper import load_response_from_cache
from fixed_helper import add_response_to_cache

        
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


def FIXED_get_all_cases_transactions(limit=0):
    #; limit makes sense if just want a sample of some transactions
    
    # where case_id=case_id
    stmt="""
    MATCH (t:Transaction)
    RETURN t
    """
    if limit:
        stmt+="\nLIMIT "+str(limit)
        
    jsonl=local_query2jsonl(stmt)
    
    tts={}
    ## Re-index at transaction id
    for j in jsonl:
        id=j['t']['id']
        tts[id]=j['t']
    return tts,{}

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
    ## Add computable fields to transactions

    for id in tts:
        tt=tts[id]
        
        ### VARIOUS
        
        ## Hyperlink
        tt['hyperlink_url']=alg_generate_transaction_hyperlink(tt)

        ## Node image (check):
        #node_image=''

        tts[id]=tt

    return tts



def interface_preload_cache_transactions(case_id,kind='',expires=24*60*60):
    ## Cache
    # - expires every day ( only 1.5s to refresh )
    # PERFORMANCE
    # [A]  Initial query, markup, store ==  1.5s (at 2.5k transactions)
    #    - 2.5k tts 1.0s, +(hyperlinks & storage) +0.35 = 1.5s total
    # [B]  Reload from cache == 0.024s

    tts={}
    meta={}
    meta['used_cache']=False

    start_time=time.time()
    
    ## TRY CACHE LOAD
    tts,load_meta=load_response_from_cache(case_id,kind=kind,expires=expires)
    meta.update(load_meta) #'age'
    
    if not tts:
        logging.info("[info] doing initial query for transactions: "+str(case_id)+" cache meta: "+str(load_meta))
        
        ############################################################
        ## GET BASE
        tts=FIXED_get_all_transactions(case_id=case_id)
        ## ADD MARKUPS
        tts=add_transaction_fields(tts)
        ############################################################
        
        ## CACHE
        #- see mem for smart query cache
        add_response_to_cache(case_id,tts,kind=kind)

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
    
    tts,meta=interface_preload_cache_transactions(case_id)

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

    return



def dev_dump_transactions():
    
    if 'one case' in []:
        tts,meta=interface_preload_cache_transactions('65a8168eb3ac164610ea5bc2')

    tts,meta=FIXED_get_all_cases_transactions()

    filename='sample_all_debit_descriptions.txt'
    fp=codecs.open(filename,"w",encoding='utf-8',errors='ignore')
    seen={}
    for id in tts:
        tt=tts[id]
        if tt['transaction_description'] in seen: continue
        seen[tt['transaction_description']]=True
        if not 'is_credit' in tt: continue
        if not tt['is_credit']:
            try: fp.write(str(tt['transaction_description'])+"\n")
            except:
                print ("[debug] skip 1")

    fp.close()
    print ("Wrote to: "+str(filename))
        
    return

def dev_account_flows():
    #*** USE FOR DUMPING INFO for classification of transactions
    #> migrate from macro_queries.py
    
    # cypher_query_account_flows
    ## Return  SENDER (DEBIT_FROM) -> Transaction - (CREDIT_TO) RECEIVER
    # Entity == SENDER/RECEIVER or loosely account

    case_id='65a8168eb3ac164610ea5bc2' ## Big new age

    stmt = f"""
MATCH (DebitEntity:Entity)-[:DEBIT_FROM]->(Transaction:Transaction)-[:CREDIT_TO]->(CreditEntity:Entity)
WHERE
    Transaction.case_id = '{case_id}'
RETURN
    Transaction,DebitEntity,CreditEntity
ORDER BY Transaction.transaction_date
    """
    data_response,df,tx,meta=Neo.run_stmt_to_normalized(stmt,tx='')

    liner=[]
    entries=[]
    for record in data_response:
#D        print ("TR: "+str(record['Transaction']))
        name_debit=record['DebitEntity']['name']
        name_credit=record['CreditEntity']['name']
        amount=abs(record['Transaction']['transaction_amount'])
        description=record['Transaction']['transaction_description']
        
        if name_credit in ['main_account']: continue
        if not 'is_credit' in record['Transaction']: continue
        if not record['Transaction']['is_credit']:
            text_line=f"{name_credit}\t{description}"
#            print ("> "+str(text_line))

        entries+=[(name_debit,name_credit,amount,description)]
        liner=[name_debit]
        liner+=[name_credit]
        liner+=[description]

        # Append as strings
        ss=liner
        print ("\t".join(ss)+"")
        entries+=["\t".join(liner)]
        

#    for entry in entries:
#        print (str(entry))

    return stmt



    return

if __name__=='__main__':

    branches=['dev1']
    branches=['dev2']
    branches=['call_preload_cache_transactions']
    branches=['call_auto_join_transaction_meta']

    branches=['dev_dump_transactions']
    branches=['dev_account_flows']


    for b in branches:
        globals()[b]()
    










