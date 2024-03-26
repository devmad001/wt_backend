import os
import sys
import codecs
import json
import re
import requests
#from configparser import ConfigParser

import unittest

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")


from w_mindstate.mindstate import Mindstate
from w_mindstate.mindstate import broadcast_to

from z_apiengine.services.timeline_service import get_service_timeline_data


#0v1#  JC Nov 13, 2023  Init


class TestAPIBasic(unittest.TestCase):
    def setUp(self):
        print ("Sample test_local")

    def test_something(self):
        self.assertEqual(2+2, 4)
#        self.assertEqual(2+1, 4)


"""
- recall, test_broadcast_ws, etc.
"""

def dev1():
    print (" SIMULATE FRONT END DASHBOARD")
    
    ## TEST CASE?
    case_id='chase_3_66_5ktransfer' #ok timeline
    
    ## ACTION
    action_from=[]
    action_from+=['backend_broadcast_answer']
    action_from+=['default_load']
    action_from+=['user_ask']
    
    ## VIEW COMPONENT
    component=[]
    component+=['timeline_timeline']
    component+=['timeline_barchart']
    component+=['timeline_map']
    component+=['square']

    b=[]
    b+=['get_state_from_mindstate']
    b=[]
    b+=['front_end_timeline_timeline']
    
    if 'get_state_from_mindstate' in b:
        print ("mindstate.py, broadcast_to, Mindstate()")
        Mind=Mindstate()
        sesh,session_id,is_created=Mind.start_or_load_session(case_id=case_id)
        
        print ("SESH: "+str(sesh))

    if 'front_end_timeline_timeline' in b:
        #http://127.0.0.1:8008/api/v1/case/chase_3_66_5ktransfer/timeline?maxWidth=48&maxHeight=400
        url_for_timeline_component="""
            D3ChartComponent
             const apiUrl = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8008';
             const defaultUrl = `${apiUrl}/api/v1/case/${caseId}/timeline?maxWidth=${maxWidth}&maxHeight=${enforcedMaxHeight}`;
        """
        refresh_timeline_component_via="RELOAD_TIMELINE_IFRAME_UR"
        #> mindstate -> broadcast_to front-end.
        #^^ fine but very communication, hardcoded, etc.
        #- instead, wrap in a Dashboard proxy view so can see without front UI
        
        
        #^ fast_main.py -> timeline_router -> timeline_service.py
        #
        data_for_timeline_timeline=get_service_timeline_data(case_id)
        print ("data_for_timeline_timeline: "+str(data_for_timeline_timeline))

    return


def dev_test_broadcast_to():
    ## Recall mindstate
    #>> message

    case_id='chase_3_66_5ktransfer' #ok timeline

    Mind=Mindstate()
    sesh,session_id,is_created=Mind.start_or_load_session(case_id=case_id)
    
    answer_dict=Mind.get_field(session_id,'last_answer_meta')
    
    print ("GOT BACK last answer meta: "+str(answer_dict))
    print ("GOT BACK last answer meta: "+str(answer_dict.keys()))
    print ("GOT BACK last answer meta: "+str(answer_dict['multimodal'].keys()))

    return

def dev_test_dashboard():
    case_id='chase_3_66_5ktransfer' #ok timeline
    case_id='case_atm_location'
#    force_show_decision='barchart'
    force_show_decision=''
    broadcast_to(case_id,session_id='',message={},force_show_decision=force_show_decision)

    
    ## recall:  http://127.0.0.1:5173/  for jon view
    return

def dev_local_ask_question():
    case_id='case_atm_location'

    ## Preload some multimodal data
    from kb_ask.kb_ask import interface_kb_ask
    
    ## Store output?
    question='show me all the atm locations'
    answer,meta,Agent=interface_kb_ask(question,case_id=case_id)

    print ("QUESTION: "+str(question))
    print ("ANSWER: "+str(answer))
    return



if __name__ == "__main__":

    #unittest.main()
    #dev1()
    #dev_test_broadcast_to()
    dev_test_dashboard()
#    dev_local_ask_question()


