# test_main.py
import os,sys
import json
import requests

from fastapi.testclient import TestClient

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../../../../")
        
        

#0v1# JC  Dec 28, 2023  Setup test

"""
   Case status list etc.

"""
        
## Allow for local debug -- but usually not needed
if not __name__=='__main__':
    from z_apiengine.fast_main import app  # Import the FastAPI app instance from your main module
    client = TestClient(app)


"""
    RECALL TESTING USING:
    - python -m pytest
    - python -m pytest tests/test_timeline.py for specific
"""

def TBD_test_post_fin_session_id():
    #** jon tested with POSTMAN desktop 
    # Define the data to be posted
    post_data = {
        "fin_session_id": "example_session_id",
        # Include other fields if required by your endpoint
    }

    # Send a POST request to the appropriate endpoint
    response = client.post("/path/to/your/endpoint", json=post_data)

    # Check that the response status code is 200 (OK) or other expected status code
    assert response.status_code == 200

    # Optionally, check the content of the response
    # For example, checking if the response confirms that the data was saved
    data = response.json()
    assert "success" in data  # Replace with your actual success confirmation key

    # Additional assertions as required for your application logic


def dev_test_cases_list():
    print ("dev testing user...")
    
    b=['run_via_app']
    b=['run_via_url_request']
    
    if 'run_via_app' in b:
    
        from z_apiengine.fast_main import app  # Import the FastAPI app instance from your main module
        client = TestClient(app)
    
        user_id_dev='6571b86a88061612aa2fc8b7'
    
        response = client.get("/api/v1/user/list_cases_statuses?user_id="+user_id_dev)
        print ("RES: "+str(response.json()))
    
    else:
        user_id_dev='6571b86a88061612aa2fc8b7'
        local_url= 'http://127.0.0.1:8008/'
        local_url+='api/v1/user/list_cases_statuses?user_id='+user_id_dev
        print ("GET TO: "+str(local_url))
        response=requests.get(local_url)
        print ("RES: "+str(response.json()))
        
    """
    FE_user.py -> local_get_case_states_and_map_to_view()
    FE_cases_page_states.py -> describe_case_processing_status(case_id)
    
    from services.FE_cases_page_states import interface_list_cases_states
    from c_jobs_manager.mega_job import interface_get_verbose_job_status

    """
    return


def dev1():
    print ("**recall:  run with python -m pytest")
    raise Exception("dev1 not implemented")

    return


if __name__=='__main__':
    branches=['dev_test_cases_list']
    for b in branches:
        globals()[b]()
    
