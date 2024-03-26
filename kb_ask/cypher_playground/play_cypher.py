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

#from w_storage.gstorage.gneo4j import Neo
#from dev_kb_ask import call_get_graph_schema_str
from kb_ask.kb_ask import AI_handle_kb_question

from get_logger import setup_logging

logging=setup_logging()


#0v1# JC  Oct 6, 2023  Init

"""
    Real llm cypher writing dev
"""



def dev1():
    case_id='demo_a'

    print ("Sample ask cypher")
    question='What is the total of all transactions?'
    question='What is the total of all cash transactions?'
    question='What is the breakdown of transactions by type?'
    question='What is the breakdown of transactions by type and amount?'
    question='What transaction contain the word: London?'

    response,meta,Agent=AI_handle_kb_question(question,case_id=case_id)
    
    print ("RE: "+str(response))
    print ("meta: "+str(meta))

    print ("="*30)
    print ("llm prompt: "+str(meta['llm_query_make_cypher']))
    print ("="*30)
    print ("cypher created:\n"+str(meta['cypher']))

    print ("="*30)
    print ("ANSWER:\n"+str(response))
    
    return


if __name__=='__main__':
    branches=['dev1']
    for b in branches:
        globals()[b]()

