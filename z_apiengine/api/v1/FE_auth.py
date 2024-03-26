import os, sys
import time

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi import Query
from pydantic import BaseModel, Field
from typing import List, Optional


LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")

from services.case_service import does_case_exist
from z_apiengine.database_models import FinSession
from z_apiengine.database import SessionLocal


#0v2# JC  Dec  8, 2023  Store fin_session_id ot db
#0v1# JC  Nov 28, 2023


"""
    AUTHENTICATION HANDSHAKE
    - store key & user id
    - link user to case??

"""


router = APIRouter()



class AuthRequest(BaseModel):
    user_id: str = Field(..., description="The unique identifier of the user")
    token: str = Field(..., description="The authentication token for the user")
    expiry: int = Field(43200, description="The expiry time in seconds, default is 12 hours (43200 seconds)")

    class Config:
        schema_extra = {
            "example": {
                "user_id": "user123",
                "token": "abcdef12345",
                "expiry": 3600  # Example expiry time in seconds
            }
        }


@router.post("/auth_handshake", summary="Authenticate a User",
             description="This endpoint authenticates a user by their ID and token.")
async def auth_handshake(auth_request: AuthRequest, request: Request):
    """
    Perform an authentication handshake using the provided user ID and token.

    Args:
        auth_request (AuthRequest): The authentication request containing user ID and token.
        request (Request): The request object.

    Returns:
        dict: A dictionary with the authentication status.
    """
    #auth_request_dict = auth_request.dict()
    user_id=auth_request.user_id
    user_id=None
    print ("[ ] user_id is actual .id integer not the external str")
    
    if False:
        ip_address = request.client.host if request.client.host else None
        user_agent = request.headers.get('user-agent') if 'user-agent' in request.headers else None
    
        auth_session = FinSession(
            token=auth_request.token,
            expiry=auth_request.expiry,
            ip_address=ip_address,
            user_agent=user_agent
        )
    
        # Add logic here to save auth_session to the database
        with SessionLocal() as db:
            db.add(auth_session)
            db.commit()
            
    ## Informal status
    if not auth_request.user_id:
        return {"status": "error", "message": "User ID is required"}
    else:
        return {"status": "ok"}


## GLOBAL STATE CHECK
# Does case_id exist anywhere

@router.get("/is_case_id_exist", response_model=bool)
async def is_case_id_exist(case_id: str, fin_session_id: Optional[str] = None):
    """
    Check if a given case_id exists.

    - **case_id**: The unique identifier of the case to check.
    - **fin_session_id**: An optional (for now) fin_session_id identifier for additional context or filtering.

    
    Returns True if the case_id exists, False otherwise.
    """
    # Implement logic to check if case_id exists
    # This is a placeholder for the actual logic
    # Example:
    # exists = check_case_id_existence(case_id, fin_session_id)
    # return exists
    exists=does_case_exist(case_id)

    return exists  # Placeholder return value





