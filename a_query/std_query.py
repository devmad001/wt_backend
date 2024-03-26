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

from get_logger import setup_logging
logging=setup_logging()

#0v1# JC  Sep  6, 2023  Init



def ALT_write_via_pypher():
    # https://github.com/emehrkay/Pypher
    p = Pypher()
    p.MATCH.node('mark', labels='Person').rel(labels='knows').node('mikey', labels=['Cat', 'Animal'])
    p.RETURN(__.mark, __.mikey) 
    print ("GOT: "+str(p))# str(p) # MATCH (mark:`Person`)-[:`knows`]-(mikey:`Cat`:`Animal`) RETURN mark, mikey
    return

def do_query(mega):
    return

def dev1():
    print ("Do cypher query to db")

    ## Inter nodes
    for dd in Neo.iter_stmt("MATCH (n) RETURN n LIMIT 25"):   #response to dict
        print ("cypher insert response> "+str(dd))

    return

def dev2():
    # https://github.com/emehrkay/Pypher
    p = Pypher()
    p.MATCH.node('mark', labels='Person').rel(labels='knows').node('mikey', labels=['Cat', 'Animal'])
    p.RETURN(__.mark, __.mikey) 
    print ("GOT: "+str(p))# str(p) # MATCH (mark:`Person`)-[:`knows`]-(mikey:`Cat`:`Animal`) RETURN mark, mikey
    return


def cypher_queries_dev():
    print ("Check that relation was created even though (z) not defined:")
    stmt="""
    MATCH (z:Entity {name:"Zelle", role:"Payer", id:"case_1_Zelle", case_id:"case_1"})-[r:TRANSFERRED_TO]->(m1:Entity {name:"Mariza Haircut 12415184384", role:"Recipient", id:"case_1_Mariza Haircut 12415184384", case_id:"case_1"})
    RETURN z, r, m1
    """

    ## Inter nodes
    for dd in Neo.iter_stmt(stmt,verbose=True):   #response to dict
        print ("cypher insert response> "+str(dd))
    return

def dev_case_raw_for_excel():

    stmt="""
    """

    ## Select all transactions where case_id='case_2'

    stmt="""
    MATCH (n)
    RETURN n;
    """

    ## Count all labels in db
    stmt="""
    CALL db.labels()
    YIELD label
    RETURN label, COUNT(label) AS count
    ORDER BY count DESC;
    """

    stmt="""
    MATCH (n:Account)
    RETURN n;
    """

    stmt="""
    MATCH (n:Transaction {case_id: 'case_1'})
    RETURN n;
    """

    stmt="""
    MATCH (n:Transaction)
    RETURN n;
    """

    stmt="""
        MATCH (n:Transaction)
        RETURN n
        ORDER BY n.transaction_date ASC
        """


    case_id='SGM BOA'

    stmt="""
        MATCH (n:Transaction {case_id: '"""+str(case_id)+"""'})
        RETURN n
        ORDER BY n.transaction_date ASC
        """

    stmt="""
        MATCH (n:Transaction {case_id: '""" + str(case_id) + """'})
        RETURN
            n.transaction_date as date,
            n.transaction_amount as amount,
            n.transaction_description as description
        ORDER BY n.transaction_date ASC
    """

    ## TO RETURN JUST KEY VALUES:
    #  MATCH (t:Transaction)
    #  RETURN properties(t) AS TransactionAttributes;

    ## Inter nodes
    print ("[query]: "+str(stmt))

    ## Iter is fine but expects response is n (not specific params)
#    for dd in Neo.iter_stmt(stmt,verbose=True):   #response to dict
#        print ("cypher insert response> "+str(dd))

    results,tx=Neo.run_stmt(stmt,verbose=True)
    for Record in list(results):
        record=Record.data()
        if record.get('date','') and record.get('amount',''):

            ## Format output
            float_value=float(record.get('amount','0.0'))
            record['amount']="{:.2f}".format(float_value)

            record['description']=re.sub(r'[\n\r]+',' ',record.get('description',''))
            record['description']=re.sub(r'[\s\s]+',', ',record.get('description',''))

            print("> "+str(record))

#    for dd in Neo.iter_stmt(stmt,verbose=True):   #response to dict
#        print ("cypher insert response> "+str(dd))

    return

def dev_query_get_excel_data_raw_1(case_id):
    result_dicts=[]
    stmt="""
        MATCH (n:Transaction {case_id: '""" + str(case_id) + """'})
        RETURN
            n.transaction_date as date,
            n.transaction_amount as amount,
            n.transaction_description as description
        ORDER BY n.transaction_date ASC
    """
    ## Inter nodes
    print ("[query]: "+str(stmt))

    results,tx=Neo.run_stmt(stmt,verbose=True)
    for Record in list(results):
        record=Record.data()
        if record.get('date','') and record.get('amount',''):

            ## Format output
            float_value=float(record.get('amount','0.0'))
            record['amount']="{:.2f}".format(float_value)

            record['description']=re.sub(r'[\n\r]+',' ',record.get('description',''))
            record['description']=re.sub(r'[\s\s]+',', ',record.get('description',''))

            print("> "+str(record))

            result_dicts+=[record]


    return result_dicts,{}

def dev_calls():
    case_id='SGM BOA'
    dev_query_get_excel_data_raw_1(case_id)
    return

def dev_debug_normalizer():
    stmt="""
    MATCH (n:Transaction)-[:CREDIT_TO]->(e:Entity)
    WHERE n.case_id = 'case_o3_case_single'
    RETURN n, e
    """
    stmt="""
    MATCH (n:Transaction)-[:CREDIT_TO]->()
    WHERE n.case_id = 'case_o3_case_single'
    RETURN n.transaction_amount
    """
    jsonl,df,tx,meta=Neo.run_stmt_to_normalized(stmt)
    
    print ("RAW JSONL: "+str(jsonl))

    return


if __name__=='__main__':
    branches=['dev1']
    branches=['dev2']
    branches=['cypher_queries_dev']
    branches=['dev_case_raw_for_excel']
    branches=['dev_calls']
    branches=['dev_debug_normalizer']
    for b in branches:
        globals()[b]()


"""
"""
