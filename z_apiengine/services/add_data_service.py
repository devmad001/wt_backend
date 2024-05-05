import os
import sys
import codecs
import json
import re
from decimal import Decimal
from fastapi import FastAPI

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")

sys.path.insert(0,LOCAL_PATH+"../..")
 
 
from w_storage.gstorage.gneo4j import Neo
from get_logger import setup_logging
from b_extract.alg_resolve_transaction_id import alg_generate_transaction_id
from database_models import TransactionRecord
from database import SessionLocal

logging=setup_logging()

def escape_string(value):
    #0v3#
    #Assumes string


    # Ensure value is a string
    if not isinstance(value, (str, bytes)):
        # Convert value to string if it's not None; otherwise, set it to an empty string
        value = str(value) if value is not None else ''

    # Normalize any already escaped single quotes
    value = re.sub(r"''", "'", value)
    
    # Escape single quotes by doubling them up for Cypher
    value = value.replace("'", "''")

    # Assume that dollar signs prefixed with a backslash should be unescaped
    value = re.sub(r'\\\$','$', value)
    
    # Replace 'â€œ' and 'â€' with a standard double quote
    value = value.replace('â€œ', '\"').replace('â€', '\"')

    return value


## VERSION v0 (original is html blob)
def update_data_tx(case_id,properties):
    stmt="""
    MATCH (t:Transaction)
    WHERE t.id='"""+str(properties.transaction_id)+"""'
    return t
    """
    jsonl,df,tx,meta=Neo.run_stmt_to_normalized(stmt)
    ex_transaction={}
    for record in jsonl:
        ex_transaction=record['t']

    stmt="""
    MATCH (b:BankStatement)
    WHERE b.case_id='"""+str(case_id)+"""'
    return b
    """
    jsonl,df,tx,meta=Neo.run_stmt_to_normalized(stmt)
    records=[]
    for record in jsonl:
        records.append(record['b'])
     
     
    transaction_id=properties.transaction_id
    unique_value = transaction_id
    if isinstance(unique_value, (float, int, Decimal)):
        unique_prop_str = f"id: {unique_value}"
    else:
        unique_prop_str = f"id: '{unique_value}'"
    transaction={}
     
    mod_field=[]
    if properties is not None and properties.transaction_amount is not None: 
      transaction['transaction_amount']=properties.transaction_amount
    if properties is not None and properties.transaction_date is not None: 
      transaction['transaction_date']=properties.transaction_date
    if properties is not None and properties.transaction_description is not None: 
      transaction['transaction_description']=properties.transaction_description
    if properties is not None and properties.section is not None: 
      transaction['section']=properties.section  
    

    props_list = []
    for key, value in transaction.items():
        if isinstance(value, (float, int, Decimal)):
            props_list.append(f"{key}: {value}")
        else:
            escaped_value=escape_string(value)
            props_list.append(f"{key}: '{escaped_value}'")
    props_list.append(f"transaction_id:'{transaction_id}'")
    props_list.append(f"file_name:'{ex_transaction['filename']}'")
    props_list.append(f"page_num:'{properties.page_number}'")
    
    node_var='transaction'
    node_type='Transaction'  
    props_str = ', '.join(props_list)
    set_str = f"{node_var} += {{{props_str}}}"
    
    try:
      with SessionLocal() as db:
        for key, value in transaction.items():
            new_record = TransactionRecord(transaction_id=transaction_id,field=key,previous_value=ex_transaction[key],new_value=value,user_id=properties.user_id,page_num=properties.page_number,file_name=ex_transaction['filename'])
            db.add(new_record)
            db.commit() 
            
            query = (
                f"CREATE (a:Audit {{{props_str}}}) "
            )
            print(query)
            jsonl,df,tx,meta=Neo.run_stmt_to_normalized(query)
    except Exception as e:
      print(e)
      return str(e)
        
    
      
    query = (
        f"MERGE ({node_var}:{node_type} {{{unique_prop_str}}}) "
        f"ON CREATE SET {set_str} "
        f"ON MATCH SET {set_str}"
    )
     
    jsonl,df,tx,meta=Neo.run_stmt_to_normalized(query)
     
    return jsonl
 
 
def add_data_tx(case_id,properties):
    stmt="""
    MATCH (b:BankStatement)
    WHERE b.case_id='"""+str(case_id)+"""'
    return b
    """
    jsonl,df,tx,meta=Neo.run_stmt_to_normalized(stmt)
    records=[] 
    statement_id=''
    print(jsonl)
    for record in jsonl:
        statement_id=record['b']['id']
    
    stmtcount="""
    MATCH (t:Transaction)
    WHERE t.case_id='"""+str(case_id)+"""'
    return count(t) as total
    """
    jsonl,df,tx,meta=Neo.run_stmt_to_normalized(stmtcount)
    records=[]
    natural_offset=0
    for record in jsonl:
        natural_offset=record['total']
    
    file_page_number=properties.page_number
    
    print("@#@#"*100)
   
    transaction_id=alg_generate_transaction_id(statement_id,file_page_number,natural_offset) 
    unique_value = transaction_id
    print(unique_value)
    if isinstance(unique_value, (float, int, Decimal)):
        unique_prop_str = f"id: {unique_value}"
    else:
        unique_prop_str = f"id: '{unique_value}'"
    transaction={}
    transaction['case_id']=case_id
  
    ## Extra meta
    transaction['transaction_date']=properties.transaction_date
    transaction['transaction_amount']=properties.transaction_amount
    transaction['transaction_description']=properties.transaction_description
    transaction['section']=properties.section 
    date_str=transaction.get('transaction_date','')
    props_list = []
    for key, value in transaction.items():
        if isinstance(value, (float, int, Decimal)):
            props_list.append(f"{key}: {value}")
        else:
            escaped_value=escape_string(value)
            props_list.append(f"{key}: '{escaped_value}'")
    
    
    node_var='transaction'
    node_type='Transaction'  
    props_str = ', '.join(props_list)
    set_str = f"{node_var} += {{{props_str}}}"
      
    query = (
        f"MERGE ({node_var}:{node_type} {{{unique_prop_str}}}) "
        f"ON CREATE SET {set_str} "
        f"ON MATCH SET {set_str}"
    )
    
    jsonl,df,tx,meta=Neo.run_stmt_to_normalized(query)
    print(jsonl)
    
        
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
        
    return jsonl
 

  
  
  