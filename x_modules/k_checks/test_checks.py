import os,sys
import re
import json
import time
import unittest

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../../")


from check_view_validation import interface_serve_check_image
from check_view_validation import interface_load_case_checks
from check_matcher import check_matcher_pipeline

from z_apiengine.database import SessionLocal
from z_apiengine.database_models import Check


#0v1# JC  Feb  3, 2024  Init


"""
    BASIC TEST FOR CHECK IMAGES
    [ ] requires test cases in db (todo: add to test data)
    
    'check_identifier': 'December 2021 Skyview Capital Bank Statement.pdf_5092_11_0_0', 'case_id': 'case_December 2021 Skyview Capital Bank Statement', 'check_id': '5092'
"""


class TestCheckImages(unittest.TestCase):
    def setUp(self):
        self.case_id='case_December 2021 Skyview Capital Bank Statement'
        self.checks=interface_load_case_checks(self.case_id)
        return

    def test_get_check_images(self):
        self.assertTrue(len(self.checks)>0)
        print("[debug] Number of checks: ",len(self.checks))
        for transaction_id in self.checks:

            check_image_bytes,check_image_filename,meta=interface_serve_check_image(self.checks[transaction_id]['check_identifier'])

            self.assertTrue(len(check_image_filename)>0)
            self.assertTrue(len(check_image_bytes)>0)
            self.assertTrue(len(meta)>0)

            ## Check check is bytes
            self.assertTrue(isinstance(check_image_bytes,bytes))

        return
    
    def test_check_matcher(self):
        #, again, uses db test case but fine for now
        meta=check_matcher_pipeline(self.case_id,commit=False)
        self.assertTrue(meta['total_match_count']>0)

        return
    
    def test_no_check_images_query(self):
        ## Do query WITH images athen without
       
        start_time = time.time()

        with SessionLocal() as db:
            checks_no_images = db.query(Check).options(Check.query_without_image_bytes()).filter(Check.case_id == self.case_id).all()

        no_image_runtime = time.time() - start_time

        start_time = time.time()
        with SessionLocal() as db:
            checks_with_images = db.query(Check).filter(Check.case_id == self.case_id).all()
        with_image_runtime = time.time() - start_time
        
        
        ## Runtimes
        self.assertGreater(with_image_runtime, no_image_runtime)
        
        ## Lengths
        self.assertEqual(len(checks_no_images), len(checks_with_images))

        return




def dev1():
    return


if __name__ == "__main__":
    unittest.main()




"""

"""
