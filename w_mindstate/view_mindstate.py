import os
import sys
import codecs
import uuid
import json
import re
import time

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")

from mindstate import Mindstate
from w_chatbot.wt_brains import Bot_Interface

#0v1# JC  Sep 11, 2023  Setup


"""
    VIEW MINDSTATE
    - essentially the debug view of the web app state
"""



def dev1():
    case_id='case_schoolkids'
    Mind=Mindstate()
    
    #
    Bot=Bot_Interface()
    #- provides chat capabilities to front-end
    #^ also uses Mindstate
    
    b=[]
    b+=['view raw mind state']
    
    if 'view raw mind state' in b:
        sesh,session_id,is_created=Mind.start_or_load_session(case_id=case_id)
        
        print ("[current sesh vars]: "+str(sesh))
    
    print ("*view mindstate should be simliar to debug view of webpage")
    return


if __name__=='__main__':
    branches=['dev1']
    for b in branches:
        globals()[b]()



        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
