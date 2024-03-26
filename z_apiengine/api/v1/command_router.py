import os, sys

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi import Query

from sqlalchemy.orm import Session

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")

from services.command_services import get_process_state_html
from services.command_services import get_process_start_html
from services.command_services import get_process_admin_html

from services.command_services import get_execution_log_html


#0v2# JC Dec 29, 2023  Move to v1
#0v1# JC Nov  2, 2023


"""
    DEBUG VIEW
    - execution logs
    - admin html

"""


router = APIRouter()

# Set up the templates directory
templates = Jinja2Templates(directory="templates")


@router.get('/{case_id}/execution_log', response_class=HTMLResponse)
async def get_execution_log(case_id: str):
    #fin_session_id
    html_content=get_execution_log_html(case_id)
    return HTMLResponse(content=html_content)


#D1  @router.get('/{case_id}/process_status', response_class=HTMLResponse)
#D1  async def process_status(case_id: str):
#D1      #fin_session_id
#D1      html_content=get_process_state_html(case_id)
#D1      return HTMLResponse(content=html_content)
#D1  
#D1  @router.get('/{case_id}/process_admin', response_class=HTMLResponse)
#D1  async def process_admin(case_id: str):
#D1  #D1 #D1       #fin_session_id
#D1      html_content=get_process_admin_html(case_id)
#D1      return HTMLResponse(content=html_content)
    

#v0# @router.get('/{case_id}/process_start', response_class=HTMLResponse)
#v0# async def process_start(case_id: str):
#v0#     html_content=get_process_start_html(case_id)
#v0#     return HTMLResponse(content=html_content)
    
    
"""
exe1_657904fc20668da6f77cd64a_2023_12_13_08_53
657904fc20668da6f77cd64a
http://127.0.0.1:8008/api/v1/case/65858e0c198ceb69d5058fc3/timeline

http://127.0.0.1:8008/api/v1/case/657904fc20668da6f77cd64a/process_status

http://127.0.0.1:8008/api/v1/case/657904fc20668da6f77cd64a/execution_log


"""