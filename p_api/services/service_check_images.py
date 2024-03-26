import os, sys
import re

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi import Query


#from sqlalchemy.orm import Session

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")
sys.path.insert(0,LOCAL_PATH+"../../")


from x_modules.k_checks.load_checks_into_db import interface_post_check_to_db


#0v1# JC Feb  1, 2024


"""

    HANDLING PATH FOR CHECK IMAGES
    - wt_hub/k_checks/run_check_pipeline.py -> POST p_api/api/v1/route_checks.py -> here
    - here -> Checks db for meta and image
    
    Future workflow:
    - proper test cases
    - state of processing (has it been integrated?)
    - match check to transaction_id
    - migrate data into Graph knowledge base

"""



def store_posted_check_to_database(case_id,check_meta,image_bytes):
    ## See x_modules/k_checks/load_checks_into_db
    is_valid,is_posted,is_duplicate=interface_post_check_to_db(case_id,check_meta,image_bytes)
    return is_valid,is_posted,is_duplicate




def dev1():

    """
        Focus on querying data:
            
        i)    get all case data  =>  case_id=xxx
        ii)   get check image    =>  check_image_id=xxx
        iii)  get check meta for transaction => transaction_id=xxx
        iv)   get check meta for pdf filename  (?is this how we're matching?)

    """
    return


if __name__ == "__main__":
    dev1()