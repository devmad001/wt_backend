import os, sys

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi import Query

from sqlalchemy.orm import Session

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")

#from services.command_services import get_process_state_html


#0v1# JC Jan 30, 2024


"""

"""


router = APIRouter()

# Set up the templates directory
#templates = Jinja2Templates(directory="templates")

@router.get('/{case_id}/execution_log', response_class=HTMLResponse)
async def get_execution_log(case_id: str):
    #fin_session_id
    html_content=get_execution_log_html(case_id)
    return HTMLResponse(content=html_content)

    
    
"""

"""