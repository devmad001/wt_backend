import os
import sys
import codecs
import json
import re
import requests
from configparser import ConfigParser

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")
sys.path.insert(0,LOCAL_PATH+"../../")

from w_utils import am_i_on_server


#0v1# JC Nov  3, 2023  Setup

"""
    If FraudAPI gets unknown session, it should send a handshake request to the frontend

"""

## ROOT CONFIG
Config = ConfigParser()
Config.read(LOCAL_PATH+"../../w_settings.ini")
FRAUDAPI_PORT=Config.get('services','fraudapi_port')

## For now, default testing local
TEST_LIVE_LOCAL=True
BASE_ENDPOINT='http://127.0.0.1:'+str(FRAUDAPI_PORT) #Hard coded port in fast_main.py

FRONTEND_ENDPOINT='http://'


"""
"""


def dev_session_handshake():
    given={}
    cols=['user_id','case_id','session_id','session_key']
    
    for col in cols:
        given[col]=''
    
    cols['case_id']=''

    ## session_id:   unique created by browser
    ## session_key:  password auth
    
    return


if __name__=='__main__':
    branches=['dev_session_handshake']
    for b in branches:
        globals()[b]()


"""

"""
