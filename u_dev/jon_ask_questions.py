import os
import sys
import time
import codecs
import json
import re

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")

from w_storage.gstorage.gneo4j import Neo

#from a_agent.RUN_sim_wt import call_normal_full_run
#from a_agent.sim_wt import wt_main_pipeline
#
#from a_query.queryset1 import query_statements
#from a_query.queryset1 import query_transaction
#from a_query.queryset1 import query_transactions
#from a_query.admin_query import admin_remove_case_from_kb

from w_chatbot.wt_brains import Bot_Interface


from get_logger import setup_logging
logging=setup_logging()


#0v1# JC  Oct 11, 2023  Init

"""
    DEV entry for asking specific questions
"""


def dev1():
    print ("messy here but use std interfaces")
    case_id='case_atm_location'
    case_id='case_wells_fargo_small'

    Bot=Bot_Interface()
    Bot.set_case_id(case_id)
    
    #[x]# question='How many transactions are there?'
    #[ ok but long dup list ]#  question='What is the account number?' #[ ] possibly group
    #question='What is the total of cash transactions?'  ok but required sample
    #question='What are the dates and amounts of cash transactions?'
    #question='Where are the ATMs?'
#    question="What is the total deposits and additions grouped by month?"
#    question="What is the total deposits and additions for the Month?" #[x] was assuming specific time value
#    question="What is the total deposits and additions for the Month?" #[x] was assuming specific time value
    #question="What is the total deposits and additions for the quarter?"
    #question="What is the total deposits and additions for the day?"
    #[x] remove company from suggestion cause its' orgnization [x] question='List of all companies where monies were sent and received?'
    
    if False:
        print ("Jon needs to review these cause in Wells Fargo where are credit payments??")
        question="The total number of outflows via credit card payments?"
    
#    question='Total number if inflows from Zelle?' #q is out but in sample only
    
    # No, 'for the time period should assume for all dates'
    question='List top 10 payees for time-period with totals for each'


    print ("[asking]: ",question)
    answer,answer_dict=Bot.handle_bot_query(question)
    print ("[asking]: ",question)
    print ("[answer]: ",answer)

    return


if __name__=='__main__':
    branches=['dev1']
    for b in branches:
        globals()[b]()


"""
[A] "For the month?" don't guess on month. do it group by month
What is the total deposits and additions for the Month?
[write cypher now prompting LLM4...
[debug] started llm query [gpt-4]: 2023-10-14 11:01:51.143441 timeout: 204
[debug] LLM runtime: 6.023916959762573 seconds
[AI] cypher (to execute):
MATCH (Transaction:Transaction {case_id: 'case_wells_fargo_small', transaction_type: 'deposit'})
WHERE Transaction.transaction_date >= '2022-01-01' AND Transaction.transaction_date <= '2022-01-31'
RETURN sum(Transaction.transaction_amount) as total_deposits_and_additions_for_the_month


[B]  credit card payment outflows?
MATCH (Transaction:Transaction {case_id: 'case_wells_fargo_small', transaction_method: 'credit_card', transaction_type: 'withdrawal'})
RETURN count(Transaction) as total_outflows_via_credit_card_payments

"""



"""
Task:Generate Cypher statement to query a graph database.
Instructions:
Use only the provided relationship types and properties in the schema.
Do not use any other relationship types or properties that are not provided.
- WHERE n.case_id = 'case_atm_location'  property filter MUST be used!
- date fields are formatted: 2021-12-31
Schema:
Node properties are the following:
[{"labels": "Transaction", "properties": [{"property": "transaction_method", "type": "STRING"}, {"property": "filename", "type": "STRING"}, {"property": "transaction_type", "type": "STRING"}, {"property": "account_id", "type": "STRING"}, {"property": "section", "type": "STRING"}, {"property": "transaction_amount", "type": "FLOAT"}, {"property": "transaction_description", "type": "STRING"}, {"property": "versions_metadata", "type": "STRING"}, {"property": "transaction_date", "type": "STRING"}, {"property": "statement_id", "type": "STRING"}, {"property": "filename_page_num", "type": "INTEGER"}, {"property": "case_id", "type": "STRING"}, {"property": "transaction_method_id", "type": "STRING"}, {"property": "account_number", "type": "STRING"}, {"property": "id", "type": "STRING"}, {"property": "label", "type": "STRING"}]}, {"labels": "Entity", "properties": [{"property": "type", "type": "STRING"}, {"property": "account_holder_address", "type": "STRING"}, {"property": "entity_id", "type": "STRING"}, {"property": "role", "type": "STRING"}, {"property": "id", "type": "STRING"}, {"property": "case_id", "type": "STRING"}, {"property": "bank_name", "type": "STRING"}, {"property": "account_holder_name", "type": "STRING"}, {"property": "bank_address", "type": "STRING"}, {"property": "account_number", "type": "STRING"}, {"property": "name", "type": "STRING"}, {"property": "label", "type": "STRING"}]}]
Relationship properties are the following:
[{"type": "DEBIT_FROM", "properties": [{"property": "date", "type": "STRING"}, {"property": "amount", "type": "STRING"}]}, {"type": "CREDIT_TO", "properties": [{"property": "date", "type": "STRING"}, {"property": "amount", "type": "STRING"}]}, {"type": "HAS_TRANSACTION", "properties": [{"property": "transaction_date", "type": "DATE"}]}]
Relationship are the following:
["(:Transaction)-[:CREDIT_TO]->(:Entity)", "(:Entity)-[:DEBIT_FROM]->(:Transaction)"]


Data field samples:
Field: Transaction.transaction_type, samples: withdrawal, book_transfer, deposit, transfer, fee
Field: Transaction.section, samples: Withdrawals and Debits, Checks Paid, Deposits and Credits
Field: Transaction.transaction_method, samples: other, check, book_transfer, cash, debit_card, fed_wire
Field: Transaction.transaction_date, samples: 2021-12-02, 2021-12-13, 2021-12-28
Field: Entity.type, samples: check, bank, organization, account, individual, other, main_account
Field: Entity.account_holder_address, samples: 100 CAMPUS DR STE 200E, FLORHAM PARK NJ 07932, Florham Park NJ 07932-1020 US, 100 CAMPUS DRIVE STE200 E, FLORHAM PARK NJ 07932
Field: Entity.role, samples: SENDER, RECEIVER, MAIN_ACCOUNT
Field: Entity.case_id, samples: case_o1_case_single, case_o3_case_single, demo_a
Field: Entity.account_holder_name, samples: UNITED CALL CENTER SOLUTIONS LLC, United Call Center Solutions LLC
Field: BankStatement.opening_balance, samples: -1,898.43, 119,534.98
Field: BankStatement.closing_balance, samples: 5,661,719.25, 378,489.09

Note: Do not include any explanations or apologies in your responses.
Do not respond to any questions that might ask anything else than for you to construct a Cypher statement.
Do not include any text except the generated Cypher statement.
Use descriptive variable names (Node.id rather then n.id, Transaction rather then t).
If a relationship is not needed, query the node directly.

The question is:
How many transactions are there?
Cypher must include case_id:
{}
"""






