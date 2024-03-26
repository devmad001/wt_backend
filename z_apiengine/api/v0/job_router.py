import os, sys

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi import Query


from fastapi.responses import FileResponse, JSONResponse
#from sqlalchemy.orm import Session


LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")

#from services.general_services import generate_excel
#from services.general_services import serve_pdf_content

#from services.square_service import get_service_square_data


#0v1# JC Nov  5, 2023

"""
    JOB MANAGEMENT
    - migrate from x_components/serve_ui_flask.py
"""


router = APIRouter()



#D1# @router.get("/{case_id}/view_runnings")
#D1# def view_runnings(request: Request):
#D1#     case_id = request.query_params.get('case_id')
#D1#     session_id = request.query_params.get('session_id')
#D1#     print("CASE:", case_id)
#D1#     # Load from cache (mind state)
#D1#     Mind, session_id, answer_dict = local_load_multimodal(case_id)
#D1#     html = 'view_runnings recall elsewhere too'
#D1#     return HTMLResponse(content=html)
#D1# 
#D1# @router.get("/{case_id}/dev_view_case_report")
#D1# @router.get("/{case_id}/dev_view_case_graph")
#D1# @router.get("/{case_id}/dev_runnings_debug")
#D1# def view_runnings_debug(request: Request):
#D1#     case_id = request.query_params.get('case_id')
#D1#     session_id = request.query_params.get('session_id')
#D1#     print("CASE:", case_id)
#D1#     # Load from cache (mind state)
#D1#     Mind, session_id, answer_dict = local_load_multimodal(case_id)
#D1#     html = 'view_runnings_debug recall elsewhere too'
#D1#     return HTMLResponse(content=html)
