import os, sys
import json

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi import File, Form, UploadFile, Header
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi import Query
from typing import Optional

from sqlalchemy.orm import Session


LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")
sys.path.insert(0,LOCAL_PATH+"../..")

from services.service_check_images import store_posted_check_to_database



#0v1# JC Feb  1, 2024


"""
    Handle check meta + image posts into db
    - advertise service capabilities to internal client via json


"""

router = APIRouter()



def API_get_system_auth_key():
    system_auth_key = "CHANGE_ME_AUTH_KEY"
    return system_auth_key

#? receiving None even when set correctly?!
def verify_auth_key(auth_key: Optional[str] = Header(None)):
    # Replace 'your_auth_key' with your actual auth key
    expected_auth_key = API_get_system_auth_key()
    print ("GOT auth key (should not be None): "+str(auth_key))
    if auth_key != f"Bearer {expected_auth_key}":
        print ("[expected]: "+str(expected_auth_key)+" got: "+str(auth_key))
        raise HTTPException(status_code=401, detail="Unauthorized")
    return True


"""
    Expect:  r=requests.post(backend_api_post_handler, data=post_data, files=post_files)
"""

#* custom header check for now since Header not reading auth correctly


@router.post("/{case_id}/post_check")
async def handle_check_meta_image_post(
    request: Request,
    case_id: str,
    check_meta: str = Form(...),
    check_image: UploadFile = File(...)
    ):
    meta={}

    #######################################################################
    # Retrieve the Authorization header directly from the request
    auth_key = request.headers.get('Authorization')
    # Fetch the expected auth key (replace 'API_get_system_auth_key' with your actual function)
    expected_auth_key = API_get_system_auth_key()
    # Construct the expected Authorization header value
    expected_header_value = f"Bearer {expected_auth_key}"
    # Verify the Authorization header
    if auth_key != expected_header_value:
        print(f"[Error] Authorization failed. Expected: {expected_header_value}, Received: {auth_key}")
        raise HTTPException(status_code=401, detail="Unauthorized")
    print("Authorization successful. Proceeding with request handling.")
    #######################################################################

    # Debugging info
    print(f"[debug] raw check_meta: {check_meta}")

    # Convert 'check_meta' from JSON string to a Python dict
    check_meta_json = json.loads(check_meta)
    print(f"[debug] parsed check_meta: {check_meta_json}")

    # Read the binary content of the uploaded file
    check_image_bytes = await check_image.read()
    
    is_valid,is_posted,is_duplicate=store_posted_check_to_database(case_id,check_meta_json,check_image_bytes)

     #Assuming 'is_valid' and 'is_posted' are determined here
    if is_duplicate:
        meta['is_duplicate']=True
    elif not is_valid:
        raise HTTPException(status_code=400, detail="Invalid check_meta")
    elif not is_posted:
        raise HTTPException(status_code=500, detail="Failed to post check to database (or duplicate)")

    # Don't forget to close the file (UploadFile object)
    await check_image.close()
    
    # Return a success message or any other response as needed
    return {"status": "ok", "meta":meta}


@router.get("/{case_id}/ping_check")
async def handle_ping(
    case_id: str
):
    #auth_key_verified: bool = Depends(verify_auth_key)
    # Debug from wt_hub call
    return {"status": "ok"}

    
"""

"""