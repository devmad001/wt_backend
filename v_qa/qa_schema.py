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

from kb_ai.schemas.SCHEMA_kbai import gold_schema_definition
from kb_ai.schemas.SCHEMA_graph import GRAPH_SCHEMA, GRAPH_INDEXES #*informally controlled?

from kb_ask.dev_kb_ask import get_graph_schema_str



from get_logger import setup_logging
logging=setup_logging()

#0v1# JC  Sep 29, 2023  Init



def validate_schema():
    return

def active_schema_tracking():
    print ("> GOLD SCHEMA")
    print ("> GRAPH SCHEMA")
    print ("> schema on KB (what nodes or edges or fields to update)")

    return

def dev1():
    print ("> CHECK EXPECTED SCHEMA VS ACTUALS")
    print ("> USE THIS AS CENTRAL POINT FOR SCHEMA CHANGES OR UPDATES")
    return

def filter_relationships(relationships):
    keep_only_rels=[]
    #kb_ask filter for clean #keep_only_rels = ['DEBIT_FROM', 'CREDIT_TO']
    # REGEX  Filtering relationships
    relationships = [rel for rel in relationships if any(re.search(keep_rel, rel) for keep_rel in keep_only_rels)]
    #keep_only_rels += [r'Transaction.*Transaction']  #Invalid in db quick patch

    filter_rels=[r'Transaction.*Transaction']
    filter_rels+=[':Account']
    relationships = [item for item in relationships if not any(re.search(filter_rel, item) for filter_rel in filter_rels)]
    return relationships

def check_graph_schema():
    # Recall a_query, qa_query etc.
    summary=[]
    
    # Recall dump via kb_ask!
    schema_str=get_graph_schema_str()
    print ("SCHEMA STR", schema_str)
    
    schema=Neo.get_schema() # used by schema_str
    print ("RAW: "+str(schema))
    
    node_properties=schema[0]
    relationship_properties=schema[1]
    relationships=schema[2]

    ## LABELS aka node kindes
    labels = [item['labels'] for item in node_properties]
    unique_labels = list(set(labels))
    summary+=["KNOWN LABELS: "+str(unique_labels)]
    
    ## RELATIONSHIPS
    #relationships=filter_relationships(relationships)
    for rel in relationships:
        summary+=["RELATIONSHIP: "+str(rel)]
    
    qchecks=[]
    qchecks+=['check labels in schema']
    qchecks+=['check at sep29']

    if 'check labels in schema' in qchecks:
        print ("CHECKING LABELS IN SCHEMA")
        for label in unique_labels:
            if label not in gold_schema_definition['nodes'].keys():
                print ("WARNING: "+label+" not in GRAPH_SCHEMA['labels']")
            else:
                print ("OK: "+label+" in GRAPH_SCHEMA['labels']")
                
    if 'check at sep29' in qchecks:
        print ("Check known 'frozen' schema for now v 1.3")
        if len(unique_labels) >3:
            print ("WARNING: "+str(len(unique_labels))+" labels found in schema.  Expected 3")


    print ("========= SCHEMA SUMMARY ==========")
    for item in summary:
        print ("[schema]: "+str(item))

    return

def formal_process_add_new_schema_feature():
    #** SEE:
    return

if __name__=='__main__':
    branches=['dev1']
    branches=['check_graph_schema']

    for b in branches:
        globals()[b]()

print (">>> see_w_pipeline__source_schema.py")

"""

gold_schema_definition = {
    "version": "1.3",
    "description": "Cover basics of bank account transactions.  Most transaction are between Account.main and Entity (Entity can have account)",
    "nodes": {
        "Transaction": {
            "properties": ["id","transaction_id", "transaction_amount", "transaction_date", "transaction_method", "transaction_type","algList"],
            "constraints": ["UNIQUE(transaction_id)"],
            "examples": {
                "transaction_type": ["withdrawal", "deposit", "book_transfer","loan_disbursement", "loan_repayment", "transfer", "reversal", "refund", "fee", "interest_received", "interest_paid", "other"],
                "transaction_method": ["ATM", "wire_transfer", "check", "cash", "fed_wire", "debit_card", "credit_card", "online_payment", "mobile_payment", "Zelle", "Venmo","other"],
                "algList": ['create_ERS']
            }
        },
        "Entity": {
            "properties": ["entity_id", "type", "name", "associated_account_id","bank_name","role","location"],
            "constraints": ["UNIQUE(entity_id)"],
            "examples": {
                "entity_id": ["Check id"],
                "type": ["main_account","individual", "bank","merchant", "vendor", "account", "online", "organization","atm","cash","other"],
                "role": ["SENDER","RECEIVER","MAIN_ACCOUNT","OTHER"]
            }
        },
        "Account": {
            "description": "Account is a child of Entity",
            "properties": ["account_id", "account_balance", "account_type"],
            "constraints": ["UNIQUE(account_id)"],
            "examples": {
                "account_type": ["main", "standard", "cash", "savings", "checking", "loan", "credit", "investment", "other"],
                "transaction_method": ["ATM", "wire_transfer", "check", "cash", "debit_card", "credit_card", "online_payment", "mobile_payment", "other"]
            }
        },
        "BankStatement": {
          "properties": ["primary_account_number", "date"],
          "constraints": ["UNIQUE(primary_account_number)"],
        }
    },
    "relationships": {
        "DEBITED_FROM": {
            "start_node": "Account",
            "end_node": "Transaction",
            "properties": ["amount", "timestamp", "method"]
        },
        "CREDITED_TO": {
            "start_node": "Transaction",
            "end_node": "Entity",
            "properties": ["amount", "timestamp"]
        },

        "PROCESSED_BY": {
            "start_node": "Entity",
            "end_node": "Entity",
            "properties": ["timestamp", "transaction_id","desc"],
            "examples": {
                "desc": ["ATM deposit"]
            }
        }
    }
}


"""
