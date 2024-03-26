import os
import sys
import codecs
import json
import re
import datetime
import uuid


LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"

sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")
sys.path.insert(0,LOCAL_PATH+"../..")

from w_storage.gstorage.gneo4j import Neo

from get_logger import setup_logging
logging=setup_logging()


        
#0v1# JC Jan 30, 2024  Setup


"""
    PLAYGROUND FOR DEVELOPER & CYPHER GRAPH DATABASE


"""


def sample_query_maps():
    """
    // Cypher for: "Show me where the ATMs are"
        MATCH (Transaction:Transaction {case_id: 'case_atm_location', transaction_method: 'atm'})-[:PROCESSED_BY]->(Processor:Processor)
    
    """

    case_id='case_atm_location'
    stmt="""
        MATCH (t:Transaction)
        WHERE t.case_id='"""+str(case_id)+"""'
        RETURN t
    """

    stmt="""
        MATCH (transaction:Transaction {case_id: 'case_atm_location', transaction_method: 'atm'})-[:PROCESSED_BY]->(processor:Processor)
        WHERE transaction.case_id='"""+str(case_id)+"""'
        RETURN transaction,processor
    """

    print ("FO: "+str(stmt))
    jsonl,df,tx,meta=Neo.run_stmt_to_normalized(stmt)

    ## Map node fields together
    #: Processor has: lat,lng,type  (type:atm or debit_card")
    
    REMOVE_FIELDS=['label','statement_id','algList','versions_metadata']
    
    ## Map fields to new record
    records={}
    for j in jsonl:
        transaction=j['transaction']
        processor=j['processor']

        ## Create new record
        record={}
        record.update(transaction)

        ## Include processor info
        record['lat']=processor['lat']
        record['lng']=processor['lng']
        record['type']=processor['type']
        
        ## Remove
        record={k:v for k,v in record.items() if k not in REMOVE_FIELDS}
        
        if not records:
            print (">> "+str(record))

        ## Add to records
        records[transaction['id']]=record
        

    return




def pcypher_notes():
    ##1.  see q_query
    ##2.  see m_macros
    
    return
    

if __name__=='__main__':
    branches=['pcypher_notes']
    branches=['sample_query_maps']
    for b in branches:
        globals()[b]()



"""
"""