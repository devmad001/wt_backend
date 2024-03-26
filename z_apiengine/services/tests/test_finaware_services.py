import os
import sys
import codecs
import json
import re


LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")
sys.path.insert(0,LOCAL_PATH+"../..")

import unittest
from unittest.mock import MagicMock
from finaware_services import (front_list_user_buttons, front_list_user_cases, front_list_user_faqs, 
                              front_get_user_info, front_create_set_case, front_create_set_file, 
                              front_session_is_user_authenticated, front_start_processing_case, 
                              front_get_processing_case_status)

from get_logger import setup_logging
logging=setup_logging()


# Set up the database session mock
mock_db = MagicMock()

# Mock the backend functions
list_buttons = MagicMock()
list_user_cases = MagicMock()
list_user_faqs = MagicMock()
get_user = MagicMock()
create_set_case = MagicMock()
create_set_file = MagicMock()
alg_is_user_session_valid = MagicMock()
interface_run_pipeline_in_background = MagicMock()
interface_get_job_dict = MagicMock()

# Mock the outgoing services
back_fetch_file_from_backend = MagicMock()


#0v1# JC Nov  9, 2023


def setup_create_test_objects():
    from case_service import create_set_case
    from user_service import create_set_user
    from session_service import create_set_session
    
    username='jontest1'
    case_id='casetest1'
    session_id='1234'

    print ("> create case: ", case_id)
    create_set_case(case_id=case_id)
    print ("> create user: "+str(username))
    create_set_user(username=username)
    print ("> force set user session")
    alg_set_user_session(username=username, session_id=session_id)
    
    return

class TestFrontListUserButtons(unittest.TestCase):
    def test_buttons_returned(self):
        # Your test code here
        pass

class TestFrontListUserCases(unittest.TestCase):
    def test_cases_returned(self):
        # Your test code here
        pass

class TestFrontListUserFAQs(unittest.TestCase):
    def test_faqs_returned(self):
        # Your test code here
        pass

class TestFrontGetUserInfo(unittest.TestCase):
    def test_user_info_returned(self):
        # Your test code here
        pass

class TestFrontCreateSetCase(unittest.TestCase):
    def test_case_created(self):
        # Your test code here
        pass

class TestFrontCreateSetFile(unittest.TestCase):
    def test_file_created(self):
        # Your test code here
        pass

class TestFrontSessionIsUserAuthenticated(unittest.TestCase):
    def test_session_authenticated(self):
        # Your test code here
        pass

class TestFrontStartProcessingCase(unittest.TestCase):
    def test_processing_started(self):
        # Your test code here
        pass

class TestFrontGetProcessingCaseStatus(unittest.TestCase):
    def test_case_status_returned(self):
        # Your test code here
        pass

if __name__ == '__main__':
    unittest.main()



if __name__=='__main__':
    branches=['dev1']
    for b in branches:
        globals()[b]()


"""
"""