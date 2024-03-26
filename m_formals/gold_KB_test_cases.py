import os
import sys
import codecs
import json
import re
import time
import requests

import configparser as ConfigParser


LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")
sys.path.insert(0,LOCAL_PATH+"../../")

from w_storage.gstorage.gneo4j import Neo
from a_query.cypher_helper import cypher_create_update_node

from get_logger import setup_logging
logging=setup_logging()



#0v1# JC  Feb  2, 2023  Setup



"""
    TEST CASES THAT EXIST IN GRAPH KNOWLEDGE BASE
    -

"""



def create_small_world_test_graph():

    return


def dev1():
    print ("Known case_id ( take pdf or take nodes and create test case)")
    
    ## CREATE TEST CASE GRAPH FROM EXISTING CASE UNDER TEST
    #> query for small world to test
    #> create test graph from it
    #> run test on specific
    
    print ("1.  case_id -> transactions -> sub_transactions")
    print ("2.  create_test_case_id_X -> repost sub_transactions to test_case_id_X")
    print ("3.  optionally delete test_case_id_X")

    return

def local_query_case_transaction_subset(case_id,page_number=0,statement_id=''):
    if statement_id:
        raise ValueError("Not yet implemented")
    
    stmt="""
            MATCH (n:Transaction)
            WHERE n.case_id='"""+str(case_id)+"""'
            RETURN n
        """
    jsonl,df,tx,meta=Neo.run_stmt_to_normalized(stmt)
    
    c=0
    trecords=[]
    for dd in jsonl:
        keep_it=False

        c+=1
        filename_page_num=dd['n']['filename_page_num']
        
        if not page_number:
            keep_it=True
        elif page_number==filename_page_num:
            keep_it=True
        else:
            pass
        
        if keep_it:
            trecords+=[dd['n']]

        if c<10:
            print (dd)

    return trecords



def create_test_case_subgraph_from_transaction_records(test_case_id,trecords):
    
    ### PREP NEW CASE TRANSACTION RECORDS
    ## Create new transaction id for each
    new_records=[]
    for record in trecords:
        new_record=record.copy()

        new_record['case_id']=test_case_id

        new_record['id']=test_case_id+'-'+record['id']
        
        new_record.pop('label','') #Not when inserting
        new_records+=[new_record]
        
    ### INSERT NEW TRANSACTION RECORDS INTO GRAPH DB
    #? clean interface?
    # a_query/cypher_helper -> cypher_create_update_node
    # b_extract/do_cypher.py --> do_transactions2cypher
    
    ## One at a time?
    transaction_label='Transaction'
    c=0
    cypher=''
    for transaction in new_records:
        c+=1

        this_cypher=cypher_create_update_node(transaction_label,transaction,unique_property='id',node_var='transaction'+str(c))

        cypher+=this_cypher
        cyphers_as_list=[this_cypher]
        
        print ("> "+str(cypher))

#        break

    print ("INSERT CYPHER...")
    for dd in Neo.iter_stmt(cypher,verbose=True):   #response to dict
        print ("cypher insert response> "+str(dd))

    return


def create_test_transaction_subgraph(case_id,page_number):
    ## TARGET TO TEST:
    test_kind='default' #collision on page etc.
    
    ## OR BY TRANSACTION ID?  OR can likely pull nodes by page
    trecords=local_query_case_transaction_subset(case_id,page_number=page_number)
    
    print ("Building test case for case: "+str(case_id)+" page: "+str(page_number)+" has "+str(len(trecords))+" transactions")
    
    test_case_id='test_'+test_kind+'_'+case_id+'_'+str(page_number)
    
    create_test_case_subgraph_from_transaction_records(test_case_id,trecords)

    new_trecords=local_query_case_transaction_subset(test_case_id,page_number=page_number)
    print ("Source sub-graph case has "+str(len(trecords))+" transactions")
    print ("Test case has "+str(len(new_trecords))+" transactions")
    
    if not len(new_trecords)==len(trecords):
        print ("ERROR:  Test case has different number of transactions than source")
    else:
        print ("OK test case graph created for: "+str(test_case_id))
    
    return


def interface_create_test_transaction_subgraph(case_id,page_number):
    create_test_transaction_subgraph(case_id,page_number)
    return


def test_call_interface_create_test_transaction_subgraph():
    # check deposit flagged as wrong transaction type
    #>> likely need to include sign of transaction if just 'Checks' section
    """
       tt['meta']['case_id']='65a8168eb3ac164610ea5bc2'
    tt['meta']['url']="https://core.epventures.co/api/v1/case/65a8168eb3ac164610ea5bc2/pdf/72d85b81-c416-4ffd-950c-f0c1fd62f251.pdf?page=194&key=d5c891217c4bb3f96f0b4e0fd2b2dc8568bc8a7b952e234f861ede8ab9035acb&highlight=1000.00|235087%2A"

    """
    
    case_id='65a8168eb3ac164610ea5bc2'
    page_number=194
    interface_create_test_transaction_subgraph(case_id,page_number)

    return


def dev2():
    stmt="""
         MATCH (n:Transaction {case_id: 'test_default_65a8168eb3ac164610ea5bc2'})
            RETURN n
        """
    jsonl,df,tx,meta=Neo.run_stmt_to_normalized(stmt)
    for dd in jsonl:
        print (">  "+str(dd))
    print ("DONE NO?")

    return
            

if __name__=='__main__':
    branches=['dev1']
    branches=['dev2']
    branches=['test_call_interface_create_test_transaction_subgraph']

    for b in branches:
        globals()[b]()


"""
{'n': {'is_credit': True, 'transaction_date': '2020-11-02', 'filename_page_num': 2, 'account_number': '334049185630', 'is_cash_involved': True, 'transaction_amount': 245.75, 'section': 'Cash transactions', 'transaction_method': 'other', 'label': 'Transaction', 'statement_id': '65a8168eb3ac164610ea5bc2-2020-11-01-334049185630-72d85b81-c416-4ffd-950c-f0c1fd62f251.pdf', 'transaction_type': 'deposit', 'transaction_description': 'MERCHANT BNKCD DES:DEPOSIT ID:323242463996 INDN:PLANET SMOOTHIE 19109 CO', 'algList': ['create_ERS'], 'account_id': '65a8168eb3ac164610ea5bc2-334049185630', 'filename': '72d85b81-c416-4ffd-950c-f0c1fd62f251.pdf', 'case_id': '65a8168eb3ac164610ea5bc2', 'versions_metadata': '{"transaction_method_id": "llm_markup-transaction_type_method_goals-", "transaction_type": "llm_markup-transaction_type_method_goals-", "is_cash_involved": "llm_markup-transaction_type_method_goals-", "transaction_method": "llm_markup-transaction_type_method_goals-"}', 'id': 'ec7dc18580087519dbce4e665f11e405bc88919aa2ede1f137389979421ace5b', 'transaction_method_id': '323242463996'}}
"""