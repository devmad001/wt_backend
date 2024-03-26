import os, sys

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi import Query
from fastapi.responses import FileResponse, JSONResponse

from pydantic import BaseModel

#from sqlalchemy.orm import Session


LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")

from services.finaware_services import front_get_processing_case_status


from get_logger import setup_logging
logging=setup_logging()



#0v1# JC Nov 15, 2023

"""
    FINAWARE SERVICES ROUTER
"""


router = APIRouter()


###############################################################
#  FRONT-END (FinAware)
###############################################################

#class CaseStatusResponse(BaseModel):
#    case_id: str
#    is_case_started: bool
#    is_case_running: bool
#    is_case_ready_to_query: bool
#    last_state: str
#    case_status_word: str
#    case_files: list[str]
#    estimated_case_running_time_remaining_m: int
#    age_of_last_active_m: float
#    has_job_ever_finished: bool
#    job_page_count: int
#
#@router.get("/{case_id}/get_case_processing_status", response_model=CaseStatusResponse)
#async def get_case_processing_status(case_id: str, request: Request):
#    a=stopp_checkk
#    # Assuming front_get_processing_case_status returns a dictionary matching the CaseStatusResponse model
#    data_dict = front_get_processing_case_status(case_id=case_id)
#    return data_dict['case_state']
#
##    #  {'case_id': 'case_atm_location', 'is_case_started': True, 'is_case_running': False, 'is_case_ready_to_query': True, 'last_state': 'end_KBAI_processing_pipeline', 'case_status_word': 'Ready to Answer', 'case_files': ['07A210E6-B60D-46B6-9D40-9B3239237F05-list.pdf'], 'estimated_case_running_time_remaining_m': 0, 'age_of_last_active_m': 14853.6, 'has_job_ever_finished': True, 'job_page_count': 5}