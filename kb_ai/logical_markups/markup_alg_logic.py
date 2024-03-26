import os
import sys
import codecs
import copy
import json
import re
import threading  #future multi

LOCAL_PATH=os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")

from w_utils import util_get_modified_keys

from get_logger import setup_logging
logging=setup_logging()

from schemas.SCHEMA_kbai import gold_schema_definition


#0v1# JC  Sep 28, 2023  Init

"""
    MARKUP USING SPECIFIC ALG LOGIC
    - (recall alternative is relying on LLM -- keep that stand-alone)
    - see do_llm_markup for sample fow (esp on version tracking) 
"""


def LOGIC_add_check_card_stuff(record):
    ## Direct record manipulation
    #* recall, custom logic regex here OR use schema regex OR use schema regex written by LLM
    
    #via claude:
    #check_numbers = re.findall(r'CHECK#\s*(\d+)|\s+(CHECKCARD)\s+(\d+)', transaction_desc)
    
    #via gpt-4
    #check_numbers = re.findall(r'(?:CHECK#|CHECKCARD)\s*(\d+)', str(record))
    
    #(i)
    check_numbers = re.findall(r'(?:CHECK#)\s*(\d+)', str(record))
    
    #(ii)
    # 'CHECKCARD  1208 MICROSOFT*365 MSBILL.INFO | WA 74430991342400815000389 CKCD 5045 | XXXXXXXXXXXX6164',
    #{ either end of description or \d' in str(record)}
    if 'CHECKCARD' in str(record.get('transaction_description','')):
        #** End with $, a space or an or sign
        m=re.search(r'XXXX([\d]+)(?:$|[ $|])',str(record['transaction_description']))
        if m:
            check_numbers+=[m.group(1)]
            
    #(iii)
    # Wells Fargo is:  
    # ^205 Check$
    m=re.search(r'^([\d]+) Check',str(record['transaction_description']).strip())
    if m:
        check_numbers+=[m.group(1)]

    # ^Check 205$
    m=re.search(r'^Check ([\d]+)',str(record['transaction_description']).strip())
    if m: check_numbers+=[m.group(1)]

    if check_numbers:
        record['check_num']=check_numbers[0]

    return record

def logic_markup_single_records(**vars):
    meta={}
    meta['count_records_changed']=0
    ### GIVEN
    # Records
    Records=vars['Records']
    new_records=[]
    given_records=Records.dump_all_records()
    
    ### PROCESS EACH RECORD
    new_records=[] 
    for record in given_records:

        #####################################
        ## BRANCHES -- SINGLE RECORD ALG

        if 'LOGIC_add_check_card_stuff' in vars['markup_goals']:
            org_record=copy.deepcopy(record)
            
            ####  EXECUTE SPECIFIC LOGIC AGAINST record
            record=LOGIC_add_check_card_stuff(record)
            
        else:
            stopp=okk


        ####  VALIDATION -- CHECK THAT ONLY TARGET FIELDS MODIFIED
        is_mod=False
        allowed_modified_fields=vars['schema'].get('fields_to_update',[]) #org spec 'schema' params
        if allowed_modified_fields:
            ## Check fields are allowed to be modified
            modified_fields=util_get_modified_keys(org_record,record)
            for modified_field in modified_fields:
                is_mod=True
                if modified_field not in allowed_modified_fields:
                    raise Exception("Field %s is not allowed to be modified. Only these fields are allowed to be modified: %s" % (modified_field, allowed_modified_fields))
        else:
            raise Exception("No fields_to_update specified in schema")

        if is_mod:
            meta['count_records_changed']+=1
            logging.info("[dev] [logic modded record]: "+str(record)+" at fields: "+str(modified_fields))
        new_records+=[record]
    
    ###  Acknowledge processed records
    #- recall, more relevant when processing can fail/batches/multi (LLM etc)
    Records.process_and_update_records(new_records)  #Assume all 'passed' (processed correctly -- only real issue with LLM retries)
    finished_records,unfinished_records=Records.FINALLY_get_all_records()

    ### Stats
    #ok below#  logging.info("[finished logic markup] record count: %s" % len(finished_records)+" modified: %s" % meta['count_records_changed'])
    return finished_records,unfinished_records,meta




def do_logic_markup(*args,**vars):
    ### RECALL:
    #- which alg to use comes via map-question_need_to_alg_offer()
    
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
    """
    
    ## Map back to va
    # touch givens
    vars['markup_goals']=vars['markup_goals'] #ie/ alg to run
    

    ### LOOKUP LOGIC BRANCH
    #- recall, set during mapping (call_kbai.py -> map_question_need_to_alg_offer))
    if 'LOGIC_add_check_card_stuff' in vars['markup_goals']:
        #finished_records,unfinished_records,markup_meta=logic_markup_template(**vars)
        finished_records,unfinished_records,markup_meta=logic_markup_single_records(**vars)
        meta.update(markup_meta)

    else:
        raise Exception("Unknown markup_goals: %s" % vars['markup_goals'])

    logging.info("[finished logic markup] record count: %s" % len(finished_records)+" modified: %s" % meta['count_records_changed'])

    return finished_records,unfinished_records,meta



if __name__=='__main__':
    branches=['do_markup_alg_logic']

    for b in branches:
        globals()[b]()

"""
    LOGIC ROUTINE IDEAS:
        main_account=''
        print ("Yeah, is main account withdrawl or deposit -- seems like an easy question")
"""
