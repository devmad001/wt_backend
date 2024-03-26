import os, sys
import urllib.parse

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi import Query
from fastapi import status
from typing import Any, Dict, List, Optional

from fastapi.responses import FileResponse, JSONResponse
#from sqlalchemy.orm import Session


LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")

from services.fixed_query_services import FIXED_transaction_tracker


from get_logger import setup_logging
logging=setup_logging()



#0v1# JC Jan 23, 2024  Setup



"""
    ROUTER FOR FIXED DATA QUERIES
    - "canned" queries

"""


router = APIRouter()


###############################################################
#  TRANSACTION TRACKER
###############################################################
# case_id='65a8168eb3ac164610ea5bc2' ## Big new age

@router.get(
    "/{case_id}/transaction_tracker",
    response_model=Dict[str, Any],
    summary="Retrieve Transaction Tracker Data",
    description="This endpoint retrieves transaction tracker data for a given case ID.",
    responses={
        200: {"description": "Data successfully retrieved"},
        404: {"description": "Case ID not found"}
    }
)

async def handle_fixed_query_transaction_tracker(case_id: str,  fin_session_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Generate Excel Handler

    This function handles requests to retrieve transaction tracker data associated with a specific case ID.
    It asynchronously queries the transaction tracker data using the `FIXED_query_transaction_tracker` function.

    Args:
    case_id (str): The unique identifier for the case.

    Returns:
    Dict[str, Any]: A dictionary containing the case ID and corresponding transaction data.
    """
    #[ ] add fin_session_id

    data_results = await FIXED_transaction_tracker(case_id=case_id)
    if data_results is None:
        return Response(status_code=status.HTTP_404_NOT_FOUND)
    
    response = {
        "case_id": case_id,
        "data": data_results
    }
    return response




