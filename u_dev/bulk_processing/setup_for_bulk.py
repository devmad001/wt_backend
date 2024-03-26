import os
import sys
import time
import datetime
import codecs
import json
import re
import pandas as pd
import shutil

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")
sys.path.insert(0,LOCAL_PATH+"../../")

#from w_storage.gstorage.gneo4j import Neo
#from w_chatbot.wt_brains import Bot_Interface
#
#from a_query.admin_query import admin_remove_case_from_kb
#from a_agent.sim_wt import wt_main_pipeline
#from kb_ai.call_kbai import interface_call_kb_auto_update

from a_agent.RUN_sim_wt import MAIN_ENTRYPOINT_CASE_processing_pipeline

from get_logger import setup_logging
logging=setup_logging()


#0v1# JC  Oct 12, 2023  Init

"""
    BULK PROCESSING
    - process each candidate pdf as its' own file
"""

def dev1():
    
    b=['copy all files']
    b=['run_all_cases']

    input_directory='C:/scripts-23/watchtower/Watchtower Solutions AI/bulk_pdfs'
    c=0
    for file in os.listdir(input_directory):
        full_file=input_directory+'/'+file

        filename=os.path.basename(file)
        print (filename)

        target_directory=re.sub('.pdf','',filename)
        
        base_dir='________________________________________________ager/storage'
        
        target_dir=base_dir+'/case_'+target_directory
        
        case_name='case_'+target_directory
        
        try: os.mkdir(target_dir)
        except:pass
        
        target_filename=target_dir+'/'+filename
        
        
        if 'copy all files' in b:
            print ("FROM: "+str(full_file)+" to: "+str(target_filename))
            shutil.copyfile(full_file,target_filename)
            
        if 'run_all_cases' in b:
            c+=1
            print ("#"+str(c)+")  RUNNING_BULK: "+str(case_name))
            
            try:
                MAIN_ENTRYPOINT_CASE_processing_pipeline(case_name)
            except Exception as e:
                print ("RUNNING_BULK exception: at case: "+str(case_name)+" "+str(e))


        
    return

if __name__=='__main__':
    branches=['dev1']
    for b in branches:
        globals()[b]()








