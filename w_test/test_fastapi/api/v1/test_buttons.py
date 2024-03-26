# test_main.py
import os,sys
import json
import requests
import pytest

from fastapi.testclient import TestClient

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../../../../")
        
        
#0v1# JC Dec  9, 2023  Setup test

        
## Allow for local debug -- but usually not needed
if not __name__=='__main__':
    from z_apiengine.fast_main import app  # Import the FastAPI app instance from your main module
    client = TestClient(app)


"""
    RECALL TESTING USING:
    - python -m pytest
    - python -m pytest tests/test_timeline.py for specific
    
works as raw post
https://core.epventures.co/api/v1/case/6573a74f50560b89044dcf58/create_button?label=Test Button label
- but 422 otherwise
"""

base_url='/api/v1/case'


@pytest.fixture(scope="module")
def created_button_id():
    # Create a new button and return its ID
    create_response = client.post(
        base_url + "/case123/create_button",
        json={"user_id": "test_user", "label": "Test Button", "action": "http://example.com"})
    assert create_response.status_code == 200
    button_id = create_response.json()["button_id"]
    return button_id

#ok# def test_created_button():
#ok#     # Create a new button and return its ID
#ok#     create_response = client.post(
#ok#         base_url + "/case123/create_button",
#ok#         json={"user_id": "test_user", "label": "Test Button", "action": "http://example.com"}
#ok#     )
#ok#     assert create_response.status_code == 200
#ok#     button_id = create_response.json()["button_id"]
#ok#     return button_id

def test_get_dashboard():
    # List buttons
    response = client.get(base_url + "/case123/get_buttons?user_id=test_user")
    assert response.status_code == 200
    assert "data" in response.json()

def dtest_update_button(created_button_id):
    # Update the button created in the fixture
    update_response = client.post(
        base_url + f"/case123/update_button/{created_button_id}",
        json={"user_id": "test_user", "label": "Updated Test Button"}
    )
    assert update_response.status_code == 200
    assert update_response.json() == {"button_id": created_button_id}

def test_delete_button(created_button_id):
    # Delete the button created in the fixture
    delete_response = client.post(  # Changed to POST as per updated endpoint
        base_url + f"/case123/delete_button/{created_button_id}",
        json={"user_id": "test_user", "fin_session_id": "some_session_id"}
    )
    assert delete_response.status_code == 200
    assert delete_response.json() == {"status": "success", "message": f"Button {created_button_id} deleted successfully"}


#org#@pytest.fixture(scope="module")
#org#def created_button_id():
#org#    # Create a new button and return its ID
#org#    create_response = client.post(
#org#        base_url+"/case123/create_button?label=Test Button label&action=http://example.com",
#org#        json={"label": "Test Button", "action": "http://example.com"}
#org#    )
#org#    #^^maybe needs data?  because form post works
#org#    
#org#    assert create_response.status_code == 200
#org#    button_id = create_response.json()["button_id"]
#org#    return button_id
#org#
#org#def test_update_button(created_button_id):
#org#    # Update the button created in the fixture
#org#    update_response = client.post(
#org#        base_url+f"/case123/update_button/{created_button_id}",
#org#        json={"label": "Updated Test Button"}
#org#    )
#org#    assert update_response.status_code == 200
#org#    assert update_response.json() == {"button_id": created_button_id}
#org#
#org#def test_get_dashboard():
#org#    # List buttons
#org#    response = client.get(base_url+"/case123/get_buttons")
#org#    assert response.status_code == 200
#org#    assert "data" in response.json()
#org#
#org#def test_delete_button(created_button_id):
#org#    # Delete the button created in the fixture
#org#    delete_response = client.delete(base_url+f"/case123/delete_button/{created_button_id}")
#org#    assert delete_response.status_code == 200
#org#    assert delete_response.json() == {"status": "success", "message": f"Button {created_button_id} deleted successfully"}
#org#    

#individual# 
#individual# def test_get_dashboard():
#individual#     response = client.get("/case123/get_buttons")  # Replace 'case123' with an actual case_id
#individual#     assert response.status_code == 200
#individual#     assert "data" in response.json()
#individual# 
#individual# def test_create_button():
#individual#     response = client.post(
#individual#         "/case123/create_button",
#individual#         json={"label": "Test Button", "action": "http://example.com"}
#individual#     )
#individual#     assert response.status_code == 200
#individual#     assert "button_id" in response.json()
#individual# 
#individual# def test_update_button():
#individual#     # Assuming button_id 1 exists
#individual#     response = client.post(
#individual#         "/case123/update_button/1",
#individual#         json={"label": "Updated Test Button"}
#individual#     )
#individual#     assert response.status_code == 200
#individual#     assert response.json() == {"button_id": 1}
#individual# 
#individual# def test_delete_button():
#individual#     # Assuming button_id 1 exists
#individual#     response = client.delete("/case123/delete_button/1")
#individual#     assert response.status_code == 200
#individual#     assert response.json() == {"status": "success", "message": "Button 1 deleted successfully"}
#individual#     


def test_requests_created_button():
    # Define the base URL and endpoint
    base_url = 'http://localhost:8008'  # Replace with the actual base URL of your API
    endpoint = "/api/v1/case/case123/create_button"  # Adjust the endpoint as needed

    # Send a POST request to create a new button
    create_response = requests.post(
        base_url + endpoint,
        json={"user_id": "test_user", "label": "Test Button", "action": "http://example.com"}
    )
    
    print ("STATUS CODE: "+str(create_response.status_code))

    # Assert that the response status code is 200
    assert create_response.status_code == 200

    # Extract and return the button ID from the response
    button_id = create_response.json()["button_id"]
    return button_id



def dev1():
    print ("**recall:  run with python -m pytest")

    test_requests_created_button()


    
#    TBD_test_get_dashboard()
    

#    raise Exception("dev1 not implemented")
#    # Load from file
#    sample_json_data=LOCAL_PATH+"marner_data.json"
#    the_json=json.load(open(sample_json_data, 'r'))
#    print ("TOP KEYS: "+str(the_json.keys()))
#    print ("TOP KEYS: "+str(the_json['records'][0].keys()))

    return

def bug_get_buttons():
    user_id='6571b86a88061612aa2fc8b7'
    case_id='65858e0c198ceb69d5058fc3'

    return

if __name__=='__main__':
    branches=['dev1']
    for b in branches:
        globals()[b]()
    







