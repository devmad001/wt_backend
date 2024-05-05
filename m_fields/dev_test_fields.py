import os
import sys
import codecs
import json
import re
import time
import requests


LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")


from get_logger import setup_logging
logging=setup_logging()


from w_llm.llm_functions import ask_llm_dict2dict
from kb_ai.cypher_markups.markup_alg_cypher_EASY_CREDIT_DEBIT import is_transaction_credit


#0v1# JC  Mar 24, 2024  Setup


"""
*** THIS IS DEV
    FIELDS FORMALIZATION
    - more schema based then data specific (so stand-alone)
    - integrate with audit where possible
    - single clean definitions (Part of extended app formalization)
    
    NOTES:
    - Dev using org function vs LLM powered function to validate
"""


def sample_get_date_prompt(dt):
    print ("[info] using LLM to resolve date: "+str(dt))
    prompt="""You are a date conversion tool and return the response in valid json.
        Output should look like: {'date':'2018-09-21'} in yyyy--mm-dd format.
        Please convert the following date (if there are two dates return the first): """+str(dt)
    return prompt

def get_credit_debit_prompt(record):
    print ("[info] using LLM to resolve credit/debit from: "+str(record))
    prompt="""You are a date conversion tool and return the response in valid json.
        Output should look like: {'is_credit':True'}  (or False if debit)
        Given the following record. Determin if the bank transactions is credit or debit: """+str(record)
    return prompt


def dev_llm_credit_debit():
    print ("> migrate from rules based to schema")
    
    ## https://watchdev.epventures.co/fin-aware/dashboard?case_id=65f5d2d87a047045e56b3da0
    #[ ] org fail but add section as a feature (optionally log when don't with final option to go back?)
    bad_sample={
            "transaction_description": "GOORIN BROS WHOLESALE 415-431-9196 CA",
            "transaction_amount": 2834.98,
            "transaction_date": "2018-10-31",
            "section": "PURCHASE",
            "amount_sign": "+"
        }
    
    prompt=get_credit_debit_prompt(bad_sample)

    response=ask_llm_dict2dict(bad_sample,prompt=prompt,fields_to_change=['is_credit'])

    print ("GOT end: "+str(response))
    
    ## Real-time trial against original
    # * special format
    tcredit={}
    tcredit['dev1']=bad_sample
    tt=bad_sample
    tt['id']='dev1'
    is_credit,tcredit,reasons=is_transaction_credit(tt,tcredit=tcredit)
    
    print ("ORG REs: "+str(is_credit))
    print ("ORG REs: "+str(tcredit))
    print ("ORG REs: "+str(reasons))


    return



print ("[ ] field specific:  optional to rerun on raw record. move to schema etc. various")



if __name__=='__main__':
    
    branches=['dev_llm_credit_debit']
    for b in branches:
        globals()[b]()





