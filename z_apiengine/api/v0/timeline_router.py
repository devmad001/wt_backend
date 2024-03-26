import os, sys
import json

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi import Query
from fastapi.responses import JSONResponse



from sqlalchemy.orm import Session

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")

from services.timeline_service import get_service_timeline_data
from services.timeline_service import get_service_dynamic_timeline_data
from services.barchart_service import get_service_barchart_data
from services.map_service import load_map_poi_features


#0v1# JC Nov  2, 2023


"""
    TIMELINE (crdit/debit)
    maps
"""


##SAMPLE:  http://127.0.0.1:8008/api/v1/case/chase_3_66_5ktransfer/timeline


router = APIRouter()

# Set up the templates directory
templates = Jinja2Templates(directory="templates")


config_file=LOCAL_PATH+'../../../'+'w_config_dashboard.json'
def load_config():
    global config_file
    with open(config_file, 'r') as fp:
        CONFIG = json.load(fp)
    return CONFIG

CONFIG=load_config()


#############################################################
#  TIMELINE
#############################################################
#
@router.get("/{case_id}/timeline_data")
def get_timeline_data(case_id):
    ## Straight timeline_data uses cypher query 
    ## Add session, params, etc.
    data=get_service_timeline_data(case_id)
    return data

@router.get("/{case_id}/timeline_dynamic_data")
def get_dynamic_timeline_data(case_id):
    ## Dynamic timeline_data uses data from answer (multimodal timeline)
    data=get_service_dynamic_timeline_data(case_id)
    return data


@router.get("/{case_id}/timeline_dynamic", response_class=HTMLResponse)
@router.get("/{case_id}/timeline", response_class=HTMLResponse)
async def get_timeline(
    case_id: str, 
    request: Request, 
    maxWidth: int = Query(None),  # None as default, making them optional
    maxHeight: int = Query(None)
    ):
    global CONFIG
    
    #err# session_id=request.session.session_id  #TBD#
    session_id=""
    
    # Check if the request is for dynamic timeline
    is_dynamic = "/timeline_dynamic" in str(request.url)

    
    ## GIVEN:
    #: maxWidth/maxHeight come from top of react App.tsx

    # Sample global var
    am_i_on_server = request.app.state.is_on_server

    # Construct the data URL

    data_endpoint = "timeline_dynamic_data" if is_dynamic else "timeline_data"
    if am_i_on_server:
        #data_url = f'https://{CONFIG["dashboards"]["fraudapi"]["live"]}/api/v1/case/{case_id}/{data_endpoint}?session_id={session_id}'
        ## Hardcode!
        data_url = f'https://core.epventures.co/api/v1/case/{case_id}/{data_endpoint}?session_id={session_id}'
    else:
        data_url = f'http://127.0.0.1:{CONFIG["dashboards"]["fraudapi"]["port"]}/api/v1/case/{case_id}/{data_endpoint}?session_id={session_id}'
        


    print ("Got timeline request for width: "+str(maxWidth)+" and height: "+str(maxHeight))
    # Render and return the template with the context
        #"timeline_index_v2.html", 
        #"timeline_index_v1b_fisheye.html",
    return templates.TemplateResponse(
        "timeline_index_v3.html", 
        {
            "request": request, 
            "data_url": data_url,
            "maxWidth": maxWidth,
            "maxHeight": maxHeight
        }
    )



#############################################################
#  BARCHART
#############################################################
#
@router.get("/{case_id}/barchart_data")
def get_timeline_data(case_id):
    ## Add session, params, etc.
    records,x_axis_title=get_service_barchart_data(case_id)

    data={}
    data['data']={}
    data['data']['records']=records
    
    ## Top level styles
    data['style']={}
    data['style']['main_title']=''
    data['style']['x_axis_title']=x_axis_title
    data['style']['y_axis_title']=''
    
    big_data={}
    big_data['data']=data

    return big_data


@router.get("/{case_id}/barchart", response_class=HTMLResponse)
async def get_barchart(
    case_id: str, 
    request: Request, 
    maxWidth: int = Query(None),  # None as default, making them optional
    maxHeight: int = Query(None)
    ):
    global CONFIG
    
    #v0:  No data in there, sample of how multimodal could load alternative via url
    
    chart_html='index_barchart_v0.html' #No data but idea of what it could look like
    
    #err# session_id=request.session.session_id  #TBD#
    session_id=""
    
    ## GIVEN:
    #: maxWidth/maxHeight come from top of react App.tsx

    # Sample global var
    am_i_on_server = request.app.state.is_on_server

    # Construct the data URL
    if am_i_on_server:
        ## Point to url above!!
        #data_url='https://'+CONFIG['dashboards']['fraudapi']['live']+'/api/v1/case/'+case_id+'/barchart_data?session_id=session_id'
        ## Hard code
        data_url='https://core.epventures.co'+'/api/v1/case/'+case_id+'/barchart_data?session_id=session_id'
    else:
        ## Local
        data_url='http://127.0.0.1:'+str(CONFIG['dashboards']['fraudapi']['port'])+'/api/v1/case/'+case_id+'/barchart_data?session_id=session_id'

    print ("Got timeline request for width: "+str(maxWidth)+" and height: "+str(maxHeight))
    # Render and return the template with the context
    return templates.TemplateResponse(
        chart_html, 
        {
            "request": request, 
            "data_url": data_url,
            "maxWidth": maxWidth,
            "maxHeight": maxHeight
        }
    )



#############################################################
#  MAPS
#############################################################
@router.get("/{case_id}/map/get_pois")
async def get_pois(case_id: str):
    poi_data=load_map_poi_features(case_id)
    return JSONResponse(content=poi_data)

@router.get("/{case_id}/map/view")
async def map_view(request: Request, case_id: str):
    return templates.TemplateResponse("index_here_map_async_v2.html", {
        "request": request,
        "case_id": case_id
    })




#@router.post("/", response_model=CaseInDB)
#def create_case(case: CaseCreate, db: Session = Depends(get_db)):
#    db_case = Case(**case.dict())
#    db.add(db_case)
#    db.commit()
#    db.refresh(db_case)
#    return db_case
#
#
#@router.get("/")
#def get_all_cases():
#    return {"message": "All cases returned"}
#
#@router.post("/")
#def create_case(case: CaseCreate):
#    # Logic to create a new case
#    return {"message": "Case created"}
