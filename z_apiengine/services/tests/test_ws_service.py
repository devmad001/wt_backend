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

from services.ws_service import request_init_data

#0v1# JC Jan 16, 2024


"""
    test for ws_service  (websocket service fucntionality)
    - not websocket focused but it init_data coming through with format

"""


class TestWSinit_data(unittest.TestCase):
    def setUp(self):
        pass
    
    def test_init_data_format(self):
        # Your test code here

        case_id='case_atm_location' #Hardcode test case for now
        
        ## BASE CALL
        init_data=request_init_data(case_id=case_id, target='dev')
#        print ("GOT INIT MSG: "+str(json.dumps(init_data,indent=4)))
        
        ## CHECK credits_used
        
        ## Assert field exists: init_data['data']['dsettings']['credits_used']
        #[ ] dynamic data so can't assert value
        self.assertTrue(init_data['data']['dsettings']['credits_used'])


if __name__ == '__main__':
    unittest.main()



"""
SAMPLE init_data

 {'action': 'init_data', 'meta': {'dashboard_types': ['ChatComponent', 'TimelineComponent', 'SquareComponent', 'IFRAMEComponent', 'WaterfallComponent', 'ButterflyComponent', 'BarchartComponent'], 'layout_types': ['view_standard_1', 'view_standard_2']}, 'data': {'dsettings': {'layout_type': 'view_standard_1', 'custom_layout': {}, 'case_id': 'case_atm_location', 'datahash': '92e1ae12d6a4864a8697b78a1e30e9e40c4d65223561a688027d175c6ca9fe90'}, 'components': [{'type': 'chat', 'id': 'chat_1', 'position': 'bottom_left', 'component_name': 'ChatComponent', 'src': 'https://chatbot.epventures.co?case_id=case_atm_location&session_id=wfrix', 'datahash': '123', 'is_main': False}, {'type': 'timeline', 'id': 'timeline_1', 'position': 'top_full', 'component_name': 'IFRAMEComponent', 'src': 'http://127.0.0.1:8008/api/v1/case/case_atm_location/timeline_dynamic', 'datahash': '92e1ae12d6a4864a8697b78a1e30e9e40c4d65223561a688027d175c6ca9fe90', 'is_main': True}, {'type': 'square', 'id': 'IFRAMEComponent_1', 'position': 'bottom_right', 'component_name': 'IFRAMEComponent', 'src': 'http://127.0.0.1:8008/api/v1/case/case_atm_location/square', 'datahash': '92e1ae12d6a4864a8697b78a1e30e9e40c4d65223561a688027d175c6ca9fe90', 'is_main': False}]}}
 
"""