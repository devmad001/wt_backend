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
    STANDARD DETAILED FIXED MAP QUERY

"""


def run_map_query_v2(case_id=''):
    """
        MAP DATA QUERY
        - Transaction nodes AND Processor nodes
        - The Processor nodes contain latitude & longitude information
            ## Map node fields together
            #: Processor has: lat,lng,type  (type:atm or debit_card")
    
    """
    
    ## Top-level assumptions
    ASSUME_ONLY_INCLUDE_TRANSACTIONS_WITH_LOCATION=True


    HIDE_FIELDS=['label','statement_id','algList','versions_metadata']


    stmt="""
        MATCH (transaction:Transaction {case_id: 'case_atm_location', transaction_method: 'atm'})-[:PROCESSED_BY]->(processor:Processor)
        WHERE transaction.case_id='"""+str(case_id)+"""'
        RETURN transaction,processor
    """

    ## Execute query
    jsonl,df,tx,meta=Neo.run_stmt_to_normalized(stmt)

    ## Map fields to new record
    records={}
    for j in jsonl:
        transaction=j['transaction']
        processor=j['processor']
        
        ## Top-filter
        if 'lat' not in processor:
            if ASSUME_ONLY_INCLUDE_TRANSACTIONS_WITH_LOCATION:
                continue

        ## Create new record
        record={}
        record.update(transaction)

        ## Include processor info
        record['lat']=processor['lat']
        record['lng']=processor['lng']
        record['type']=processor['type']
        
        ## Remove
        record={k:v for k,v in record.items() if k not in HIDE_FIELDS}
        
        if not records:
            print (">> "+str(record))

        ## Add to records
        records[transaction['id']]=record
        
    response={}
    response['data']=records
    return response





def pcypher_notes():
    ##1.  see q_query
    ##2.  see m_macros
    case_id='case_atm_location'
    response=run_map_query_v2(case_id=case_id)
    
    return
    

if __name__=='__main__':
    branches=['sample_query_maps']
    branches=['pcypher_notes']
    for b in branches:
        globals()[b]()



"""
"""