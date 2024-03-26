import os
import sys
import codecs
import uuid
import json
import re
import time
import hashlib

import pandas as pd
from collections import Counter


import configparser as ConfigParser

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")


from get_logger import setup_logging
logging=setup_logging()


#0v1# JC  Jan 24, 2024  Centralize config for dashboard

"""
    CENTRAL CONFIG FOR DASHBOARD VIEW TYPES
    - optionally migrate to single config file
    - recall, urls not just on UI but injected by mindstate decision system

"""


## CONFIG FOR BROADCASTS
config_file=LOCAL_PATH+'../'+'w_config_dashboard.json'
def load_config():
    global config_file
    with open(config_file, 'r') as fp:
        CONFIG = json.load(fp)
    return CONFIG
CONFIG=load_config()


### ROOT CONFIG
RootConfig = ConfigParser.ConfigParser()
RootConfig.read(LOCAL_PATH+"../w_settings.ini")

FRAUDAPI_PORT=RootConfig.get('services','fraudapi_port')
FRAUDAPI_subdomain=RootConfig.get('services','fraudapi_subdomain')
FRAUDAPI_domain=RootConfig.get('services','fraudapi_domain')


ON_LIVE_SERVER=True
if os.name=='nt': ON_LIVE_SERVER=False

if ON_LIVE_SERVER:
    BASE_ENDPOINT='https://'+FRAUDAPI_subdomain+"."+FRAUDAPI_domain
else:
    BASE_ENDPOINT='http://127.0.0.1:'+str(FRAUDAPI_PORT)


#####################################################


def config_get_map_view_url(case_id,session_id='',user_id='',version=''):
    global BASE_ENDPOINT
    ## Various!
    if ON_LIVE_SERVER:
        # Upgrade to node based map
        #url=BASE_ENDPOINT+'/api/v1/case/'+case_id+'/map/view'
        #url='https://nets.epventures.co/[caseid]/mapview?fin_session_id=&user_id='
        url=BASE_ENDPOINT+'/api/v1/case/'+case_id+'/map/view'
        url='https://nets.epventures.co/'+case_id+'/mapview?fin_session_id='+session_id+'&user_id='+user_id
        url='https://nets.epventures.co/'+case_id+'/mapview'

    else:
        # Fallback to local dev env (here maps non-node)
        #url=BASE_ENDPOINT+'/api/v1/case/'+case_id+'/map/view'
        url=BASE_ENDPOINT+'/api/v1/case/'+case_id+'/map/view'
        url='https://nets.epventures.co/'+case_id+'/mapview?fin_session_id='+session_id+'&user_id='+user_id
        url='https://nets.epventures.co/'+case_id+'/mapview'

    return url


if __name__=='__main__':
    branches=['dev1']
    for b in branches:
        globals()[b]()





        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
