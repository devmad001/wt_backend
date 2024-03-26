import os
import sys
import codecs
import json
import re
import ast
import random

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")

from w_storage.gstorage.gneo4j import Neo
from w_llm.llm_interfaces import OpenAILLM

from a_query.cypher_helper import cypher_create_update_node
from a_query.cypher_helper import cypher_create_relationship
from a_query.cypher_helper import cypher_add_create_relationship


from get_logger import setup_logging
logging=setup_logging()


#0v1# JC  Sep  9, 2023  Init


def general_cypher():
    ## [ ] create unique constraint on transaction node
    # CREATE CONSTRAINT unique_transaction_id ON (t:Transaction) ASSERT t.transaction_id IS UNIQUE
    return

def do_transactions2cypher(transactions,case_id='case_2',statement_id='debug_statement_id_1',filename='',filename_page_num='',verbose=True):
    ## NOTES:
    #- use as model for gold_KB_test_cases creation of test transactions

    ## {'all_transactions':[]}
    #> extra fields just required for transaction meta: statement_id, filename, filename_page_num

    ## SCHEMA:
    #- transactions as nodes
    """
    CREATE (account:Account {name: 'MyAccount', balance: 10000})
    CREATE (recipient:Account {name: 'Melissa', balance: 5000})
    CREATE (transaction:Transaction {description: 'Zelle to Melissa', amount: 1000, date: '2023-09-09'})
    CREATE (account)-[:DEBIT {amount: 1000}]->(transaction)
    CREATE (transaction)-[:CREDIT {amount: 1000}]->(recipient)
    """

    cyphers_as_list=[]
    cypher=""

    ## Top check givens
    if not 'all_transactions' in transactions or not transactions:
        logging.warning("[do_cypher] Bad transaction format or empty: "+str(transactions))
        return cypher,[],{}
        #raise Exception("[do_cypher] Bad transaction format found: "+str(transactions))

    c=0
    for entry in transactions['all_transactions']:
        c+=1
        
        if not entry.get('id',''):
            raise Exception("[do_cypher] Missing transaction id: "+str(entry))

        ## VALIDATION
        #- transaction_amount?
        is_entry_valid=True
        #if not entry.get('payer_id',''): is_entry_valid=False
        #if not entry.get('receiver_id',''): is_entry_valid=False

        if not is_entry_valid:
            logging.warning("[do_cypher] Skipping invalid entry: %s"%entry)
            raise Exception("[do_cypher] Skipping invalid entry: %s"%entry)
            continue

        ## Transaction
        #**watch transaction_id
        transaction_label='Transaction'
        transaction={}

        transaction.update(entry)  ## Include all even if ie payer_id is redudant
#mv alg_resolve_transaction_id#        transaction['id']=alg_generate_transaction_id(entry)
        transaction['case_id']=case_id

        ## Extra meta
        transaction['statement_id']=statement_id
        transaction['filename']=filename
        transaction['filename_page_num']=filename_page_num


        ## APPEND CYPHER CREATE NODES
        #cypher+=cypher_create_node(transaction_label,transaction,node_var='transaction'+str(c))
        this_cypher=cypher_create_update_node(transaction_label,transaction,unique_property='id',node_var='transaction'+str(c))

        cypher+=this_cypher
        cyphers_as_list=[this_cypher]

        #print ("CYPHER: ")
        #print (cypher)

#D#        print ('[debug] break at one cypher block')

        cypher+="\n" #Block space

    return cypher,cyphers_as_list,{}

def do_cypher_link_transactions_to_BankStatement(transactions,statement_id):
    ## USE IDS
    tx=''
    for entry in transactions.get('all_transactions',[]):

        transaction_id=entry['id']
#        statement_id=entry['statement_id'] #Early dup
        date_str=entry.get('transaction_date','')
        
        #From node:  BankStatement.id=statement_id
        #To node:    Transaction.id=transaction_id
        #rel type:  HAS_TRANSACTION
        
        if date_str:
            stmt = """
            MATCH (bs:BankStatement {id: '""" + statement_id + """'}), (t:Transaction {id: '""" + transaction_id + """'})
            MERGE (bs)-[r:HAS_TRANSACTION]->(t)
            ON CREATE SET r.transaction_date = date('""" + date_str + """')
            """
        else:
            stmt = """
            MATCH (bs:BankStatement {id: '""" + statement_id + """'}), (t:Transaction {id: '""" + transaction_id + """'})
            MERGE (bs)-[r:HAS_TRANSACTION]->(t)
            """
            logging.dev("[warning] no date for transaction on link to bank statement: "+str(entry))

        print ("LINKING_LINKING: "+str(stmt))
        
        try:
            results,tx=Neo.run_stmt(stmt,tx=tx)
        except Exception as e:
            ## Fails if date not right etc?
            logging.error("[could not add transaction to statement id]: "+str(stmt)+" because: "+str(e))
            logging.dev("[could not add transaction to statement id]: "+str(stmt)+" because: "+str(e))

    return


def call_do_cypher():
    ## Given transactions
    #- easy clean fields
    #- easy add fields
    #- prepare cypher

    return


if __name__=='__main__':
    branches=['call_do_cypher']
    for b in branches:
        globals()[b]()


"""
"""
