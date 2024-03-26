# test_main.py
import os,sys
import json

from fastapi.testclient import TestClient

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../../../../")
        
        
#0v1# JC Dec  2, 2023  Setup test

##** Beware: requires test fixtures to find jinga templates

        
## Allow for local debug -- but usually not needed
if not __name__=='__main__':
    from z_apiengine.fast_main import app  # Import the FastAPI app instance from your main module
    client = TestClient(app)


"""
    ORG CHARTS SHOULD STILL BE ACTIVE
    - timeline_dynamic_nodes
    - map
    - barchart
    - html view endpoint
"""

TEST_CASE_ID='MarnerHoldingsB'

def test_ORG_timeline_dynamic_nodes1():
    TEST_CASE_ID='MarnerHoldingsB'
    case_id=TEST_CASE_ID

    response = client.get("/api/v1/case/"+case_id+"/timeline")
    assert response.status_code == 200
    return

def test_ORG_timeline_dynamic_nodes2():
    TEST_CASE_ID='MarnerHoldingsB'
    case_id=TEST_CASE_ID

    response = client.get("/api/v1/case/"+case_id+"/timeline_dynamic")
    assert response.status_code == 200

    return

def test_ORG_timeline_map():
    TEST_CASE_ID='MarnerHoldingsB'
    case_id=TEST_CASE_ID

    response = client.get("/api/v1/case/"+case_id+"/map/view")
    assert response.status_code == 200
    return

def test_ORG_timeline_barchart():
    TEST_CASE_ID='MarnerHoldingsB'
    case_id=TEST_CASE_ID

    response = client.get("/api/v1/case/"+case_id+"/barchart")
    assert response.status_code == 200

    return

def dev2():
    global TEST_CASE_ID
    case_id=TEST_CASE_ID
    response = client.get("/api/v1/case/"+case_id+"/waterfall_data")
    assert response.status_code == 200

    # Should be {'data':[]}
    data=response.json()
    assert data.get('data',[])!=[]
    return



def dev1():
    print ("**recall:  run with python -m pytest")

    return


if __name__=='__main__':
    branches=['dev1']
    for b in branches:
        globals()[b]()
    
