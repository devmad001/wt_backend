import os,sys
import re
import json
import time
import copy
import codecs

import requests

from pathlib import Path
import shutil

import numpy as np
from a_query.queryset1 import query_transactions


LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../../")

from z_apiengine.database import SessionLocal
from z_apiengine.database_models import Check

CHECK_MEDIA_STORAGE_DIR=LOCAL_PATH+"CHECK_MEDIA_STORAGE"

#0v1# JC  Feb  1, 2024  Init


"""
    >> use algs from check_management demo
"""



def local_query_transactions(case_id):
    ## Local (on server?)
    
    #jcase_transactions_url="http://127.0.0.1:8008/api/v1/case/65a8168eb3ac164610ea5bc2/run_query?query=jon"
    case_transactions_url="http://127.0.0.1:8008/api/v1/case/"+case_id+"/run_query?query=jon"

    r=requests.get(case_transactions_url)
    the_json=r.json()
    records=the_json['data']
    print ("[debug] logging info loaded transactions count: "+str(len(records)))
    return records


def clean_to_check_id(description=''):
    given=copy.deepcopy(description)

    check_id=description
    # remove amounts:  negative onwards ([ ] possibly .00):  1455*-900.00'
    #[ ] stand-alone function?
    check_id=re.sub(r'-[\d\,]+\.\d\d\b','',check_id)

    # Remove all beginning non-numeric
    check_id=re.sub(r'^[^0-9]*','',check_id)
    check_id=re.sub(r'[^0-9]*$','',check_id)
    check_id=re.sub(r' ','',check_id)
    if len(check_id)>4:
        #print ("[debug] check check_id: "+str(check_id)+" given: "+str(given))
        pass
    return check_id


def query_get_case_transactions(case_id=''):
    ## Use local neo or queryset
    trs=[]
    #(using classical query but could use new jsonl)
    for tr in query_transactions(case_id=case_id):
        trs+=[tr]
    return trs

def logic_if_transaction_looks_like_a_check(tr):
    a_check=False
    if 'check' in tr['section'].lower():
        a_check=True
#D    print ("SECTION: "+str(tr['section']))
        
    #[ ] optionally if description looks like check ___ need example
    return a_check


def clean_image_record(record):
    ## check_id (already removed trailling non words)
    return




def dev1():
    return


if __name__ == "__main__":
    dev1()




"""

"""
