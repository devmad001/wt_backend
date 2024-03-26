import os
import sys
import codecs
import json
import re
import copy
import datetime

from typing import Dict, Tuple, Any,List

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
import asyncio
import websockets  #pip install websockets

import configparser as ConfigParser

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")
        
from w_utils import am_i_on_server
from fast_ws_v1 import ALLOW_ORIGINS_LIST 

from get_logger import setup_logging
logging=setup_logging()




#0v1# JC  Jan 24, 2024  ws endpoint for dashboard updates (time estimation etc)


"""
    WEBSOCKET CLIENT (for testing)
    -

"""


####################################
### APP CONFIGURATION
## CONFIG FOR BROADCASTS
if False:
    config_file=LOCAL_PATH+'../'+'w_config_dashboard.json'
    def load_config():
        global config_file
        with open(config_file, 'r') as fp:
            CONFIG = json.load(fp)
        return CONFIG
    
    app.state.DASH_CONFIG=load_config()  #Ports or org dashboard options
    
    ### ROOT CONFIG
    Config = ConfigParser.ConfigParser()
    Config.read(LOCAL_PATH+"../w_settings.ini")
    FRAUDAPI_PORT=Config.get('services','fraudapi_port')  #ie/ 8008
    FRAUDWS_PORT=Config.get('services','fraudws_port')    #ie/ 8010
    logging.info("[WS] PORT: "+str(FRAUDWS_PORT))
####################################



async def websocket_client(uri, case_id, session_id):
    
    async with websockets.connect(uri) as websocket:
        # Connect to the server
        await websocket.send(json.dumps({"action": "connect", "case_id": case_id, "session_id": session_id}))
        
        # Wait for a response from the server after connecting
        response = await websocket.recv()
        print(f"< Server: {response}")

        # Keep the connection open and listen for messages
        try:
            async for message in websocket:
                print(f"< Message: {message}")
        except websockets.exceptions.ConnectionClosed as e:
            print(f"Connection closed: {e}")


if __name__ == "__main__":
    uri = "ws://your-websocket-server.com"  # Replace with your WebSocket server URI

    case_id = "your_case_id"  # Replace with your case ID
    session_id = "your_session_id"  # Replace with your session ID

    if 'standard ws' in []:
        uri = "ws://127.0.0.1:8009/ws?case_id="+case_id

    elif 'ws_case_plus':
        uri = "ws://127.0.0.1:8009/ws_case_pulse?case_id="+case_id

    asyncio.get_event_loop().run_until_complete(
        websocket_client(uri, case_id, session_id)
    )
    

    

"""
"""
