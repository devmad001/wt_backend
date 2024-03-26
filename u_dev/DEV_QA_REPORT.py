import os
import sys
import time
import codecs
import json
import re

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")

from w_storage.gstorage.gneo4j import Neo

from a_query.queryset1 import query_transactions_with_relations

from get_logger import setup_logging
logging=setup_logging()


#0v1# JC  Nov  3, 2023  Evolve QA report from dev_challanges




def QA_transactions_without_debit_credit(case_id='chase_4_a_33'):
    issue_transactions=[]

    mem_credit_debit={}
    results=[]
    all_ids={}

    for result in query_transactions_with_relations(case_id=case_id):
        id=result[0]['t']['id']
        all_ids[id]=result[0]['t']
        if result[1] in ['CREDIT_TO','DEBIT_FROM']:
            mem_credit_debit[result[0]['t']['id']]=True
#        results+=[result]

    for id in all_ids:
        if not id in mem_credit_debit:
            print ("[warning] NO CREDIT_TO or DEBIT_FROM at transaction: "+str(id))
            issue_transactions+=[(id,all_ids[id],'NO CREDIT_TO or DEBIT_FROM')]

    return issue_transactions

if __name__=='__main__':
    branches=['QA_transactions_without_debit_credit']

    for b in branches:
        globals()[b]()
