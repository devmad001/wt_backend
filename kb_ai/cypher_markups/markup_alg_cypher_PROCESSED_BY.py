import os
import sys
import codecs
import copy
import json
import re
import time
import threading  #future multi

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")
sys.path.insert(0,LOCAL_PATH+"../../")

from w_utils import util_get_modified_keys
from w_storage.gstorage.gneo4j import Neo

from a_query.cypher_helper import cypher_create_update_node
from a_query.cypher_helper import cypher_create_relationship
from a_algs.geo_algs.alg_resolve_address import alg_resolve_address

from common_markup_helpers import get_target_records

from get_logger import setup_logging
logging=setup_logging()

from schemas.SCHEMA_kbai import gold_schema_definition


#0v2# JC  Oct 18, 2023  Extend to cleaner
#0v1# JC  Oct  7, 2023  Init

"""
    CODE NODE AND RELATIONSHIP FOR 'PROCESSED BY'
    - self-contained (logic + cypher update here)
    
    - Project transaction_method kind to Entity that transaction -- PROCESSED_BY --> E

"""


def do_cypher_markup(*args,**vars):
    ### RECALL:
    #** follow do_logic_markup flow
    
    ## GIVEN RECALL:
    # markup_goals == which alg here to run
    # Records      == bite sized list of dumped records from KB to markup!
    # schema       == essentially a bunch of parameters
    #                 ^^^*** separate logical tweaks from this routine!
    #                     ^^^ ie/ schema regex examples to apply when
    #                             looking for check number. default here tweaks there.
    # meta_doc     == other meta not available in raw transaction "Records"
    
    ## Recall, cypher update & field versions are handled external call_kbai.py
    #- version tracking  (like do_llm_markup) #- cypher update     (like do_llm_markup)
    meta={}
    finished_records=[]
    unfinished_records=[]
    
    """
        dd={}
        dd['case_id']=ptr['case_id']
        dd['schema']=ptr['schema']
        dd['Records']=Records
        dd['markup_goals']=ptr['markup_goals']
        dd['meta_doc']=meta_doc
        dd['DEFAULT_LLM_GROUP_SIZE']=options['DEFAULT_LLM_GROUP_SIZE']  #10 a big 
        dd['markup_version'] ** cause doing update to db
        dd['commit'] ** cause doing update to db
    """
    
    ## Map back to va
    # touch givens
    vars['markup_goals']=vars['markup_goals'] #ie/ alg to run
    

    ### LOOKUP CYPHER BRANCH
    #- recall, set during mapping (call_kbai.py -> map_question_need_to_alg_offer))
    
    if 'add_processed_by_nodes' in vars['markup_goals']:
        dev_local_processed_by(vars['case_id'],commit=vars.get('commit',True))

        ## DO direct manipulation or via pass back records?
        #- recall versioning maybe include it here
        #cypher_meta=CYPHER_add_PROCESSED_BY(**vars)
        #meta.update(cypher_meta) #<-- count_records_changed

    elif 'CYPHER_add_PROCESSED_BY' in vars['markup_goals']:
        raise Exception("Unknown markup_goals: %s" % vars['markup_goals'])
#        ## DO direct manipulation or via pass back records?
#        #- recall versioning maybe include it here
#        cypher_meta=CYPHER_add_PROCESSED_BY(**vars)
#        meta.update(cypher_meta) #<-- count_records_changed

    else:
        raise Exception("Unknown markup_goals: %s" % vars['markup_goals'])

    logging.info("[finished cypher markup] count changed/matched: "+str(meta.get('count_records_changed','')))

    return finished_records,unfinished_records,meta

def local_map_transaction_methods(transaction_method,examples):
    #Unknown samples:  unknown, direct_deposit, ach_debit, ach, cash_concentration_transfer
    #Gold: METHODS=['atm', 'wire_transfer', 'check', 'cash', 'book_transfer','fed_wire', 'debit_card', 'credit_card', 'online_payment', 'mobile_payment', 'zelle', 'venmo','other']
    new='other'
    if 'ach' in transaction_method.lower():
        new='online_payment'
    elif 'unknown' in transaction_method.lower():
        new='other'
    elif 'direct_deposit' in transaction_method.lower():
        new='online_payment'
    elif 'cash_concentration_transfer' in transaction_method.lower():
        new='wire_transfer'
    else:
        new='other'
        
    new=new.lower()
    return new

def hard_code_transaction_method(trecord):
    ## Quick adjustments should be easy to catchall

    ## Fargo Zell type
    if re.search(r'Zel\*',trecord['transaction_description']):
        trecord['transaction_method']='zelle'
    return trecord

def do_processed_by(trecord,case_id,commit=True):
    ## Map to official method from schema!!
    meta={}
    meta['log_processors']=[]
    meta['commit']=commit
    
    ## Hard code some
    trecord=hard_code_transaction_method(trecord)

    if not trecord.get('transaction_method',''):
        logging.info("[warning] no transaction_method: "+str(trecord))
        return 

    trecord['transaction_method']=trecord['transaction_method'].lower()

    transaction_method=trecord['transaction_method']
    
    if not transaction_method in gold_schema_definition['nodes']['Processor']['examples']['type']:
        auto_type=local_map_transaction_methods(transaction_method,gold_schema_definition['nodes']['Processor']['examples']['type'])
        logging.dev('[unknown transaction method]: '+str(transaction_method)+" MAPPED TO: "+str(auto_type))
        trecord['transaction_method']=auto_type
        transaction_method=auto_type

    
    ## Processor node
    processor={}
    processor['case_id']=case_id
    processor['id']=None
    processor['name']=''
    processor['location']=None
    
    ### AUTO RESOLVE ADDRESS
    #[ ] optionally look through transaction_description (not specific to method id)
    #place,meta=alg_resolve_address(trecord['transaction_description'])
    place_blob=trecord.get('transaction_method_id','')
    if place_blob:
        # try-except cause encoding??
        try: place,meta=alg_resolve_address(trecord['transaction_method_id'])
        except: place={}
        if place and place.get('relevance',0.0)>0.50:
            processor['lat']=place['lat']
            processor['lng']=place['lng']
            processor['location']=place['label']
        else:
            ## Try via transaction description
            try: place,meta=alg_resolve_address(trecord['transaction_description'])
            except: place={}
            if place and place.get('relevance',0.0)>0.50:
                processor['lat']=place['lat']
                processor['lng']=place['lng']
                processor['location']=place['label']

    ##########################################
    ## Get transaction_method
    ### Special cases
    #? credit_card is a method but credit_card_account is an Entity
    ## Cash is a method PROCESSED_BY PhysicalCash
    #- It's also a special kind of untraceable Account aka Entity
    if re.search(r'cash',transaction_method,flags=re.I):
        processor['type']='cash'
        processor['id']=trecord.get('transaction_method_id','unknown')
    elif re.search(r'zelle',transaction_method,flags=re.I):
        processor['type']='zelle'
        processor['id']=trecord.get('transaction_method_id','unknown')
    elif re.search(r'check',transaction_method,flags=re.I):
        processor['type']='check'
        processor['id']=trecord.get('transaction_method_id','unknown')
    elif transaction_method in ['unknown','na',None,'']:
        processor={}
    else:
        processor['type']=transaction_method
        processor['id']=trecord.get('transaction_method_id','unknown')
        
    ## Set or refine name
    processor['name']=processor.get('id','')
    
    ## Pull in extra location info from trecord
    #Integrated Call Center Solutions, Florham Park NJ, 07932- US'}) ON
        
    if processor.get('id','') and processor.get('type',''):
        ## Create Entity
        ## Link with PROCESSED_BY relation
        processor['id']=resolve_processor_id(processor['id'],case_id)
        
        ## Create Rel
        PROCESSED_BY={}
        PROCESSED_BY['method']=processor['type']
        PROCESSED_BY['date']=trecord['transaction_date']
        PROCESSED_BY['amount']=trecord['transaction_amount']  #YES again

        PROCESSED_BY['from_id']=trecord['id']
        PROCESSED_BY['to_id']=processor['id']
        
        ## Insert 1 node  (Processor )
        meta['log_processors']=[processor]

        create_cypher=cypher_create_update_node('Processor',processor)

        logging.info("nod processed by: "+str(create_cypher)) #'charmap' codec can't encode characters in position 209-210: character maps to <undefined>

        if commit:
            start_time=time.time()
            for rr in Neo.run_stmt(create_cypher,verbose=True):
                pass
                ## May be session var
                #try: print ("[cypher] Processor create result: "+str(rr.data()))
                #except:pass
            logging.info ("[cypher] Processor create time: "+str(time.time()-start_time)+" for: "+str(create_cypher))
        else:
            logging.info("[test mode no cypher commit]")
            
        ## Insert 1 relation ** ensure processor is id dict only
        start_time=time.time()
        create_rel=cypher_create_relationship('Transaction','Processor','PROCESSED_BY',{'id':trecord['id']},{'id':processor['id']})
        
        if commit:
            created=False
            for rr in Neo.run_stmt(create_rel,verbose=True):
                try:
                    the_data=rr.data()
                    print ("[cypher] Processor create rel result1: "+str(the_data))
                    if the_data:
                        created=True
                except:pass
            logging.info ("[cypher] Processor create time: "+str(time.time()-start_time)+" for: "+str(create_rel))
    
            if not created:
                raise Exception("Failed to create Processor node and rel: "+str(processor))
        else:
            logging.info("[test mode no cypher commit]")

    return meta

def resolve_processor_id(id,case_id):
    # Recall id can be unknown as its' source from transaction_method_id
    #- include 'p' prefix for processed by!
    iid=case_id+'-'+'p'+'-'+str(id)
    return iid

def dev_local_processed_by(case_id,commit=True):
    ## Official
    #> PROCESSED_BY definition
    #- note:  check is a processed_by.  credit_card_acount is NOT, but maybe credit is.
    unofficial_methods=['book_transfer','cash','credit','debit','check','wire','ach','paypal','venmo','zelle','physical']
    unofficial_methods+=['fed_wire','debit_card','bank']
    
    methods=gold_schema_definition['nodes']['Processor']['examples']['type']
    
    undefined=['bank_used'] #<-- facilitates or just poc
    
    ##########################################
    ## Get transaction_method
    ## Create Entity of type/kind method
    ## Link with PROCESSED_BY relation

    logging.info("[info] getting Transactions to process...")
    trecords=get_target_records(case_id)
    logging.info("[info] count: "+str(len(trecords)))
    
    for transaction in trecords:
        ## PROCESS, CREATE, INSERT node + rel
        do_processed_by(transaction['t'],case_id,commit=commit)

    
    return


def dev_interface_do_processed_by(transaction,case_id,commit=True):
    logging.info ("Does processed by and updates KB!!")
    meta=do_processed_by(transaction,case_id,commit=commit)
    # 'log_processors[]
    return meta

def dev_local_cypher_markup_processed_by():
    case_id='demo_a'
    case_id='case_o3_case_single'
    case_id='case_atm_location'
    #get_target_records(case_id)
    dev_local_processed_by(case_id)

    return


if __name__=='__main__':
    branches=['do_markup_alg_logic']
    branches=['dev_local_cypher_markup_processed_by']
    for b in branches:
        globals()[b]()
