print ("python -m uvicorn papi_main:app --port 8007 --workers 2")
import os
import sys
import codecs
import json
import re
import datetime

from typing import Dict, Tuple, Any,List

import uvicorn

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
from router import router_v1

from get_logger import setup_logging
logging=setup_logging()


#0v1# JC  Jan 30, 2024  Use fast_main as model for this



#### CREATE APP

def create_app(run_version: str = "v1") -> FastAPI:
    app = FastAPI()
    app.include_router(router_v1, prefix="/api/v1/case", tags=[])
    return app


app = create_app()

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
SERVICEAPI_PORT=Config.get('services','service_port')
####################################


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:3000",  # Localhost with specific port
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5177",
        "http://127.0.0.1:8008",
        "http://3.134.162.56",
        "http://3.20.195.157",
        'http://18.118.67.255',
        "https://3.134.162.56",
        "https://3.20.195.157",
        'https://18.118.67.255',    
        "https://watchdev.epventures.co",
        "https://watch.epventures.co",
        "https://nets.epventures.co"
        # Add other origins as needed
    ],
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)



# Mount the static directory to the /static path
app.mount("/static", StaticFiles(directory=LOCAL_PATH+"static"), name="static")


## SERVE MISC STATIC FILES
@app.get("/static/{file_path:path}")  # Using path converter to accept any string, including slashes.
async def serve_static(file_path: str):
    print("Serving:", file_path)
    file_location = Path(__file__).parent / "static" / file_path

    if file_path.endswith('.js'):
        return FileResponse(path=file_location, media_type='application/javascript')

    return FileResponse(path=file_location)

@app.get("/favicon.ico")
async def favicon():
    fav_path=LOCAL_PATH+"static/favicon.ico"
    return FileResponse(str(fav_path), media_type='image/vnd.microsoft.icon')        




if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=SERVICEAPI_PORT)
    




    








