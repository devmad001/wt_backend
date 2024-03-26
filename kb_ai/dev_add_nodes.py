import os
import sys
import codecs
import json
import re

from fastapi import FastAPI

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")

from schemas.SCHEMA_kbai import gold_schema_definition
from get_logger import setup_logging
logging=setup_logging()


#0v1# JC  Sep 20, 2023  Init


"""
    DEV notes for auto adding new nodes
"""



def NOTES_dev_add_entity_node():
    entity_schema=gold_schema_definition['nodes']['Entity']

    print ("[entity_schema] "+str(entity_schema))

    """
    [entity_schema] {'properties': ['entity_id', 'type', 'name', 'associated_account_id', 'bank_name', 'role'], 'constraints': ['UNIQUE(entity_id)'], 'examples': {'type': ['individual', 'bank', 'merchant', 'vendor', 'account', 'organization'], 'role': ['SENDER', 'RECEIVER', 'MAIN_ACCOUNT', 'OTHER']}}
    """

    """
        APPROACH:
        - use transaction meta to infer SENDER and RECEIVER nodes.

        WATCH:
        - watch multiple entities w/ multiple transactions (real or synthetic)

          [1.10]  ATM cash deposit to main account:
            Transaction says:  Cash deposit [ATM]->[MainAccount]
            ENTITIES:
            - a MainAccount
            - an atm (is the transaction_method).  ATM as an entity too possibly DEPOSITED_AT (from transaction to specific ATM)
            - Cash:  From PhysicalCash  (Possibly subset of Account)

"relationships": {
    "DEBITED_FROM": {
        "start_node": "Transaction",
        "end_node": "Entity",  // This will be the Check
        "properties": ["timestamp", "amount"]
    },
    "CREDITED_TO": {
        "start_node": "Transaction",
        "end_node": "Account",   // This will be the MainAccount
        "properties": ["timestamp", "amount"]
    },
    "PROCESSED_BY": {
        "start_node": "Transaction",
        "end_node": "Entity",  // This will be the ATM
        "properties": ["timestamp"]
    }
}

            - [cash]  ([CashAccount] ?)

            Inherently, this means:
                [CashAccount]    ->    [ATM]    ->    [MainAccount]
                        vtransaction_id    transaction_id

          [1.20]  ATM check deposit to main account:
            Transaction says:  Check id deposit at ATM [ATM]->[MainAccount]
            ENTITIES:
            - a physical check
            - an atm
            - a MainAccount

[ ] location properties
- attach to both transaction AND entity ie/ atm

    """

    print ("see:  add_account to transaction in extract_b")
    print (">  keep formal likely via schema def")

    ## IMPACTS VARIOUS SCHEMAS
    #- better to go straight to cypher??

    print ("JC: incremental dict control or complete cypher to llm?")
    #- ultimatly, like before, too hard to modify + validate cypher so do this way for now

    print ("SENDER ENTITY: PhysicalCash")
    print ("RECEIVER ENTITY: MainAccount")
    print ("PROCESSED_BY ENTITY: ATM")
    print ("transaction_method: ATM") #if not then update

    ## Given transaction record relevant fields

    ##>> suggest based on data or page contains

    #1)  sender entity
    #2)  receiver entity

    #2)  processed_by
    #3)  add to transaction meta too like method or that should exist JUST ADDED!


    return



if __name__=='__main__':
    branches=['NOTES_dev_add_entity_node']
    branches=['dev_add_entity_node']

    for b in branches:
        globals()[b]()






"""
"""








