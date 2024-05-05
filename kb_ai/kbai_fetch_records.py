import os
import sys
import codecs
import json
import copy
import re

import configparser as ConfigParser

from fastapi import FastAPI

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")

from a_query.queryset1 import query_transaction
from markup_llm import do_llm_markup
#from markup_alg_logic import do_markup_alg_logic
from class_live_records import Live_Records

from kb_query import query_get_all_case_nodes
from alg_doc_meta import alg_source_doc_meta

from get_logger import setup_logging
logging=setup_logging()

Config = ConfigParser.ConfigParser()
Config.read(LOCAL_PATH+"../w_settings.ini")
BASE_STORAGE_DIR=Config.get('files','base_storage_rel_dir')
BASE_STORAGE_DIR=LOCAL_PATH+"../"+BASE_STORAGE_DIR


#0v3# JC  Sep 26, 2023  Fetch for record processing batch size
#0v2# JC  Sep 19, 2023  Generalize puller
#0v1# JC  Sep 17, 2023  Init


"""
    KB_records
    - [ ] migrate away from Transaction only
    - question poised and these raw data records returned

"""

def alg_is_record_uptodate(record,fields_to_update=[],markup_version='default_always'):
    #**field specific:  kb_update_type --> field_update
    # Date or latest?
    # Assume active markup_version is LATEST!
    # is_uptodate IF active markup_version equals field markup version

    is_uptodate=False

    #    'versions_metadata': '{"transaction_method": "llm_markup", "transaction_type": "llm_markup"}',

    ## 
    fields_to_check=copy.deepcopy(fields_to_update)

    ## Check stored version
    versions=record.get('versions_metadata',{})
    if versions:
        versions=json.loads(versions)
    else:
        versions={}

    for field in versions:
        stored_markup_version=versions[field]

        if field in fields_to_check:
            if stored_markup_version==markup_version:
                fields_to_check.remove(field)  #Good so pop

    if not fields_to_check:
        is_uptodate=True
#D        logging.info("[is_uptodate]!")
    else:
        is_uptodate=False
#D        logging.info("NOT [is_uptodate]: "+str(versions)+" vs: "+str(markup_version))

    return is_uptodate


def fetch_KB_records_for_update(case_id='case_3',thread_count=0,record_batch_size=0,schema={},force_update_all=False,markup_version='default',verbose=True):

    logging.info ("="*60)
    logging.info ("SCHEMA KIND: "+str(schema['kind'])) # transaction_type_method_goals
    logging.info ("="*60)

    ## GOAL IS TO APPLY TARGET SCHEME TO KB RECORDS
    #- schema:  typically nodes,rels or fields to update
    #- query for raw records
    #- if 'field level' and not alg applied (or no field) then candidate
    
    ### See dynamic group selection!
        #dd['record_batch_MIN_size']=15 #hard coded to match DEFAULT_LLM_GROUP_SIZE
    """
        #### DYNAMICALLY SETTING RECORD PROCESSING BATCHES BASED ON THREAD_COUNT
        record_groups: A batch of 60/record_batch_size to be processed by a single thread
                       - each record_group is then processed in chunks of DEFAULT_LLM_GROUP_SIZE/15
        Ideally,
        - given 200 transactions. 10 threads.
        - target record_batch_sizes=200/10=20
        - each thread then processes 20 records in chunks of 15 at a time
           ^ Ideally the target record batch size is multiple of DEFAULT_LLM_GROUP_SIZE
    """
    
    
    
    meta_doc={}
    records_groups=[]


    ###################################
    ### INPUTS FROM SCHEMA
    node_label=schema.get('source_node_label','')         #[ ] check against GRAPH_SCHEMA (Transaction?)
    kb_update_type=schema['kb_update_type'] #field_update
    fields_to_update=schema['fields_to_update'] #['transaction_type','transaction_method']
    only_use_these_fields=schema.get('only_use_these_fields',[]) #['transaction_description','section']

    ## Sub-type: schema.alg_name, ie/ attached to Transaction.algList once run (so don't grab to run again)
    alg_name=schema.get('alg_name','')

    if not kb_update_type in ['field_update','node_create']:
        print ("[ ] update downstream ie/ aig_is_record_uptodate")
        raise Exception("ERROR: kb_update_type not supported: "+str(kb_update_type))

    if not node_label in ['Transaction']:
        #[ ] see below
        raise Exception("ERROR: node_label not supported: "+str(node_label))

    ###################################
    ### CANDIDATE RECORDS FETCH
    records=query_get_all_case_nodes(case_id=case_id,label=node_label)
    
    print ("SAMPLE RE: "+str(records[0]))
    """
    SAMPLE JAN 24:
     {'transaction_date': '2021-09-24', 'filename_page_num': 194, 'is_credit': False, 'account_number': '3340 4918 5630', 'transaction_amount': 0.55, 'section': 'Withdrawals and other debits', 'label': 'Transaction', 'statement_id': '65a8168eb3ac164610ea5bc2-2021-09-01-3340 4918 5630-72d85b81-c416-4ffd-950c-f0c1fd62f251.pdf', 'transaction_description': 'AMERICAN EXPRESS DES:AXP DISCNT ID:0000019109 INDN:PLANET SMOOT5104512413 CO ID:1134992250 CCD', 'account_id': '65a8168eb3ac164610ea5bc2-3340 4918 5630', 'filename': '72d85b81-c416-4ffd-950c-f0c1fd62f251.pdf', 'amount_sign': '-', 'case_id': 'test_default_65a8168eb3ac164610ea5bc2_194', 'id': 'test_default_65a8168eb3ac164610ea5bc2_194-d4aeec2cc09ed62a4420e3f929fdda8ff43b904a48456eb4321106d96552506c'}
    """

    ###################################
    ### FILTER RECORDS
    #- by value or internal logic 
    #- if values exist with latest alg, then skip

    full_records_list=[]
    for record in records:
        keep_it=True
        if verbose:
            pass
            #D# print ("[fetch TK RECORD candidate]: "+str(record)) #Beware print


## DEV
#        if not 'transaction_amount' in record: keep_it=False
#        if not 'deposit' in record.get('transaction_description','').lower() or not 'addition' in record.get('transaction_description','').lower():
#            keep_it=False
#        if 'withdraw' in record.get('transaction_description','').lower():
#            keep_it=False

        if not force_update_all:
            ## [1] if alg already applied (markup_version check) then skip data processing
            if 'field_update' in kb_update_type:
                is_uptodate=alg_is_record_uptodate(record,fields_to_update=fields_to_update,markup_version=markup_version)
                if is_uptodate:
                    keep_it=False
                    if verbose:
                        logging.info("[record field already up-to-date] so skip for now")

        if 'create_node' in kb_update_type:
            keep_it=True #Process Node for creation eitherway

        ##[ ] FILTER if alg_name exists in Transaction.algList
        if not force_update_all:
            if alg_name and 'algList' in record:
                if alg_name in record['algList']:
                    keep_it=False
                    logging.info("[ ] skipping doing alg on fetch_records Transaction record has alg_name: "+str(alg_name))

        ##[2] if no description then skip (assumes Transaction see above)
        if not record.get('transaction_description',''):
            keep_it=False

        if keep_it:
            full_records_list+=[record]
    logging.info("[custom keep record count]: "+str(len(full_records_list))+" of candidates: "+str(len(records)))
    if not len(records):
        logging.info("[WARNING] no records at case_id: "+str(case_id))

    ###################################
    ## RECORDS CLASS
    #
    exclude_fields=[] #['filename_page_num','filename','statement_id','case_id','idd']
    only_use_these_fields=only_use_these_fields #['transaction_description','section']

    ###################################
    ## BATCH INTO RECORD CLASSES!
    #
    crecords=len(full_records_list)
    if not crecords:
        pass
    elif thread_count:
        ## SPECIAL BATCHING
        MIN_BATCH_SIZE=15  #Hardcode assume same as 'DEFAULT_LLM_GROUP_SIZE'

        count_evenly=int(crecords/thread_count)
        if count_evenly<MIN_BATCH_SIZE:
            count_evenly=MIN_BATCH_SIZE
        logging.info("[threaded batch size]: "+str(count_evenly)+" batch size across: "+str(thread_count)+" threads for total records: "+str(crecords))

        # Batch at size
        for i in range(0,len(full_records_list),count_evenly):
            Records=Live_Records()
            Records.set_records(full_records_list[i:i+record_batch_size],only_use_these_fields=only_use_these_fields,exclude_fields=exclude_fields)
            Records.set_record_type(node_label)
            records_groups+=[Records]

    elif not record_batch_size:
        Records=Live_Records()
        Records.set_records(full_records_list,only_use_these_fields=only_use_these_fields,exclude_fields=exclude_fields)
    
        Records.set_record_type(node_label) # graph_schema approved 
        records_groups=[Records]
    else:
        # Batch at size
        for i in range(0,len(full_records_list),record_batch_size):
            Records=Live_Records()
            Records.set_records(full_records_list[i:i+record_batch_size],only_use_these_fields=only_use_these_fields,exclude_fields=exclude_fields)
            Records.set_record_type(node_label)
            records_groups+=[Records]

    return records_groups


def fetch_KB_meta(case_id,schema,Records):
    ## *best way to streamline??
    ## DOCUMENT LEVEL meta_doc?
    #- recall, sometimes need raw pdf page if page_text corrupt or odd
    #- meta_doc: #snotes+=['document_meta_doc'+ " "+str(meta_doc.get("document_meta_doc",{}))] # is_BOA?

    meta_doc={}

    if not Records.record_type=='Transaction':
        raise Exception("ERROR: Records.record_type must be Transaction")

    ### LOAD FILENAME INFO FOR PROCESSING DOC
    sample_record=Records.sample_record() #Assumes these are transactions!
    if not sample_record:
        logging.info("[warning] no records (or sample records)")
        return meta_doc

    #print ("[debug] sample record: "+str(sample_record))

    if not 'idd' in sample_record:
        raise Exception("ERROR: sample_record must have idd: "+str(sample_record))

    sample_transaction_id=sample_record['idd'] #Recall remapped!

    #sample_transaction_id=Records.sample_record()['id'] #Assumes these are transactions!

    transaction=query_transaction(transaction_id=sample_transaction_id)

    ## CHECK GIVENS
    if not transaction:
        raise Exception("ERROR: transaction not found: "+str(sample_transaction_id))

    if not 'filename' in transaction:
        raise Exception("ERROR: transaction must have filename: "+str(transaction))
    else:
        filename=transaction['filename']


    full_filename=BASE_STORAGE_DIR+'/'+case_id+"/"+transaction['filename']
    if not os.path.exists(full_filename):
        logging.info("[warning] full_filename not found (possibly test case or not local): "+str(full_filename))

    meta_doc={}
    #doc_mta['page_metas']
    meta_doc=alg_source_doc_meta(transaction_id=sample_transaction_id,full_filename=full_filename,case_id=case_id)

#D2 FULL DOCUMENT#    print ("- DOC META: "+str(json.dumps(meta_doc,indent=4)))

    #meta_doc['page_metas']['1']['extracted'][method][pages]

    ## PAGE TEXT
    #page_text='' #Depends on transaction used but preloaded in meta_doc

    return meta_doc

def ORG_fetch_KB_records_for_update(case_id='case_3'):
    ## TEST DATA
    #- include real-time doc_meta
    from kbai_pipeline import HARDCODE_get_records

    meta_doc={}
    records=HARDCODE_get_records(case_id=case_id)
    all_transactions=records.get("all_transactions",[])

    ## Pre-filter raw records
    custom_keep=[]
    for record in all_transactions:
#        keep_it=True
#        if not 'transaction_amount' in record: keep_it=False
#
#        if not 'deposit' in record.get('transaction_description','').lower() or not 'addition' in record.get('transaction_description','').lower():
#            keep_it=False
#
        if record.get('transaction_description',''):
            keep_it=True
        else:
            keep_it=False

        if 'withdraw' in record.get('transaction_description','').lower():
            keep_it=False

        if keep_it:
            custom_keep+=[record]

    ## Records
    exclude_fields=['filename_page_num','filename','statement_id','case_id','idd']
    only_use_these_fields=['transaction_description','section']
    Records=Live_Records()
    Records.set_records(custom_keep,only_use_these_fields=only_use_these_fields,exclude_fields=exclude_fields)

    Records.set_record_type('Transaction') #schema approved 

    from alg_doc_meta import alg_source_doc_meta
    ## DOCUMENT LEVEL meta_doc?
    #- recall, sometimes need raw pdf page if page_text corrupt or odd
    #- meta_doc: #snotes+=['document_meta_doc'+ " "+str(meta_doc.get("document_meta_doc",{}))] # is_BOA?

    ## Per transaction or per document?
    sample_transaction_id=custom_keep[0]['id']
    transaction=query_transaction(transaction_id=sample_transaction_id)

    ASSUME_BASE_DIR=LOCAL_PATH+'../../Watchtower Solutions AI/Bank Statements - for Beta Testing'
    full_filename=ASSUME_BASE_DIR+'/'+transaction['filename']
    full_filename=re.sub(r'\\','/',full_filename)


    doc_meta={}
    #doc_mta['page_metas']
    doc_meta=alg_source_doc_meta(transaction_id=sample_transaction_id,full_filename=full_filename,case_id=case_id)

#D2 FULL DOCUMENT#    print ("- DOC META: "+str(json.dumps(doc_meta,indent=4)))

    #doc_meta['page_metas']['1']['extracted'][method][pages]

    ## PAGE TEXT
    page_text='' #Depends on transaction used but preloaded in meta_doc

    return Records,page_text,meta_doc

if __name__=='__main__':
    branches=['dev1']
    for b in branches:
        globals()[b]()





"""
"""
