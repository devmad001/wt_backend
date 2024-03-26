import os
import sys
import codecs
import copy
import json
import re
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

from get_logger import setup_logging
logging=setup_logging()

from schemas.SCHEMA_kbai import gold_schema_definition

from common_markup_helpers import get_target_records
from cleaner_algs import alg_is_valid_account_number

#0v1# JC  Oct 18, 2023  Init


"""
    SIMILAR TO Applying logic
    - apply to existing KB (on already processed record)
    - see do_llm_markup for sample fow (esp on version tracking) 
    
    - see markup_alg_cypher
    - this routine can work on entire grpah OR a case_id
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
    """
    
    ## Map back to va
    # touch givens
    vars['markup_goals']=vars['markup_goals'] #ie/ alg to run
    

    ### LOOKUP CYPHER BRANCH
    #- recall, set during mapping (call_kbai.py -> map_question_need_to_alg_offer))
    
    if 'add_processed_by_nodes' in vars['markup_goals']:
        ## DO direct manipulation or via pass back records?
        #- recall versioning maybe include it here
        dev_local_processed_by(vars['case_id'])
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

def do_processed_by(trecord,case_id):
    ## Map to official method from schema!!
    meta={}
    meta['log_processors']=[]
    
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
        ## Catch for now cause encoding??
        try: place,meta=alg_resolve_address(trecord['transaction_method_id'])
        except:
            place={}

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
        print ("nod: "+str(create_cypher))
        for rr in Neo.run_stmt(create_cypher,verbose=True):
            pass
            ## May be session var
            #try: print ("[cypher] Processor create result: "+str(rr.data()))
            #except:pass
            
        ## Insert 1 relation ** ensure processor is id dict only
        create_rel=cypher_create_relationship('Transaction','Processor','PROCESSED_BY',{'id':trecord['id']},{'id':processor['id']})
        created=False
        for rr in Neo.run_stmt(create_rel,verbose=True):
            try:
                the_data=rr.data()
                print ("[cypher] Processor create rel result1: "+str(the_data))
                if the_data:
                    created=True
            except:pass
        if not created:
            raise Exception("Failed to create Processor node and rel: "+str(processor))

    return meta

def resolve_processor_id(id,case_id):
    # Recall id can be unknown as its' source from transaction_method_id
    #- include 'p' prefix for processed by!
    iid=case_id+'-'+'p'+'-'+str(id)
    return iid

def dev_local_processed_by(case_id):
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
        do_processed_by(transaction['t'],case_id)

    
    return


def dev_interface_do_processed_by(transaction,case_id):
    print ("Does processed by and updates KB!!")
    meta=do_processed_by(transaction,case_id)
    # 'log_processors[]
    return meta

def dev_local_cypher_markup_processed_by():
    case_id='demo_a'
    case_id='case_o3_case_single'
    case_id='case_atm_location'
    #get_target_records(case_id)
    dev_local_processed_by(case_id)

    return

def CLEAN_remove_single_node(id='',label='',):
    oops=watchhh_add_validation_on_one_entity
    if not id and label:
        raise Exception("Need id or label")
    stmt = f"MATCH (n:{label} {{id: '{id}'}}) DELETE n"
#    stmt = f"MATCH (n:{label} {{id: '{id}'}}) REMOVE n.account_number"
    logging.info("[remove node]: "+str(stmt))
    for rr in Neo.run_stmt(stmt,verbose=True):
        pass
        #print (">> "+str(rr))
    return

def CLEAN_remove_single_node_property(id='',label='',property=''):
    if not (id and label and property):
        raise Exception("Need id and property")

#    stmt = f"MATCH (n:{label} {{id: '{id}'}}) DELETE n"
    
    ## Validate only applies to 1 node
    stmt = f"MATCH (n:Entity {{id: '{id}'}}) RETURN count(n) as count"
    jsonl,df,tx,meta=Neo.run_stmt_to_normalized(stmt)
    the_count=jsonl[0]['count']
    
    if the_count>1:
        raise Exception("More than 1 node found: "+str(the_count)+" for: "+str(stmt))

    stmt = f"MATCH (n:{label} {{id: '{id}'}}) REMOVE n.{property}"
    logging.info("[remove property]: "+str(stmt))
    for rr in Neo.run_stmt(stmt,verbose=True):
        try: the_data=rr.data()
        except: the_data=[]
        
        if the_data:
            raise Exception("Failed to remove property: "+str(the_data)+" at: "+str(stmt))
    return

def CLEAN_ALGS(commit=False, case_id='',force_all_cases=False):
    ## Try to group into query types
    
    #[1]# Account numbers
    
    if force_all_cases:
        stmt="""
        MATCH (Entity:Entity)
        RETURN Entity.id AS id, Entity.account_number AS Account_Number   
        """
    else:
        stmt="""
        MATCH (Entity:Entity {case_id: 'Marner'})
        RETURN Entity.id AS id, Entity.account_number AS Account_Number   
        """
    jsonl,df,tx,meta=Neo.run_stmt_to_normalized(stmt)
    c=0
    for rr in jsonl:
        c+=1
        rrate=str(c/len(jsonl)*100)+"%"
        if not c%10: logging.info("Progress: "+str(rrate))
        #print ("> "+str(rr))
        
        #[1] Account numbers
        #[ ] performance:  remove all where None or len=20!!
        if not alg_is_valid_account_number(rr['Account_Number']):
            print ("[ ] invalid account number: "+str(rr['Account_Number']))
            #cypher_update_account_number(rr['Account_Number'])
            if commit:
                #watch# CLEAN_remove_single_node(id=rr['id'],label='Entity')
                CLEAN_remove_single_node_property(id=rr['id'],label='Entity',property='account_number')

    return


#def ENTER_clean_unit(tt):
#    ## OR at cypher level
#    
#    #[1]#  Chase barcodes are not account numbers
#    #(i) if account_number looks like:  '11756070502000000065'
#    #     - false
#    #(ii) remove where Entity.account_number is length x
#
#    return
#
#def ENTER_clean_case():
#    case_id='Marner'
#    
#    ## CLEAN AT TRANSACTION LIST:
#    trecords=get_target_records(case_id)
#    for trecord in trecords:
#        ENTER_clean_unit(trecord['t'])
#        
#    ## Special queries
#    return
#
#def ENTER_clean_whole_kb():
#    return


### NOTES:
#- follow _PROCESSED_BY.py layout.

def run_local_query():
    stmt="""
    MATCH (Entity:Entity {case_id: 'Marner'})
    RETURN Entity.account_number AS Account_Number   
    """

    jsonl,df,tx,meta=Neo.run_stmt_to_normalized(stmt)
    
    for rr in jsonl:
        print ("> "+str(rr))

    return

def dev1():
    print ("CLEAN!")
    case_id='Marner'
    force_all_cases=True
    commit=True
    CLEAN_ALGS(commit=commit,case_id=case_id,force_all_cases=force_all_cases)

    return

if __name__=='__main__':
    branches=['ENTER_clean_whole_kb']
    branches=['run_local_query']
    branches=['ENTER_clean_case']
    branches=['dev1']

    for b in branches:
        globals()[b]()

    print ("")
    print ("[ ] checklist:  changes should be reflected in expected schema")
    print ("[ ] checklist:  changes should have tests + clear metrics")






