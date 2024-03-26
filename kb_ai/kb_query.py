import os
import sys
import codecs
import json
import re

from fastapi import FastAPI

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")

from w_storage.gstorage.gneo4j import Neo
from schemas.SCHEMA_graph import GRAPH_SCHEMA

from get_logger import setup_logging
logging=setup_logging()


#0v1# JC  Sep 19, 2023  Init


"""
    STD QUERIES
    - local
"""


def query_get_all_case_nodes(case_id='',label=''):
    records=[]

    if label:
        stmt="""
            MATCH (n:"""+label+""" {case_id: '"""+str(case_id)+"""'})
            RETURN n
            """
    else:
        stmt="""
            MATCH (n {case_id: '"""+str(case_id)+"""'})
            RETURN n
            """
    ## Inter nodes
    for dd in Neo.iter_stmt(stmt):
        dd=dd[0]  #unpack
        records+=[dd]
    #        print ("DEBUG: "+str(dd))
    if not records:
        logging.info("[no records] for case_id: "+str(case_id)+" --> "+str(stmt))
    return records


if __name__=='__main__':
    branches=['dev1']
    for b in branches:
        globals()[b]()



"""
"""
