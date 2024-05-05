import time
import os
import sys
import codecs
import copy
import json
import re
import datetime
import hashlib
import random
import pandas as pd


LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"..")


from w_llm.llm_interfaces import LazyLoadLLM


from get_logger import setup_logging
logging=setup_logging()


#0v1# JC  Mar 24, 2024  Setup



"""
    Standardize LLM as a function 
    - DICT2DICT markup guarentee
    - (recall applied to date resolution)
    - (apply to credit/debit classification)
       This Purchase currently as credit:  https://core.epventures.co/api/v1/case/65f5d2d87a047045e56b3da0/pdf/0e8345f5-9ae9-4442-9cbb-67e5e6da0d8a.pdf?page=640&key=3f26474fa7cbffaa8c2d6ced1b3f0c5630e3eb9a6a39e26a2054b07c6745edfb&highlight=2266.66|415-431-9196|WHOLESALE|GOORIN
    - leverage existing interface is fine
    - dict=, jsonl=, df=   *interesting multi-data suppot

    NOTES:
    - Consider borrowing from algs_extract as well
    - Possible to use OpenAI functions but keep LLM approach generic

"""
## Common attempt
def alg_json2dict(given,depth=0):
    #0v2# JC Mar 24, 2024  Use local but no changes yet
    #0v1# JC Sep  8, 2023  Init

    ## NOTES:
    #i)  Auto repair ie/ if fails first and has alpha at start
    # Given str return dict
    #1)  json
    #2)  eval
    #3)  swap ' for "
    dd={}

    if not isinstance(given,dict) and depth<=1:
        try:
            dd=json.loads(given)
        except:
            try:
                dd = ast.literal_eval(given)
            except:
                pass

            if not dd or not isinstance(dd,dict):
                ##Try swapping ' for "" but not if it's escaped or buried
                given = re.sub(r"(?<!\\)\'", '"', given)

                ##Try removing characters at start (ie...look for [ and { )
                given=re.sub(r'^.*?([\[\{\`])', r'\1', given,flags=re.DOTALL).strip()

                dd=alg_json2dict(given,depth=depth+1)

    elif isinstance(given,dict):
        dd=given
    else:
        dd={}
    return dd


def get_date_prompt(dt):
    print ("[info] using LLM to resolve date: "+str(dt))
    prompt="""You are a date conversion tool and return the response in valid json.
        Output should look like: {'date':'2018-09-21'} in yyyy--mm-dd format.
        Please convert the following date (if there are two dates return the first): """+str(dt)
    return prompt


def ask_llm_dict2dict(dict_in,prompt='',prompt_kind='',fields_to_change=[]):
    #? ignore fields?

    ## INIT
    LLM=LazyLoadLLM.get_instance()
    dict_out=copy.deepcopy(dict_in)
    
    ## PREP PROMPT
    if prompt:
        pass
    elif prompt_kind=='date' and 'date' in dict_in:
        prompt=get_date_prompt(dict_in.get('date',''))
    else:
        raise Exception("ask_llm_dict2dict: Unknown prompt_kind: "+str(prompt_kind))
    
    print ("[debug] raw prompt: "+str(prompt))
    
    ## DO QUERY
    response=LLM.prompt(prompt)
    print ("[debug] raw raw result: "+str(response))

    try:
        result=alg_json2dict(response)
    except Exception as e:
        print ("[debug] warning on json2dict: "+str(e))
        result={}

    ## MAP TO DICT
    for f in fields_to_change:
        if f in result:
            dict_out[f]=result[f]

    return dict_out


def pdev_local_test():
    print ("Watch no double imports / instances")
    dd={}
    dd['date']='2022-  09-21'
    prompt_kind='date' #Assume data structure
    fields_to_change=['date']  #Hardcode so nothing too odd
    dd2=ask_llm_dict2dict(dd,prompt_kind=prompt_kind,fields_to_change=fields_to_change)
    print ("GIVEN: "+str(dd))
    print ("RESULT: "+str(dd2))
    if not dd2.get('date','')=='2022-09-21':
        raise Exception("pdev_local_test: Failed")
    return


if __name__=='__main__':
    branches=['pdev_local_test']
    for b in branches:
        globals()[b]()


        
"""
"""