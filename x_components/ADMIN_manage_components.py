import os
import sys
import codecs
import json
import re

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")

from w_file_repo.manage_pdfs import interface_get_pdf_content

from flask import Flask, render_template, send_from_directory, request, Response
from flask_cors import CORS

from get_logger import setup_logging
logging=setup_logging()


#0v1# JC  Oct 13, 2023  Init

"""
    ADMIN Management of various component views
"""

### CONFIG
config_file=LOCAL_PATH+'../'+'w_config_dashboard.json'
def load_config():
    global config_file
    DASH={}
    with open(config_file, 'r') as fp:
        CONFIG = json.load(fp)
    DASH=CONFIG['dashboards']['square']
    return CONFIG,DASH
CONFIG,DASH=load_config()


print("dashboard:", DASH)


def dev_component_notes():
    print ("[square view]")
    print ("> handle views in serve_ui_flask")
    
    view_names=[]
    #> upload_viewport is stand alone service
    view_names+=['dump_excel','view_cases_status','start_case_processing','view_debug_logs']
    

    view_types=[]

    view_types+=['square']
    view_types+=['pdf_viewer_in_square_flask_only']
    view_types+=['[button] -> upload drag & drop viewport']


    view_types+=['[button] -> dump excel handler http://127.0.0.1:8081/case/case_wells_fargo_small/get_excel?case_id=case_wells_fargo_small&session_id=1']
    view_types+=['[button] -> view running status viewport']
    ## Extra
    view_types+=['[button] -> ?handle run request for case']
    view_types+=['[button] -> view debug logs']


    return


if __name__ == "__main__":
    dev_component_notes()
    

"""

"""

