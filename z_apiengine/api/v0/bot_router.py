import os, sys
import re

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi import Query, Depends

from pydantic import BaseModel

from typing import Optional

from sqlalchemy.orm import Session

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")

from services.bot_service import handle_question, handle_feedback


#0v1# JC Nov  2, 2023

"""
    USER COMMANDS OR QUESTIONS
    - see:  app_parenty.py
    
    - wt_flask_handle too

"""


router = APIRouter()

# Set up the templates directory
templates = Jinja2Templates(directory="templates")


## From wt_flask_handle
# FastAPI path operation for '/case/{case_id}/view/submit'
@router.api_route('/{case_id}/view/submit', methods=['POST', 'GET'])
async def handle_submit(
    case_id: str,
    query: Optional[str] = None
):
    """
    BUTTON CLICK OR SUBMIT HANDLER
    - Handles submissions for specific case_ids
    """

    output = {}
    
    if query:
        output,meta=handle_question(question, case_id)
        
    else:
        output['error'] = 'No query parameter provided'

    return JSONResponse(content=output)



# Define the FastAPI route
@router.api_route('/{case_id}/ask', methods=['POST', 'GET'])
async def handle_ask(
    request: Request, 
    case_id: str,
    query: Optional[str] = None,
    session_id: Optional[str] = None,
):
    """
    STANDARD CHATBOT QUESTION HANDLER
    """
    output = {}

    # Placeholder for user authentication
    # if not your_authentication_check():
    #     raise HTTPException(status_code=403, detail="Forbidden: The user doesn't have access to the resource")

#    # Sanitize the path
#    path = re.sub(r'^/', '', path)
#    path = re.sub(r'/ask', '', path)
#
#    # Log the received path and query
#    print(f"GOT PATH: {path}")

    print(f"GOT params: {request.query_params}")
    print(f"GOT query: {query}")
    
    meta={}
    
    if query and case_id:
        #** hard fail
        output,meta=handle_question(query, case_id,params=request.query_params)
        try:
            pass

        except Exception as e:
            print(f"[bot_router.py] handle_bot_query openai maybe error: {e}")
            if 'auth_subrequest_error' in str(e):
                output['generated_text'] = 'auth_subrequest_error'
            else:
                output['generated_text'] = 'Internal error 1008'
    else:
        output['generated_text'] = "You forgot to ask properly."

    if False:
        print(f"[done handle ask]: {output}")
        ## df can't be dumped.  But is this just a field or the whole output?
        for kk in output:
            print ("[handle_ask] output: "+str(kk)+" -- "+str(type(output[kk])))
            
    ## Catch bad output format
    if isinstance(output.get('generated_text',''), dict):
        logging.warning("[generated text is dict, not str]: "+str(output))
        output['generated_text'] = ""


    return JSONResponse(content=output)


class FeedbackData(BaseModel):
    feedback: dict


# Define the FastAPI route
@router.api_route('/{case_id}/submit_feedback', methods=['POST'])
async def handle_submit_feedback(
    request: Request, 
    case_id: str,
    feedback_data: FeedbackData = Depends()):

    output = {}
    feedback={}
    
    # Accessing the feedback data sent in the POST request
    
    if request.method == "POST":
        # Handle POST request
        feedback = feedback_data.feedback
        
    ## Posted as dict with inner list?  Clean here to dict
    if 'feedback' in feedback:
        feedback=feedback['feedback']
    if isinstance(feedback, list) and len(feedback)==1:
        feedback=feedback[0]

    feedback['case_id']=case_id

    if feedback:
        try:
            # Assuming handle_feedback is a function you've defined to process the feedback
            output, meta = handle_feedback(feedback, case_id)
        except Exception as e:
            print(f"[Error in handle_feedback]: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    return JSONResponse(content=output)
        
