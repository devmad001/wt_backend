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

#from routers.timeline_router import router as timeline_router
#from routers import case_router
#from . import timeline, case


#0v1# JC Nov  2, 2023  Setup

"""
    Test entire broadcast loop from mindstate to frontend and back
    
    RECALL:
    - This test is not a unit test, but a full integration test
    - test tells mindstate to send ping to front end

    - mindstate sends broadcast request to fraudapi
    - fraudapi sends broadcast request to dashboards via websocket
    - dashboards send broadcast request to frontend via websocket
    - frontend sends broadcast request to fraudapi via websocket

"""

## ROOT CONFIG
Config = ConfigParser()
Config.read(LOCAL_PATH+"../../w_settings.ini")
FRAUDAPI_PORT=Config.get('services','fraudapi_port')
FRAUDAPI_PORT=8009

## For now, default testing local
TEST_LIVE_LOCAL=True
BASE_ENDPOINT='http://127.0.0.1:'+str(FRAUDAPI_PORT) #Hard coded port in fast_main.py


"""
"""


def ORG_local_broadcast_to(case_id='',message={}):
    """
        RECALL STEPS TO TEST:
        (1)  Ensure case is running + ws is connected ie:
            cd wt_dash
            npm run dev
            http://127.0.0.1:5173
            wt_dash/src/main.tsx
            wt_dash/src/*components
        (2) get case_id:  FraudAPI Components: chase_3_66_5ktransfer
        (3) F12 to see WebSocketProvider caseId: matches means connected.
        (4) Run this and see front update
        
        ## How to update front-end action?
        - recall main.tsx
    """
        
    from w_mindstate.mindstate import validate_message_format
    
    #[ ] remove see mindstate.
    if not case_id:
        case_id='chase_3_66_b4'
        case_id='chase_3_66_5ktransfer' #<-- default react now


    ## ORG MESSAGE KINGS
    message={}
    message['RELOAD_TIMELINE_IFRAME_URL']='' #If blank, will refresh
    is_valid=validate_message_format(message=message) #will raise error
    

    ## May need to load from session db
    session_id=''

    full_endpoint=BASE_ENDPOINT+"/broadcast_listener"

    print("Broadcasting to: at: "+str(full_endpoint))
            
    data={}
    data['case_id']=case_id
    data['session_id']=session_id
    data['message']=message

    ## Pre-check base endpoint?
    try:
        response = requests.post(full_endpoint, json={"data": data})
        is_sent=True
    except Exception as e:
        print("[mindstate] could not post to: "+str(full_endpoint)+" error: "+str(e))
        is_sent=False
    print ("SENT: "+str(is_sent))
   
    return is_sent

def local_broadcast_to(case_id='',message={}):
    """
        RECALL STEPS TO TEST:
        (1)  Ensure case is running + ws is connected ie:
            cd wt_dash
            npm run dev
            http://127.0.0.1:5173
            wt_dash/src/main.tsx
            wt_dash/src/*components
        (2) get case_id:  FraudAPI Components: chase_3_66_5ktransfer
        (3) F12 to see WebSocketProvider caseId: matches means connected.
        (4) Run this and see front update
        
        ## How to update front-end action?
        - recall main.tsx
    """
        
    from w_mindstate.mindstate import validate_message_format
    
    ## INTERNAL MESSAGE CRAFTING
    # message is now crafted more formally (mostly just init_data)
    # may even just be a pass the case_id
    
    ## Internal msg (see fast_ws_v1.py for basic message data dict
    req={}
    req['data']={}
    req['data']['case_id']=case_id
    req['data']['session_id']=''
    req['data']['update_type']='init_data' # if blank will do init data
    req['data']['message']={} #Prepared downstream

    req['data']['force_datahash_change']=True # for dev reasons
    req['data']['force_datahash_change']=False

    
    ## ENDPOINT
    full_endpoint=BASE_ENDPOINT+"/broadcast_listener"
    print("Broadcasting to: at: "+str(full_endpoint))
            
    ## Pre-check base endpoint?
    try:
        #response = requests.post(full_endpoint, json={"data": data})
        response = requests.post(full_endpoint, json=req)
        is_sent=True
    except Exception as e:
        print("[mindstate] could not post to: "+str(full_endpoint)+" error: "+str(e))
        is_sent=False
    print ("SENT: "+str(is_sent))
   
    return is_sent

def test_local_broadcast_to():
    case_id='MarnerHoldingsB'  #<- of course, it should be connected
    local_broadcast_to(case_id=case_id,message={})
    return

if __name__=='__main__':

    branches=['full_integrated_broadcast_to']
    branches=['test_local_broadcast_to']
    for b in branches:
        globals()[b]()


"""

"""
