import os, sys

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi import Query

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")

from services.square_service import get_service_square_data_html
from services.square_service import get_service_square_data_records


#0v1# JC Nov 23, 2023


"""
    VERSION: v1
    SQUARE VIEW OR "TABLE VIEW"
    (v1 returns json data records for FE rendering)
    
    Test at: /w_test/test_fastapi/api/v1/test_square_table.py

"""


router = APIRouter()

# Set up the templates directory
templates = Jinja2Templates(directory="templates")


@router.get("/{case_id}/square_data")
async def get_square(case_id, request: Request):
    ## Render as html
    #- see: x_components/serve_ui_flask.py -> dynamic_square
    #am_i_on_server = request.app.state.is_on_server

    list_of_dicts=get_service_square_data_records(case_id)
    
    the_json={}
    the_json['data']=list_of_dicts

    return the_json


#v0 html view as well in v1
@router.get("/{case_id}/square")
async def get_square(case_id, request: Request, response_class=HTMLResponse):
    ## Render as html
    #- see: x_components/serve_ui_flask.py -> dynamic_square
    
    am_i_on_server = request.app.state.is_on_server

    html=get_service_square_data_html(case_id)

    return templates.TemplateResponse(
        "square_jinja1.html",
        {
            "request": request,
            "dynamic_content": html
        }
    )