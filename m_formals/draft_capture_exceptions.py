import os
import sys
import codecs
import json
import re
import time
import requests

import configparser as ConfigParser


LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")
sys.path.insert(0,LOCAL_PATH+"../../")

from get_logger import setup_logging
logging=setup_logging()


#0v1# JC  Jan 29, 2023  Setup



"""
    DRAFT CAPTURE EXCEPTIONS


"""



def dev1():
    
    """
    Jan 29, 2024
    - LLM find start balance on pdf page check. (not page 2 transactions!)

    PJ Plumbing consolidated balances etc can't find start balance						[ ] test blend of accounts + inner statement accounts.  Bank-state-2. Should be 167k we have 134k			
    """


    

    return



if __name__=='__main__':
    branches=['dev1']
    for b in branches:
        globals()[b]()





