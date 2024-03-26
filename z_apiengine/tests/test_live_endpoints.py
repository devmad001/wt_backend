import os
import sys
import codecs
import json
import re
import requests

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")
sys.path.insert(0,LOCAL_PATH+"../../")

from w_utils import am_i_on_server




#from routers.timeline_router import router as timeline_router
#from routers import case_router
#from . import timeline, case


#0v1# JC Nov  1, 2023  Setup


## For now, default testing local
TEST_LIVE_LOCAL=True

BASE_ENDPOINT='http://127.0.0.1:8008' #Hard coded port in fast_main.py


"""
    TEST LIVE ENDPOINT
    - allow for remote testing (watch auth)
    - use in combination with unit test for services (prior to launch)
    - 
    - use fastapi:  from fastapi.testclient import TestClient
        - to locally test app performance
        client = TestClient(app)
        response = client.get("/your_endpoint")
        assert response.status_code == 200
        
    - optionally add tests as part of dev process build out

"""

def test_live_timeline():
    global BASE_ENDPOINT
    case_id='chase_3_66_b4'  #Validate directory exists or case exists (via list cases per user)

    # tp://127.0.0.1:8008/api/v1/case/timeline/chase_3_66_5ktransfer/timeline_data
    url = BASE_ENDPOINT+"/api/v1/case/timeline/"+case_id+"/timeline_data"
    
    # Sending a GET request
    response = requests.get(url)
    
    # Checking if the status code is 200 (OK)
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code} at {url}"
    
#    # Further assertions based on your API's contract
#    # For example, checking the response content
#    expected_response_content = {"key": "value"}
#    assert response.json() == expected_response_content, f"Expected {expected_response_content}, got {response.json()}"
    
#def test_timeline_functionality():
#    return


##################################################################
# 200 status checks
#- debug mode?
##################################################################
#

"""
router> {'path': '/openapi.json', 'name': 'openapi', 'methods': None}
router> {'path': '/docs', 'name': 'swagger_ui_html', 'methods': None}
router> {'path': '/docs/oauth2-redirect', 'name': 'swagger_ui_redirect', 'methods': None}
router> {'path': '/redoc', 'name': 'redoc_html', 'methods': None}
router> {'path': '/static', 'name': 'static', 'methods': ['GET'], 'description': 'Static Files'}
router> {'path': '/api/v1/case/{case_id}/timeline_data', 'name': 'get_timeline_data', 'methods': ['GET']}
router> {'path': '/api/v1/case/{case_id}/timeline', 'name': 'get_timeline', 'methods': ['GET']}
router> {'path': '/api/v1/case/{case_id}/map/get_pois', 'name': 'get_pois', 'methods': ['GET']}
router> {'path': '/api/v1/case/{case_id}/map/view', 'name': 'map_view', 'methods': ['GET']}
router> {'path': '/api/v1/case/{case_id}/square', 'name': 'get_square', 'methods': ['GET']}
router> {'path': '/api/v1/case/{case_id}/generate_excel', 'name': 'generate_excel', 'methods': ['GET']}
router> {'path': '/api/v1/case/{case_id}/pdf/{filename}', 'name': 'view_pdf', 'methods': ['GET']}
router> {'path': '/api/v1/case/{case_id}/pdf/{filename}/{page_num:path}', 'name': 'view_pdf', 'methods': ['GET']}
router> {'path': '/api/v1/case/view_runnings', 'name': 'view_runnings', 'methods': ['GET']}
router> {'path': '/api/v1/case/dev_runnings_debug', 'name': 'view_runnings_debug', 'methods': ['GET']}
router> {'path': '/api/v1/case/dev_view_case_graph', 'name': 'view_runnings_debug', 'methods': ['GET']}
router> {'path': '/api/v1/case/dev_view_case_report', 'name': 'view_runnings_debug', 'methods': ['GET']}
router> {'path': '/api/v1/case/start_case_processing', 'name': 'start_case_processing', 'methods': ['GET']}
router> {'path': '/api/v1/case/{case_id}/view/submit', 'name': 'handle_submit', 'methods': ['POST', 'GET']}
router> {'path': '/api/v1/case/{case_id}/ask', 'name': 'handle_ask', 'methods': ['POST', 'GET']}
router> {'path': '/api/v1/case/{case_id}/process_status', 'name': 'process_status', 'methods': ['GET']}
router> {'path': '/api/v1/case/{case_id}/process_start', 'name': 'process_start', 'methods': ['GET']}
router> {'path': '/api/v1/case/{case_id}/process_admin', 'name': 'process_admin', 'methods': ['GET']}
router> {'path': '/ws', 'name': 'websocket_endpoint', 'methods': None}
router> {'path': '/broadcast_listener', 'name': 'handle_dashboard_parenty', 'methods': ['POST']}
router> {'path': '/static/{file_path:path}', 'name': 'serve_static', 'methods': ['GET']}
router> {'path': '/favicon.ico', 'name': 'favicon', 'methods': ['GET']}
"""


def test_api_stack():
    SERVER_LOCAL=True   #Optionally test remote server (admin auth?)
    
    test_case_id='chase_4_a'
    ### TEST 'ALL' ROUTES
    BASE_ENDPOINT='http://127.0.0.1:8008'
    BASE_URL=BASE_ENDPOINT+"/api/v1/case/"+test_case_id+'/'
    
    
    b=[]
    b+=['list_all_routes']    #<-- does full backend load too
    b+=['check_case_status']

    b=['check_map']
    b=['test_run_case']
    
    if 'list_all_routes' in b:
        ### LIST ALL ROUTES
        from fast_main import get_all_routes  #Loads full backend **slow
        for item in get_all_routes():
            print ("router> "+str(item))
        
    if 'check_case_status' in b:
        url=BASE_URL+"process_status"
        r=requests.get(url)
        assert r.status_code == 200
    #    assert r.json() == {"msg": "Hello World"}
    
    if 'check_map' in b:
        BASE_URL=BASE_ENDPOINT+"/api/v1/case/case_atm_location/"

        url=BASE_URL+"map/get_pois"
        r=requests.get(url)
        assert r.status_code == 200
        print ("POIS: "+str(r.content))

        url=BASE_URL+"map/view"
        r=requests.get(url)
        assert r.status_code == 200
        
    if 'test_run_case' in b:
        BASE_URL=BASE_ENDPOINT+"/api/v1/case/case_atm_location/"
        url=BASE_URL+"process_start"
        r=requests.get(url)
        assert r.status_code == 200
        print ("response: "+str(r.content))

    #router> {'path': '/api/v1/case/{case_id}/process_status', 'name': 'process_status', 'methods': ['GET']}

    return



if __name__=='__main__':
    branches=['test_live_timeline']
    branches=['test_api_stack']
    
    for b in branches:
        globals()[b]()
        
    print ("**PASSED**")


"""

"""
