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

from a_agent.RUN_sim_wt import call_normal_full_run
from a_agent.sim_wt import wt_main_pipeline

from a_query.queryset1 import query_statements
from a_query.queryset1 import query_transaction
from a_query.queryset1 import query_transactions
from a_query.queryset1 import query_transaction_relations

from get_logger import setup_logging
logging=setup_logging()


#0v1# JC  Oct  2, 2023  Init


def view_case(case_id='case_o3_case_single'):
    ## Recall Nodes + rels etc.
    #- need easy visual
    b=['hard_code_transaction_case']
    b=['standard case view']

    if 'hard_code_transaction_case' in b:
        ## Hard code sample
        transaction_id='1902247342Fs'
        for rel in query_transaction_relations(transaction_id=transaction_id):
            pass
    
    if 'standard case view' in b:
        for statement_id in query_statements(case_id=case_id):
            print ("statement id> "+str(statement_id))
            ## Now internally transactions!
            for transaction in query_transactions(statement_id=statement_id):
                print ("="*40)
    
                print ("transaction> "+str(json.dumps(transaction,indent=4)))
                
                ## Query transaction relations
                has_rels=False
                for rel in query_transaction_relations(transaction_id=transaction['id']):
                    has_rels=True
                    pass
                
                if not has_rels:
                    print ("No relations for transaction> "+str(transaction['id']))
    
    #            break
    

    return


def dup_challenges_queries():
    b=['case to statements']
    b=['statement filename to transaction']
    
    if 'case to statements' in b:
        case_id='case_chase_dev_1'
        print ("Case to statement ids (for easy kb query)")
        
        for statement_id in query_statements(case_id=case_id):
            print ("statement id> "+str(statement_id))
            
            ## Now internally transactions!
            for transaction in query_transactions(statement_id=statement_id):
                print ("transaction> "+str(transaction))
                        
            break
        
    if 'statement filename to transaction' in b:
        ## of course filenames is NOT unique
        filename='Chase statements 1.pdf'
        filename='Schoolkidz-December-2021-statement.pdf'
        for transaction in query_transactions(filename=filename):
            print ("transaction> "+str(transaction))

    return


def dup_challenge_narrow_audit():
    ## of course filenames is NOT unique
#    filename='Chase statements 1.pdf'
    filename='Schoolkidz-December-2021-statement.pdf'
    for transaction in query_transactions(filename=filename):
        if str(transaction.get('filename_page_num',''))=='3':
            print ("transaction> "+str(transaction))

    return

if __name__=='__main__':
    branches=['view_case']

    for b in branches:
        globals()[b]()




"""

"""
