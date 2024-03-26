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

from the_dashboard import get_timeline_urls


#0v1# JC  Jan 24, 2024  Basic test for dashboard as build out features



## Basic test setup for dashboard
class TestDashboard(unittest.TestCase):
    def test_get_timeline_urls(self):
        test_case_id='657f172f9a57063d991dd88b' #
        test_case_id='test_case_id'

        has_map_kind=False
        urls=get_timeline_urls(test_case_id,session_id='')
        for url_kind in urls:
            print(str(url_kind)+"\t"+str(urls[url_kind]))
            if 'map' in urls[url_kind].lower():
                has_map_kind=True
        self.assertTrue(has_map_kind)

        return



def dev1():
    return



if __name__=='__main__':
    unittest.main()





        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
