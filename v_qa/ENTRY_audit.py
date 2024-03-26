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



#0v1# JC  Jan 22, 2023  Setup



"""
    "AUTO AUDIT"
    - broad definition of exactly what it does

"""


def note_application_ideas():
    ideas=[]
    ideas+['tweak requests are general problems -- not specific cases (process for handling)']
    ideas+['[ ] sample is: withdrawls shown during deposit query -- jon thinks credit/debit class @timeline']

    return


def load_target_space():
    target_scopes=[]
    
    ## @ CASE LEVEL

    ## @ FILE LEVEL

    ## @ STATEMENT LEVEL

    ## @ PAGE LEVEL

    ## @ TRANSACTION LEVEL

    return


def audit_target_space():
    return

def auto_resolve():
    return


def dev1():

    return



if __name__=='__main__':
    branches=['dev1']
    for b in branches:
        globals()[b]()
