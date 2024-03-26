import os
import sys
import codecs
import time
import json
import re
import random
import copy

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")

from get_logger import setup_logging
logging=setup_logging()

from a_query.queryset1 import query_all_transactions
from a_query.cypher_helper import cypher_add_fields_to_node
from w_storage.gstorage.gneo4j import Neo


#0v1# JC  Sep 23, 2023  Init

"""
    APPLY CLEANER LOGIC:
    - to new records
    - to existing records
    - (recall node field updates has possible versioning)

"""

def dev1():
    print ("Across entire KB:  cypher get, update")
    print ("Integrate into new records:  into logic ?call just func or call new routine?")
    return

def cleaner_query_kb():
    return

def cleaner_apply_function_to_records():
    return

def cleaner_validate_changes():
    return

def cleaner_commit_changes():
    return

def get_dict_of_just_changed_fields(record_old,record_new):
    record={}
    for k in record_new:
        if not record_new[k]==record_old[k]:
            record[k]=record_new[k]
    return record

def apply_function_across_kb(verbose=False):
    ##
    # [ ] watch tests & commit ie/ before after record compare
    print ("Across entire KB:  cypher get, update")

    b=['Clean all transaction_descriptions']

    if 'Clean all transaction_descriptions' in b:
        from b_extract.alg_clean_transactions import adjust_transactions_top_level
        for transaction in query_all_transactions():
            given=copy.deepcopy(transaction)

            ## APPLY
            transaction=adjust_transactions_top_level(transaction=transaction)

            if not transaction==given and verbose:
                print ("OLD:  ",     given)
                print ("NEW:  ",transaction)

            dd=get_dict_of_just_changed_fields(given,transaction)
            if dd:
                cypher=cypher_add_fields_to_node('Transaction',dd,transaction['id'])

#use cypher_helper try_clean_cypher                cypher=clean_cypher_query(cypher)

                print ("="*30)
                print ("cypher:  ",cypher)
                print ("^"*30)
                for rr in Neo.iter_stmt(cypher,verbose=False):
                    raise Exception("ERROR:  ",rr)

    return


if __name__=='__main__':
    branches=['apply_function_across_kb']
    for b in branches:
        globals()[b]()


"""
"""
