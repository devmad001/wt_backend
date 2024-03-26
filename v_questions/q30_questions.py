import os
import sys
import codecs
import json
import re

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")

from pypher import __, Pypher
from w_storage.gstorage.gneo4j import Neo

from a_agent.RUN_sim_wt import call_normal_full_run
from a_agent.sim_wt import wt_main_pipeline

from a_query.queryset1 import query_statements
from a_query.queryset1 import query_transaction
from a_query.queryset1 import query_transactions
from a_query.queryset1 import query_transaction_relations
from a_query.queryset1 import dev_query_data_focused

from get_logger import setup_logging
logging=setup_logging()


#0v1# JC  Oct  2, 2023  Init

"""
    50 Qs
"""

def q1_list_account_numbers(case_id='',verbose=True):
    ## Account number
    #[x] ok, just watch return format
    #[ ] ideally grab from statement object
    meta={}
    meta['ideally']=['Use Statement node']

    qq="""
    MATCH (t:Transaction)
    WHERE t.case_id = '"""+case_id+"""'
    RETURN DISTINCT t.account_number as account_number
    """
    jsonl,df,tx,meta=Neo.run_stmt_to_normalized(qq)

    return jsonl,df,qq,meta

def q2_beginning_monthly_balance(case_id='',verbose=True):
    ## Possibly multiple statements
    qq = f"""
    MATCH (bs:BankStatement {{case_id: '{case_id}'}})
    WHERE exists(bs.opening_balance) AND exists(bs.statement_date)
    RETURN bs.account_number, bs.statement_date AS statement_date, bs.opening_balance AS opening_balance
    """
    #OK BUT BEWARE IN LARGE DICT#  RETURN bs
    meta={}
    jsonl=[]
    for dd in Neo.run_stmt_to_data(qq):
        jsonl+=[dd]
    df,meta_convert=graph_to_df(jsonl)
    return jsonl,df,qq,meta

def q13_total_inflows(case_id='',verbose=True):
    ## Total inflows (money coming into account)
    #[ ] add to watch internal loan accounts, book transfers
    meta={}
    qq="""
    MATCH (s)-[:DEBIT_FROM]->(t:Transaction)
    WHERE exists(t.transaction_amount) AND exists(s.name)
        AND t.case_id='"""+case_id+"""'
    RETURN
        coalesce(s.name, s.id) AS sender_name,
        t.transaction_amount AS transaction_amount,
        t.transaction_date AS transaction_date
    ORDER BY
        transaction_date ASC;
    """
    
    if verbose:
        print ("{running]: "+str(qq))
    jsonl,df,tx,meta=Neo.run_stmt_to_normalized(qq)
    
    if verbose:
        print ("[q13] inflows")
        print (df)

    return jsonl,df,qq,meta

## NEXT PRIORITIES:
def q25_balance_by_date(case_id='',verbose=True):
    return jsonl,df,qq,meta

def q_flow_by_type(case_id='',verbose=True):
    flow_directions=['inflow','outflow']
    types=['zelle','check','cash','wire','bank fee']
    return

def q_withdrawl_types(case_id='',verbose=True):
    types=['atm','debit_card']
    return

## BEYOND 25
def q25_balance_by_date(ase_id='',verbose=True):
    ## Daily balances
    #- Chase includes at end of document
    #- can map or precalculate at BankStatement node?
    return

# 26-35
def q_entities_involved(case_id='',verbose=True):
    transaction_type=['book_transfer','zelle','fed_wire','companies']
    transaction_type+=['bank','atm','payees','payors']
    return

## BEYOND 35
def q36_mod_1000(case_id='',verbose=True):
    return

def q37_q40_transaction_locations(case_id='',verbose=True):
    return

def q43_list_credit_cards_paid(case_id='',verbose=True):
    ## [ ] sample?
    # is credit?
    # credit_num
    return

def q44_list_accounts_debit_cards(case_id='',verbose=True):
    # is debit?
    return

def q45_q48_transaction_word_search(case_id='',verbose=True):
    return

def q49_cash_withdrawls(case_id='',verbose=True):
    #> 'written to cash' (check?), ATM withdrawls
    return


def dev1():

    q1_10="""
    STATEMENT SPECIFIC:
        [ ] ideally have a statement object HAS_TRANSACTION
        i)   account number
        ii)  beginning balance
        iii) date opened (aka, oldest date)

    - statement.account number, transaction.account number
    
    TRANSACTION SPECIFIC
    - total deposits + additions
    - by date
    """
    
    q1="Get account number from transactions"
    q4_12="debit + credits by date"
    
    case_id='case_o3_case_single'

    ccaall=[]
    ccaall+=['q13_total_inflows'] # inflows
    ccaall+=['q1_list_account_numbers']  # account number
    ccaall=[]
    ccaall+=['q2_beginning_monthly_balance']  # account number
    
    for b in ccaall:
        jsonl,df,qq,meta=globals()[b](case_id=case_id)
        print ("="*30)
        print ("[results to function call]: "+str(b))
        print (df)
    
    return


if __name__=='__main__':
    branches=['dev1']
    for b in branches:
        globals()[b]()




"""

"""
