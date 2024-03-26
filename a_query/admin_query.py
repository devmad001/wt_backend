import os
import sys
import codecs
import json
import re
import time

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")

from w_storage.gstorage.gneo4j import Neo

from get_logger import setup_logging
logging=setup_logging()

#0v1# JC  Sep  6, 2023  Init


def admin_remove_entity_nodes(case_id=''):
    raise Exception("Admin only")
    stmt="""
        MATCH (n)-[r:CREDIT_TO | DEBIT_FROM]->()
        WHERE n.case_id = '"""+case_id+"""'
        DETACH DELETE n
        """
    for dd in Neo.iter_stmt(stmt,verbose=True):   #response to dict
        print (" response> "+str(dd))
    return

def admin_remove_case_from_kb(case_id=''):
    ## Not Label specific (slower but complete)
    stmt="""
    MATCH (n)
    WHERE n.case_id = '"""+case_id+"""'
    DETACH DELETE n
    """

    print ("[REMOVE ENTIRE CASE ID (in 5s)]: "+str(stmt))
#    time.sleep(5)

    ## Inter nodes
    for dd in Neo.iter_stmt(stmt,verbose=True):   #response to dict
        print ("cypher insert response> "+str(dd))

    return


def admin_remove_all_nodes():
    # ** deletes relationships too
    raise Exception("Admin only")
    stmt="""
    MATCH (n)
    DETACH DELETE n
    """

    print ("[REMOVE ALL NODES  and relationships (in 10s)]: "+str(stmt))
    time.sleep(10)

    ## Inter nodes
    for dd in Neo.iter_stmt(stmt,verbose=True):   #response to dict
        print ("cypher insert response> "+str(dd))
    return

def dev1():
    case_id='SGM BOA'
    case_id='case_o1_case_single'
    admin_remove_case_from_kb(case_id=case_id)
    return

def admin_remove_specifics():
    #ie/ after code logic updated but have strange in graph
    
    b=['Checking Summary now a removed section']

    if 'Checking Summary now a removed section' in b:
        ##1/  Remove transaction nodes where section='Checking Summary'
        stmt = """
        MATCH (n:Transaction {section: 'Checking Summary'})
        DETACH DELETE n
        """
    

    print("[REMOVE SPECIFIC NODES (in 10s)]: " + str(stmt))

    for dd in Neo.iter_stmt(stmt, verbose=True):  # response to dict
        print("cypher insert response> " + str(dd))

    
    return


def debug_creation():
    stmt="""MERGE (sender49:Entity {id: 'chase_5_a-1287'}) ON CREATE SET sender49 += {name: 'main_account', entity_id: '1287', type: 'debit_card', role: 'SENDER', id: 'chase_5_a-1287', label: 'Entity'} ON MATCH SET sender49 += {name: 'main_account', entity_id: '1287', type: 'debit_card', role: 'SENDER', id: 'chase_5_a-1287', label: 'Entity'} WITH sender49 MERGE (receiver49:Entity {id: 'chase_5_a-Wal Sam's Club 141'}) ON CREATE SET receiver49 += {name: 'Wal Sam\'s Club 141', entity_id: 'Wal Sam\'s Club 141', type: 'merchant', role: 'RECEIVER', id: 'chase_5_a-Wal Sam\'s Club 141', label: 'Entity'} ON MATCH SET receiver49 += {name: 'Wal Sam\'s Club 141', entity_id: 'Wal Sam\'s Club 141', type: 'merchant', role: 'RECEIVER', id: 'chase_5_a-Wal Sam\'s Club 141', label: 'Entity'}"""

    stmt="""MERGE (sender49:Entity {id: 'chase_5_a-1287'}) ON CREATE SET sender49 += {name: 'main_account', entity_id: '1287', type: 'debit_card', role: 'SENDER', id: 'chase_5_a-1287', label: 'Entity'} ON MATCH SET sender49 += {name: 'main_account', entity_id: '1287', type: 'debit_card', role: 'SENDER', id: 'chase_5_a-1287', label: 'Entity'} WITH sender49 MERGE (receiver49:Entity {id: 'chase_5_a-Wal SamsClub141'}) ON CREATE SET receiver49 += {name: 'Wal Sams Club 141', entity_id: 'Wal Sams Club 141', type: 'merchant', role: 'RECEIVER', id: 'chase_5_a-Wal Sams Club 141', label: 'Entity'} ON MATCH SET receiver49 += {name: 'Wal Sams Club 141', entity_id: 'Wal Sams Club 141', type: 'merchant', role: 'RECEIVER', id: 'chase_5_a-Wal Sams Club 141', label: 'Entity'}"""
    print ("STATEMENT IS:")
    print (str(stmt))
    Neo.run_stmt(stmt)
    return
    
if __name__=='__main__':
    branches=['dev1']
    branches=['admin_remove_all_nodes']
    branches=['admin_remove_specifics']
    branches=['debug_creation']
    
    for b in branches:
        globals()[b]()


"""
"""
