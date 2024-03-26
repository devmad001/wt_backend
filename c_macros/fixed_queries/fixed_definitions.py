import os
import sys
import time
import codecs
import json
import re

from datetime import datetime


LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"

sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")
sys.path.insert(0,LOCAL_PATH+"../../")

from w_storage.ystorage.ystorage_handler import Storage_Helper

from w_storage.gstorage.gneo4j import Neo
from z_apiengine.services.alg_generate_pdf_hyperlink import alg_generate_transaction_hyperlink

        
from get_logger import setup_logging
logging=setup_logging()


#0v1# Jan 22, 2024


"""
    FIXED DEFINITIONS
    - a bit more formal def of objects (ie/ is_wired, is_check) for counts etc.
    - can converge with cyphers (optionally)
    - more compute related (ie/ check dict)
"""


################################
#  TRANSACTION SCOPED COMPUTES #
################################
#

def COMPUTE_hyperlink(tt):
    hyperlink_url=alg_generate_transaction_hyperlink(tt)
    return hyperlink_url

def COMPUTE_is_wire(tt):
    ## exceptions:
    #- if transaction_method='wire' or 'wire_transfer' or zelle
    is_wire=0
    if 'wire' in tt.get('transaction_method','').lower():
        is_wire=1
    elif 'wire' in tt.get('transaction_type','').lower():
        is_wire=1
    elif 'zelle' in tt.get('transaction_method','').lower():
        is_wire=1
    ## Optional description of Wire?
    return is_wire

def COMPUTE_is_check_paid(tt):
    ##[ ] Assume "check paid" means check was sent out
    # check paid vs check recieved.  So check out
    if not tt.get('is_credit',''): # Not ok to assume false
        if tt.get('transaction_method','')=='check':
            return 1
    return 0


def dev1():

    return


if __name__=='__main__':
    branches=['dev1']

    for b in branches:
        globals()[b]()
    










