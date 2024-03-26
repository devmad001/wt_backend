print ("python -m pytest -s test_pytest_ws_v1.py") #-s is no capture so show prints

import os, sys
import re

import pytest
from starlette.testclient import TestClient


LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")

from fast_ws_v1 import app  # Import your FastAPI app


#0v1# JC  Jan 24, 2024  ws test  [ ]TODO:  register into overall 


#### ROOT CONFIG
#Config = ConfigParser.ConfigParser()
#Config.read(LOCAL_PATH+"../w_settings.ini")
#FRAUDAPI_PORT=Config.get('services','fraudapi_port')  #ie/ 8008
#FRAUDWS_PORT=Config.get('services','fraudws_port')    #ie/ 8009
#LOCAL_ENDPOINT='http://127.0.0.1:8010/ws'

LOCAL_ENDPOINT='/ws'  #Test endpoint

#ERR#        assert ws.is_connected

## NOTES:
#- starlette has no is_connect state so check on raw connection


@pytest.mark.asyncio
async def test_websocket_connection():
    client = TestClient(app)
    with client.websocket_connect(LOCAL_ENDPOINT+'?case_id=test_case&fin_session_id=test_session') as ws:
        try:
            # Attempt to send and receive a message
            ws.send_json({'action': 'request_init_data'})
            response = ws.receive_json()
            print ("[debug] response: "+str(response))
            assert 'action' in response and response['action'] == 'init_data'
            connection_successful = True
        except Exception:
            connection_successful = False
        
        assert connection_successful

@pytest.mark.asyncio
async def test_websocket_connection_no_case_id():
    client = TestClient(app)
    # Attempt to connect without case_id and check the server's response
    with client.websocket_connect(LOCAL_ENDPOINT+'?fin_session_id=test_session') as ws:
        try:
            # If the server does not disconnect, send a ping to test the connection
            ws.send_json({'action': 'request_ping'})
            ws.receive_json()
            connection_successful = True
        except Exception:
            connection_successful = False

        assert not connection_successful
        