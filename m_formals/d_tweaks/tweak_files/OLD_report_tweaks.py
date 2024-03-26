import os
import sys
import codecs
import json
import uuid
import re
import random

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")

from w_storage.gstorage.gneo4j import Neo
from w_storage.ystorage.ystorage_handler import Storage_Helper

from get_logger import setup_logging
logging=setup_logging()


#0v1# JC  Nov 21, 2023  SETUP



"""
    FORMALIZE feedback, adjustments queue, tasks, logical adjustements, and tests

"""



def dev1():

    """
    1//  RESOLVE BY:  Suggesting the Additions and Deposits was a section heading
    symptom:  transaction section as 'Electronic Withdrawal' but not even in the pdf! $141,680
    https://dash.epventures.co/case/MarnerHoldings/run
    https://core.epventures.co/api/v1/case/MarnerHoldings/pdf/2021-06June-statement-0823.pdf?page=1&key=798669380686ea0bfad31c5e69805b0c42f4edbcd556bb5bf226dde92e00d30a
    debug approach:
    - manually process 1 page pdf
    - check section extractor
    [x] options=['only_page'] -> see and u_entrypoints/ENTRY_tweak_run_single_pdf_page.py
    [x] options=['db_commit']=False
    """

    """
    2//  RESOLVE BY:  [x]  was using pdf_miner (bad) but we now do OCR so do pdf table thing
         SYMPTOM:   Withdrawl section still thinking its' a credit?
         page_url='https://core.epventures.co/api/v1/case/MarnerHoldings/pdf/2021-06June-statement-0823.pdf?page=9&key=798669380686ea0bfad31c5e69805b0c42f4edbcd556bb5bf226dde92e00d30a
         

    3//  EASY PDF missing one transactions
    ** goto ENTRY_tweak_run_single_pdf_page
    http://127.0.0.1:8008/api/v1/case/MarnerHoldingsJune/pdf/2021-06June-statement-0823.pdf?page=1&key=14b3f30104701f2ffd565d0efbcfa86e997f65e35cdf6e3c9867973603532a89
    http://127.0.0.1:8008/api/v1/case/MarnerHoldingsJune/timeline?maxWidth=1771&maxHeight=600
    http://127.0.0.1:5173/case/MarnerHoldingsJune/run
    RESOLUTION:  $1222.00 amounts need to have spaces before them
    
    
    """
    
    
    return



if __name__=='__main__':
    branches=[]
    branches+=['dev1']

    for b in branches:
        globals()[b]()
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
