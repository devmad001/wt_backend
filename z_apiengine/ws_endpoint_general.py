import os
import sys
import codecs
import json
import re
import copy
import datetime

from typing import Dict, Tuple, Any,List

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.routing import APIRoute, Mount,APIRouter

from starlette.responses import FileResponse
from pathlib import Path


import asyncio

import configparser as ConfigParser

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")
        
from w_utils import am_i_on_server
from fast_ws_v1 import ALLOW_ORIGINS_LIST 
from ws_manager import ConnectionManager

from get_logger import setup_logging
logging=setup_logging()

#0v1# JC  Jan 15, 2024  ws endpoint for dashboard updates (time estimation etc)


"""
    WEBSOCKET ENDPOINT FOR DASHBOARD UPDATES
    [A]  Real-time case processing status
    ?support for multiple cases?

"""

raise Exception("Not implemented/tested but continue here")


## REF:
print ("python -m uvicorn fast_main:app --port 8008 --workers 1")  #1 so can --reloadj

app = FastAPI()

####################################
### APP CONFIGURATION
app.state.is_on_server = am_i_on_server()

## CONFIG FOR BROADCASTS
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


app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOW_ORIGINS_LIST,
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)
####################################

manager = ConnectionManager()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    # Extract query parameters
    case_id = websocket.query_params.get("case_id","")
    session_id = websocket.query_params.get("fin_session_id", "")
    user_id=''
    
    ## CHECK GIVENS
    if not case_id:
        logging.warning(f"WebSocket connection rejected. Missing case_id: {case_id}")

    await manager.connect(websocket, case_id=case_id, session_id=session_id)
    init_data_message = request_init_data(case_id=case_id,session_id=session_id,usre_id=user_id,target='default')
    await manager.send_message(json.dumps(init_data_message), case_id, session_id)

    try:
        while True:
            # Receive messages from the client
            data = await websocket.receive_text()
            
            try:
                message = json.loads(data)
            except:
                try:
                    data=str(data)
                except:
                    logging.warning("[could not convert ws message data to string]")
                    data=None
                message={}

            # Process different types of messages
            if message['action'] == 'request_init_data':
                response = request_init_data()
            elif message['action'] == 'request_ping':
                response = client_pong()
            else:
                response = {"error": "Unknown action: "+str(data)}

            # Send response to the client
            await manager.send_message(json.dumps(response), case_id, session_id)

    except WebSocketDisconnect:
        logging.warning(f"WebSocket disconnected for case_id: {case_id}, session_id: {session_id}")
        await manager.disconnect(case_id, session_id)
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        # Handle other exceptions as needed
        

if __name__ == "__main__":
    import uvicorn
#    uvicorn.run(app, host="0.0.0.0", port=8008,reload=True)
    uvicorn.run(app, host="0.0.0.0", port=FRAUDWS_PORT)

    

"""

"""
