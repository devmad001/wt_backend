# test_main.py
import os,sys
import json

from fastapi.testclient import TestClient

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../../../../")
        
        

#0v1# JC Nov 24, 2023  Setup test

        
## Allow for local debug -- but usually not needed
if not __name__=='__main__':
    from z_apiengine.fast_main import app  # Import the FastAPI app instance from your main module
    client = TestClient(app)


"""
    RECALL TESTING USING:
    - python -m pytest
    - python -m pytest tests/test_timeline.py for specific
"""
TEST_CASE_ID='MarnerHoldingsB'


def test_get_square_table_data():
    global TEST_CASE_ID
    case_id=TEST_CASE_ID
    response = client.get("/api/v1/case/"+case_id+"/square_data")
    assert response.status_code == 200
#    assert response.headers["content-type"] == "application/javascript"

    # Should be {'data':[]}
    data=response.json()
    assert data.get('data',[])!=[]

    return


def dev1():
    print ("**recall:  run with python -m pytest")
    # Load from file
    sample_json_data=LOCAL_PATH+"marner_data.json"
    the_json=json.load(open(sample_json_data, 'r'))
    print ("TOP KEYS: "+str(the_json.keys()))
    print ("TOP KEYS: "+str(the_json['records'][0].keys()))
    

    return


if __name__=='__main__':
    branches=['dev1']
    for b in branches:
        globals()[b]()
    

