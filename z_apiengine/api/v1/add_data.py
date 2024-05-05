import os, sys

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi import Query

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")

from services.add_data_service import update_data_tx

from pydantic import BaseModel
from datetime import date, time, timedelta
from typing import Annotated


class Item(BaseModel):
    transaction_id:str
    transaction_amount: float
    transaction_description: str | None = None
    transaction_date:  str | None  = None,
    section: str | None = None 
    page_number: int 

#0v1# JC Nov 23, 2023
 

router = APIRouter()

# Set up the templates directory
templates = Jinja2Templates(directory="templates")


@router.post("/{case_id}/update_data")
async def add_data(case_id,properties:Item, request: Request):
   
    update_data_tx(case_id,properties)
    
    the_json={}

    return the_json

 