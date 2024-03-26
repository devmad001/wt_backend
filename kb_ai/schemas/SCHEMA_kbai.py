import os
import sys
import codecs
import json
import re

from fastapi import FastAPI

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")

from get_logger import setup_logging
logging=setup_logging()


#0v1# JC  Sep 13, 2023  Init

"""
    KB AI SCHEMA
    - SEE  v_qa/ qa_schema.py for: ONGOING AUDITS, NEW ADDITION VALIDATION ETC.
"""


## NOTES ON SCHEMA CHANGES:
#
# version 1.1
#- remove payment transaction type (want really just deposit or withdrawl) (redundant with transaction method)
# version 1.2
#- add Entity.role = SENDER, RECEIVER, MAIN_ACCOUNT, OTHER

#**recall Entity['id'] is actually case_id-entity_id!!

###
#Sample BankStatement HAS_TRANSACTION -> Transaction
#   MATCH (bs:BankStatement {id: 'case_o3_case_single-2021-12-01-000000373171278-Continuum Chase statement 1278 Dec 2021.pdf'}), (t:Transaction {id: '1740200341Jo'})
#        MERGE (bs)-[r:HAS_TRANSACTION]->(t)
#        ON CREATE SET r.transaction_date = date('2021-12-07')

### ADD
# NOTES ON supeona tracker:
#- [ ] Case
#- [ ] pages per statement?


# version 1.4
#- add PROCESSED_BY PhysicalCash example
#- remove Account
#- prep for visualization + ongoing visualization


#** transaction_method == PROCESSED_BY Entity!

# PROCESSED_BY node types ALSO transaction.transaction_method
#- NOT bank (bank is a facilitator and bank_name in transaction should capture for now)

# version 1.5
# Processor separate from Entity def: atm is Processor NOT entity target

METHODS=['atm', 'wire_transfer', 'check', 'cash', 'book_transfer','fed_wire', 'debit_card', 'credit_card', 'online_payment', 'mobile_payment', 'zelle', 'venmo','other']

# Target is credit_card_account

gold_schema_definition = {
    "version": "1.4",
    "description": "Cover basics of bank account transactions.  Most transaction are between Account.main and Entity (Entity can have account)",
    "nodes": {
        "Transaction": {
            "properties": ["id","transaction_id", "transaction_amount", "transaction_date", "transaction_method", "transaction_type","bank_name","algList","is_cash_involved","is_wire_transfer"],
            "constraints": ["UNIQUE(transaction_id)"],
            "examples": {
                "bank_name": ["JP Morgan","Chase"],
                "transaction_type": ["withdrawal", "deposit", "payment","purchase","loan_disbursement", "loan_repayment", "transfer", "reversal", "refund", "fee", "interest_received", "interest_paid", "other"],
                "transaction_method": METHODS,
                "transaction_method_id": ["2345 (Check #)", "0433333 (Zelle #)","unknown"],
                "is_cash_involved": [True],
                "is_wire_transfer": [False],
                "algList": ['create_ERS']
            },
            "notes": {
                "bank_name": ["Bank name is a facilitator and want to query against (ideally node) here for now."],
            }
        },
        "Entity": {
            "properties": ["entity_id", "type", "name", "associated_account_id","bank_name","role","location"],
            "constraints": ["UNIQUE(entity_id)"],
            "examples": {
                "entity_id": ["Merchant name","Account number"],
                "type": ["main_account","individual", "cash", "bank","merchant", "vendor", "account", "online", "organization","credit_card_account","other"],
                "role": ["SENDER","RECEIVER","MAIN_ACCOUNT","OTHER"]
            },
            "notes": {
                "accounts": ["Entity is essentially an Account"],
            }

        },
        "Processor": {
            "notes": {
                "PROCESSED_BY": ["Not strictly a account Entity but a processor of the transaction"],
            },
            "properties": ["entity_id", "type", "name", "role","location"],
            "constraints": ["UNIQUE(entity_id)"],
            "examples": {
                "entity_id": ["Check id"],
                "type": METHODS,
            }
        },
        "BankStatement": {
          "properties": ["primary_account_number", "date"],
          "constraints": ["UNIQUE(primary_account_number)"],
        }
    },
    "relationships": {
        "DEBITED_FROM": {
            "start_node": "Entityt",
            "end_node": "Transaction",
            "properties": ["amount", "timestamp", "method"]
        },
        "CREDITED_TO": {
            "start_node": "Transaction",
            "end_node": "Entity",
            "properties": ["amount", "timestamp"]
        },

        "PROCESSED_BY": {
            "start_node": "Transaction",
            "end_node": "Processor",
            "properties": ["timestamp", "transaction_id","desc"],
            "examples": {
                "desc": ["transaction_method list is processed by!","ATM deposit","Cash from Terry is PROCESSE_BY PhysicalCash entity"]
            }
        }
    }
}



## PROPERTY MAPPING
#- these are incremental LLM markup attributes:

schema_extractions = {

    ## TRANSACTION TYPE
    "transaction_type": "DEPOSIT",
    "transaction_type": "WIDTHDRAWL",

    ## ENTITY NAME + TYPE
    ## [source] -> [transaction] -> [target]
    "sender_entity_name": "Entity.name",
    "sender_entity_type": "Entity.type",
        "sender_entity_id": "Entity.entity_id",

    "receiver_entity_name": "Entity.name",
    "receiver_entity_type": "Entity.type",
        "receiver_entity_id": "Entity.entity_id",

    ## MISC
    "is_sender_main_account": True,
    "is_receiver_main_account": False,

}

## EXTRA CLASSIFICATIONS: (30qs- > 50qs)
#- is_cash (transaction on output?  Sine could be cheque written to cash
#- (16)                                     [check      ] has id [check_id]
#- (29)  Zelle with payment id 
#- (32)  Is Entity an Account, AccountType=loan
#- (43)  Transaction, Target Entity is_type [credit card] has id [credit_card_number]
#- (44)  MainAccount --> Debit cards
#- (40)  Transaction {property} location


"""

30 question additions to base schema

SCHEMA/Data properties:

BankStatement.primary_account_holder='name'

Entity.location=''                #GPS tracking or extra node
Account.start_date=''
Account.beginning_balance=''

Transaction.check_number=''       #per 30q
Transaction.zelle_id=''           #per 30q 
Transaction.zelle_payment_id=''   #per 30q


SCHEMA ADDITIONS:
[x]  transaction_type='book'
[x]  fed_wire transaction method (per 30qs)

"""


"""
JON ASSUMPTION:

1)  Bank name is important so keep at top level entity  (Q26)

On treating target accounts as Entity nodes:
    - simplify transactions go to Entity where Entity is a merchant or individual or account
    - later can move account in place of entity if appropriate.
    - see associated_account_id as a poiner to the Account id

"Entity"
-> Tim (person) is an Entity.type = "individual"

"""


"""
SAMPLE ENTRY ::
// Your account is debited
(yourAccount:Account {accountID: "A1"})-[:DEBIT_TRANSACTION {amount: 100, timestamp: "2023-01-01"}]->(tx:Transaction {transactionID: "T1", description: "Zelle to Tim"})
// Tim is credited
(tx)-[:CREDIT_TRANSACTION {amount: 100, timestamp: "2023-01-01"}]->(tim:Entity {name: "Tim"})
"""

def generate_cypher_from_schema(schema):
    cypher_queries = []

    # Generate nodes
    for node, attributes in schema['nodes'].items():
        for constraint in attributes.get("constraints", []):
            if "UNIQUE" in constraint:
                property_name = constraint.split("(")[1].split(")")[0]
                query = f"CREATE CONSTRAINT ON (n:{node}) ASSERT n.{property_name} IS UNIQUE"
                cypher_queries.append(query)

    # (Additional code can be written for relationships, indexes, etc.)

    return cypher_queries


def dev1():
    print(generate_cypher_from_schema(schema_definition))
    return

if __name__=='__main__':
    branches=['dev1']
    for b in branches:
        globals()[b]()

"""
"""
