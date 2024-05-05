import os
import sys
import codecs
import time
import json
import re
import ast
import random

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")

from w_storage.gstorage.gneo4j import Neo


from get_logger import setup_logging
logging=setup_logging()


#                       MOVED TO markup_alg_cypher_EASY_CREDIT_DEBIT
#0v2# JC  Oct 31, 2023  Update to transaction.is_credit during cypher markup
#0v1# JC  Oct 27, 2023  Init

"""
    Classify Debit or Credit
    - For excel debit or credit
    - For main timeline debit or credit

    NOTE:
    - ideally already done (meta should exist)
    - but D & C in relation to MAIN account (which isn't always obvious)
    
    - Current:  in excel (assumptions there)

"""


def resolve_debit_credit_main_account(n,entity_sender,entity_receiver,verbose=False):
    #0v2#  Oct 27:  migrate from v_questions (excel) to general usage

    ## FOR MAIN ACCOUNT

    ## Logic tree
    is_credit=[]
    is_debit=[]
    
    is_credit_plus=[]
    is_debit_plus=[]

    #(i)   mostly expect main_account to be in sender or receiver
    if 'main_account' in str(entity_sender): is_debit+=['entity']
    if 'main_account' in str(entity_receiver): is_credit+=['entity']

    #(ii)  otherwise infer vs section
    ## SECTION: Deposit and Addition
    if 'section' in n:
        if re.search(r'deposit',n['section'],re.IGNORECASE): is_credit+=['section']
        if re.search(r'credit',n['section'],re.IGNORECASE): is_credit+=['section']

        if re.search(r'withdraw',n['section'],re.IGNORECASE): is_debit+=['section']
        if re.search(r'paid',n['section'],re.IGNORECASE): is_debit+=['section']
    

    #(iii)  otherwise infer vs transaction type (withdrawl or deposit)
    ## transaction type
    # 'transaction_type': 'refund',
    if re.search(r'refund',n.get('transaction_type',''),re.IGNORECASE): is_credit+=['type']
    if re.search(r'deposit',n.get('transaction_type',''),re.IGNORECASE): is_credit+=['type']
    if re.search(r'withdraw',n.get('transaction_type',''),re.IGNORECASE): is_debit+=['type']

    #** extra for ties
    if re.search(r'deposit',n.get('transaction_description',''),re.IGNORECASE): is_credit_plus+=['description']
    if re.search(r'withdraw',n.get('transaction_description',''),re.IGNORECASE): is_debit_plus+=['description']
    
    credit=False
    debit=False
    if len(is_credit)>len(is_debit):
        credit=True
        debit=False
    elif len(is_credit)==len(is_debit):
        ## SPECIAL CASE LOGIC
        if re.search(r'fee',n['transaction_description'],flags=re.I):
            debit=True
            credit=False
            
        ## Check for tie breakder
        elif len(is_credit_plus) and len(is_credit_plus)>len(is_debit_plus):
            credit=True
            debit=False

        elif len(is_debit_plus) and len(is_debit_plus)>len(is_credit_plus):
            credit=False
            debit=True

        else:
            pass
            if False:
                print ("******** BEWARE THINK BOTH SENDER AND RECEIVER?")
                print ("AT: "+str(n))
                print ("AT send: "+str(entity_sender))
                print ("AT receive: "+str(entity_receiver))
                print ("[debug] credit cause: "+str(is_credit))
                print ("[debug] debit cause: "+str(is_debit))
                logging.warning("[error] debit/credit is both sender and receiver at: "+str(n))
    else:
        credit=False
        debit=True
        
    if verbose:
        if is_credit: print ("[debug] credit cause: "+str(is_credit))
        if is_debit: print ("[debug] debit cause: "+str(is_debit))

    return credit,debit,n['transaction_amount']


def alg_resolve_via_transaction_fields(tt,verbose=False):
    ### Recall, formalizes in terms of main account
    ## markup_alg_cypher_EASY_CREDIT_DEBIT.py
    
    credit=False
    debit=False
    if tt.get('is_credit',False):
        credit=True
        debit=False
    else:
        credit=False
        debit=True

    ## JC: single patch -- assume correct section
    if tt.get('section','')=='ELECTRONIC WITHDRAWALS':
        credit=False
        debit=True

    print ("CREDIT: "+str(credit)+" at: "+str(tt))  #*** DONE AT is_credit original classifier
    return credit,debit

    return credit,debit

def resolve_debit_credit_main_account_v2(tt,verbose=False):
    ## Should be same logic but apply to timeline or just know transaction is possible?
    #tt:  transaction record only

    is_credit,is_debit=alg_resolve_via_transaction_fields(tt,verbose=verbose)

    if verbose:
        print ("===>  "+str(tt))
        print ("is credit ^^===>  "+str(is_credit))
        print ("is debit ^^===>  "+str(is_debit))
        
    if not is_credit:
        if not is_debit:
            raise Exception("NO DEBIT OR CREDIT: "+str(tt))

    return is_credit,is_debit


def local_cypher_transactions(case_id=''):
    global Neo
    #** via z_apiengine/services/timeline_service

    stmt="""
    MATCH (t:Transaction)
    WHERE t.case_id='"""+str(case_id)+"""'
    return t
    """
    jsonl,df,tx,meta=Neo.run_stmt_to_normalized(stmt)
    records=[]
    for record in jsonl:
        records.append(record['t'])
    return records
    

if __name__=='__main__':
    branches=['dev_local_try_on_case']
    for b in branches:
        globals()[b]()


"""
"""
