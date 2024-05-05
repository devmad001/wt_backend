import os
import sys
import codecs
import json
import re

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")

from pypher import __, Pypher
from w_storage.gstorage.gneo4j import Neo

from get_logger import setup_logging
logging=setup_logging()


#0v1# JC  Oct  4, 2023  Init




def dev1():
    print ("PROXY 'sim' for user interaction")
    print ("- see sim_user.py for original flow options")
    
    b=[]
    b+['user_submits_chatbot_question']
    b+['user_clicks_button']
    b+['jon_simulates_button_click']
    
    print ("WATCH state update to mindstate.py")
    
    if 'user_submits_chatbot_question' in b:
        print ("1) User submits chat question to streamlit")
        print ("2) Streamlit question posted to wt_flask_handler.py")
        print ("3) Served by Bot_Interface() wt_brains.py")
        print ("4) Routed in kb_ask.py (interface_kb_ask) to: KB_AI_Agent")
        print ("5) AI agent writes cypher query, exe, summarizes, responds")
        print ("6) Response is stored to mindstate.py 'session mem'")
        print ("7) Answer back through wt_flask_handler to front-end streamlit")
        print ("8) wt_flask broadcasts response to front-end parenty.html via ws_websockets")
        print ("9) parenty children components (timeline, square, etc) are either force refreshed or pushed parameters")

    if 'user_clicks_button' in b:
        print ("User clicks button == pre_defined_question request")
        print ("- flow is the same as above except:")
        print ("1.b) button submits post to wt_flask_handler.py")
        print ("4.c) kb_ask.py SPECIAL_ROUTING on 'button_name")
        print ("5.b) question to kb_router.py answers question")
        
    if 'jon_simulates_button_click' in b:
        print ("*recall, part to dev multimodal responses")
        print ("> option #1:   v_ux/ this entry")

        print ("> option #2:   kb_router.py 'button_name' entry")
        print ("> option #2:   kb_router.py 'button_name' entry")
        print ("> option #2:   kb_router.py 'button_name' entry")
        print ("> option #2:   kb_router.py 'button_name' entry")
        print ("** manually update       mindstate.py 'session mem'")


    return


if __name__=='__main__':
    branches=['dev1']
    for b in branches:
        globals()[b]()




"""
"""
