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

from get_logger import setup_logging
logging=setup_logging()

#0v1# JC  Sep  6, 2023  Init


"""
    ADJUST KB when oddities arise
"""


def remove_amount_zero():
    ## case_schoolkids:  'amount':'0' but also transaction_amount='33.22' good

    stmt="""
    MATCH (n:Transaction)
    WHERE n.amount = '0'
    REMOVE n.amount
    """
    print ("[cypher]: "+str(stmt))
    ## Inter nodes
    for dd in Neo.iter_stmt(stmt,verbose=True):   #response to dict
        print ("cypher insert response> "+str(dd))

    return

def dev1():

    remove_amount_zero()
    return

if __name__=='__main__':
    branches=['dev1']
    for b in branches:
        globals()[b]()


"""
"""
