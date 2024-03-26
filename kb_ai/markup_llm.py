import os
import sys
import time
import codecs
import copy
import uuid
import json
import re
import threading  #future multi

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")

from get_logger import setup_logging
logging=setup_logging()

from schemas.SCHEMA_kbai import gold_schema_definition

from class_live_records import Live_Records

from prompt_eng import Prompt_Eng
from prompt_eng import prompt_authoring

from w_llm.llm_interfaces import LazyLoadLLM
from w_llm.llm_interfaces import OpenAILLM    #threaded

from a_custom.algs_extract import alg_json2dict


#0v2# JC  Sep 26, 2023  Threaded support (from above [Records])
#0v1# JC  Sep 14, 2023  Init

"""
    LLM MARKUP
    - reuse learnings from b_extract (page2trans & add_accounts)
"""

"""
NOTES ON MULTI_THREADED:
- can get complicated because re-runs of records sub-groups + reasons tracking + LLM usage. => move upstream to [Records]
"""


## DEV NOTES:
ASSUME_THREADED=True
if ASSUME_THREADED:
    print ("[assuming threading]=> Separate LLM interfaces (no lazy)")

def get_local_LLM():
    ## Assume threaded and/or pass LLM down from pre-allocated pool
    LLMLOCAL=OpenAILLM(model_name='gpt-3.5-turbo')
    return LLMLOCAL

def execute_llm_prompt(the_prompt,prompt_records,LLMLOCAL,thread_id):
    ## Separate for thread safe
    #[ ] threads tbd
    response=LLMLOCAL.prompt(the_prompt,json_validate=False)
    return response,prompt_records,thread_id

def do_llm_markup(Records,schema={},markup_goals=[],page_text='',meta_doc={},case_id='',DEFAULT_LLM_GROUP_SIZE=10):
    ## GOAL:  Add fields to records
    #- real-time prompt re-adjustments an retry
    # markup_goals:  High-level goal of markup (determines prompt etc ie/ add Entity field etc)
    # meta_doc:  document level meta (ie/ is_BOA, alg_source_doc_meta -> page extractions
    # schema:  Defined schema  (ie/ how to construct prompt/do inserts etc)
    # case_id: optional?

    ## Check given
    if not schema: raise Exception("No schema given")

    lm_meta={}
    lm_meta['total_tokens_used']=0
    lm_meta['count_invalid_llm_json_responses']=0

    #LLM=LazyLoadLLM.get_instance()
    LLMLOCAL=get_local_LLM()

    MAX_TOKENS=int(LLMLOCAL.MAX_INPUT_TOKENS*0.80)  ## LOCAL BUFFER

    #############################################
    #  PROMPT ENGINEERING + EXECUTION
    #############################################
    Eng=Prompt_Eng()
    eng={} #tbd on dict or class
    eng['default_group_size']=DEFAULT_LLM_GROUP_SIZE  #10 small for MANY records
    eng['prompt_eng_method']='default'
    eng['group_size']=eng['default_group_size']
    eng['markup_goals']=markup_goals
    
    print ("[debug] markup goals: "+str(markup_goals))
    print ("[debug] field names: "+str(Records.list_field_names()))


    ##
    ALG_manual_clean_records={}


    #?combine to overall cycle status?
    stats={}
    stats['conseq_failures']=0  #consequtive failures
    stats['global_reasons']=[]  #collect all
    stats['count_loops']=0
    stats['count_processed']=0
    stats['count_unprocessed']=0
    stats['count_target_records']=Records.size()

    reasons=[]
    llm_markup_running=True
    last_was_invalid=False
    the_prompt=''
    while llm_markup_running and stats['count_target_records']>0:

        ### LOOP STATS + STATUS
        stats['count_loops']+=1

        stats['count_processed']=Records.count_processed()
        stats['count_unprocessed']=Records.count_unprocessed()

        stats['progress']=round(stats['count_processed']/stats['count_target_records'],0)*100
        logging.info("[llm_markup]  Progress: "+str(stats['progress'])+"%  "+str(stats['count_processed'])+"/"+str(stats['count_target_records']))
        if stats['global_reasons']: logging.info("[issue reasons seen]: "+str(stats['global_reasons']))

        if stats['conseq_failures']:
            logging.dev("BAD PROMPT?: "+str(the_prompt))
            logging.info("[warning] LLM consequtive failures: "+str(stats['conseq_failures']))
            logging.warning("[warning] LLM consequtive failures: "+str(stats['conseq_failures']))
            
            if stats['conseq_failures']>15: #3k on ...2d3c case.
                raise Exception("LLM consequtive failures: "+str(stats['conseq_failures']))

        #############################################
        ###  BUILD PROMPT
        #- prompt engineer decides on prompt method ([ ] can move to class)
        #[] watch token length

        ## WATCH PAST FAILURES
        stats['conseq_failures'] = stats['conseq_failures'] + 1 if reasons else 0
        if reasons:
            ## Track fail reasons
            if stats['conseq_failures']>0:
                print ("="*20+" consecutive fails: "+str(stats['conseq_failures'])+" "+"="*20)

            logging.info("[warning] LLM last respnse was invalid: "+str(reasons))
            # Recall, these should align with Records methods  (class_live_records.py)
            # default, half_group, randomize, first_x
            if stats['conseq_failures']==1:
                eng['prompt_eng_method']='half_group'
            else:
                eng['prompt_eng_method']='randomize'  #Maybe half & randomize?
        else:
            eng['prompt_eng_method']='default'
        logging.info("[prompt engineer method: "+str(eng['prompt_eng_method'])+"]")


        ### WRITE PROMPT
        #- locally pre-validate token length!
        prompt_looks_good=False
        retries=3
        while retries>0 and not prompt_looks_good:
            retries-=1
            the_prompt=''
            
            ### DETERMINE GROUP SIZE
            local_group_size=eng['group_size']
            if stats['conseq_failures']>3:
                group_size_factor=0.75**stats['conseq_failures']
                local_group_size=max(1,int(local_group_size*group_size_factor))
                logging.dev("[warning] reducing group size via conseq failure factor: "+str(group_size_factor)+" size now: "+str(local_group_size))
                logging.warning("[warning] reducing group size via conseq failure factor: "+str(group_size_factor)+" size now: "+str(local_group_size))

            ### WRITE PROMPT
            if eng['prompt_eng_method'] in ['default','randomize']:
    
                ## Get record sub-group 'batch'
                prompt_records=Records.dump_sub_records(group_size=local_group_size,method=eng['prompt_eng_method'])
                print ("[D4] prompt records: "+str(prompt_records))
                print ("[debug] prompt_records count: "+str(len(prompt_records)))
            
                #? prompt limit?
                the_prompt=prompt_authoring(prompt_records,schema=schema,markup_goals=markup_goals,page_text=page_text,meta_doc=meta_doc)

            elif eng['prompt_eng_method'] in ['half_group']:
                ## Get record sub-group 'batch'
                prompt_records=Records.dump_sub_records(group_size=local_group_size,method=eng['prompt_eng_method'])
                print ("[D4] prompt records: "+str(prompt_records))
                print ("[debug] prompt_records count: "+str(len(prompt_records)))
            
                #? prompt limit?
                the_prompt=prompt_authoring(prompt_records,schema=schema,markup_goals=markup_goals,page_text=page_text,meta_doc=meta_doc)

            elif eng['prompt_eng_method'] in ['half_group']:
                pass
    
            else:
                stopp=prompt_method_check
            count_of_prompt_tokens=LLMLOCAL.count_tokens(the_prompt)

            ## Local check
            if count_of_prompt_tokens>MAX_TOKENS:
                Records.process_failed(prompt_records,reasons=['token_maxed'])
                local_group_size=int(local_group_size*0.75)
                print ("[info] reducing prompt size due to token length from ORG: "+str(eng['group_size'])+" to: "+str(local_group_size))
            else:
                prompt_looks_good=True

        virtual_record_ids=[r['id'] for r in prompt_records]
        print ("PROMPT"+"="*30+" ("+str(count_of_prompt_tokens)+" tokens)")
        print (str(the_prompt))
        print ("PROMPT"+"^"*30+" ("+str(count_of_prompt_tokens)+" tokens)")

        #############################################
        #############################################
        ### Execute LLM
        reasons=[]

        #[ ] handle LLM lib failures or catch
        #[ ] watch token length!
        lm_meta['total_tokens_used']+=LLMLOCAL.count_tokens(the_prompt)
        

        ### INNER THREAD SAFE EXE OF LLM
        # Add a dictionary to store responses from each thread
        thread_responses = {}
        
        #print ("RECORDS to PROCESS (limited keys): "+str(prompt_records))
        
        got_response = False
        while not got_response:
            ## Not threaded
            thread_id=str(uuid.uuid4())
            response,prompt_records,thread_id=execute_llm_prompt(the_prompt,prompt_records,LLMLOCAL,thread_id)
            got_response=True


        print ("[LLM RESPONSE]: "+str(response))
    
        ## External JSON validation
        new_records=alg_json2dict(response)

        ## Special case where response=response['response']=[]
        #** patch.
        if isinstance(new_records,dict) and 'response' in new_records and isinstance(new_records['response'],list):
            new_records=new_records['response']
    
        ## Is response valid?  (json valid, record counts, etc)
        if not new_records:
            reasons+=['invalid_json']
            # regex if ... within 10 chars of end
            if re.search(r'\.\.\.[.]{0,10}$',str(response)):
                reasons+=['invalid_json_3dots']
        elif isinstance(new_records,str):
            reasons+=['response_is_str']
            print ("RESPONSE IS STR: "+str(response))
            stopp=checkk
        else:
            ### POST RESPONSE MESSAGE
            ## Migrate ids from int to str
            try:
                new_record_id_set=set([r.get('id','') for r in new_records])
            except Exception as e:
                logging.error("COULD NOT PROCESS: "+str(new_records))
                new_record_id_set=set([])
                #raise error bad on threaded#  new_record_id_set=set([r.get('id','') for r in new_records])
                
            ## Patch
            #> LLM response with records indexed at ['1']   ['2'] etc in which case need to re-index. Where id is within record dict
            is_llm_responded_number_strings=False
            try:
                if new_records['1']['id']:
                    is_llm_responded_number_strings=True
            except: pass
            if is_llm_responded_number_strings:
                reindexed=[]
                for num_str in new_records:
                    reindexed.append(new_records[num_str])
                new_records=reindexed
                
            ### Normalize id
            for record in new_records:
                if 'id' in record:
                    record['id'] = str(record['id'])

            ### PATCH  auto match ids if generated ones are blank or the same & still same counts
            if len(new_record_id_set)==1: #set(['']):
                if len(new_records)==len(prompt_records):
                    i=-1
                    for record in new_records:
                        i+=1
                        record['id']=str(prompt_records[i]['id'])
                        logging.info("[warning] no ids in response but can assume matches")

            ## Watch or bad response
            try:
                response_record_ids=[str(r.get('id','')) for r in new_records]
            except Exception as e:
                logging.warning("[warning] bad llm response at llm_markup: (**force remove -- and system will retry) "+str(e))
                logging.warning("[warning] new records not expect format: "+str(new_records))
                #response_record_ids=[str(r.get('id','')) for r in new_records]
                new_records=[]


            ## High-level checks
            #[ ] token lenth error (ie/ drop group_size)
            if len(new_records)!=len(prompt_records):
                reasons+=['invalid_json_count expected: '+str(len(prompt_records))+' got: '+str(len(new_records))]
            elif len(new_records)==0:
                reasons+=['invalid_json_count_0']
            elif len(new_records)>len(prompt_records):
                reasons+=['invalid_json_count_gt']
            elif not set(virtual_record_ids)==set(response_record_ids):
                logging.warning("[warning] LLM response record ids do not match prompt record ids: "+str(virtual_record_ids)+" "+str(response_record_ids))
                reasons+=['virtual_ids_mismatch']
            else:
                pass
            """
            BAD COLLECTION:
            [LLM RESPONSE]: Since the JSON provided does not include any bank statement transactions, I cannot infer any details about the sender and receiver entities. However, if you provide the actual bank statement transactions in a valid JSON format, I will be able to infer the details for each transaction.
            """

        stats['global_reasons']+=reasons

        ## UPDATE STATUS
        if reasons: #FAIL
            logging.info("[warning] LLM invalid response: "+str(reasons))
            ## Mark records as unprocessed
            Records.process_failed(prompt_records,reasons=reasons) #<-- puts back into active pool

            ##***custom debug
            if not 'invalid_json_3dots' in str(reasons):
                logging.dev("[LLM_invalid_json] (goes back into pot -logged to dev): "+str(response))
                lm_meta['count_invalid_llm_json_responses']+=1
                time.sleep(10)

        else: #PASS + update records
            last_was_invalid=False
            logging.info("[GOOD LLM RESPONE] for record count: "+str(len(new_records)))
            Records.process_and_update_records(new_records)

        ## BREAK AT
        if Records.count_unprocessed()==0:
            logging.info("[llm_markup]  All records processed!")
            llm_markup_running=False
    

    #############################################
    ## Assemble records  (handled by Live_Records)
    finished_records,unfinished_records=Records.FINALLY_get_all_records()

    print ("[debug] finished record count: "+str(len(finished_records)))
    print ("[debug] unfinished record count: "+str(len(unfinished_records)))
    print ("**recall unfinished are simply not have transaction_amounts")

    ## Manual clean out_records
    ## Manual remove out_records

    ## Final validation
    #OK# if 'add_sender_receiver_nodes' in markup_goals: a=okk_llm_markup

    return finished_records,unfinished_records,lm_meta


## See get test data in call_kbai.py
def call_do_llm_markup(case_id='case_3',Records=None,page_text='',meta_doc={},markup_goals=['transaction_receiver_entity']):
    unused=moved_to_call_kbai

    ## Implied or real-time/
    given_field_names=Records.list_field_names()

    ## GIVEN LIST OF RECORDS, UPDATE THEM
    ## GET SCHEMA VIA MARKUP

    from schema_sender_entity import schema
    if not 'sender_entity' in schema['kind']: stopp=checks

    ## CALL MARKUP
    new_records,unprocessed_records,meta_markup=do_llm_markup(Records,schema=schema,markup_goals=markup_goals,page_text=page_text,meta_doc=meta_doc)

    ## New field names (real-time calc)
    if new_records:
        new_field_names=list(set(list(new_records[0].keys()))-set(given_field_names))

    return new_records,unprocessed_records,new_field_names,meta_markup


def dev_threaded_do_markup():
    print ("Test/dev for multi-threaded option")

    return


if __name__=='__main__':
    branches=['call_do_llm_markup']
    branches=['dev_threaded_do_markup']

    for b in branches:
        globals()[b]()

"""
    global THREADED,THREAD_COUNT

#D1# def get_multi_llms():
#D1#     global THREADED,THREAD_COUNT
#D1#     #No shared lazy load
#D1#     llms=[]
#D1#     if THREADED:
#D1#         for i in range(THREAD_COUNT):
#D1#             llms.append({'owner':'','llm':OpenAILLM()})
#D1#     return llms
#!! moved upstream
DRAFT if threaded then use LLM assigned to thread id

            if THREADED:
                if len(ATHREADS) >= THREAD_COUNT:
                    # Check if any threads have finished
                    for thread_id in list(ATHREADS.keys()):  # Iterating over a copy of the keys
                        if not ATHREADS[thread_id].is_alive():
                            ATHREADS[thread_id].join()  # Make sure the thread has completed
                            
                            # Retrieve and process the response
                            response = thread_responses.pop(thread_id, None)  # Get and remove response
                            if response:
                                # Handle your response here
                                got_response = True
                                break
        
                            # Release the LLM claim
                            for res in LLMS:
                                if res['owner'] == thread_id:
                                    res['owner'] = ''
                                    break
        
                            del ATHREADS[thread_id]  # Remove the thread
                            
                    time.sleep(1)
                else:
                    # Start a new thread
                    thread_id = str(uuid.uuid4())
                    
                    # Claim LLM
                    claimed = False
                    for res in LLMS:
                        if not res['owner']:
                            res['owner'] = thread_id
                            claimed = True
                            LOCAL_LLM = res['llm']
                            break
                    
                    if claimed:
                        ATHREADS[thread_id] = threading.Thread(target=execute_llm_prompt, args=(the_prompt, prompt_records, LOCAL_LLM, thread_id, thread_responses))
                        ATHREADS[thread_id].start()
"""
