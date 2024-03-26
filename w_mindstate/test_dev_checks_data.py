import os
import sys
import codecs
import uuid
import json
import re
import time
import hashlib
import pandas as pd
from collections import Counter
import unittest

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")

#from the_dashboard import get_timeline_urls
from z_apiengine.services.timeline_service import get_service_timeline_data
from z_apiengine.services.check_service import DEMO_merge_check_data
from x_modules.k_checks.check_view_validation import interface_load_case_checks


#0v1# JC  Jan 28, 2024  Basic setup



"""
    TODO:  This is a work in progress, see timeline_service.py
    
    Raw dev tests for integrating demo/sample checks data
    - this is funcitonal level test for quick integration demo

"""


class TestGetTimelineData(unittest.TestCase):
    def setUp(self):
        return

    def xxtest_get_check_images(self):
        
        ## CHECKS DATA
        case_id='65a8168eb3ac164610ea5bc2'# force_checks_meta_filename=LOCAL_PATH+"manual_match_checks_newage.json"
        validate=interface_load_case_checks(case_id)
        print ("VALIDATED length: "+str(len(validate)))
        self.assertTrue(len(validate)>0)
        

        return
    
    def xxtest_get_dynamic_timeline_data(self):
        ## NORMAL TIMELINE DATA
        case_id='65a8168eb3ac164610ea5bc2'# force_checks_meta_filename=LOCAL_PATH+"manual_match_checks_newage.json"
        data=get_service_timeline_data(case_id=case_id)
        records_list=len(data['records'])
        print ("Record count:"+str(records_list))
        print ("Single record: "+str(data['records'][0]))
        for record in data['records']:
            transaction_id=record['id']
            
        self.assertTrue(len(data['records'])>0)

        return
    
    def test_merge_check_data(self):
        case_id='65a8168eb3ac164610ea5bc2'# force_checks_meta_filename=LOCAL_PATH+"manual_match_checks_newage.json"
        validated=interface_load_case_checks(case_id)
        data=get_service_timeline_data(case_id=case_id)
        new_records,status_check_identifiers=DEMO_merge_check_data(case_id,validated,data['records'])
        
        self.assertGreater(len(status_check_identifiers),0)

        return
    

def dev1():
    return



if __name__=='__main__':
    unittest.main()





        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
