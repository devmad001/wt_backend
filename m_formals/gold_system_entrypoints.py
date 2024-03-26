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

from support_gold import url2testcase

from get_logger import setup_logging
logging=setup_logging()




#0v1# JC  Jan 29, 2023  Setup



"""
**this is semi-formal -- not real code.

    GOLD SYSTEM ENTRYPOINTS
    ^various ways to run the system
    
    - input related?
        - extractor?

    - output related?
        - Q&A?
        - neo4j?

"""



"""
>> ADD FUNCTION TO support_gold.py?
>> ENTER AT FIND STATEMENT START BALANCE??

"""


def dev1():

    return




if __name__=='__main__':
    branches=['dev1']
    for b in branches:
        globals()[b]()
