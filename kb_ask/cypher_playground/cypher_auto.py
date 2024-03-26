import os
import sys
import codecs
import time
import json
import re

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")
sys.path.insert(0,LOCAL_PATH+"../../")

from w_storage.gstorage.gneo4j import Neo
from dev_kb_ask import call_get_graph_schema_str

from get_logger import setup_logging

logging=setup_logging()


#0v1# JC  Oct 6, 2023  Init

"""
    Explain Neo4j schem to LLM for cypher writing
"""


def dev_default_raw():
    schema=Neo.get_schema() 
    print ("SCHEMA: "+str(json.dumps(schema,indent=4)))
    ss=call_get_graph_schema_str()
    
    return

def dev_include_cypher_suggestions():
    #[ ] can base on similarity to known Qs
    return

def dev_default_suggestion():
    return

def dev_get_node_field_sample(label,field):

    stmt="""
    MATCH (t:Transaction)
    WITH t.transaction_type AS transactionType, COUNT(t) AS frequency
    ORDER BY frequency DESC
    RETURN transactionType, frequency;
    """

    stmt="""
    MATCH (t:Transaction)
    WITH t.transaction_type AS transactionType, COUNT(t) AS frequency, COUNT(DISTINCT t) AS totalTransactions
    WITH transactionType, frequency, totalTransactions, (frequency * 1.0) / totalTransactions AS uniqueness_ratio
    ORDER BY frequency DESC
    RETURN transactionType, frequency, uniqueness_ratio;
    """

    jsonl,df,tx,meta=Neo.run_stmt_to_normalized(stmt)
    
    for record in jsonl:
        samples[field].append(record['transactionType'])
        
    # Top 10
    samples[field]=samples[field][:10]
    
    return

def get_node_field_sample(label,field):
    # transaction_types:

    samples=[]

    stmt="""
    MATCH (t:Transaction)
    WITH t.transaction_type AS transactionType, COUNT(t) AS frequency
    ORDER BY frequency DESC
    RETURN transactionType, frequency;
    """

    stmt="""
    MATCH (t:"""+label+""")
    WITH COUNT(t) AS totalNodes
    MATCH (t:"""+label+""")
    WITH t."""+field+""" AS fieldName, COUNT(t) AS frequency, totalNodes
    RETURN fieldName, frequency, (frequency * 1.0) / totalNodes AS uniqueness_ratio
    ORDER BY frequency DESC;
    """
    
#D1#    print ("[stmt] "+stmt)

    jsonl,df,tx,meta=Neo.run_stmt_to_normalized(stmt)
    
    total_unique=0
    for record in jsonl:
#raw#        if len(samples[field])<10: print ("> "+str(record))

        if record['fieldName'] is None or not record['fieldName']:
            pass
        elif isinstance(record['fieldName'],list) or isinstance(record['fieldName'],dict):
            pass
        else:
            samples.append(record['fieldName'])
        total_unique+=record['uniqueness_ratio']
        

    if samples:
        avg_unique=total_unique/len(samples)
    else:
        avg_unique=0

#D2#    print ("AU: "+str(avg_unique))
    
    if avg_unique<0.01:
        print ("[WARN]  Field "+field+" is not unique enough")
        samples=[]
        
    # Top 10
    samples=samples[:10]
    
    # If not enough samples then odd field?
    
    return samples

def generate_neo4j_field_samples():
    ## OPTION A:  real-life values
    ## OPTION B:  schema expected values
    filename=LOCAL_PATH+"snapshot_neo4j_field_samples.json"

    ## Check real schema
    #    self.schema=(node_properties,relationships_properties,relationships)
    schema=Neo.get_schema() 
#    print ("^"*80)
    
    ## Node properties
    all_samples={}
    for node in schema[0]:
        label=node['labels'] #Transaction
        properties=[]
        for prop in node['properties']:
            properties.append(prop['property']) #property,type
            
        ## Get samples for each field
        for property in properties:
            sample_name=label+"."+property
            samples=get_node_field_sample(label,property)
            if samples:
                print ("[samples for]: "+str(sample_name)+": "+str(samples))
                all_samples[sample_name]=samples
    
    # Dump to file
    with open(filename,'w') as f:
        f.write(json.dumps(all_samples,indent=4))

    print ("SAMPLES: "+str(json.dumps(all_samples)))
    print ("[saved] "+filename)
    return

def load_relevant_neo4j_samples():
    # Relevance depends on fields
    all_samples={}
    filename=LOCAL_PATH+"snapshot_neo4j_field_samples.json"
    with open(filename,'r') as f:
        all_samples=json.loads(f.read())
        
    ignore_fields=[]
    ignore_fields+=['Transaction.filename']
    ignore_fields+=['Transaction.account_id']
    ignore_fields+=['Transaction.statement_id']
    ignore_fields+=['Transaction.versions_metadata']
    ignore_fields+=['Transaction.filename_page_num']
    ignore_fields+=['Transaction.case_id']
    ignore_fields+=['Transaction.account_number']
    ignore_fields+=['Transaction.account_holder_address']
    ignore_fields+=['Transaction.label']
    ignore_fields+=['Transaction.case_id']

    ignore_fields+=['Entity.name']
    ignore_fields+=['Entity.bank_name']
    ignore_fields+=['Entity.bank_address']
    ignore_fields+=['Entity.account_number']
    ignore_fields+=['Entity.label']
    ignore_fields+=['Entity.case_id']

    #OCT17: Entity.role, samples: SENDER, RECEIVER, MAIN_ACCOUNT, CASH
    #^^ may confuse cypher. SENDER/RECEIVER via CREDIT_TO and DEBIT_FROM
    #^^MAIN_ACCOUNT should come from entity id since linked to name
    #^^CASH is a type
    ignore_fields+=['Entity.role']

    ignore_fields+=['Processor.id']
    ignore_fields+=['Processor.label']
    ignore_fields+=['Processor.case_id']
    
    limit_to_2=['Transaction.check_num','Entity.account_holder_name','Entity.account_holder_address']
    limit_to_2+=['BankStatement.opening_balance','BankStatement.closing_balance']
    limit_to_2+=['Processor.lat','Processor.lng']
    limit_to_2+=['Processor.location']

    keep_samples={}
    for field in all_samples:
        if field in ignore_fields:
            pass
        elif 'BankStatement' in field and not 'balance' in field:
            pass
        else:
            ## Limit samples
            
            if field in limit_to_2:
                keep_samples[field]=all_samples[field][:2]
                
            elif 'transaction_method' in field:
                keep_samples[field]=all_samples[field]
                #Lower case on each element
                keep_samples[field]=[x.lower() for x in keep_samples[field]]
                
            elif 'Entity.type'==field:
                keep_samples[field]=all_samples[field]
                ## Remove 'baddies'
                #[ ] ideally upstream
                if 'company' in keep_samples[field]:
                    keep_samples[field].remove('company') #organization

            ## Keep normal
            else:
                keep_samples[field]=all_samples[field]

            ## Ensure sample
            if field=='Entity.type' and not 'cash' in keep_samples[field]:
                keep_samples[field]=['cash']+keep_samples[field]
            
#D            print ("sample>> "+str(field)+": "+str(keep_samples[field]))
            

#    print ("SAMPLES: "+str(json.dumps(keep_samples)))
    return keep_samples


def use_hardcoded_samples():
    return

if __name__=='__main__':
    branches=['dev_default_raw']
    branches=['load_relevant_neo4j_samples']
    branches=['generate_neo4j_field_samples']
    for b in branches:
        globals()[b]()

"""

Data field samples:
Field: Transaction.transaction_type, samples: withdrawal, deposit, other, transfer, fee, payment, book_transfer, online_payment, refund, reversal
Field: Transaction.transaction_method, samples: online_payment, other, check, debit_card, atm, zelle, zelle, wire_transfer, cash, book_transfer
Field: Transaction.is_wire_transfer, samples: True
Field: Transaction.is_cash_involved, samples: True
Field: Transaction.check_num, samples: 6164, 6164929912072900524
Field: Entity.account_holder_name, samples: GTA AUTO, INC., SKYVIEW CAPITAL GROUP MANAGEMENT LLC
Field: Entity.account_holder_address, samples: 6829 LANKERSHIM BLVD STE 116, NORTH HOLLYWOOD CA 91605, 125 BEVINGTON LN, WOODSTOCK GA 30188-5421
Field: Entity.type, samples: cash, individual, organization, bank, merchant, check, account, main_account, other, main_account_cardField: BankStatement.opening_balance, samples: 0.00, 10277.6
Field: BankStatement.closing_balance, samples: 4,680.37, 4784.88
Field: Processor.lat, samples: 34.086756009649, 46.28693384
Field: Processor.type, samples: other, zelle, check, online_payment, wire_transfer, debit_card, book_transfer, cash, atm, fed_wire
Field: Processor.lng, samples: -84.481317021177, 6.099725
Field: Processor.location, samples: 12172 Highway 92, Woodstock, GA, 30188, USA, 01210, Versonnex, Auvergne-Rhône-Alpes, FRA
"""





