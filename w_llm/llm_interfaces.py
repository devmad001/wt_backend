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
import threading
import pandas as pd

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)

import langchain
from langchain.llms import OpenAI #pip install langchain
from langchain.chat_models import ChatOpenAI  #New ? timeout?

from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate, PromptTemplate
from langchain.prompts.chat import SystemMessage

## Notes on extra langchain libs
#from langchain.embeddings.openai import OpenAIEmbeddings
#from langchain.vectorstores import Chroma
#from langchain.text_splitter import CharacterTextSplitter
#from langchain.chains import RetrievalQA

import tiktoken #pip isntall tiktoken  https://github.com/openai/tiktoken

sys.path.insert(0,LOCAL_PATH+"..")

from get_logger import setup_logging
from w_storage.ystorage.ystorage_handler import Storage_Helper

from llm_support import num_tokens_from_string
from llm_support import cache_llm,load_cache,remove_cache_entry, iter_cache
from llm_support import generate_hash
from llm_accounts import Manage_LLM_Accounts

logging=setup_logging()


#0v9# JC  Jan 14, 2023  Extend for multiple accounts support
#0v8# JC  Jan 14, 2023  Migrate functions to llm_support
#0v7# JC  Dec 20, 2023  openai rate limit
#0v6# JC  Nov 23, 2023  Admin stats: is service up? normal response times?
#0v5# JC  Nov 20, 2023  gpt-4.5
#0v4# JC  Oct  9, 2023  Formal log timeouts etc?
#                         - oct 9:  various 180 timeouts
#0v3# JC  Sep  7, 2023  Load from cache via hash
#0v2# JC  Sep  6, 2023  Possible timeout issue?
#0v1# JC  Sep  2, 2023  Init


"""
    openai version:
    VERSION: 0.27.5  (Nov 11)
"""

"""
USE LANGCHAIN FOR NOW
llm_portal.py

check version
print(f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")

REF:
https://github.com/langchain-ai/langchain/blob/master/libs/langchain/langchain/llms/openai.py
"""


## GLOBAL CONFIGS
OPENAI_BAD_QUOTA_ACCOUNTS={}  #account key and time.time()
MAX_OPENAI_RETRIES=2 #5
ASSUMED_OPENAI_GPT4_RATE_LIMIT=10000



## Use singleton pattern to load once
class LazyLoadLLM:
    _instances = {}
    _lock = threading.Lock()

    @classmethod
    def get_instance(cls, model_name='gpt-3.5-turbo'):
        with cls._lock:
            if model_name not in cls._instances:
                cls._instances[model_name] = OpenAILLM(model_name=model_name)
                
                ## Hard code model configs
                #- set to two because should auto retry at application level (possibly gpt-4 or another model)
                #- open PR for runnable retries: https://github.com/langchain-ai/langchain/pull/11309
                cls._instances[model_name].max_retries=2  #Default 6 assuming openaillm https://github.com/langchain-ai/langchain/blob/master/libs/langchain/langchain/llms/openai.py

        return cls._instances[model_name]


class BaseLLM():
    def __init__(self):
        self.model_name=''
        self.library=''
        return

def get_template(template_kind='bank2json'):
    # For newer ChatOpenAI ie gpt-4
    if 'bank2json' in template_kind:
        template = ChatPromptTemplate.from_messages(
            [ SystemMessage(
                    content=(
                        "You transform bank statements information into valid json responses."
                    )
                ), HumanMessagePromptTemplate.from_template("{text}"),
            ])
    elif 'cypher' in template_kind:
        #Jan 16: it seems to be suggesting cypher rather then writting exactly like before.                        "You write cypher queries using given schema information."
        """
        [debug] results: You can use the following Cypher query to count all nodes in the graph:

```cypher
MATCH (n)
RETURN count(n)
```

        """
        template = ChatPromptTemplate.from_messages(
            [ SystemMessage(
                    content=(
                        "You write cypher queries using given schema information."
                    )
                ), HumanMessagePromptTemplate.from_template("{text}"),
            ])
    elif 'no_system' in template_kind:
        print ("[warning] unknown LLM template kind: "+str(template_kind))
        template = ChatPromptTemplate.from_messages(
            [ SystemMessage(
                    content=(
                        ""
                    )
                ), HumanMessagePromptTemplate.from_template("{text}"),
            ])
    else:
        
        print ("[warning] unknown LLM template kind: "+str(template_kind))
        template = ChatPromptTemplate.from_messages(
            [ SystemMessage(
                    content=(
                        ""
                    )
                ), HumanMessagePromptTemplate.from_template("{text}"),
            ])

    return template


class OpenAILLM(BaseLLM):
    """
    OPTION: via langchain
    OPTION: via openai
    """
    global MAX_OPENAI_RETRIES

    def __init__(self,model_name='gpt-3.5-turbo'):
        super().__init__()
        
        self.model_name=self.resolve_model_name(model_name)
        
        self.Accounts=Manage_LLM_Accounts()

        self.refresh_llm(auto_validate=False) #<- model_name

        self.stats={}
        return
    
    def refresh_llm(self,auto_validate=False):
        #-> use set_active_account_bad if haven't already

        ## ACCOUNTS
        Account=self.Accounts.get_next_account(auto_validate=auto_validate) #Slow or always do?

        if 'gpt-3.5' in self.model_name:
            self.MAX_INPUT_TOKENS=4096 #gpt-3.5-turbo
        else:
            self.MAX_INPUT_TOKENS=4096 #gpt-3.5-turbo
            
        ## Prompt template change dependent on model_name
        if 'gpt-3' in self.model_name:
            # https://api.python.langchain.com/en/latest/llms/langchain.llms.openai.OpenAI.html#
            self.llm = OpenAI(model_name=self.model_name, max_retries=MAX_OPENAI_RETRIES,openai_api_key=Account.apikey)
            self.use_template=False
        else:
            # gpt-4 & new api method (chat based)
            # maxRetries??
            # timeout?
            self.llm = ChatOpenAI(model_name=self.model_name, openai_api_key=Account.apikey)
            self.use_template=True

        return
    
    def resolve_model_name(self,given_name):
        ## model_names are not consistent (4.5 is  model_name='gpt-4-1106-preview' #Nov 18, gpt-4.5 turbo )
        model_name=given_name
        
        ## Allow mapping from easy application name to model name
        if given_name=='gpt-4-slow':
            model_name='gpt-4'
        elif given_name=='gpt-4-fast':
            model_name='gpt-4-1106-preview'
        elif given_name=='gpt-3-fast':
            model_name='gpt-3.5-turbo'
        else:
            logging.info("[warning] using non-mapped LLM model name: "+str(model_name))
        return model_name

    def count_tokens(self,prompt):
        return num_tokens_from_string(str(prompt))

    def get_model_version(self):
        vv={}
        vv['model_name']=self.model_name
        vv['library']=self.library
        return vv

    def get_template(self,template_kind='bank2json'):
        ## Migration to ChatOpenAI requires template basis
        ##2/
        return get_template(template_kind=template_kind)

    def _is_cache_custom_valid(self,results):
        ## json loadable
        ## empty?
        # {'all_transactions': []}  #Custom data
        is_valid=True

        if isinstance(results,dict):
            if 'all_transactions' in results:
                if not results['all_transactions']:
                    is_valid=False
        elif str(results)=='{}':
            is_valid=False
        # {'all_transactions': []}  #Custom data
        elif str(results)=='{"all_transactions": []}':
            is_valid=False
        return is_valid

    def prompt(self,prompt,json_validate=False,try_cache=True,verbose=False,template_kind='bank2json'):
        ## Basic prompt
        #- include timeout but possible .method timeout decorator needed
        
        #[ ] add cache: if use_template and not template_kind set properly -- raise (requires system prompt)
        
        reasons=[]

        self.library='langchain.openai'

        # Meta (sent to cache/log)
        meta={}
        meta['model_name']=self.model_name
        meta['library']=self.library
        meta['tokens']=-1

        results={}

        ## Check cache
        if try_cache:
            results=load_cache(prompt,meta)
            ## Do early json validate!
            if json_validate:
                local_valid_json=False
                try:
                    results=json.loads(results)
                    local_valid_json=True
                except:
                    results={}

                ## Cache remove options
                custom_cache_good=self._is_cache_custom_valid(results)
                if not custom_cache_good or not local_valid_json or results=={} or results=="" or results==str(""):
                    #logging.info("[error] INVALID JSON RESPONSE ! removing from cache: "+str(results))
                    #logging.info("^^^ why is this being saved anyways???")
                    remove_cache_entry(prompt,meta)
                    results={}

        if verbose:
            print ("[verbose] prompt hash is: "+str(generate_hash(prompt)))
            if results:
                print ("[verbose] llm has cache response length: "+str(len(results)))
            else:
                print ("[verbose] NO CACHE FOR PROMPT!")

        if results and not str(results)=='{}':
            print ("[debug] loaded response from cache length: "+str(len(results))+" validate json?: "+str(json_validate))
            #THREADED QUIET#  logging.info("[>> "+str(results))  #encode error?

        else: 
            ## Do query
            start_time=time.time()
    
            retries=2
            results={}
            count_loops=0
            while not results and retries:
                count_loops+=1
                retries-=1

                start_time=time.time()
                

                ## NEW MULTIPLE WAYS TO QUERY!

                print ("[debug] recall, 5 retries if timeout...won't throw errror until all 5 tried (Internal to  langchain)")

                try:

                    if self.use_template: #gpt-4
                        request_timeout=204
                        print ("[debug] [A] started llm query ["+str(self.model_name)+"]: "+str(datetime.datetime.now())+" timeout: "+str(request_timeout))
                        template=self.get_template(template_kind=template_kind)
                        aimessage=self.llm(template.format_messages(text=prompt),request_timeout=request_timeout)
                        results=aimessage.content
    
                    else:
                        #request_timeout=3*60 #600 frozen? 3 min for single page ok
                        request_timeout=203 #Oct 9
                        print ("[debug] [B] started llm query ["+str(self.model_name)+"]: "+str(datetime.datetime.now())+" timeout: "+str(request_timeout))
                        results=self.llm(prompt, request_timeout=request_timeout) #600 default (gpt-4 may need it)

                except Exception as e:
                    str_e=str(e)

                    #*debug echo all
                    logging.warning("[warning] log llm exception: "+str(e))
                    ## ? GENERIC HANDLER?
                    # Option 1)  Switch openai accounts (.refresh_llm())

                    ## Handle custom LLM (openai) errors
                    
                    ## Throttling throughput
                    if 'exceeded your current quota' in str_e:
                        #** Big problem because related to monthly quota

                        logging.error("[openai quote exceeded]: "+str(e))
                        logging.info("*requires account swapping")
                        self.Accounts.set_active_account_bad(reasons=[str_e])
                        self.refresh_llm()

                    elif 'Rate limit reached' in str(e):  #ie/ Rate limit per minute
                        reasons+=['rate_limit']

                        # Rate limit reached for gpt-4 in organization org-KkEHX0rnegU95X5mmDrqAagQ on tokens_usage_based per min: Limit 10000, Used 9298, Requested 1161. Please try again in 2.754s. Visit https://platform.openai.com/account/rate-limits to learn more.
                        #(extract with findall but don't enforce must be found ([0]))

                        
                        """
                        ERROR MESSAGE 2 (from langchain -- which will backoff and retry)
                        error_code=rate_limit_exceeded error_message='Rate limit reached for gpt-4 in organization org-KkEHX0rnegU95X5mmDrqAagQ on tokens_usage_based per min: Limit 10000, Used 9116, Requested 1239. Please try again in 2.13s. Visit https://platform.openai.com/account/rate-limits to learn more.' error_param=None error_type=tokens_usage_based message='OpenAI API error received' stream_error=False

                        Retrying langchain.chat_models.openai.ChatOpenAI.completion_with_retry.<locals>._completion_with_retry in 4.0 seconds as it raised RateLimitError: Rate limit reached for gpt-4 in organization org-KkEHX0rnegU95X5mmDrqAagQ on tokens_usage_based per min: Limit 10000, Used 9116, Requested 1239. Please try again in 2.13s. Visit https://platform.openai.com/account/rate-limits to learn more..

                        """
                        
                        
                        limit={}
                        limit['models']=re.findall(r'Rate limit reached for (\w+)',str(e))
                        limit['strict']=re.findall(r'Limit (\d+)',str(e))
                        limit['used']=re.findall(r'Used (\d+)',str(e))
                        limit['requested']=re.findall(r'Requested (\d+)',str(e))
                        limit['wait']=re.findall(r'Please try again in ([\d\.]+)',str(e))

                        logging.warning("[rate limit stats]: "+str(limit))
                        
                        ## Wait & back-off  (exponential ideally, but )

                        ## Wait between 2-12 seconds
                        ASSUME_MIN_WAIT=random.randint(2,14)
                        try:
                            requested_wait=int(limit['wait'][0]) *3   #*3 to be safe
                        except:
                            requested_wait=ASSUME_MIN_WAIT
                        wait_time=max(requested_wait,ASSUME_MIN_WAIT)
                        logging.info("[LLM rate limit wait for]: "+str(wait_time)+" seconds")
                        time.sleep(wait_time)
                        if count_loops<5: #Avoid infinite loop
                            retries+=1  #Allow full retry since 3rd party limit (not our fault)

                    elif 'maximum context length' in str(e):
                        reasons+=['query_too_many_tokens']
                        logging.warning ("[llm exception]: QUERY TOO LONG, too many tokens"+str(e))
                        retries=0
                        results={}

                    elif 'auth_subrequest_error' in str(e):
                        logging.warning ("[llm exception]: MAYBE ERROR CODE 502 bad gateway??"+str(e))

                    elif 'Read timed out' in str(e):
                        logging.warning ("[llm exception]: TIMEOUT -- and tried multiple times already: "+str(e))
                        
                    else:
                        logging.warning ("[llm exception]: "+str(e))
                        
                    
                meta['runtime']=time.time()-start_time
                logging.info ("[debug] LLM runtime: "+str(meta['runtime'])+" seconds")

                if meta['runtime']<=1:
                    logging.warning("[LLM] response too fast.  Possibly retry or discard? at: "+str(results))
                    logging.info("[debug] response is: "+str(results))
                    
                if isinstance(results,str): results=results.strip()
                if str(results)==str("") or not results or str(results)=='{}' or str(results)=='[]':
                    results={}
    

            if verbose:
                logging.info("[verbose llm raw result]: "+str(results))

            self.stats=meta
            cache_llm(prompt,results,meta)

        ## json validate option
        #- option to requery
        is_valid_json=False
        if json_validate:
            try:
                results=json.loads(results)
                is_valid_json=True
            except:
                try: #Possible single quotes
                    results = ast.literal_eval(results)
                    if isinstance(results,dict):
                        is_valid_json=True
                except:
                    pass

            ## Top-level adjustment
            #:  The JSON output should be as follows:
            #: Remove beginning characters up to [ or {
            if not is_valid_json:
                results=auto_clean_bad_json(results)
                try:
                    results=json.loads(results)
                    is_valid_json=True
                except:
                    pass


            if not is_valid_json:
                if isinstance(results,dict):
                    pass
                else:
                    try: logging.warning("[error] INVALID JSON RESPONSE (not json loadable): "+str(results))
                    except: pass
            
        #reasons
        return results

    def get_stats(self):
        # most recent stats
        return self.stats

    def TODO_token_length_limit(self):
        return


## Specifically adjust the transaction_description area in the text and escape double quotes so valid json
def clean_field_values(text,field='transaction_description'):
    # Expect transaction_descriptin=".....",    note comma could have " within 
    pattern = r''+str(field)+r'": "(.*?)(?=",)' #expect comma after! otherwise " inside it!
    matches = re.findall(pattern, text)

    for match in matches:
        ##[A] Escape inner double quotes
        escaped_match = match.replace('"', '\\"')

        ##[B] Escape inner slashes (single only)
        escaped_match=re.sub(r'(?<!\\)\\(?!\\)', r'\\\\', escaped_match)

        text = text.replace(field+f'": "{match}"', field+ f'": "{escaped_match}"')
    if not matches:
        logging.info ("[dev] warning no field found to clean: "+str(field))

    return text

def auto_clean_bad_json(blob,verbose=True):
    ### ** recall:  would already have failed at least once
    ## CLEAN LLM OUTPUT FOR json loading
    #* expect json is quoted

    if isinstance(blob,list):
        if len(blob)==1:
            blob=blob[0]
        else:
            blob=str(blob)

    if isinstance(blob,dict):
        return blob
    
    if not isinstance(blob,str):
        logging.warning("[error] blob is not string: "+str(blob))
        blob=str(blob)

    blob=blob.strip() #<-- will fail on non str but ok during dev

    #1//
    # Remove beginning until bracket (ie ignore text at start)
    try: blob=re.sub(r'^.*?([\[\{\`])',r'\1',str(blob),flags=re.DOTALL).strip()
    except: #Could fail for encoding etc, but works in most case
        pass

    #2// if line ends with " expect a comma (even if last line would be ok
    lines=[]
    for liner in re.split(r'\n',blob):
        liner=re.sub(r'\"[\s]{0,5}$','",',liner)
        lines+=[liner]
    blob='\n'.join(lines)

    #3// remove right double quotes:  ”
    blob = blob.replace('“', '\"').replace('”', '\"')

    #5/
    blob=re.sub(r'[\‘\’]',' ',blob)  #

    #6/
    blob=clean_field_values(blob)

    #7  \\" to \"
    blob=re.sub(r'\\\\\"','\\\"',blob)

    #8
    blob=blob
    #8 Remove: ```json from front`
    #8 Remove: ``` from front`
    #8 Remove: ``` from end
    blob= re.sub(r'^```json', '', blob, flags=re.MULTILINE)
    blob= re.sub(r'^```', '', blob, flags=re.MULTILINE)
    blob= re.sub(r'```[ ]*$', '', blob, flags=re.MULTILINE)
    
    #9
    # remove last comma after }
    #ie;         "transaction_date": "2017-04-11",
    #       "section": "",
    #   }
    blob=re.sub(r',(?=\s*[}\]])', '', blob, flags=re.MULTILINE)
    
    #10 custom to transactions where -3,200.00 without quotes throws error
    # Remove commas from "transaction_amount" values
    blob = re.sub(r'("transaction_amount":\s*-?\d+),(\d+\.\d+)', r'\1\2', blob)
    
    #11  swap single to double quotes
    # {'bank_name': 'Wells Fargo'}

    
    blob=blob.strip()

    return blob



def dev_clean_bad_json():
    # re.sub(r'\,[\s]{0,5}$',',"',liner)
    blob="""
    ```json {"all_transactions": [
    {"transaction_description": "Withdrawal -100.00\n\nATM WITHDRAWAL\n\nATM"
                               " 123 MAIN ST\n"
                               "NEW YORK, NY 12345",
     "transaction_amount": -100.0,
     "transaction_date": "2019-12-26",
     "section": "ATM & DEBIT CARD WITHDRAWALS"},
    {"transaction_description": "Check #6510 ~35.00\n\nCHASE BANK\n"
                               "456 PARK AVE\n"
                               "NEW YORK, NY 12345",
    ```
    """
    new_blob=auto_clean_bad_json(blob)
    print ("NEW: "+str(new_blob))
    return


def report_admin_stats():
    meta={}
    meta['is_llm_up']=False
    meta['avg_response_times']=[]
#    https://gptforwork.com/tools/openai-api-and-other-llm-apis-response-time-tracker
    
    ## 
    
    iter_cache()

    return

def test_ask_chat_question():
    LLM=OpenAILLM()
    prompt="Hello, my name is John. What is your name?"

    print ("[query]: "+str(prompt))
    count_tokens=num_tokens_from_string(prompt)
    print ("[token count]: "+str(count_tokens))

    #results=LLM.prompt(prompt)
    results=LLM.prompt(prompt,try_cache=False)
    logging.info("[llm result]: "+str(results))
    return



if __name__=='__main__':
    branches=['dev_clean_bad_json']
    branches=['report_admin_stats']

    branches=['test_ask_chat_question']

    for b in branches:
        globals()[b]()

        
"""
ODD EXCEPTIONS:


Response to one query (rare)
[>> Sorry, I cannot provide the solution as it goes against OpenAI's use case policy

"""