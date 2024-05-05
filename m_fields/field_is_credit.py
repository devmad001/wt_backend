import os
import sys
import copy
import json
import re


LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")


from get_logger import setup_logging
logging=setup_logging()


from w_llm.llm_functions import ask_llm_dict2dict
from kb_ai.cypher_markups.markup_alg_cypher_EASY_CREDIT_DEBIT import is_transaction_credit


#0v1# JC  Mar 24, 2024  Setup


"""
    FIELDS FORMALIZATION
    - more schema based then data specific (so stand-alone)
    - integrate with audit where possible
    - single clean definitions (Part of extended app formalization)
    
    NOTES:
    - Dev using org function vs LLM powered function to validate
"""


def get_credit_debit_prompt(record,ignore=[]):
    
    ## Easy local filter
    record=copy.deepcopy(record)
    for ignore in ignore:
        if ignore in record:
            del record[ignore]
            
    print ("[info] using LLM to resolve credit/debit from: "+str(record))
    prompt="""You are a date conversion tool and return the response in valid json.
        Output should look like: {'is_credit':True'}  (or False if debit)
        Given the following record. Determin if the bank transactions is credit or debit: """+str(record)
    return prompt



def field_is_credit_debit(given):
    ## LLM BASED!
    # (for original see alg_classify_debit_credit VERY OLD)
    # (for newer original see markup_alg_cypher_EASY_CREDIT_DEBIT.py
            
    ## BEWARE:
    #-  if transaction_type is present, be careful because usually done with/after is_credit class so may confuse
    
    ## TOP CONFIG
    CHECK_IF_MATCHES_HEURISTICS=True
    REDO_IF_EXISTS=True
    if not REDO_IF_EXISTS: raise Exception("Not implemented")


    ## INIT
    meta={}
    record=copy.deepcopy(given)

    ## GET PROMPT
    prompt=get_credit_debit_prompt(record,ignore=['id','transaction_date'])

    ## DO LLM QUERY
    response=ask_llm_dict2dict(record,prompt=prompt,fields_to_change=['is_credit'])

    
    ## Local check for retry
    resolved_is_credit=response.get('is_credit',None)
    is_credit_org=None
    if resolved_is_credit is None or CHECK_IF_MATCHES_HEURISTICS:
        ## Real-time trial against original
        # * special format
        tcredit={}
        tcredit['dev1']=record
        tt=record
        tt['id']='dev1'
        is_credit_org,tcredit,reasons=is_transaction_credit(tt,tcredit=tcredit)
        
        ## Overwrite only if none
        if resolved_is_credit is None:
            response['is_credit']=is_credit_org
            
        ## Log status for meta only if bad
        
        meta['matches_heuristics']=is_credit_org==resolved_is_credit
        if is_credit_org is not None and not is_credit_org==resolved_is_credit:
            meta['is_credit_org']=is_credit_org
            meta['is_credit_org_reasons']=reasons
    
    return response,meta




def call_is_credit_debit():
    """
        - optional to rerun on raw record. move to schema etc. various
    ## https://watchdev.epventures.co/fin-aware/dashboard?case_id=65f5d2d87a047045e56b3da0
    """
    record={
            "transaction_description": "GOORIN BROS WHOLESALE 415-431-9196 CA",
            "transaction_amount": 2834.98,
            "transaction_date": "2018-10-31",
            "section": "PURCHASE",
            "amount_sign": "+"
        }
    
    record_new,meta=field_is_credit_debit(record)
    print ("[ ] new record: "+str(record_new))
    print ("[ ] new record meta: "+str(meta))

    return



if __name__=='__main__':
    
    branches=['dev_llm_credit_debit']
    branches=['call_is_credit_debit']

    for b in branches:
        globals()[b]()





