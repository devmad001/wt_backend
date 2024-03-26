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
    INTERNAL QUESTIONS
    - vs 50Q
    - consider exposing these as buttons
    - typical data views is the goal

"""

def execute_question():
    ## Return consumable df
    return

def question_view_case(case_id=''):
    print ("Focus on standardizing responses")
    
    ## (see view_case.py view_case()0)
    
    if True:
        for statement_id in query_statements(case_id=case_id):
            print ("statement id> "+str(statement_id))
            ## Now internally transactions!
            for transaction in query_transactions(statement_id=statement_id):
                print ("="*80)
    
                print ("transaction> "+str(json.dumps(transaction,indent=4)))
                
                ## Query transaction relations
                has_rels=False
                for record_t_relationship_type_related in query_transaction_relations(transaction_id=transaction['id']):
                    has_rels=True
                    pass
    
    return

def dev_data_query(case_id=''):
    for statement_id in query_statements(case_id=case_id):
        for transaction in query_transactions(statement_id=statement_id):
            for dd in dev_query_data_focused(transaction_id=transaction['id']):
                print ("dd> "+str(dd))
    return

def dev1():
    print ("Recall dev_challenges put us here")
    case_id='case_o3_case_single'

    input_dict={}
    input_dict['case_id']=case_id
    
    output_request={}
    output_request['output_format']='list_of_dicts'
    
    #rr=question_view_case(**input_dict)
    #rr=dev_data_query(case_id=case_id)

    return

def question_list_entity_sources():
    case_id='case_o3_case_single'
    #
    stmt="""
    MATCH (s:SENDER)-[:DEBIT_FROM]->(t:TRANSACTION)
    RETURN s.name AS sender_name, t.amount AS transaction_amount
    ORDER BY sender_name, transaction_amount DESC;
    """
    print ("^^ above assumes SENDER but it's an Entity")

    stmt="""
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
    
    print ("{running]: "+str(stmt))
    jsonl,df,tx,meta=Neo.run_stmt_to_normalized(stmt)

    #jsonl=[]
    #for dd in Neo.run_stmt_to_data(stmt):
    #    jsonl+=[dd]
    #    
    #updated Neo# table,meta=graph_to_df(jsonl)
    #updated Neo# print ("table> "+str(table))

    return

def question_full_statement_info():
    
    opts=[]
    opts+=['account number']
    opts+=['account holder name']
    opts+=['account holder address']

    opts+=['credit cards on account']
    opts+=['debit cards on account']

    opts+=['date account opened']

    opts+=['statement opening balance']
    opts+=['statement balances'] #closing or alt or calculate
    
    jon=[]
    jon+=['minimum_opening_balance'] #[ ] create statement node

    return

if __name__=='__main__':
    branches=['dev1']
    branches=['question_list_entity_sources']
    branches=['question_list_entity_sources']

    for b in branches:
        globals()[b]()




"""

"""
