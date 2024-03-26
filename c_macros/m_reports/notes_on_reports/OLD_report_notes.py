import os
import sys
import codecs
import json
import uuid
import re
import random

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")

from w_storage.gstorage.gneo4j import Neo
from w_storage.ystorage.ystorage_handler import Storage_Helper

from get_logger import setup_logging
logging=setup_logging()


#0v1# JC  Nov 21, 2023  SETUP



"""
    AI driven helper
    - have already
    - codebase entrypoint discovery  (pre-index?)
    - statements, entrypoints, align, etc.

"""




def jon_areas():

    areas=['qa','tweaks','processing','user']
    areas+=['integration','pm_people']


    jon_task=random.shuffle(areas)
    print ("JON TASK: "+str(jon_tast))

    return


def entrypoints():
    print ("Recall all entrypoints: u_entrypoings/")
    ENTRY_run_pipeline_against_pdf_page=[]
    return




"""
CURRENT:
https://dash.epventures.co/case/MarnerHoldings/run

GPT raw response times?
https://gptforwork.com/tools/openai-api-and-other-llm-apis-response-time-tracker

"""



def dev1():
    print ("Last files uploaded (check directory)")
    print ("Last gpt-4 response times")
    print ("Last gpt-x response times")
    
    print ("Is it running?")
    print ("Can it run")

    return



"""
    CASES ARE PROCESSING
    - processing state, resources (cpu limts), job queues, remaining time
    - endpoints active
    - latest files, partial files,
    
    - run auto pdf viewer generation once done processing
    - run case report once done processing
    
    - cost to run, time to run, 

"""




def qq_throughput_of_llm_model():
    print (">> llm_interfaces.py -> local sqlite cache -> added date nov 23")
    # https://gptforwork.com/tools/openai-api-and-other-llm-apis-response-time-tracker
    
    return



def dev_stack_of_reportable_processing_items():
    
    qq=[]
    qq+['qq_throughput of llm model']
    
    for q in qq:
        globals()[q]()


    return





if __name__=='__main__':
    branches=[]
    branches+=['dev_stack_of_reportable_processing_items']

    for b in branches:
        globals()[b]()
        
print ("[ ] general reminders where...fine here in reports for now...do backups![ ] ")        
        
       

       

if __name__=='__main__':
    branches=[]
    branches+=['dev1']

    for b in branches:
        globals()[b]()
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
