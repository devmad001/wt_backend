import os
import sys
import codecs
import json
import re
import requests
from configparser import ConfigParser

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")
sys.path.insert(0,LOCAL_PATH+"../../")

from w_utils import am_i_on_server


#0v1# JC Nov  9, 2023  Setup

"""
    "SHIVAM" ENDPOINTS
    - list cases
    - list jobs running (sub-query of cases)
    - list user buttons

    - input create user (shivam sync push from his login)
    - input file upload (shivam sync push from his UI)
    - 


"""

## ROOT CONFIG
Config = ConfigParser()
Config.read(LOCAL_PATH+"../../w_settings.ini")
FRAUDAPI_PORT=Config.get('services','fraudapi_port')

## For now, default testing local
TEST_LIVE_LOCAL=True
BASE_ENDPOINT='http://127.0.0.1:'+str(FRAUDAPI_PORT) #Hard coded port in fast_main.py

FRONTEND_ENDPOINT='http://'


"""
"""

def dev_formalize_shivamapi():
    ## Front-end 'fraud' endpoint
    
    """
    STANDARD:
[A] get_user_cases(user_id)
  ^includes job status % done, status.
[B] post_create_case(user_id,case_id,case_dict)
[C] start_processing_case(case_id)
[D] load_user_buttons(user_id)
[E] load_user_faqs(user_id)
[F] get_user_info(user_id)    *for instance, styling preferences etc.ADVANCED:
// authentication:
[1.a)]  get_is_user_authenticated(user_id,session_id)
[1.b)]  *my FraudAPI will check if user session valid.  If unknown, FraudAPI will either (i)  ping ShivamAPI to get confirmation on user_id,session_id is authenticated or (ii) Check ShivamDB directly to check on session auth (will need db user from server @3.20.195.157).// file upload:
[2]  Files uploaded and pushed to tracker + FraudAPI.
Option (i)  post_location_of_file(user_id,case_id,filename,file_url)
Option (ii)
Post_content_of_file(user_id,case_id,filename, STREAM_UPLOAD?)DASHBOARD WIDGETS:
- I’ll modify the dashboard.ts  But, it will essentially populate the 3 widget areas via iframe content from FraudAPI.
        ## GET CONTENT IS UPDATED VIA WEBSOCKET ETC.
        ee+=['dashboard_widget_timeline']
        ee+=['dashboard_widget_square']
        ee+=['dashboard_widget_chat']
    """


    ## ROUTER PREFIX:  /front/

    ee=[]
    
#    ee+=['get_user_cases']
#    #> GET get_user_cases(user_id)
#    ee+=['load_user_buttons']
#    #> GET load_user_buttons(user_id)
#    ee+=['load_user_faqs']
#    #> GET load_user_faqs(user_id)
#    ee+=['get_user_info']
#    #> GET get_user_info(user_id)
#    ee+=['post_create_case']
#    #> POST post_create_case(user_id,case_id,case_dict)
#    ee+=['post_case_file_location']
#    #> POST post_case_file_location(user_id,case_id,filename,file_url)

#?    ee+=['post_case_file_content']
#?    #> POST post_case_file_content(user_id,case_id,filename,file_content)

#?    ee+=['backend_list_case_files']
#?    #> GET backend_list_case_files(user_id,case_id)

#    ee+=['is_user_authenticated']
#    #> GET is_user_authenticated(user_id,session_id)


    ee+=['start_processing_case']
    #> GET start_processing_case(case_id)

    ee+=['get_processing_case_status']
    #> GET get_processing_case_status(case_id)


    ## Outgoing:
    ee+=['backend_is_user_authenticated']
    #> GET backend_is_user_authenticated(user_id,session_id)

    return



if __name__=='__main__':
    branches=['dev_session_handshake']
    for b in branches:
        globals()[b]()


"""

"""
