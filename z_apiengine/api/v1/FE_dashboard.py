import os, sys

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi import Query

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")

#from services.square_service import get_service_square_data_records


#0v1# JC Nov 28, 2023


"""
    DASHBOARD
    - mostly ws
    (push logic to services)

"""


router = APIRouter()


## get version of ws
@router.get("/get_dashboard")
async def get_dashboard(case_id, request: Request):
    the_json={}
    the_json['status']='ok'
    return the_json


## Buttons

## FAQs


def dev1():
    
    print ("*** MOVEDTO FE_ws_protocol...")

    dash={}
    dash['dashboard']={}
    
    dash['dsettings']={}
    
    ## Dashboard layout:
    dash['dsettings']['layout_type']='view_tall_chart'  #timline right half
    dash['dsettings']['layout_type']='view_standard_3'  #main timeline, bottom two
    dash['dsettings']['custom_layout']={}               # maximize window state, etc.
    
    ## Components:
    dash['components']=[]
    
    ## Square def
    component_square={}
    component_square['type']='square'
    component_square['id']='square_1'
    component_square['position']='bottom_right'
    component_square['component_name']='SquareComponent'
    component_square['src']=None
    dash['components'].append(component_square)
    
    ## Timeline def
    component_timeline={}
    component_timeline['type']='timeline'
    component_timeline['id']='timeline_1'
    component_timeline['position']='bottom_left'
    component_timeline['component_name']='TimelineComponent'
    component_timeline['src']=None
    dash['components'].append(component_timeline)
    
    ## Chat def
    component_chat={}
    component_chat['type']='chat'
    component_chat['id']='chat_1'
    component_chat['position']='bottom_left'
    component_chat['component_name']='IFRAMEComponent'
    component_chat['src']='http://core.epventures.com/api/v1/get_chat?case_id=1'
    dash['components'].append(component_chat)
    
    
    print ("DASH OPTION:")
    
    print (str(dash))

    return



if __name__=='__main__':
    branches=['dev1']
    for b in branches:
        globals()[b]()


"""

{'dashboard': {}, 'dsettings': {'layout_type': 'view_standard_3'}, 'components': [{'type': 'square', 'id': 'square_1', 'position': 'bottom_right', 'component_name': 'SquareComponent', 'src': None}, {'type': 'timeline', 'id': 'timeline_1', 'position': 'bottom_left', 'component_name': 'TimelineComponent', 'src': None}, {'type': 'chat', 'id': 'chat_1', 'position': 'bottom_left', 'component_name': 'IFRAMEComponent', 'src': 'http://core.epventures.com/api/v1/get_chat_NOTEXISTS?case_id=1'}]}

"""



































