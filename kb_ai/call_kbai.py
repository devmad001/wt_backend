import os
import sys
import time
import codecs
import json
import copy
import re

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")

from a_query.queryset1 import query_transaction
from markup_llm import do_llm_markup
from logical_markups.markup_alg_logic import do_logic_markup
from cypher_markups.markup_alg_cypher_PROCESSED_BY import do_cypher_markup as do_cypher_markup_PROCESSED_BY
from cypher_markups.markup_alg_cypher_EASY_CREDIT_DEBIT import do_cypher_markup_EASY_DEBIT_CREDIT
from class_live_records import Live_Records

from schemas.schema_sender_receiver_entity import schema as schema_sender_receiver_entity
from schemas.schema_transaction_type_method import schema as schema_transaction_type_method

from kbai_fetch_records import fetch_KB_records_for_update
from kbai_fetch_records import fetch_KB_meta

from kb_update import dev_cypher_update
from multi import Multi_Wrap

from get_logger import setup_logging
logging=setup_logging()



#0v4# JC  Dec 16, 2023  Extra multi-threaded logging for any stuck threads
#0v3# JC  Sep 28, 2023  Update mapping for logic entry
#0v2# JC  Sep 25, 2023  Clean + setup for multi-processing
#0v1# JC  Sep 17, 2023  Init



"""
    MAIN ENTRYPOINT FOR RESOLVING KB AI QUERIES
    - KB update (llm markup)
    - combo of query + update  (stay user answer focused)
    !! watch tracking of:  has update already been applied  (algsList for node level & field versions!)
        ^ standalone check [  ]

"""

## MULTI-PROCESS POOL
Multi=None
THREAD_COUNT=12   # seems stable
THREAD_COUNT=14   # Dec 20, 2023  [ ] boosted 12-14 but need to validate outputs
                  # 224 transactions in groups of 100 suggests 3 groups or 3-4 threads
THREAD_COUNT=0    #
THREAD_COUNT=14   # Jan 2. frozen at boa 2/15

### ALLOW DEV BOX NO MULTI
#if os.name=='nt':
#    logging.info("========================== 1 THREAD MAIN EXE  ")
#    THREAD_COUNT=0

if THREAD_COUNT:
    Multi=Multi_Wrap(multi='thread',max_workers=THREAD_COUNT)
else:
    logging.warning("[warning] running in single thread mode!")


def dev_validate_given_schema(schema,markup_alg_branch=''):
    ## Move externally to schema validation routines?
    ## kb_update_type:: field_update, node_create  # see downstream fetch records

    for required_field in ['kind','kb_update_type']:
        if not required_field in schema:
            logging.info("[full schema debug]: "+str(schema))
            raise ValueError ("[ERROR] missing required field in schema: "+str(required_field))
            return False
        
    if not schema['kb_update_type'] in ['field_update','node_create']: #rel_create?
        raise ValueError ("[ERROR] unknown kb_update_type: "+str(schema['kb_update_type']))
        
    if schema['kb_update_type']=='field':
        if not 'fields_to_update' in schema:
            # **what fields expected to update
            raise ValueError ("[ERROR] missing required field in schema: "+str(required_field))
            return False
        
    if not 'only_use_these_fields' in schema and markup_alg_branch=='llm_markup':
        # **narrow down the fields required for input (really only llm requirement)
        raise ValueError ("[ERROR] missing required field in schema: "+str(required_field))
        return False
    
    if not 'source_node_label' in schema:
        # Transaction field update always for now on source
        raise ValueError ("[ERROR] missing required field in schema: "+str(required_field))

    return True

def call_cypher_push_updated_records(new_records,ptr):
    ## More stand-alone mapping (keeps main pipelien cleaner)
    
    dd={}
    dd['case_id']=ptr['case_id']
    dd['kb_update_type']=ptr['schema']['kb_update_type']
    dd['node_label']=ptr['schema']['source_node_label']
    dd['new_records']=new_records
    dd['fields_to_update']=ptr['new_field_names']
    dd['markup_version']=ptr['markup_version']
    dd['schema']=ptr['schema']
    dd['force_fields_to_update']=True  #True: default

    dev_cypher_update(**dd)

    return

def map_question_need_to_alg_offer(question,ptr):
    ## GIVEN:         question
    ## MAP TO ALG ==  markup_branch (LLM OR LOGIC), ALG_NAME, VERSION
    ## SCHEMA     ==  how to handle update (ie/ node, field, rel)
    
    ## TO SET:
    ptr['markup_alg_branch']=''    #LLM or LOGIC
    ptr['markup_goals']=[]  # Algs to apply
    markup_version_sub=''   #-v1  (for tracking if field has latest) (possibly update downstream at alg-level)
    
    ##################################
    ### LLM MARKUP OPTIONS
    if 'transaction_type_method' in question:
        ptr['markup_alg_branch']='llm_markup'
        ptr['given_query']='[instruction]  Add Transaction properties: transaction_type and transaction_method and transaction_method_id to the Transaction (graph) node.'
        ptr['markup_goals']=['transaction_type_method_goals']
        if not 'schema_transaction_type_method' in globals():
            raise Exception ("[ERROR] missing schema_transaction_type_method") #sample
        ptr['schema']=schema_transaction_type_method


    elif 'add_sender_receiver_nodes' in question:
        ptr['markup_alg_branch']='llm_markup'
        ptr['given_query']='[instruction]  Add entities for sender + receiver & link to transaction.'
        ptr['markup_goals']=['add_sender_receiver_nodes']
        ptr['schema']=schema_sender_receiver_entity
        # ^^ only use these fields!
        
    ##################################
    ### LOGIC MARKUP OPTIONS
    elif 'logical_card_check_numbers' in question:
        ptr['markup_alg_branch']='logic_markup'
        #aka alg name
        ptr['markup_goals']=['LOGIC_add_check_card_stuff']

        ptr['given_query']='[instruction]  Add check_num to transaction field, create node Entity for Check or Card type'

        ## LOCAL SCHEMA DEF
        #** recall, these will throw errors upon validation if missing required fields
        ptr['schema']={}
        ptr['schema']['kind']='tbd'
        ptr['schema']['source_node_label']='Transaction'
        ptr['schema']['kb_update_type']='field_update' #<-- tells to fetch records
        ptr['schema']['fields_to_update']=['check_num']  #Assumes Transaction!


    ##################################
    ### CYPHER GRAPH MARKUP OPTIONS
    elif 'add_PROCESSED_BY' in question:
        ptr['markup_alg_branch']='cypher_markup'
        ptr['given_query']='[instruction]  Add entities for PROCESSED_BY to transaction.'
        ptr['markup_goals']=['add_processed_by_nodes']
        ptr['schema']=schema_sender_receiver_entity

    elif 'easy_credit_debit_main' in question:
        ptr['markup_alg_branch']='cypher_markup'
        ptr['given_query']='[instruction]  Add credit_main=T/F to transaction (use Graph Entities etc)'
        ptr['markup_goals']=['easy_credit_debit_main_goal']
        
        #** schema enforced control of data fields
        ptr['schema']={}
        ptr['schema']['kind']='tbd'
        ptr['schema']['source_node_label']='Transaction'
        ptr['schema']['kb_update_type']='field_update' #<-- tells to fetch records
        ptr['schema']['fields_to_update']=['is_credit']

        pass
        #ptr['markup_alg_branch']='cypher_markup'
        ##aka alg name
        #ptr['markup_goals']+=['CYPHER_add_PROCESSED_BY']

#D1        #not needed#  ptr['markup_goals']=['CYPHER_add_keyword_chemical']
#D1        ptr['given_query']='[instruction]  Add keyword_chemical to transaction field'
#D1        ## LOCAL SCHEMA DEF
#D1        #** recall, these will throw errors upon validation if missing required fields
#D1        ptr['schema']={}
#D1        ptr['schema']['kind']='tbd'
#D1        ptr['schema']['source_node_label']='Transaction'
#D1        ptr['schema']['kb_update_type']='field_update' #<-- tells to fetch records
#D1        ptr['schema']['fields_to_update']=['has_keyword_chemical']  #Assumes Transaction!


    else:
        raise Exception ("[ERROR] unknown question: "+str(question))

    #### VALIDATION
    #** extra notes (ie/ frame around schema + question + goals)
    ##########################
    ## VALIDATE INPUT
    #- Validate input schema (since steers a lot of the logic)
    dev_validate_given_schema(ptr['schema'],markup_alg_branch=ptr['markup_alg_branch'])

    #### TBD [ ] TOUCH SYSTEM SCHEMAS
    gold_schema={}    #schemas.SCHEMA_kbai.py
    graph_schema={}   #[ ] see local_graph_schema
    ## Query current KB to decide if answer is possible
    print ("[call_kbai] <create cypher query> from given text query + knowing graph_schema")
    cypher_query={}
    print ("[choose to update KB]")
    kb_query_or_update='update'   #Chose

    ############################
    # TRACK VERSION
    ############################
    if len(ptr['markup_goals'])>1:
        raise Exception ("[ERROR] multiple markup_goals not supported yet: "+str(ptr['markup_goals']))

    ptr['markup_version']=ptr['markup_alg_branch']+"-"+ptr['markup_goals'][0]+"-"+markup_version_sub

    return ptr

def call_kb_auto_solver_flow(question,case_id, force_update_all=False,DEFAULT_LLM_GROUP_SIZE=12,commit=True,force_thread_count=0):
    logging.info("[call_kb_auto_solver_flow] start")

    ## GIVEN QUESTION, UPDATE KB
    #- question: Internal question ~ [transaction_type_method]
    #- assume KB query tried to answer already (gap/need exists, knowledge gap)
    #- Graph space (cypher) --> df space (Records) for controlled update
    #- "markup" via LLM or LOGIC
    
    ## LLM MARKUP OPTION TWEAKING
    #  DEFAULT_LLM_GROUP_SIZE=20;  how many records to ask for update on each LLM prompt  #10 a big small
    #                           ;  20 seems to miss some things ;  15 still a bit long + may miss so try 12 next

    response={}
    response['total_tokens_used']=0

    ##########################
    ## GIVENS
    ptr={}  # pointer + flow state memory
    ptr['case_id']=case_id

    ##########################
    ## MAP QUESTION TO ALG + SCHEMA
    ptr=map_question_need_to_alg_offer(question,ptr)
    #^^
    #:: markup_alg_branch "kind" (llm_markup or logic_markup)
    #:: markup_goals aka "alg name" (add_sender_receiver_nodes)
    #:: schema "specific instructions for resolving (ie/ examples of what a sender node looks like))"

    ## PREFETCH RECORD GROUPS  (optional real-time later)
    records_groups=[]

    ##########################
    ## FETCH KB Records  (df, Records space data (workable format))
    meta={}
    dd={}
    dd['case_id']=ptr['case_id']
    dd['schema']=ptr['schema']
    dd['force_update_all']=force_update_all
    dd['markup_version']=ptr['markup_version']
    #fetch only# dd['commit']=commit


    #### DYNAMIC (see notes below)
    dd['record_batch_size']=60 #Non-threaded (otherwise this value overwritten based on thread count)
    
    if force_thread_count:
        local_thread_count=force_thread_count
    else:
        local_thread_count=THREAD_COUNT
        
    dd['thread_count']=local_thread_count
    
    ## RECORD BATCHING
    if 'cypher_markup' in ptr['markup_alg_branch']:
        logging.info("[no pre-fetch of data for cypher updater]")
        record_groups=['not_group_cypher_records_realtime']
    else:

        # For logic updates its' essentially one group
        # For llm updates it's many
        record_groups=fetch_KB_records_for_update(**dd)

        if record_groups:
            logging.info("[info]  Fetched "+str(len(record_groups))+" record groups for update of size: "+str(record_groups[0].size())+" each.")

    threaded_results=[]
    
    ## STATUS META SETUP:
    counter = 0
    start_time = time.time()
    last_print_time = start_time

    while record_groups:  #aka multi-processing
        ## STATUS META:
        counter += 1
        current_time = time.time()
        
        print ("[extra verbose but check at counter 1] record_groups: "+str(len(record_groups))+" c: "+str(counter))
        # Check if 10 seconds have passed since the last print
        if current_time - last_print_time >= 10:
            elapsed_time = current_time - start_time
            print(f"Total time: {elapsed_time:.2f} seconds, Loops: {counter} size of record_groups: {len(record_groups)}")
            last_print_time = current_time


        Records=record_groups.pop(0)
        new_records=[]
        
        options={}
        options['DEFAULT_LLM_GROUP_SIZE']=DEFAULT_LLM_GROUP_SIZE
        

        if local_thread_count>1:
            ## Get thread and execute if able otherwise wait
            #- response not needed since cypher update included
            logging.info("[call at thread count]: "+str(local_thread_count))
            Multi.execute(execute_markup_threadsafe,case_id=case_id,markup_alg_branch=ptr['markup_alg_branch'],Records=copy.deepcopy(Records),ptr=copy.deepcopy(ptr),options=options,commit=commit)
            #^^ possible no return?
            
            ### CHECK FOR COMPLETION RESPONSES
            #- hard fail on error?
            #- see: wait_for_completed, get_completed, etc.
            completed=Multi.get_completed(fail_on_error=True,verbose=True )#Dec 16 verbose)
            threaded_results+=completed
            if completed: print ("[debug] raw THREAD RESPONSE: "+str(completed))

        else:
            non_threaded_response=execute_markup_threadsafe(case_id=case_id,markup_alg_branch=ptr['markup_alg_branch'],Records=copy.deepcopy(Records),ptr=copy.deepcopy(ptr),options=options,commit=commit)
            #thread_response:  just meta or ie/ how many tokens used

    ## FINAL WAIT FOR COMPLETION
    if local_thread_count>1:
        logging.info("[threaded wait for all results]...")

        max_wait_time=2000 #Jan 3 2/15 never on BOA. (maybe just on pent??)
        try:
            all_results=Multi.wait_for_all_results(fail_on_error=True,max_wait_time=max_wait_time,verbose=True) # Dec 16 verbose
        except Exception as e:
            logging.error("[error]  Multi.wait_for_all_results failed: "+str(e))
            logging.dev("[error]  Multi.wait_for_all_results failed: "+str(e))
            all_results=[]

        threaded_results+=all_results
        response['output']=threaded_results
    else:
        response['output']=non_threaded_response

    print ("** WATCH ABOVE FREEZE WAITING FOR ALL THREADS TO COMPLETE **")
    print ("** RESPONSE NOT USED YET: "+str(response))
    return response


def execute_markup_threadsafe(case_id='',markup_alg_branch='',Records=[],ptr={},options={},commit=True):
    response={}

    ## Track fields changed (Recall try: because cypher is empty)
    if 'cypher_markup' in markup_alg_branch:
        meta_doc={} #[ ] or optionally pull from non Records()
    else:
        given_field_names=Records.list_field_names()  # Track meta
        meta_doc=fetch_KB_meta(case_id,ptr['schema'],Records)

    ##########################
    #  CALL   MARKUP METHOD  #
    ##########################

    if 'llm_markup'==markup_alg_branch:
        # CALL llm_markup
        logging.info("[info]  Ready to call llm_markup...")
        ## Setup params for llm_markup
        dd={}
        dd['case_id']=ptr['case_id']
        dd['schema']=ptr['schema']
        dd['Records']=Records
        dd['markup_goals']=ptr['markup_goals']
        dd['meta_doc']=meta_doc
        dd['DEFAULT_LLM_GROUP_SIZE']=options['DEFAULT_LLM_GROUP_SIZE']  #10 a big small? (20 starts to misss things)
    
        new_records,unprocessed_records,meta_markup=do_llm_markup(**dd)

        response['total_tokens_used']=meta_markup.get('total_tokens_used',0)
        response['markup_output']=new_records

    elif 'logic_markup'==markup_alg_branch:
        logging.info("[info]  Ready to call logic_markup...")
        ## Setup params for logic_markup
        dd={}
        dd['case_id']=ptr['case_id']
        dd['schema']=ptr['schema']
        dd['Records']=Records
        dd['markup_goals']=ptr['markup_goals']
        dd['meta_doc']=meta_doc
        new_records,unprocessed_records,meta_markup=do_logic_markup(**dd)
        response['markup_output']=new_records

    elif 'cypher_markup'==markup_alg_branch:
        logging.info("[info]  Ready to call cypher_markup...")
        
        if 'add_processed_by_nodes' in ptr['markup_goals']:
    
            dd={}
            dd['case_id']=ptr['case_id']
            dd['schema']=ptr['schema']
            dd['Records']=None  #Records #<-- not used at cypher
            dd['markup_goals']=ptr['markup_goals'] #<-- add_processed_by_nodes 
            dd['meta_doc']=meta_doc
            dd['markup_version']=ptr['markup_version']
            dd['commit']=commit
    
            new_records,unprocessed_records,meta_markup=do_cypher_markup_PROCESSED_BY(**dd)
            response['markup_output']=new_records

        elif 'easy_credit_debit_main_goal' in ptr['markup_goals']:
            dd={}
            dd['case_id']=ptr['case_id']
            dd['schema']=ptr['schema']
            dd['Records']=None  #Records #<-- not used at cypher
            dd['markup_goals']=ptr['markup_goals'] #<-- add_processed_by_nodes 
            dd['meta_doc']=meta_doc
            dd['markup_version']=ptr['markup_version']
            dd['commit']=commit
            new_records,unprocessed_records,meta_markup=do_cypher_markup_EASY_DEBIT_CREDIT(**dd)
            response['markup_output']=new_records

        else:
            raise Exception ("[ERROR] unknown cypher_markup goal: "+str(ptr['markup_goals']))

    else:
        raise Exception ("[ERROR] unknown markup_alg_branch: "+str(markup_alg_branch))


    ##########################
    ## CYPHER UPDATE
    #- Merge upated records into cypher (field or node or rel scope)
    ## Meta check
    
    if not commit:
        logging.info("[no commit] since testing.  for "+str(ptr['markup_goals'])+" new fields into KB: record count: "+str(len(new_records)))

    elif 'cypher_markup' in markup_alg_branch:
        #** already pushed-real-time mods
        pass

    elif not new_records:
        logging.info("[no new_records] since handled by cypher side likely")

    else:
        ## Push updates to graph (via cypher)
        ptr['new_field_names']=list(set(list(new_records[0].keys()))-set(given_field_names))
        print ("[dev] insert for "+str(ptr['markup_goals'])+" new fields into KB: "+str(ptr['new_field_names'])+" record count: "+str(len(new_records)))
        call_cypher_push_updated_records(new_records,ptr)

    logging.info("[debug] return from: "+str(markup_alg_branch)+" with meta_markup: "+str(meta_markup))
    logging.info("[debug ^^ llm_markup done but frozen after this...?")
    return response


def get_algs_to_apply():
    ## All or subset
    ALL_ALGS_TO_APPLY=[]
    ALL_ALGS_TO_APPLY+=['transaction_type_method']
    ALL_ALGS_TO_APPLY+=['add_sender_receiver_nodes']
    ALL_ALGS_TO_APPLY+=['logical_card_check_numbers']
    ALL_ALGS_TO_APPLY+=['add_PROCESSED_BY']
    ALL_ALGS_TO_APPLY+=['easy_credit_debit_main']     # Upstream logic for top-level credit/debits

    return ALL_ALGS_TO_APPLY


def interface_call_kb_auto_update(case_id,force_update_all=False,force_algs_to_apply=[],commit=True,force_thread_count=0):
    meta={}
    meta['algs_run']=[]
    meta['total_tokens_used']=0
    
    print ("[ ] candidate put multi-process alg here.")
    print ("- then can move downstream as needed (ie/ chunk query to records)")

    if force_algs_to_apply:
        ALL_ALGS_TO_APPLY=force_algs_to_apply
    else:
        ALL_ALGS_TO_APPLY=get_algs_to_apply()

    outputs=[]
    for question in ALL_ALGS_TO_APPLY:
        logging.info("="*30)
        logging.info("[start question]: "+str(question)+" for case_id: "+str(case_id))
        logging.info("^^ of possible: "+str(",".join(ALL_ALGS_TO_APPLY)))

        meta['algs_run']+=[question]
        output=call_kb_auto_solver_flow(question,case_id,force_update_all=force_update_all,commit=commit,force_thread_count=force_thread_count)
        meta['total_tokens_used']+=output.get('total_tokens_used',0)

        outputs.append(output)
    return outputs,meta

def dev_interface_call_kb_auto_update(case_id,algs_to_apply=[],force_update_all=False,commit=True,force_thread_count=0):
    for question in algs_to_apply:
        call_kb_auto_solver_flow(question,case_id,force_update_all=force_update_all,commit=commit,force_thread_count=force_thread_count)
    return

def DEV_call_kb_auto_update():
    ## ENTRYPOINT FOR KB UPDATE
    print ("> question driven schema update")

    ## Higher-level do internal questions (resolve knowledge gaps by 'markup_llm')
    ALL_ALGS_TO_APPLY=get_algs_to_apply()

    checkk=calll
    ## DEV OPTIONS
    case_id='case_3'
    case_id='case_schoolkids' #transactions created 6pm 20th
    #ALL_ALGS_TO_APPLY=['[transaction_type_method]']
    #ALL_ALGS_TO_APPLY=['[logical_card_check_numbers]']

    #question='Update KB via markup_llm [transaction_type_method]'  #KEYWORD STEERING
    for question in ALL_ALGS_TO_APPLY:
        call_kb_auto_solver_flow(question,case_id)

    return



if __name__=='__main__':
    branches=['call_kb_auto_solver_flow_template']
    branches=['call_kb_auto_solver_flow_SAMPLE']

    branches=['DEV_call_kb_auto_update']

    for b in branches:
        globals()[b]()





"""
"""
