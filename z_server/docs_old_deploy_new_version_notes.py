import os
import sys
import time
import codecs
import json
import re
import subprocess

import configparser as ConfigParser

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")

from get_logger import setup_logging
logging=setup_logging()

#0v1# JC  Oct  6, 2023  Init


"""
DEPLOY NOTES Oct 15:
- check new storage endpoint
- 

"""

"""

CODEBASE PREP ON SERVER:
1)  Run new snapshot of cypher samples:
    *ensure cypher_auto.py  is running the generate function
    cd /kb_ak/cypher_playground && python cypher_auto.py
    creates> kb_ask\cypher_playground/snapshot_neo4j_field_samples.json
        > (recall, load_relevant_neo4j_samples() also prunes the final view)

SERVER deploy notes.
a)  Copy over any .ini changes  (recall those aren't sync'd like passwords etc)

b)  requirements.txt update or install
    > python -m pip install -r requirements.txt

c)  REFRESH CONFIG FILE:
        /z_server/define_dashboard.py --> produces w_config_dashboard.json for services definitions (ports etc)

d)  START ENDPOINTS:
        KILL ALL ENDPOINTS (recall, this brings site down)
        pkill python
        
        START ALL:
        /z_server/dev_auto_server.py 
        
        *RUN AGAIN TO SEE IF ALL BOOTED (should show running:True)
        /z_server/dev_auto_server.py 
        
        CHECK:
        ps -aef | grep python    & kill -9 <pid>

e)  System function test run: @pipeline, @cypher, @storage? [ ]




RECALL ENDPOINTS
http://127.0.0.1:8081/case/demo_a/upload
http://127.0.0.1:8081/case/demo_a/process_start
http://127.0.0.1:8081/case/demo_a/process_status
http://127.0.0.1:8081/case/demo_a/run

https://dashboard.epventures.co/case/demo_a/upload
https://dashboard.epventures.co/case/demo_a/process_start
https://dashboard.epventures.co/case/demo_a/process_status
https://dashboard.epventures.co/case/demo_a/run

https://dashboard.epventures.co/case/case_o3_case_single/run



"""


def dev1():
    return

if __name__=='__main__':
    branches=['dev1']
    for b in branches:
        globals()[b]()

