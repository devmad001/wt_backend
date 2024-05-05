import os
import sys
import codecs
import json
import re
import copy
import datetime
import random

from typing import Dict, Tuple, Any,List

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.routing import APIRoute, Mount,APIRouter

from starlette.responses import FileResponse, HTMLResponse
from pathlib import Path


import asyncio

import configparser as ConfigParser

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")
        

from w_utils import am_i_on_server
from services.ws_service import request_init_data, request_component_refresh, request_set_iframe_url, client_ping, client_pong
from ws_connection_manager import ConnectionManager


from get_logger import setup_logging
logging=setup_logging()

from services.case_BE_service import get_case_report
from api.v1.FE_user import local_get_case_states_and_map_to_view
from pydantic import BaseModel, condecimal
from typing import List, Optional


## TEST HYPERLINK:  __pytest__
        

#0v4# JC  Jan 24, 2024  Migrate to generic ConnectionManager (for more ws support)
#0v3# JC  Nov 30, 2023  Upgrade.
#0v2# JC  Nov 23, 2023  Upgrade for multi ws connection + threading locks
#0v1# JC  Nov 19, 2023  Centralize ws


#########################################
# CENTRALIZE WEBSOCKETS COMMUNICATION
#- removes need for redis or extra queues
#- single broadcast to client target
#########################################


# main.py

## REF:
# /docs
print ("python -m uvicorn fast_main:app --port 8008 --workers 1")  #1 so can --reloadj
#NO --reload AND --workers# print ("python -m uvicorn fast_main:app --reload --port 8008")

app = FastAPI()


####################################
### GLOBAL STATE (use in downstream routers)
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


#TEST# FRAUDWS_PORT=8010 #THIS
####################################


ALLOW_ORIGINS_LIST=[
        "http://127.0.0.1:3000",  # Localhost with specific port
        "http://127.0.0.1:5173",
        "http://127.0.0.1:8008",
        "http://3.134.162.56",
        "http://3.20.195.157",
        "https://3.134.162.56",
        "https://3.20.195.157",
        'https://18.118.67.255',
        "https://watchdev.epventures.co",
        "https://watch.epventures.co"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOW_ORIGINS_LIST,
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)


manager = ConnectionManager()


"""
    MAIN WEBSOCKET ENDPOINT
    - connects at "case_id"-level to provide ws data to FE dashboard (ie/ timeline iframe url)

"""
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    # Extract query parameters
    case_id = websocket.query_params.get("case_id","")
    session_id = websocket.query_params.get("fin_session_id", "")
    user_id='' #TODO
    
    ## CHECK GIVENS
    if not case_id:
        logging.warning(f"WebSocket connection rejected. Missing case_id: {case_id}")


    await manager.connect(websocket, case_id=case_id, session_id=session_id)
    # init_data_message = request_init_data(case_id=case_id,session_id=session_id,user_id=user_id,target='default')
    # await manager.send_message(json.dumps(init_data_message), case_id, session_id)

    try:
        while True:
            # Receive messages from the client
            data = await websocket.receive_text()
            logging.info("[debug] -------------- /ws: "+ data)
            
            try:
                message = json.loads(data)
            except:
                try:
                    data=str(data)
                except:
                    logging.warning("[could not convert ws message data to string]")
                    data=None
                message={}

            if 'action' in message:
                if message['action'] == 'request_init_data':
                    response = request_init_data() #? pass vars

                elif message['action'] == 'request_ping':
                    response = client_pong()

                elif message['action'] == 'get_case_report':
                    if 'case_id' in message:
                        data = get_case_report(message['case_id'])
                        response = {"data": data}
                    else:
                        response = {"error": "No case_id"}

                elif message['action'] == 'list_cases_statuses':
                    if 'user_id' in message:
                        cases = []
                        viewable_cases=local_get_case_states_and_map_to_view(user_id=message['user_id'])
                        cases=viewable_cases+cases
                        
                        ## Auto validation
                        # set state value to '' if state value is not string
                        for case in cases:
                            if not isinstance(case['state'], str):
                                case['state'] = ''
                        
                        ## Sort cases by state if state in ['Processing','Awaiting processing','Ready'] As top priority then the rest
                        cases=sorted(cases, key=lambda k: k['state'] in ['Processing','Awaiting processing','Ready'], reverse=True)
                        response = {"data": cases}
                    else:
                        response = {"error": "No user_id"}

                else:
                    response = {"error": "Unknown action"}
            else:
                response = {"error": "No action"}

            # Send response to the client
            await manager.send_message(json.dumps(response), case_id, session_id)

    except WebSocketDisconnect:
        logging.warning(f"WebSocket disconnected for case_id: {case_id}, session_id: {session_id}")
        await manager.disconnect(case_id, session_id)
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        # Handle other exceptions as needed

# @app.get("/test_messages", response_class=HTMLResponse)
# async def get_test_cases_report():
#     html_content = """
#     <!DOCTYPE html>
#     <html>
#     <head>
#     <title>Chat</title>
#     </head>
#     <body>
#     <h1>WebSocket Chat</h1>
#     <form action="" onsubmit="sendMessage(event)">
#     <label for="action">Action:</label>
#     <input type="text" id="action" autocomplete="off"/><br>
#     <label for="userId">User ID:</label>
#     <input type="text" id="userId" autocomplete="off"/><br>
#     <label for="caseId">Case ID:</label>
#     <input type="text" id="caseId" autocomplete="off"/><br>
#     <label for="finSessionId">Session Id:</label>
#     <input type="text" id="finSessionId" autocomplete="off"/><br>
#     <button>Send</button>
#     </form>
#     <script>
#     var ws = new WebSocket("ws://localhost:8009/ws");
#     ws.onmessage = function(event) {
#         console.log(event.data)
#     };
#     function sendMessage(event) {
#         var action = document.getElementById("action")
#         var userId = document.getElementById("userId")
#         var caseId = document.getElementById("caseId")
#         var finSessionId = document.getElementById("finSessionId")
#         data = {
#             "action": action.value,
#             "user_id": userId.value,
#             "case_id": caseId.value,
#             "fin_session_id": finSessionId.value,
#         }
#         console.log(data)
#         var jsonString = JSON.stringify(data)
#         console.log(jsonString)
#         ws.send(jsonString)
#         event.preventDefault()
#     }
#     </script>
#     </body>
#     </html>
#     """
#     return HTMLResponse(content=html_content)

def fetch_case_status_meta(case_id,wstate={}):
    #[ ] move to services
    #; wstate for tracking global vars
    case_status_meta={}
    
    ## Pseudo timer
    if not wstate.get('pseudo_total_estimated',''):
        wstate['pseudo_total_estimated']=random.randint(5*60,20*60)
        wstate['start_time']=datetime.datetime.now()

    if not wstate.get('last_time',None):
        wstate['last_time']=datetime.datetime.now()
        
    #######
    ## Update metrics
    now=datetime.datetime.now()
    seconds_elapsed=(now-wstate['start_time']).total_seconds()
    
    percentage_elapsed=round(100*seconds_elapsed/wstate['pseudo_total_estimated'],2)
    seconds_total_estimated=wstate['pseudo_total_estimated']
    seconds_remaining=seconds_total_estimated-seconds_elapsed
    
    
    ######
    ## Map to FE variables
    case_status_meta['remaining_time']=seconds_remaining
    case_status_meta['percent_complete']=percentage_elapsed
    case_status_meta['elapsed_time']=seconds_elapsed

    return case_status_meta


@app.websocket("/ws_case_pulse")
async def websocket_case_pulse_data_stream(websocket: WebSocket):
    """
    Provides real-time stats for a case (or set of cases).
    
    DESIGN NOTES:
    - Use single WebSocket connection per case being tracked.
    - Send updates every 5 seconds.
    """

    SEND_EVERY = 5  # Interval in seconds

    case_id = websocket.query_params.get("case_id", "")
    session_id = websocket.query_params.get("fin_session_id", "")
    user_id = websocket.query_params.get("user_id", "")
    
    wstate={}

    await manager.connect(websocket, case_id=case_id, session_id=session_id)

    try:
        while True:
            case_status_meta = fetch_case_status_meta(case_id,wstate=wstate)

            response = {
                'case_id': case_id,
                'status': case_status_meta
            }

            # Send response to the client
            await manager.send_message(json.dumps(response), case_id, session_id)
            
            # Delay the next send
            await asyncio.sleep(SEND_EVERY)

    except WebSocketDisconnect:
        logging.warning(f"WebSocket disconnected for case_id: {case_id}, session_id: {session_id}")
        await manager.disconnect(case_id, session_id)
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        # Handle other exceptions as needed


@app.post("/broadcast_listener")
async def handle_dashboard_update(request: Request):
    ## BROADCAST LISTENER
    #- gets request from application for foreward to FE via websocket
    #- ideally ws msgs are short and specific, practically use init_data only
    # (since has data hash to know when update)
    
    ## Data description:
    #- if no specific update type specified then forward all data (ie/ raw data)
    #- force_datahash_change:  for dev purposes (test_broadcase_ws.py) when want to see elements refresh
    
    data = await request.json()

#D1#    logging.info("[broadcast_listener] (send to FE) data: " + str(data))
    data_length=len(str(data))
    logging.info("[broadcast_listener] (send to FE) data length (beware may be long): " + str(data_length))

    case_id = data['data']['case_id']
    session_id = data['data'].get('session_id', '')
    user_id='' #TBD

    # Determine the type of update
    update_type = data['data'].get('update_type')
    logging.info("[debug] -------------- update type: "+str(update_type))
    
    # Debug options
    force_datahash_change=data['data'].get('force_datahash_change',False)

    # Format the message based on the update type
    if update_type == 'init_data':#
        ## On default and on any update (don't send raw data since that was v0)

        message = request_init_data(case_id=case_id,session_id=session_id,user_id=user_id,target='default',force_datahash_change=force_datahash_change)
        #await manager.send_message(json.dumps(init_data_message), case_id, session_id)

    elif update_type == 'force_timeline_url': #from button_hub.py, from /button_handler
        ## UPDATE main timeline view with forced item
        ## Pass extra data (layout_type)
        #print ("[debug] raw data: "+str(data))

        layout_type=data['data'].get('layout_type','')
        logging.info("[debug] force_timeline_url:  layout type: "+str(layout_type))
            
        
        message = request_init_data(case_id=case_id,session_id=session_id,user_id=user_id,target='default',force_datahash_change=force_datahash_change,layout_type=layout_type)
#        print ("AT: "+str(json.dumps(message,indent=4)))

        ## DO DIRECT INSERT INTO RESPONSE METHOD FOR FORCE URL ASSUMING init_data structure
        did_insert=False
        components=[]
        update_url_if_component_type_is_not=[''] #or are we doing as poition or is_main?
        for component in message['data']['components']:

            ## Update if timeline type (assumed top main !)
            if component['type']=='timeline':   # (#or timeline_1)]
                component['src']=data['data']['url']
                did_insert=True

            ## Catch more -- update if component is_main
            if not did_insert and component.get('is_main',False):
                component['src']=data['data']['url']
                did_insert=True

            ## Force type on waterfall & butterfly (when button clicked) patch Feb 21, 2024
            if component['src'] and '/waterfall' in component['src']: component['type']='waterfall'
            if component['src'] and '/butterfly' in component['src']: component['type']='butterfly'

            components.append(component)
        message['data']['components']=components

        if not did_insert:
            logging.info("------ WARNING ----- did not insert force_timeline_url!!")

        logging.info("[/broadcast_listener] ok new force timeline url: "+str(json.dumps(message,indent=4)))

        #await manager.send_message(json.dumps(init_data_message), case_id, session_id)

    elif update_type == 'component_refresh':
        component_id = data['data'].get('component_id')
        message = request_component_refresh(component_id)

    elif update_type == 'set_iframe_url':
        component_id = data['data'].get('component_id')
        iframe_source = data['data'].get('iframe_source', '')
        message = request_set_iframe_url(component_id, iframe_source)

    elif update_type == 'spawn_download':
        ## Assembled in button_hub
        message = data['data'] #: case_id, session_id, update_type, force_datahash_change, action, url
        #>> could pop stuff but why/
        message.pop('session_id','')

    elif not case_id:
        logging.warning(f"WebSocket connection rejected. Missing case_id: {case_id}")

    else:
        if False:
            ## FULL RAW DATA FORWARD
            message = data['data']  # Regular update

        message = request_init_data(case_id=case_id, session_id=session_id,user_id=user_id,target='default')
        #await manager.send_message(json.dumps(init_data_message), case_id, session_id)


    ######################################################
    #  REVIEW CONNECTION STATUS
    ## Auto broadcast to possibly connected clients (May be many!)
    logging.info("[ws] broadcast_listener fwd message to ws: "+str(case_id))
    is_connected = await manager.connection_exists(case_id)  #Await the async
    logging.info("[WS broadcast listener] connected to receive at: "+str(case_id)+" : "+str(is_connected)+" session: "+str(session_id))
    if True:
        c=0
        for conn in manager.get_connections():
            c+=1
            logging.info("[WS broadcast listener] known connection to: "+str(conn)) #case_id, session_id combo

        if not c:
            logging.info("="*50)
            logging.info("[WS broadcast listener] no known connections!  No broadcast sent!")
            logging.info("[debug]: "+str(manager.active_connections))

            logging.info("="*50)

    ######################################################
    #  Broadcast the message to WebSocket clients
    is_connected = await manager.connection_exists(case_id)
    if is_connected:
        await manager.send_message(json.dumps(message), case_id, session_id)

    return {"status": is_connected}


"""
NOTES
print ("python -m uvicorn fast_main:app --port 8008 --workers 1")  #1 so can --reloadj
#NO --reload AND --workers# print ("python -m uvicorn fast_main:app --reload --port 8008")
"""

if __name__ == "__main__":
    from api.v1.FE_user import router as user_router_v1
    from api.v1.FE_case_view import router as FE_case_view_v1

    app.include_router(user_router_v1, prefix="/api/v1/user", tags=[])
    app.include_router(FE_case_view_v1, prefix="/api/v1/user", tags=[])

    import uvicorn
#    uvicorn.run(app, host="0.0.0.0", port=8008,reload=True)
#    print ("SERVER: "+str(FRAUDWS_PORT))
    cmd='python -m uvicorn fast_ws_1:app --port 8009 --workers 5'
    print ("UBUNTU CMD: "+str(cmd))
    uvicorn.run(app, host="0.0.0.0", port=FRAUDWS_PORT)

    

"""

"""
