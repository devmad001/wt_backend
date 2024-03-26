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


#0v1# JC  Sep 18, 2023  Init


def query_statements(case_id=''):
    #* at this point no statement label so do via transactions

        #RETURN t.statement_id as StatementID, collect(t) as Transactions
    stmt="""
        MATCH (t:Transaction)
        WHERE t.case_id='"""+str(case_id)+"""'
        RETURN DISTINCT t.statement_id as StatementID
        ORDER BY StatementID;
        """
    record={}
    
    ## Run statements when different styles of output!
    results,tx=Neo.run_stmt(stmt,tx='',parameters={})
    results=results.data() #<-- standard normalize as list too
    for record in results:
        yield record['StatementID'] #  #{'StatementID'}
    return

def delete_transaction_node(transaction_id=''):
    if not transaction_id:
        raise Exception('Transaction ID must be provided')

    stmt = """
    MATCH (t:Transaction {id: $transaction_id})
    OPTIONAL MATCH (t)-[r]-() 
    DELETE r, t
    """

    Neo.run_stmt(stmt, parameters={'transaction_id': transaction_id})
    print('Transaction and its relationships deleted successfully')
    return
    
def query_transaction(transaction_id='',statement_id=''):
    ## Data (may not have Label)
    ## Transaction meta
    stmt=''

    if transaction_id:
        stmt="""
            MATCH (n:Transaction {id: '"""+str(transaction_id)+"""'})
            RETURN n
            """
    elif statement_id:
        raise Exception('Use query_transactions() for statement_id')
        stmt="""
            MATCH (n:Transaction)
            WHERE n.statement_id='"""+str(statement_id)+"""'
            RETURN n
            """
    else:
        raise Exception('No transaction_id or statement_id provided')
    

    if stmt:
        record={}
        # single?!
        if 'alt normal' in ['alt normal']:
            for record in Neo.iter_stmt(stmt,verbose=False):   #response to dict
                if isinstance(record,list):
                    record=record[0] #list is standard
                break
#        if 'run get list ok' in []:
#            results,tx=Neo.run_stmt(stmt,tx='',parameters={})
#            record=results.data() #[0]

    return record

def query_transactions(statement_id='',filename='',case_id=''):
    ## Data (may not have Label)
    ## Transaction meta
    #- assume one parameter only

    stmt=''

    if case_id:
        stmt="""
            MATCH (n:Transaction)
            WHERE n.case_id='"""+str(case_id)+"""'
            RETURN n
            """

    elif statement_id:
        stmt="""
            MATCH (n:Transaction)
            WHERE n.statement_id='"""+str(statement_id)+"""'
            RETURN n
            """
    elif filename:
        #** filename is NOT unique to case/statement
        stmt="""
            MATCH (n:Transaction)
            WHERE n.filename='"""+str(filename)+"""'
            RETURN n
            """
    else:
        raise Exception('No statement_id provided')
    

    if stmt:
        record={}
        # single?!
        if 'alt normal' in ['alt normal']:
            for record in Neo.iter_stmt(stmt,verbose=False):   #response to dict
                if isinstance(record,list):
                    record=record[0]
                yield record

        if 'run get list ok' in []:
            results,tx=Neo.run_stmt(stmt,tx='',parameters={})
            record=results.data() #[0]
    return

def query_all_transactions():
    ## Possibly in chunks (memory) or truly ensure iterator
    stmt="""
        MATCH (n:Transaction)
        RETURN n
        """
    record={}
    for record in Neo.iter_stmt(stmt,verbose=False):   #response to dict
        record=record[0] #list is standard
        #?.data()
        yield record
    return

def query_transaction_relations_ORG(transaction_id=''):
    ## Or, by specific type: 
    # MATCH (t:Transaction {id: '8e21aa'})-[r:CREDIT_TO|:DEBIT_FROM]->(e:Entity)
    #RETURN t, r, e

    stmt="""
    MATCH (t:Transaction {id: '"""+transaction_id+"""'})-[r]-(related)
    RETURN t, r, related
    """
    for rr in Neo.run_stmt(stmt,verbose=True):
        try:
            data=rr.data()
            if data:
                print ("data: "+str(data[0]))
                t=data[0]['t']
                r=data[0]['r']

                related=data[0]['related']
                
#                print ("r: "+str(r))
#                print ("T: "+str(t))
#            print("REL: "+str(data))
#            for item in data:
#                yield item
        except:pass
    return


def query_transaction_relations(transaction_id=''):
    ## Or, by specific type: 

    stmt = """
    MATCH (t:Transaction {id: $transaction_id})-[r]-(related)
    RETURN t, type(r) as relationship_type, r as relationship, related
    """
    
    parameters = {"transaction_id": transaction_id}
    
    for rr in Neo.run_stmt(stmt, parameters=parameters, verbose=True):
        if not hasattr(rr, 'data'): continue  #Skip Session variable
        try:
            data = rr.data()
            if data:
                for record in data:
                    t = record.get('t')
                    relationship_type = record.get('relationship_type')
                    related = record.get('related')
    
                    t_id = t.get('id')  # Replace with the actual key for transaction ID
                    related_id = related.get('id')  # Replace with the actual key for related node ID
    
                    # Determine the arrow direction based on the relationship type
                    arrow = '-->'
                    if relationship_type == 'DEBIT_FROM':
                        arrow = '<--'
    
                    print(f"{t_id} {arrow} {relationship_type} {related_id}")
                    yield record
    
        except Exception as e:
            print(f"Error processing record: {e}")

    return

def query_transactions_with_relations(case_id=''):
    stmt = """
    MATCH (t:Transaction {case_id: $case_id})-[r]-(related)
    RETURN t, type(r) as relationship_type, r as relationship, related
    """
    parameters = {"case_id": case_id}

    for rr in Neo.run_stmt(stmt, parameters=parameters, verbose=True):
        if not hasattr(rr, 'data'): continue  #Skip Session variable
        try:
            data = rr.data()
            if data:
                for record in data:
                    t = record.get('t')
                    relationship_type = record.get('relationship_type')
                    related = record.get('related')
    
                    t_id = t.get('id')  # Replace with the actual key for transaction ID
                    related_id = related.get('id')  # Replace with the actual key for related node ID
    
                    # Determine the arrow direction based on the relationship type
                    arrow = '-->'
                    if relationship_type == 'DEBIT_FROM':
                        arrow = '<--'
    
                    print(f"{t_id} {arrow} {relationship_type} {related_id}")
                    yield record,relationship_type,related_id
    
        except Exception as e:
            print(f"Error processing record: {e}")

    return

def dev_query_data_focused(transaction_id=''):
    stmt = """
    MATCH (t:Transaction {id: $transaction_id})-[r]-(related)
    RETURN t, type(r) as relationship_type, r as relationship, related
    """
    parameters = {"transaction_id": transaction_id}
    for rr in Neo.run_stmt_to_data(stmt, parameters=parameters, verbose=True):
#        print ("> "+str(rr))
        yield rr
    return


def dev1():
    return

if __name__=='__main__':
    branches=['dev1']

    for b in branches:
        globals()[b]()


"""
MATCH (t:Transaction {id: '8e2176d1a2ea9615b3ee5a3427010def974317a534e132ad93a0c96fb81b07aa'})-[r:CREDIT_TO|:DEBIT_FROM]->(e:Entity)
RETURN t, r, e

"""
