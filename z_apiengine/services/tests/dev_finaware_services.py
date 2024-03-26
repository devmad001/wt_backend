import os
import sys
import codecs
import json
import re


LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")
sys.path.insert(0,LOCAL_PATH+"../../")

import unittest
from unittest.mock import MagicMock

#from shivam_services import (front_list_user_buttons, front_list_user_cases, front_list_user_faqs, 
#                              front_get_user_info, front_create_set_case, front_create_set_file, 
#                              front_session_is_user_authenticated, front_start_processing_case, 
#                              front_get_processing_case_status)

from finaware_services import front_create_set_case
from finaware_services import front_list_user_cases


from get_logger import setup_logging
logging=setup_logging()


# Set up the database session mock
#mock_db = MagicMock()


#0v1# JC  Dec  4, 2023  Full sample data interactive dev + test


print ("SEE: FE_simulate_user_flow...")
print ("SEE: finaware_services.py as part of dev")


def workflow_create_case():
    ## Revisit spec or xxx see FE_simulate_user_flow
    
    ccase={}
    ccase['case_id']='test_case_A'
    ccase['user_id']='test_user_1'
    ccase['description']='This is a test case.'
    
    service_name='case_serivce.py create_set_case()'
    
    ## PING API DIRECTLY
    
    #/post_case_details
    # FE_case_view.py -> post_case_details

    ## PING service
    case_id=ccase.pop('case_id')
    user_id=ccase.pop('user_id')

    case_meta=ccase
    case,did_create=front_create_set_case(case_id=case_id, user_id=user_id, case_meta=case_meta)
    
    print ("Created case: "+str(case))

    return


def worflow_submit_things():

    return


def workflow_load_things():
    
    ## API Load status of case

    ## API Load list of cases (per user)
    username='test_user_1'
    cases=front_list_user_cases(username=username)
    for case in cases:
        print ("CASE: "+str(case.__dict__))
        
    print ("RAW users' cases: "+str(cases))
    
    ## API Load posted case

    ## API Load case report

    return


def database_schema_check():
    return



def dev1():
    ## Dec 4 walk through usage.
    b=['list database tables or case_service.py. ...']
    b=['workflow_create_case']
    b=['workflow_load_things']
    
    if 'workflow_create_case' in b:
        workflow_create_case()

    if 'workflow_load_things' in b:
        workflow_load_things()

    return


def test_create_case_get_case():
    #[ ] move to test routine
    case_id='test_case_A'
    username='test_user_1'

    ccase={}
    ccase['case_id']=case_id
    ccase['user_id']=username
    ccase['description']='This is a test case.'
    
    required_fields=['user_id']
    optional_fields=['name','originalName','size','threatTagging','publicCorruptionTag','description','case_creation_date','file_urls']

    service_name='case_serivce.py create_set_case()'
    ## PING API DIRECTLY
    #/post_case_details
    # FE_case_view.py -> post_case_details

    case_id=ccase.pop('case_id')
    user_id=ccase.pop('user_id')

    case_meta=ccase
    case,did_create=front_create_set_case(case_id=case_id, user_id=user_id, case_meta=case_meta)
    
    print ("DONE CREATE CASE DID CREATE (or was it existing)?: "+str(did_create))

    found_case_id=False
    cases=front_list_user_cases(username=username)
    for case in cases:
        print ("CASE: "+str(case.__dict__))
        if case.case_id==case_id:
            found_case_id=True
            break

    if not found_case_id:
        raise Exception("Did not find case_id: "+str(case_id))
    else:
        print ("Found case_id: "+str(case_id))
        
    ## REMOVE CASE + USER?

    return



if __name__=='__main__':
    branches=['dev1']
    branches=['test_create_case_get_case']

    for b in branches:
        globals()[b]()


"""
"""