import os
import sys
import time
import datetime
import codecs
import json
import re
import pandas as pd

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")

from w_storage.gstorage.gneo4j import Neo
from w_chatbot.wt_brains import Bot_Interface

from a_query.admin_query import admin_remove_case_from_kb,admin_remove_entity_nodes
from a_agent.sim_wt import wt_main_pipeline
from kb_ai.call_kbai import interface_call_kb_auto_update

from get_logger import setup_logging
logging=setup_logging()


#0v2# JC  Feb  2, 2024  Migrate test approach to stand_alone_functional_tests
#0v1# JC  Oct 12, 2023  Init

"""
    **some good question specifics here but better to use the test approaches standardized into m_formals
    MANUAL REVIEW 50Qs
"""

def local_ask_question(question,Bot):
    answer,answer_dict=Bot.handle_bot_query(question)
    print ("[answer]: ",answer_dict)
    #  fp.write(df.to_string(index=False))
    if 'df' in answer_dict:
        print(answer_dict['df'].to_string(index=False))
        
    print ("[cypher]: "+str(answer_dict.get('cypher','')))
    print ("[asking]: ",question)
    print ("[answer]: ",answer)

    return


def local_remove_all_rerun(case_id):
    print ("> local_remove_all_rerun")
    
    admin_remove_case_from_kb(case_id=case_id)

    options={}
#    options['only_pages']=[2]
#    print ("*** ONLY DOING PAGE: "+str(options))
    manual_skip_caps=[]
    meta=wt_main_pipeline(case_id=case_id,options=options)

    return

def local_run_specific_page(case_id,page_ids,force_algs_to_apply=['add_sender_receiver_nodes']):
    
    ## Call direct kb_auto_update with forced algs to apply:
    
    interface_call_kb_auto_update(case_id,force_update_all=True,force_algs_to_apply=force_algs_to_apply)
    
    if 'standard' in []:
        options={}
        options['only_pages']=page_ids
        options['force_update_all']=True
        manual_skip_caps=[]
        manual_skip_caps=['start_main_processing_pipeline'] # Skip main so only KB
    #    manual_skip_caps=['start_kbai_processing_pipeline'] # Skip main so only KB
        meta=wt_main_pipeline(case_id=case_id,options=options,manual_skip_caps=manual_skip_caps)

    return


def test_kb_queries():
    ## Any adjustments to exceptions noted need to have corresponding tests



    ##########################################################
    ##// Test ensure Payment To comes from main_account
    print ("> 'If Zelle Payment To' in transaction.description then DEbIT_FROM entity name='main_account")
    #MATCH (t:Transaction {case_id: 'case1'})
    stmt="""
    MATCH (t:Transaction)
    WHERE t.description CONTAINS 'Zelle Payment To'
    MATCH (e:Entity)
    WHERE e.name <> 'main_account'
    MERGE (e)-[:DEBIT_FROM]->(t)
    RETURN t,e.name as EntityName
    """

    print ("[1]  Check if zelle payment not from main account.")
    data_response,df,tx,meta=Neo.run_stmt_to_normalized(stmt,tx='')
    if data_response:
        print ("DATA RESPONSE: "+str(data_response))
        raise Exception("Zelle payment to should always come from main account!")

    ##########################################################
    ##// Test watch if main_account is both SENDER and RECEIVER
    stmt_any_same_sender_receivers="""
    MATCH (t:Transaction)-[:DEBIT_FROM]->(e:Entity)
    MATCH (t)-[:CREDIT_TO]->(e2:Entity)
    WHERE e.entity_id = e2.entity_id
    RETURN t, e.entity_id AS sharedEntityID
    """
    print ("Check if any same sender and receiver.")
    data_response,df,tx,meta=Neo.run_stmt_to_normalized(stmt,tx='')
    if data_response:
        print ("DATA RESPONSE: "+str(data_response))
        raise Exception("Beware, same sender and receiver on transaction ^^")

    return

"""
Data field samples:
Field: Transaction.transaction_type, samples: withdrawal, deposit, other, transfer, fee, payment, book_transfer, online_payment, refund, reversal
Field: Transaction.transaction_method, samples: online_payment, other, check, debit_card, atm, zelle, zelle, wire_transfer, cash, book_transfer
Field: Transaction.is_wire_transfer, samples: True
Field: Transaction.is_cash_involved, samples: True
Field: Transaction.check_num, samples: 6164, 6164929912072900524
Field: Entity.account_holder_name, samples: GTA AUTO, INC., SKYVIEW CAPITAL GROUP MANAGEMENT LLC
Field: Entity.account_holder_address, samples: 6829 LANKERSHIM BLVD STE 116, NORTH HOLLYWOOD CA 91605, 125 BEVINGTON LN, WOODSTOCK GA 30188-5421
Field: Entity.type, samples: cash, individual, organization, bank, merchant, check, account, main_account, other, main_account_card
Field: BankStatement.opening_balance, samples: 0.00, 10277.6
Field: BankStatement.closing_balance, samples: 4,680.37, 4784.88
Field: Processor.lat, samples: 34.086756009649, 46.28693384
Field: Processor.type, samples: other, zelle, check, online_payment, wire_transfer, debit_card, book_transfer, cash, atm, fed_wire
Field: Processor.lng, samples: -84.481317021177, 6.099725
Field: Processor.location, samples: 12172 Highway 92, Woodstock, GA, 30188, USA, 01210, Versonnex, Auvergne-Rhône-Alpes, FRA
"""

def auto_redo_markup_for_a_single_transaction(case_id):
    # tid
    #** will help with quick updates!
    #. remove relations and rerun kbai
    
    transaction_id=''
    transaction_id='8a57169329e23deabd962fb37e995b6c2af2a4bdb1c2e7edfe920586b465b212' #card purchase thinks cash?
    
    stmt_remove_relations_from_node="""
    MATCH (n)-[r]-()
    WHERE n.id = 'your_specific_id'
    DELETE r
    """
    data_response,df,tx,meta=Neo.run_stmt_to_normalized(stmt_remove_relations_from_node,tx='')
    if data_response:
        print ("DATA RESPONSE: "+str(data_response))
    
    ## Just for run alg like above rather then specific transaction ?
#        ALL_ALGS_TO_APPLY=[]
#        ALL_ALGS_TO_APPLY+=['transaction_type_method']
#        ALL_ALGS_TO_APPLY+=['add_sender_receiver_nodes']
#        ALL_ALGS_TO_APPLY+=['logical_card_check_numbers']
#        ALL_ALGS_TO_APPLY+=['add_PROCESSED_BY']
    local_run_specific_page(case_id,[],force_algs_to_apply=['add_sender_receiver_nodes'])

    return

def dev_entry():
    case_id='case_Wells Fargo Bank Statement' # 700+ pages?!
    case_id='case_wells_fargo_small'
    case_id='case_atm_location'
    
    b=['do_questions']
    b=['redo_markup_after_removing_relations']
    b=['do_full_rerun']
    b=['local_run_specific_page']
    
    if 'redo_markup_after_removing_relations' in b:
        auto_redo_markup_for_a_single_transaction(case_id)

    if 'do_questions' in b:
        print ("[x] migrated to stand_alone_functional_tests")
        Bot=Bot_Interface()
        Bot.set_case_id(case_id)
        
        #q50+=["What is the beginning monthly balance?"]
        question="What is the beginning monthly balance and date?"
        local_ask_question(question,Bot)
        
    if 'do_full_rerun' in b:
        a=kkksure
        local_remove_all_rerun(case_id)
        
    if 'local_run_specific_page' in b:
        print ("[x] migrated to stand_alone_functional_tests")
        #> Zell Payment To Anthony Bro Jpm679646739
        """
        ALL_ALGS_TO_APPLY=[]
        ALL_ALGS_TO_APPLY+=['transaction_type_method']
        ALL_ALGS_TO_APPLY+=['add_sender_receiver_nodes']
        ALL_ALGS_TO_APPLY+=['logical_card_check_numbers']
        ALL_ALGS_TO_APPLY+=['add_PROCESSED_BY']
        """

        page_ids=[2]
        page_ids=[]
        force_algs_to_apply=['logical_card_check_numbers']
        force_algs_to_apply=['transaction_type_method']

        ALL_ALGS_TO_APPLY=[]
        ALL_ALGS_TO_APPLY+=['transaction_type_method']
        ALL_ALGS_TO_APPLY+=['add_sender_receiver_nodes']
        ALL_ALGS_TO_APPLY+=['logical_card_check_numbers']
        ALL_ALGS_TO_APPLY+=['add_PROCESSED_BY']
        force_algs_to_apply=ALL_ALGS_TO_APPLY

        force_algs_to_apply=['transaction_type_method']

## REDO SEND/RECEIVE
#ok        print ("REMOVING ENTITIES AND ADDING THEM BACK IN!!!")
#ok        force_algs_to_apply=['add_sender_receiver_nodes']
#ok        admin_remove_entity_nodes(case_id=case_id)

        local_run_specific_page(case_id,page_ids=page_ids,force_algs_to_apply=force_algs_to_apply)

    return

def beware_queue():
    beware=[]
    beware+=['Transaction.is_cash_involved will trip on debit card transactions so skip for now']
    beware+=['list all cash withdrawls  <-- NO but list all cash transactions works']
    
    to_mention=[]
    to_mention+=['text refer to owner of account by name is a todo (requires local kb markup or suggestion?)']
    return

def dev_oct17():
    #Go through obvious questions

    case_id='case_atm_location'
    
    #1/  > did suggest the DEBIT_FROM and CREDIT_TO, & rmove Entity.role
    question='list all transaction payees'
    question='list all payees' #no
    # Entity.role not needed for cypher query
    # from cypher_playground.cypher_auto import load_relevant_neo4j_sample
    #  
    
    #2/  main_account verbage allow name of company??  Requires pre-catching local knowledge.
    #-
    
    #3/  zelle transfers.
    question='list all Zelle transfers' #[ ] [got response] ...check values.
    
    #5/  WIre transfer?  May need to hint at:
    #i)  group of wire transfers == Zelle, wire_transfer, etc.
    #ii.) is_wire_transfer (on transaction via add type or method)
    #iii) is cash involved?
    question='list all wire transfers deposits' #[x]

    #4/  cash
    #[x]
    question='list all cash transactions' #[x] have any?? 1.  ok for now
    
    #6/ ok
    # #    question='List all transactions in August'
    
    #X/  debug
#    question='list all transaction methods and descriptions'
#    question='list all transactions that mention the word cash'
#    question='show me the transaction description that contains "Fitness Mania"'
    
    #8/   Give me a list of all Zelle payments to Melissa
    question="Give me a list of all Zelle payments to Melissa" #[x] GREAT example of trying again it goes from name='Melissa' to name contains 'Melissa'

    #9/  Type queries:
    
    ## No...looks for ACH Tranfer method
    question='List out ACH payments'  #Or, is this wire transfer?
    
    ####
    
    #[x] works with sample only::
    question='list all cash transactions' #[x] have any?? 1.  ok for now
    
    #[ ] does not work:
    question='list all cash withdrawls'
    
    #7/   List out all American Express payments 
    print ("[ ] open issue cause returns 3")
    question='List out all American Express payments' #**beware returns 3?  maybe graph needs update?
    

    Bot=Bot_Interface()
    Bot.set_case_id(case_id)
    
#    question="What is the beginning monthly balance and date?"

    local_ask_question(question,Bot)
    
    return
    


def run_specific_query():

    stmt="""
    MATCH (Sender:Entity)-[:DEBIT_FROM]->(Transaction:Transaction)-[:CREDIT_TO]->(Receiver:Entity)
    WHERE Transaction.case_id = 'case_atm_location' AND Transaction.transaction_description CONTAINS 'American Express' AND Sender.case_id = 'case_atm_location' AND Receiver.case_id = 'case_atm_location'
    RETURN Transaction.transaction_amount, Transaction.transaction_date, Transaction.transaction_description, Sender.name, Receiver.name
        """

    stmt="""
    MATCH (Transaction:Transaction)
    WHERE Transaction.case_id = 'case_atm_location'
    AND Transaction.transaction_description CONTAINS 'American Express'
    RETURN Transaction
        """
    stmt="""
    MATCH (Sender:Entity)-[:DEBIT_FROM]->(Transaction:Transaction)-[:CREDIT_TO]->(Receiver:Entity)
    WHERE Transaction.case_id = 'case_atm_location' AND Transaction.transaction_description CONTAINS 'American Express' AND Sender.case_id = 'case_atm_location' AND Receiver.case_id = 'case_atm_location'
    RETURN Transaction.transaction_amount, Transaction.transaction_date, Transaction.transaction_description, Sender.name, Receiver.name
        """
        
    stmt="""
    MATCH (Payor:Entity)-[df:DEBIT_FROM]->(Transaction:Transaction)-[ct:CREDIT_TO]->(Payee:Entity)
    WHERE Transaction.case_id = 'case_atm_location'
    AND Transaction.contains CONTAINS 'American Express'
    RETURN Payor, Transaction, Payee
    """
    stmt="""
    MATCH (Transaction:Transaction)-[ct:CREDIT_TO]->(Payee:Entity)
    WHERE
        Transaction.case_id = 'case_atm_location'
    AND
        (Transaction.contains CONTAINS 'American Express'
        OR
        Payee.name CONTAINS 'AMEX'
        OR
        Payee.name CONTAINS 'American Express'
        )
    RETURN Transaction
    """
    
    stmt="""
    MATCH (Transaction:Transaction {case_id: 'case_atm_location'})-[ct:CREDIT_TO]->(Payee:Entity)
WHERE
    Transaction.transaction_description CONTAINS 'American Express'
    OR
    Payee.name CONTAINS 'AMEX'
    OR
    Payee.name CONTAINS 'American Express'
RETURN Transaction.transaction_amount, Transaction.transaction_date, Payee.name, Transaction.id

    """
    
    stmt="""
     MATCH (Transaction:Transaction {case_id: 'case_atm_location'})-[ct:CREDIT_TO]->(Payee:Entity)
    WHERE Transaction.transaction_method IN ['Zelle'] AND Payee.name CONTAINS 'Melissa'
    RETURN Transaction
    """
    stmt="""
     MATCH (Transaction:Transaction {case_id: 'case_atm_location'})-[ct:CREDIT_TO]->(Payee:Entity)
    WHERE Payee.name CONTAINS 'Melissa'
    RETURN Transaction
    """
    
    stmt="""
      MATCH (Transaction:Transaction {case_id: 'case_atm_location'})-[ct:CREDIT_TO]->(Payee:Entity)
    OPTIONAL MATCH (Transaction)-[:PROCESSED_BY]->(Processor)
    WHERE 
        Payee.name CONTAINS 'Melissa'
        AND (Processor.name CONTAINS 'zelle' OR Processor.name CONTAINS 'Zelle')
    RETURN Transaction, Payee, Processor
    """
    
    stmt="""
      // Cypher for: "Transaction is processed by zelle and sent to Melissa
    MATCH (Transaction:Transaction {case_id: 'case_atm_location'})-[ct:CREDIT_TO]->(Payee:Entity)
    OPTIONAL MATCH (Transaction)-[:PROCESSED_BY]->(Processor)
    WHERE
        Payee.name CONTAINS 'Melissa'
        AND (
            (Processor.name IS NOT NULL AND (Processor.name CONTAINS 'zelle' OR Processor.name CONTAINS 'Zelle'))
            OR Transaction.transaction_method CONTAINS 'zelle'
        )
    RETURN Transaction, Payee, Processor

    """
    
    stmt="""
    MATCH (Transaction:Transaction {case_id: 'case_atm_location'})
    WHERE
    (Transaction)-[:CREDIT_TO]->(:Entity {type: 'cash', case_id: 'case_atm_location'})
    OR (Transaction)-[:DEBIT_FROM]->(:Entity {type: 'cash', case_id: 'case_atm_location'})
    OR Transaction.transaction_method='cash'
    RETURN Transaction
    """

    stmt="""
    MATCH (Transaction:Transaction {case_id: 'case_atm_location'})
    WHERE
    Transaction.transaction_description CONTAINS 'ATM'
    RETURN Transaction
    """
    stmt="""
    MATCH (Transaction:Transaction {case_id: 'case_atm_location'})
OPTIONAL MATCH (Transaction)-[ct:CREDIT_TO|:CREDIT_FROM]->(CreditEntity:Entity {case_id: 'case_atm_location'})
OPTIONAL MATCH (Transaction)-[df:DEBIT_FROM|:DEBIT_TO]->(DebitEntity:Entity {case_id: 'case_atm_location'})
WHERE Transaction.transaction_method='cash'
RETURN Transaction, CreditEntity, DebitEntity
    """
    
    stmt="""
MATCH (Transaction:Transaction {case_id: 'case_atm_location'})
-[rel:CREDIT_TO|DEBIT_FROM]->
(RelatedEntity:Entity {case_id: 'case_atm_location'})
    WHERE Transaction.transaction_description CONTAINS 'ATM'
RETURN Transaction, rel, RelatedEntity

    """
    
    stmt="""
    MATCH (Transaction:Transaction {case_id: 'case_atm_location'})
WHERE
Transaction.transaction_method = 'cash'
OR Transaction.transaction_description CONTAINS 'ATM'
RETURN Transaction
"""

    stmt="""
    MATCH (Transaction:Transaction {case_id: 'case_atm_location'})-[ct:CREDIT_TO]->(Payee:Entity)
WHERE
    Transaction.transaction_description CONTAINS 'American Express'
    OR Payee.name CONTAINS 'American Express'
RETURN Transaction, COLLECT(Payee) AS Payees

    """

    print ("QUERY: "+str(stmt))
    data_response,df,tx,meta=Neo.run_stmt_to_normalized(stmt,tx='')
    for dd in data_response:
        print (" response> "+str(dd))
    return

def dev_oct17b():
    """
     List out ACH payments
     What are the total electronic withdrawals in August
     Give me a list of any cash deposits 
     Show me all ATM & debit card withdrawals

     Give me a list of all cash withdrawls made from this account
    """
    
    case_id='case_atm_location'

    #[x] 1// ok
    question='What are the total electronic withdrawals in August'

    #2/  >> partial since not sure ACH was extracted as a specific type
    question="List out ACH payments"
    question="Show me the transaction description that contains ACH"
    
    #3//
     
    question="Give me a list of all cash withdrawls made from this account"
    question="Give me a list of all cash transactions made with this account"
 

    Bot=Bot_Interface()
    Bot.set_case_id(case_id)
    
#    question="What is the beginning monthly balance and date?"

    local_ask_question(question,Bot)
    
    
    return


def run_specific_queryb():
    print ("QUERY: "+str(stmt))
    data_response,df,tx,meta=Neo.run_stmt_to_normalized(stmt,tx='')
    for dd in data_response:
        print (" response> "+str(dd))
    return

if __name__=='__main__':
    branches=['test_kb_queries']
    
    branches=['dev_entry']
    branches=['run_specific_queryb']
    branches=['dev_oct17b']

    for b in branches:
        globals()[b]()



"""
list all payees
MATCH (Entity:Entity {case_id:'case_atm_location', role:'RECEIVER'})\nRETURN Entity.name as Payees",
but no response?

list all transaction payees
MATCH (Transaction:Transaction {case_id: 'case_atm_location'})-[:CREDIT_TO]->(Entity:Entity)
RETURN Entity.name as transaction_payees


: MATCH (Transaction:Transaction {case_id: 'case_atm_location', transaction_method: 'wire_transfer'})
RETURN Transaction
[asking]:  list all wire transfers
[answer]:  I'm sorry, but I don't have the answer to that question.



"""




