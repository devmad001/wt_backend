# test_main.py
import os,sys
import json

from fastapi.testclient import TestClient

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../../../../")
        
        

#0v1# JC  Dec  8, 2023  Setup test

        
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



def dev1():
    print ("**recall:  run with python -m pytest")
    raise Exception("dev1 not implemented")

    return


if __name__=='__main__':
    branches=['dev1']
    for b in branches:
        globals()[b]()
    
