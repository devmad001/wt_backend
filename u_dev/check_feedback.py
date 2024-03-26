import os
import sys
import codecs
import json
import re
import datetime
import uuid

from fastapi import FastAPI

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")

sys.path.insert(0,LOCAL_PATH+"../..")


#from w_chatbot.wt_brains import Bot_Interface
from w_storage.ystorage.ystorage_handler import Storage_Helper

from get_logger import setup_logging
logging=setup_logging()


Storage=Storage_Helper(storage_dir=LOCAL_PATH+"../w_datasets")
Storage.init_db('feedback')

        
#0v1# JC Nov  5, 2023  Setup


"""
    BOT     SERVICES
    - org app_parenty.py
"""

def handle_question(question, case_id, params={}):
    output={}
    meta={}
    Bot=Bot_Interface()
    Bot.set_case_id(case_id)
    if question and case_id:
        output['generated_text'],meta=Bot.handle_bot_query(question, params=params)
        
    logging.info("[handle_question] bot_service.py done return")
    return output,meta

def handle_feedback(feedback, case_id):
    global Storage

    output={}
    meta={}
    
    feedback['the_date']=str(datetime.datetime.now())
    
    feedback['id']=str(uuid.uuid4().hex)
    
    ## Store
    Storage.db_put(feedback['id'],'feedback',feedback,name='feedback')

    logging.info("[handle_feedback] feedback: %s"%feedback)
    return output,meta


def review_feedback():
#    print ("Call dummy...")
#    dd={}
#    dd['jon']='hello'
#    handle_feedback(dd,'dummy1')

    print ("CHECK FEEDBACK...")
    for kk in Storage.iter_database('feedback'):
        dd=Storage.db_get(kk,'feedback',name='feedback')
        print ("> "+str(dd))

    return
    
if __name__=='__main__':
    branches=['review_feedback']
    for b in branches:
        globals()[b]()



"""
"""