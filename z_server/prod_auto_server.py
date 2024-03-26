import os
import sys
import time
import codecs
import json
import re
import subprocess
import requests

import configparser as ConfigParser

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")

from w_utils import am_i_on_server
from mod_execute.mod_execute import The_Execute_Command
from mod_execute.mod_execute import is_process_running_linux

from dev_auto_server import Local_Admin

from get_logger import setup_logging
logging=setup_logging()


#0v1# JC  Nov  9, 2023  Init


"""
    PRODUCTION AUTO SERVER
    - node (at least developer view)
    - fast_main.py API
    - ^ does that include pdf viewer?
    
    *see:  dev_auto_server.py


"""
print ("RECALL TERMINATING ALL fast_main:  lsof -t -i :8008 | xargs kill")


## CORE SETTINGS
Config = ConfigParser.ConfigParser()
Config.read(LOCAL_PATH+"../w_settings.ini")
BASE_STORAGE_DIR=Config.get('files','base_storage_rel_dir')
BASE_STORAGE_DIR=LOCAL_PATH+"../"+BASE_STORAGE_DIR

## APPS CONFIG
config_file=LOCAL_PATH+'../'+'w_config_dashboard.json'
def load_config():
    global config_file
    with open(config_file, 'r') as fp:
        CONFIG = json.load(fp)
    return CONFIG

CONFIG=load_config()

ON_SERVER=am_i_on_server()
NOHUP_LOGS_DIR=LOCAL_PATH+"nohup_logs"



def normal_start_standard():
    # (base off dev_auto_server

    Admin=Local_Admin()
    disable=['chatbot']
    

    ########################################################
    ## WS fast_ws.py
    ########################################################
    print ("cd z_apiengine & python fast_ws_v1.py")
    print ("^ at http://127.0.0.1:8009 or ws.")
    pname='fast_ws'
    is_process_running=Admin.is_process_running(pname)
    if not is_process_running:
        run_cmd='cd '+LOCAL_PATH+"../z_apiengine && python fast_ws_v1.py"   #*** keep single until verify websocket connection handling

        log_name=re.sub(r'\..*','',pname)+".log"
        print ("==== SPAWNING: ws websocket process (warning at start is normal)  "+str(run_cmd))
        Admin.spawn_process(run_cmd,log_name=log_name)

    

    ########################################################
    ## NODE DEV DASHBOARD VIEW
    ########################################################
    # cd ../wt_dash
    # npm run dev
    local_node_endpoint='http://127.0.0.1:5173'
    try: rr=requests.get(local_node_endpoint)
    except: rr=None
    if not rr:
        print ("Dev wt_dash is not activated.  cd ../wt_dash && npm run dev at :5173")
    

    if not 'chatbot' in disable:
        ########################################################
        ## CHATBOT 
        ########################################################
        bot=CONFIG['dashboards']['chatbot']
        print ("CHATBOT: "+str(bot))
        print ("CHATBOT: "+str(bot['sample_call']))
        print ("CHATBOT: "+str("http://127.0.0.1:"+str(bot['port'])))
        cmd='cd w_chatbot & python -m streamlit run wt_streamlit.py --server.port 8082'
        print ("CMD: "+str(cmd))
    
        chatbot_pname='streamlit'
        is_process_running=Admin.is_process_running(chatbot_pname)
        if not is_process_running:
            run_cmd='cd '+LOCAL_PATH+"../w_chatbot && python -m streamlit run wt_streamlit.py --server.port 8082"
            log_name=re.sub(r'\..*','',chatbot_pname)+".log"
            print ("==== SPAWNING: "+str(run_cmd))
            Admin.spawn_process(run_cmd,log_name=log_name)
    
    

    ########################################################
    ## fast_main.py  (has bot handler now)
    ########################################################
    #print ("RECALL TERMINATING ALL fast_main:  lsof -t -i :8008 | xargs kill")
    print ("cd z_apiengine & python fast_main.py")
    print ("^ at http://127.0.0.1:8008 or core.")
    pname='fast_main'
    is_process_running=Admin.is_process_running(pname)
    if not is_process_running:
        #b4 f22# run_cmd='cd '+LOCAL_PATH+"../z_apiengine && python -m uvicorn fast_main:app --port 8008 --workers 3"
        run_cmd='cd '+LOCAL_PATH+"../z_apiengine && python -m uvicorn fast_main:app --port 8008 --workers 10"
        log_name=re.sub(r'\..*','',pname)+".log"
        print ("==== SPAWNING: 10 workers!  "+str(run_cmd))
        Admin.spawn_process(run_cmd,log_name=log_name)

    return


def dev1():
    start_local_node()

    return




def force_auto_restart_server_endpoint():
#    iu=sure

    Admin=Local_Admin()

    print ("FULL SERVER ENDPOINT RESTART")
    print ("RECALL TERMINATING ALL fast_main:  lsof -t -i :8008 | xargs kill")
    cmd='lsof -t -i :8008 | xargs kill'
    print ("RUN: "+str(cmd))
    os.system(cmd)

    cmd='pkill fast_main'
    print ("RUN: "+str(cmd))
    os.system(cmd)

    print ("SLEEP 3...")
    time.sleep(3)

    ## fast_main.py  (has bot handler now)
    print ("cd z_apiengine & python fast_main.py")
    print ("^ at http://127.0.0.1:8008 or core.")
    pname='fast_main'
    is_process_running=Admin.is_process_running(pname)
    if not is_process_running:
        run_cmd='cd '+LOCAL_PATH+"../z_apiengine && python -m uvicorn fast_main:app --port 8008 --workers 10"
        log_name=re.sub(r'\..*','',pname)+".log"
        print ("==== SPAWNING: 10 workers!  "+str(run_cmd))
        Admin.spawn_process(run_cmd,log_name=log_name)

    return



if __name__=='__main__':
    branches=['force_auto_restart_server_endpoint']
    branches=['normal_start_standard']

    for b in branches:
        globals()[b]()






"""
"""
