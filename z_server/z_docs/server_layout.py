import os
import sys
import time
import codecs
import json
import re
import subprocess
import requests

import configparser as ConfigParser

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")

from get_logger import setup_logging
logging=setup_logging()




#0v1# JC  Jan 24, 2024  Init


"""
    SERVER LAYOUT NOTES
    - 

"""

NEXT_GLOBAL_OPTIONS=[]
NEXT_GLOBAL_OPTIONS+=['set full environment']

def notes_for_wt_environment():
    """
        Production
        Demo
        Dev
        (local devs)
    """

    #0v1# JC Jan 24, 2024  Snapshot info for current server setup
    
    ## Global
    region='us-east-2'
    
    ##  FINAWARE PRODUCTION
    ss={}
    ss['name']='wt_finaware_production'
    ss['ip']='3.20.195.157'
    ss['kind']='production'
    ss['key_name']='wt_finaware_new.ppk'
    ss['instance_type']='t3.xlarge'
    
    ## FINAWARE DEV 
    ss={}
    ss['name']='wt_finaware_dev'
    ss['ip']='3.137.103.23'
    ss['kind']='dev'
    ss['key_name']='wt_finaware_dev.ppk'
    ss['instance_type']='t3.large'

    ## FINAWARE DEMO
    ss={}
    ss['name']='wt_finaware_demo'
    ss['ip']='3.134.21.193'
    ss['kind']='demo'
    ss['key_name']='wt_demo_new.ppk'
    ss['instance_type']=''
    


    ### WEB  (aka tracker, aka shivam stuff)
    
    ## WEB PRODUCTION
    ss={}
    ss['todo']=['validate keys']
    ss['name']='wt_web_dev'
    ss['ip']='18.118.67.255'
    ss['endpoint']='registry' # & watchdev
    ss['kind']='production|dev'
    ss['key_name']='wt_web_production_1.ppk' #?
    ss['instance_type']=''

    ## WEB DEV
    ss={}
    ss['todo']=['validate keys']
    ss['name']='wt_web_production'
    ss['endpoint']='watch.'
    ss['ip']='3.134.162.56'
    ss['kind']='production|dev'
    ss['key_name']=''wt_web_production_1.ppk' #?
    ss['instance_type']=''

    ## WEB DEMO
    ss={}
    ss['todo']=['remove keys: wttracker_team, SilverHorcrux, no name, eru@, wt_demo, wt_web_demo1']
    ss['name']='wt_web_demo'
    ss['ip']='3.131.56.150'
    ss['endpoint']='watchdemo'
    ss['kind']='demo'
    ss['key_name']='wt_web_demo_1.ppk'
    ss['instance_type']=''
    
#https://registry.epventures.co/ That is the backend sub domain for dev version.
8:16
#please create a new domain for demo backend. ip is http://3.131.56.150#    

    return



def server_ops():
    ## Default max 5 IP addresses --> request 10
    #https://us-east-2.console.aws.amazon.com/servicequotas/home/services/ec2/quotas
    return



if __name__=='__main__':
    branches=['dev1']

    for b in branches:
        globals()[b]()


"""
web demo server logs but can't log in?
ubuntu@ip-172-31-25-135:~$ last
ubuntu   pts/0        198.52.145.121   Wed Jan 24 18:20   still logged in
ubuntu   pts/0        198.52.145.121   Tue Jan 23 23:27 - 23:27  (00:00)
ubuntu   pts/0        198.52.145.121   Tue Jan 23 23:22 - 23:26  (00:03)
ubuntu   pts/1        198.52.145.121   Tue Jan 23 21:21 - 21:24  (00:03)
ubuntu   pts/1        198.52.145.121   Tue Jan 23 21:20 - 21:20  (00:00)
ubuntu   pts/0        198.52.145.121   Tue Jan 23 21:18 - 21:21  (00:03)
ubuntu   pts/0        198.52.145.121   Tue Jan 23 20:57 - 21:17  (00:20)
ubuntu   pts/0        198.52.145.121   Tue Jan 23 20:56 - 20:57  (00:01)
ubuntu   pts/0        23.243.236.188   Tue Jan 23 20:02 - 20:05  (00:02)
ubuntu   pts/0        23.94.233.2      Tue Jan 23 15:50 - 19:09  (03:19)
ubuntu   pts/0        198.52.145.121   Tue Jan 23 12:04 - 12:04  (00:00)
"""




"""
"""
