print ("python -m uvicorn fast_main:app --port 8008 --workers 2")
import os
import sys
import codecs
import json
import re
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
from router import router_v1
from router import router_v0

from api.v1.FE_auth import router as auth_router_v1
from api.v1.FE_user import router as user_router_v1

from get_logger import setup_logging
logging=setup_logging()



#0v3# JC  Nov 23, 2023  Start formal v1 api for FinAware (and v0 for dev)
#0v2# JC  Nov 10, 2023  Send ws
#0v1# JC  Oct 26, 2023  Setup


ASSUME_SEND_WS_TO_ALL_CASE_ID_CONNECTIONS=True   #ie/ multiple logged in users with same case will get dashboard updates

#NO --reload AND --workers# print ("python -m uvicorn fast_main:app --reload --port 8008")

def create_app(run_version: str = "v1") -> FastAPI:
    app = FastAPI()

    if run_version == "v0":
        app.include_router(router_v0, prefix="/api/v0/case", tags=[])
    elif run_version == "v1":
        app.include_router(router_v1, prefix="/api/v1/case", tags=[])
        ## Include auth separately
        app.include_router(auth_router_v1, prefix="/api/v1", tags=[])
        app.include_router(user_router_v1, prefix="/api/v1/user", tags=[])
    else:
        raise ValueError("Invalid API version specified.")

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
FRAUDAPI_PORT=Config.get('services','fraudapi_port')
####################################


#app.add_middleware(
#    CORSMiddleware,
#    allow_origins=["*"],  # List of origins
#    allow_credentials=False,
#    allow_methods=["*"],  # Allow all methods
#    allow_headers=["*"],  # Allow all headers
#)
#print ("[warning] if allow_credentials=True then allow_origins can't be *")

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

print ("[warning] if allow_credentials=True then allow_origins can't be *")


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



###########################################
# ROUTES INFO
###########################################
# Define a function to recursively collect route information
def get_route_info(route) -> List[Dict[str, Any]]:
    if isinstance(route, APIRoute):
        return [{
            "path": route.path,
            "name": route.name,
            "methods": list(route.methods),
        }]
    elif isinstance(route, Mount):
        if isinstance(route.app, StaticFiles):
            # For StaticFiles, we can't list sub-routes, but we can indicate that it serves static files
            return [{
                "path": route.path,
                "name": getattr(route, "name", "static"),
                "methods": ["GET"],
                "description": "Static Files"
            }]
        else:
            # If it's not StaticFiles, we proceed assuming it has routes (FastAPI or APIRouter)
            return [item for sub_route in route.app.routes for item in get_route_info(sub_route)]
    else:
        # For any other type of route, modify or extend as needed
        return [{
            "path": route.path,
            "name": getattr(route, "name", None),
            "methods": None,
        }]



# After all routes are defined
def get_all_routes():
    url_list = [item for route in app.routes for item in get_route_info(route)]
    return url_list
    


if __name__ == "__main__":
    import uvicorn
#    uvicorn.run(app, host="0.0.0.0", port=8008,reload=True)
#    logging.config.dictConfig(LOGGING_CONFIG)
    uvicorn.run(app, host="0.0.0.0", port=FRAUDAPI_PORT)

    


"""

project_root/
│
├── app/
│   ├── main.py            # FastAPI initialization and application instance
│   ├── api/
│   │   ├── v1/            # Versioning your API is a good practice
│   │   │   ├── router.py  # Collects all the routers from the different modules
│   │   │   ├── case.py
│   │   │   ├── timeline.py
│   │   │   └── ...
│   ├── models/
│   │   ├── __init__.py    # Imports all ORM models for easy access
│   │   ├── case.py
│   │   ├── timeline.py
│   │   └── ...
│   ├── services/          # Business logic here
│   │   ├── case_service.py
│   │   ├── timeline_service.py
│   │   └── ...
│   └── database.py        # Database connection and session management
│
└── ...

"""
