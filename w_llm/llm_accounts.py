import time
import os
import sys
import codecs
import copy
import json
import re
import datetime

import configparser as ConfigParser

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)

sys.path.insert(0,LOCAL_PATH+"..")

from get_logger import setup_logging

from w_admin.load_credentials import get_creds
from w_storage.ystorage.ystorage_handler import Storage_Helper

from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate, PromptTemplate
from langchain.prompts.chat import SystemMessage


logging=setup_logging()


#0v1# JC  Jan 15, 2024  Stand-alone


"""
    MANAGE LLM ACCOUNTS
    - includes local prompt test
"""

OPENAI_CONFIG_FILE=LOCAL_PATH+"../w_admin/openai.ini"
if not os.path.exists(OPENAI_CONFIG_FILE):
    raise Exception("Missing config file: "+OPENAI_CONFIG_FILE)

## OPENAI ACCOUNTS
# future options:  allow multi-threaded use (so consider locks on use)

def interface_get_valid_openai_key(auto_validate=False):
    #** make efficient as required
    start_time=time.time()
    AM=Manage_LLM_Accounts()
    Account=AM.get_next_account(auto_validate=auto_validate)
    logging.info("[debug] getting openai api key validated took: "+str(time.time()-start_time)+" seconds")
    return Account.apikey


## Track individual account statistics:
#- rate limits
#- usage (total, per day, per month)
#- quota
class LLM_Account:
    def __init__(self,service,email,apikey):
        self.service=service
        self.email=email
        self.apikey=apikey
        self.issues=[]
        self.id=apikey
        return
    
    def __eq__(self,other):
        if not other: return False
        if self.id==other.id:
            return True
        else:
            return False
    
    def get_key(self):
        return self.apikey
    
    def account_limited(self,reasons):
        ## Track time and reasons
        ii={}
        ii['reasons']=reasons
        ii['date']=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")    
        self.issues.append(ii)
        return


class Manage_LLM_Accounts:

    def __init__(self):
        self.accounts=[]
        self.load_accounts()
        self.active_id=None

#        self.account_index=0
#        self.account=None
#        self.account_lock=threading.Lock()
        return
    
    def set_active_account_bad(self,reasons):
        #** doesn't really impact but may be useful for future
        for Account in self.iter_accounts():
            if Account.id==self.active_id:
                Account.account_limited(reasons=reasons)
                break
    
    def load_accounts(self):
        #; auto_validate:  if False it will use first account by default

        #/w_admin/openai.ini
        #ASSUME NAMING: email, email2, email3...

        service='openai'
        Config = ConfigParser.ConfigParser()
        if service=='openai':
            Config.read(OPENAI_CONFIG_FILE)
        else:
            raise Exception("Unknown service: "+service)
        
        ## Dummy check
        #email=Config.get(section,'email1')
        try:
            email=Config.get(service,'email1')
            raise Exception("Bad config file: "+service)
        except: pass #OK
        
        ptr=0
        for section in Config.sections():
#        for section in [service]:
            if section==service:
                email='default'
                while email or email=='default':
                    ptr+=1
                    if ptr==1:
                        email=Config.get(section,'email')
                        apikey=Config.get(section,'apikey')
                    else:
                        try:
                            email=Config.get(section,'email'+str(ptr))
                        except:
                            break #Done
                        apikey=Config.get(section,'apikey'+str(ptr))
                    
                    if email:
                        Account=LLM_Account(service=service,email=email,apikey=apikey)
                        self.accounts.append(Account)

        logging.info("[info] loaded "+str(len(self.accounts))+" "+service+" accounts")
        if not self.accounts:
            raise Exception("No llm accounts loaded expected: "+OPENAI_CONFIG_FILE)
        return
    
    def iter_accounts(self):
        for AA in self.accounts:
            yield AA
        return
    
    def get_next_account(self,current_account=None,auto_validate=False):
        # Generic reasons
        #[ ] future support threads
        #[ ] Account may be marked (in memomry) as limited but may try again here if valid
        
        if auto_validate: stopp=chyy

        ASSUME_FAIL_IF_NO_GOOD_ACCOUNTS=True

        good_account=None
        good_that_isnt_current=None #[ ] 
        
        ## Auto check
        for Account in self.iter_accounts():
            ## Default first if no validation
            if not auto_validate:
                good_account=Account
                break
            
            #if 'watchtower' in Account.email: continue
            ## CHECK ACCOUNTS
            logging.info("[info] checking account: "+Account.email+" auto validate: "+str(auto_validate))
            is_account_active,reasons=local_try_account(Account)

            if not is_account_active:
                logging.info("[warning] bad account: "+Account.email+" reasons: "+str(reasons))
                Account.account_limited(reasons=reasons)
            else:
                good_account=Account
                
            ## Exit if
            if good_account and good_account==current_account:
                continue #Try for more otherwise will default to good
            elif good_account:
                break
            
        if ASSUME_FAIL_IF_NO_GOOD_ACCOUNTS and not good_account:
            raise Exception("No good accounts found")

        if good_account:
            self.active_id=good_account.id
        return good_account


def local_get_template(template_kind='bank2json'):
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
        template = ChatPromptTemplate.from_messages(
            [ SystemMessage(
                    content=(
                        "You write cypher queries using given schema information."
                    )
                ), HumanMessagePromptTemplate.from_template("{text}"),
            ])
    else:
        template = ChatPromptTemplate.from_messages(
            [ SystemMessage(
                    content=(
                        ""
                    )
                ), HumanMessagePromptTemplate.from_template("{text}"),
            ])
    return template


def local_try_account(Account):
    ##[ ] upgrade to more efficient way
    reasons=[]
    start_time=time.time()
    is_account_active=False

    prompt=("How do I count all nodes?")
    template_kind='bank2json'
    template_kind='generic'  #|| no_system
    template_kind='cypher'

    model_name='gpt-3.5' #No template #<-- not possible with ChatOpenAI
    model_name='gpt-4'   #   template

    llm_model=ChatOpenAI(model_name=model_name, openai_api_key=Account.get_key())
    
    ## Jon debug cypher etc.
    template=local_get_template(template_kind=template_kind)
    
    try:
        aimessage=llm_model(template.format_messages(text=prompt))
    except Exception as e:
        str_e=str(e)
        if 'exceeded your current quota' in str_e:
            reasons+=['quota_exceeded']
        else:
            reasons+=[str_e]

    results=aimessage.content

#D    print ("[debug] results: "+str(results))
    if results:
        is_account_active=True
    else:
        reasons+=['no_results']
          
    logging.info("[debug] checking llm took: "+str(time.time()-start_time)+" seconds")
    return is_account_active,reasons


def dev_openai_accounts():

    ## INIT ACCOUNTS
    AA=Manage_LLM_Accounts()
    
    b=['get next good']
    b=['manual check']
    
    if 'manual check' in b:
        ## CHECK ACCOUNTS [ ]
        for Account in AA.iter_accounts():
#            if 'watchtower' in Account.email: continue
            
            ## CHECK ACCOUNTS
            logging.info("[info] checking account: "+Account.email)
            is_account_active,reasons=local_try_account(Account)
            if not is_account_active:
                Account.account_limited(reasons=reasons)
            break
        
    if 'get next good' in b:
        ## GET NEXT GOOD
        # [ ] future support threads
        Account=AA.get_next_account()
        logging.info("[info] using account: "+Account.email)

    return




if __name__=='__main__':
    branches=['play_chattemplate']
    branches=['dev_openai_accounts']

    for b in branches:
        globals()[b]()






