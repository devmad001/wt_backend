import time
import os
import sys
import codecs
import json
import re

import configparser as ConfigParser 


LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)


#0v2# JC  Jan 15, 2023  Upgrade to support fallback or rotation
#0v1# JC  Sep  2, 2023  Init

## OPTIONS:
#- load as dict
#- os.environ


def get_creds():
    logging.warning("[get_creds] is depreciated! Use llm_accounts.py")
    ## All or specific
    creds={}
    Config = ConfigParser.ConfigParser()

    ## OPEN AI
    Config.read(LOCAL_PATH+"openai.ini")
    creds['OPENAI_API_KEY']=Config.get('openai','apikey')

    ## SET ENV
    os.environ["OPENAI_API_KEY"] = creds['OPENAI_API_KEY']

    return creds



if __name__=='__main__':
    branches=['dev1']

    for b in branches:
        globals()[b]()




"""
os.environ.update(env_variables) #https://colab.research.google.com/drive/1kTlVSRXeJYvPL7vhRCf8oIthCLg4VcCl#scrollTo=iDA3lAm0LatM

def get_linkedin_password():
    Config = ConfigParser.ConfigParser()
    Config.read(LOCAL_PATH+"../linkedin.ini")
    return Config.get('linkedin','username'),Config.get('linkedin','password')
"""
