import os
import sys
import codecs
import json
import re
import datetime
import uuid

from fastapi import FastAPI

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")

sys.path.insert(0,LOCAL_PATH+"../..")


#from w_chatbot.wt_brains import Bot_Interface
from w_storage.ystorage.ystorage_handler import Storage_Helper
from w_storage.gstorage.gneo4j import Neo

from a_agent.sim_wt import wt_main_pipeline

from get_logger import setup_logging
logging=setup_logging()


Storage=Storage_Helper(storage_dir=LOCAL_PATH+"../w_datasets")
Storage.init_db('feedback')

        
#0v1# JC Nov 23, 2023  Setup

"""
    TWEAK single transaction
"""


def local_run_query(stmt):
    results=[]
    for dd in Neo.iter_stmt(stmt,verbose=True):   #response to dict
#        print ("cypher response> "+str(dd))
        results+=[dd]
    return results

def get_single_transaction(search_by={}):
    tt={}
    
    if 'keyword' in search_by:
        stmt="""MATCH (t:Transaction)
        WHERE t.transaction_description CONTAINS '"""+search_by['keyword']+"""'
        RETURN t
        """
        #REGEX# WHERE t.transaction_description=~ '.*"""+search_by['keyword']+""".*'
        #NORM#  WHERE t.transaction_description CONTAINS '"""+search_by['keyword']+"""'
        
        print ("QUERY keyword find in transaction: "+stmt)

        results=local_run_query(stmt)
        
        if len(results)==1:
            tt=results[0]
        elif len(results)>1:
            print ("WARNING: multiple transactions found for keyword "+search_by['keyword'])
        elif len(results)==0:
            print ("WARNING: no transactions found for keyword "+search_by['keyword'])
        else:
            pass

    return tt


def ENTRY_tweak_single_transaction():

    search_by={}
    search_by['transaction_id']=''
    search_by['case_id']=''
    search_by['page_num']=''
    search_by['keyword']=''

    search_by['keyword']='121140397208147'
    
    tt=get_single_transaction(search_by=search_by)
    
    print ("PROCESS: "+str(json.dumps(tt,indent=4)))

    return
    


if __name__=='__main__':
    branches=['ENTRY_tweak_single_transaction']

    for b in branches:
        globals()[b]()


""
