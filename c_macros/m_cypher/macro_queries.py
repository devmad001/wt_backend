import os,sys
import time
import re
import json
import copy
import pandas as pd
import datetime
import matplotlib.pyplot as plt

import configparser as ConfigParser

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../../")

from w_utils import similarity_string

from w_storage.gstorage.gneo4j import Neo
from w_chatbot.wt_brains import Bot_Interface

from a_algs.ner_algs.alg_normalize_entity_name import alg_normalize_entity_name

from get_logger import setup_logging
logging=setup_logging()



#0v1# JC  Dec 16, 2023  Migrate from macro_butterfly_waterfalintohis generci


"""
"""

def cypher_query_account_flows(case_id=''):
    ## Return  SENDER (DEBIT_FROM) -> Transaction - (CREDIT_TO) RECEIVER
    # Entity == SENDER/RECEIVER or loosely account
    stmt = f"""
MATCH (DebitEntity:Entity)-[:DEBIT_FROM]->(Transaction:Transaction)-[:CREDIT_TO]->(CreditEntity:Entity)
WHERE
    Transaction.case_id = '{case_id}'
RETURN
    Transaction,DebitEntity,CreditEntity
ORDER BY Transaction.transaction_date
    """
    if not 'ORDER BY' in stmt:
        raise Exception("ORDER BY required because waterfall dates")
    return stmt

def local_iter_run_query(stmt):
    c=0
    #for dd in Neo.iter_stmt(stmt,verbose=True):   #response to dict
    #    yield dd
    data_response,df,tx,meta=Neo.run_stmt_to_normalized(stmt,tx='')
    return data_response
    
def local_ask_question(question,case_id):
    Bot=Bot_Interface()
    Bot.set_case_id(case_id=case_id)
    answer,answer_dict=Bot.handle_bot_query(question)

    print (" answer> "+str(answer_dict))
    print (" answer> "+str(answer))

    return

def get_normalized_name_mapping(df):
    # Step 1: Extract Unique Names
    try:
        unique_names = df['name'].unique() 
    except:
        logging.warning("[warning] no name field at dataframe! (may not be any transactions)")
        unique_names=[]
    # Step 2: Normalize Names
    normalized_names = [alg_normalize_entity_name(name) for name in unique_names]
    # Step 3: Create a Mapping
    name_mapping = dict(zip(unique_names, normalized_names))
    return name_mapping


def alg_get_main_account_names(df=None,entries=[],account_holder_name=''):
    ## MAIN ACCOUNT:  sometimes mentioned by name, sometimes assumed
    ## Recall:
    #i) transaction.is_credit -> Flag to identify if the transaction is a credit or debit TO MAIN ACCOUNT !
    #   - assumes main_account is always involved in transaction!!
    
    ## LOGIC 1:  Entity.name='main_account' then it's main account
    ## LOGIC X (future ACCOUNTS_RESOLUTION):  What about when ie Marner Holdings Ltd. (main account) transfer with main_account??
    #             - how to find main account in this case?? ** this is ACCOUNTS_RESOLUTION (beyond name scope)
    #

    ##>> NEW ACCOUNTS BASED ENTITIES REQUIRED FOR TRACKING  (beyond simply names)
    #*** RESOVLING TO MAIN ACCOUNT REQUIRED
    #*** RESOVLING TO ALL FIRM ACCOUNTS REQUIRED
    
    ###### LOCALLY ASSUME:  Get names, that's it.
    
    ## LOCAL DEFS:
    #a)  main_account:  name of main account
    #b)  most frequently mentioned account:  name of most frequently mentioned account
    #c)  largest size? (usually a magnitude greater)
    #d)  if too few transactions some size assumptions will be invalid
    
    #[ ] watch name normalization! ie Marner Holdings Inc. -> Marner Holdings Inc later on for viewing
    names=[]
    
    freq={}
    amounts={}

    ## Review entries of transactions
    for entry in entries:
        ## By frequency
        freq[entry[0]]=freq.get(entry[0],0)+1
        freq[entry[1]]=freq.get(entry[1],0)+1
        
        ## By amounts
        amounts[entry[0]]=amounts.get(entry[0],0)+entry[2]
        amounts[entry[1]]=amounts.get(entry[1],0)+entry[2]

        if False: #verbose
            if 'Marner Holdings' in str(entry):
                print (" entry> "+str(entry))
            elif 'main_account' in str(entry):
                pass #Skip
            else:
               print (" entry> "+str(entry))
            
    sorted_freqs=sorted(freq.items(),key=lambda x: x[1],reverse=True)
    sorted_amounts=sorted(amounts.items(),key=lambda x: x[1],reverse=True)

    ## Sort print top 10 freq keys
    for k,v in sorted_freqs[:10]:
        print (k,v)
        
    ## Top amounts
    for k,v in sorted_amounts[:10]:
        print (k,v)

    ## Select logic
    
    #a)  main_account by default
    names+=['main_account']
    
    #b)  choose assumed company name by LOGIC:  similarity with statement account name
    #c)  choose assumed company name by LOGIC:  most frequent
    #d)  choose assumed company name by LOGIC:  most transactions
    
    ## APPLY ^^ basic:  go through top down names and choose first > 95%
    found_names=[]
    if account_holder_name:  #from statement
        c=-1
        found=False
        while not found and c<10:
            c+=1
            
            ## Watch length of arrays!
            try:
                name=sorted_freqs[c][0]
            except Exception as e:
                print ("[patch] could not load name")
                name=''
                continue

            if similarity_string(name,account_holder_name)>0.95:
                found_names+=[name]
                found=True
                break
            name=sorted_amounts[c][0]
            if similarity_string(name,account_holder_name)>0.95:
                found_names+=[name]
                found_names+=[name]
                found=True
                break
            
        found_names=list(set(found_names))
        
    # Actual names
    names+=found_names
    
    # account_holder_name
    names+=[account_holder_name]
    
    ## Finally, translate names into normalized names (aka cleaner more for view but applies here)
    names_normalized=[alg_normalize_entity_name(name) for name in names]
    
    names+=names_normalized

    names=list(set(names))

    return names


def alg_get_statement_nodes(case_id=''):
    records=[]
    for record in alg_get_statement_node(case_id=case_id,all_statements=True):
        #record['id'] must be unique!!
        records+=[record]
    return records

def alg_get_statement_node(case_id='',statement_id='',all_statements=False):
    ## ORDER BY date so can grab proper opening balance from EARLIEST statement

    ## Account name
        #MATCH (BankStatement:BankStatement)
        #MATCH (Statement:Statement {id: '{statement_id}'})
    if statement_id:
        print ("[warning] possible date cause statement id elsewhere so return by case?!")
        raise Exception("statement_id nuance")

        stmt="""
            MATCH (BankStatement:BankStatement {id: '"""+statement_id+"""'})
            RETURN BankStatement
            ORDER BY BankStatement.statement_date
            """
    elif case_id:
        #[ ] limit 1
        stmt="""
            MATCH (BankStatement:BankStatement {case_id: '"""+case_id+"""'})
            RETURN BankStatement
            ORDER BY BankStatement.statement_date
            """
    else:
        raise Exception("case_id or statement_id required")

    print ("[debug] running: "+str(stmt))
    records=[]
    record={}
    for record in local_iter_run_query(stmt):
        if all_statements:
            records+=[record]
        else:
            break
        
    if all_statements:
        return records
    else:
        return record


#[ ] move this to general
def alg_get_account_holder_name(case_id):
    ## Check statement details
    account_holder_name=''
    statement=alg_get_statement_node(case_id=case_id)
    if statement:
        if 'account_holder_name' in statement['BankStatement']:
            account_holder_name=statement['BankStatement']['account_holder_name']
    return account_holder_name

#[ ] move this to general
def alg_resolve_opening_balance(case_id=''):
    ## Not merely tied to 1 statement
    assumed_opening_balance=0
    statement=alg_get_statement_node(case_id=case_id)
    if statement:
        print ("Y: "+str(statement))
        if 'opening_balance' in statement['BankStatement']:
            assumed_opening_balance=statement['BankStatement']['opening_balance']
    return assumed_opening_balance

#[ ] move this to general
def alg_resolve_main_account_NAMES(case_id=''):
    ## [ ] cached!!
    #[ ] ideally have pre-found
    #[ ] 2nd ideally use cypher to find largest
    
    ## 1/
    account_holder_name=alg_get_account_holder_name(case_id=case_id)

    ## 2/ Load active transactions
    stmt=cypher_query_account_flows(case_id=case_id)
    entries=[]
    for record in local_iter_run_query(stmt):
#D        print ("TR: "+str(record['Transaction']))

        name_debit=record['DebitEntity']['name']
        name_credit=record['CreditEntity']['name']
        amount=abs(record['Transaction']['transaction_amount'])
        entries+=[(name_debit,name_credit,amount)]

    ## 3/
    names=alg_get_main_account_names(entries=entries,account_holder_name=account_holder_name)
    
    return names

def call_alg_resolve_main_account_NAMES(case_id=''):
    case_id='MarnerHoldingsB'
    names=alg_resolve_main_account_NAMES(case_id=case_id)
    return


def dev2():
    return

if __name__=='__main__':
    branches=['dev2']
    for b in branches:
        globals()[b]()
    

