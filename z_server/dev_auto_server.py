import os
import sys
import time
import codecs
import json
import re
import subprocess

import configparser as ConfigParser

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")

from w_utils import am_i_on_server
from mod_execute.mod_execute import The_Execute_Command
from mod_execute.mod_execute import is_process_running_linux

from get_logger import setup_logging
logging=setup_logging()

#0v1# JC  Sep 26, 2023  Init


"""
    MANAGER SERVER SERVICES
    - SLA ensure uptime!
    - Log all exceptions of downtime!
"""

## ALL CONFIG CHECK


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


class Single_Service_Manager:
    def __init__(self):
        return
    
class Local_Admin:
    def __init__(self):
        self.Exe=The_Execute_Command()
        return
    
    def is_process_running(self,pname,verbose=False):
        pname=pname.strip()
        if pname and self.Exe.is_running(pname,verbose=verbose):
            return True
        else:
            return False
        
    def is_endpoint_up(self,base_url):
        #?ping?
        return False
    
    def spawn_process_OVERWRITE_LOG(self,cmd,log_name='default_log'):
        global ON_SERVER
        if not log_name: raise Exception ("Include log name!")

        if not ON_SERVER:
            print ("ON SERVER: "+str(ON_SERVER))
            self.Exe.execute(cmd,visible=True,background=True)
        else:
            ## Linux shell cmd
            NOHUP_LOGS_DIR=LOCAL_PATH+"nohup_logs"
            print ("[dev] ready to spawn: "+str(cmd))

            ## linux wrap spawn in nohup
            cmd="nohup bash -c '"+cmd+"' > "+NOHUP_LOGS_DIR+"/"+log_name+" 2>&1 &"  #Err and normal to log

            subprocess.Popen(cmd, shell=True)

            print ("RAN> "+cmd)

        return


    def spawn_process(self, cmd, log_name='default_log'):
        #** auto increment filename on each run
        global ON_SERVER
        if not log_name:
            raise Exception("Include log name!")
    
        if not ON_SERVER:
            print("ON SERVER: " + str(ON_SERVER))
            self.Exe.execute(cmd, visible=True, background=True)
        else:
            # Linux shell cmd
            NOHUP_LOGS_DIR = LOCAL_PATH + "nohup_logs"
            if not os.path.exists(NOHUP_LOGS_DIR):
                os.makedirs(NOHUP_LOGS_DIR)
    
            # Increment log file name if it already exists
            log_index = 0
            original_log_name = log_name
            while os.path.exists(f"{NOHUP_LOGS_DIR}/{log_name}"):
                log_index += 1
                log_name = f"{original_log_name}_{log_index}"
    
            # linux wrap spawn in nohup
            cmd = f"nohup bash -c '{cmd}' > {NOHUP_LOGS_DIR}/{log_name} 2>&1 &"  # Err and normal to log
    
            subprocess.Popen(cmd, shell=True)
    
            print("RAN> " + cmd)
    
        return


def dev_manage_services():
    global ON_SERVER
    
    Admin=Local_Admin()

    print ("**keep common functions in mod_execute!")
    print ("[chatskit has executor]")
    print ("[ ] workon + mkvirtualenv")
    

    actions=[]
    ### STEP THROUGH DASHBOARD CONFIG
    for dash_id in CONFIG['dashboards']:

        dash=CONFIG['dashboards'][dash_id]

        ## PREPARE DIRS
        if not ON_SERVER:
            base_url=CONFIG['local_url']+":"+str(dash.get('port',80))
        else:
            base_url=CONFIG['base_url']+":"+str(dashget('port',80))
            
        ## PREPARE PROCESS NAMES
        pname=re.sub(r'\.py.*','.py',dash.get('server_start_cmd',''))
        pname=re.sub(r'.*[\/\\ ]','',pname).strip()
        if not pname.strip() or 'admin' == dash_id or len(str(pname).strip())==1: continue
            
        ## Check alive endpoint or assume '/'
        print ("[dev] is service ["+str(dash_id)+"] alive: "+base_url)
        is_process_running=Admin.is_process_running(pname)

        if not pname.strip() or 'admin' == dash_id or len(str(pname).strip())==1: continue
        print ("PNAME: >"+str(pname)+"< running: "+str(is_process_running))

        if dash.get('server_dir',''):
            run_cmd='cd '+LOCAL_PATH+'..'+dash['server_dir']+' && '+dash['server_start_cmd']
            print (run_cmd)
            
            if not is_process_running:
                action='RUN THIS COMMAND: '+run_cmd
                print (">>>>>>>>>>>>> "+str(action))
                actions+=[action]

        else:
            pass
            #print ("[warning] no start commend for ^^")

    return

def dev_spawn_in_background():
    cmd='cd /home/ubuntu/wt/x_timeline/bank_failures && python run_obs.py'
    print ("[dev] spawning: "+str(cmd))

    Admin=Local_Admin()
    Admin.spawn_process(cmd,log_name='')
    print ("[dev done]")
    time.sleep(5)
    return

def RUN_management_stories():
    b=['if process not running, spawn in background']

    
    Admin=Local_Admin()

    actions=[]

    ### STEP THROUGH DASHBOARD CONFIG
    for dash_id in CONFIG['dashboards']:

        dash=CONFIG['dashboards'][dash_id]

        ## PREPARE DIRS
        if not ON_SERVER:
            base_url=CONFIG['local_url']+":"+str(dash.get('port',80))
        else:
            base_url=CONFIG['base_url']+":"+str(dash.get('port',80))
            
        ## PREPARE PROCESS NAMES
        pname=re.sub(r'\.py.*','.py',dash.get('server_start_cmd',''))
        pname=re.sub(r'.*[\/\\ ]','',pname)
            
        ## Check alive endpoint or assume '/'
        print ("[dev] is service ["+str(dash_id)+"] alive: "+base_url)

        if ON_SERVER:
            is_process_running=is_process_running_linux(pname)
        else:
            is_process_running=Admin.is_process_running(pname)
        if not pname.strip() or 'admin' == dash_id or len(str(pname).strip())==1: continue
        print ("PNAME: "+str(pname)+" running: "+str(is_process_running))
        
        ########## STORY:  Spawn if not running
        if 'if process not running, spawn in background' in b:
            if not is_process_running:
                if dash.get('server_dir',''):
                    run_cmd='cd '+LOCAL_PATH+'..'+dash['server_dir']+' && '+dash['server_start_cmd']
                    print (run_cmd)
                    logging.info("[SERVER ADMIN]: Spawning process: "+run_cmd)
                    log_name=re.sub(r'\..*','',pname)+".log"
                    Admin.spawn_process(run_cmd,log_name=log_name)
                    actions+=['spawned: '+run_cmd]

    logging.info("[done RUN management stories]: "+str(actions))
    return




if __name__=='__main__':
    branches=['dev_manage_services']
    branches=['dev_spawn_in_background']
    branches=['RUN_management_stories']

    for b in branches:
        globals()[b]()






"""
source devops/chatskit/bin/activate
echo nohup python manage.py runserver 0.0.0.0:8000> nohup_runserver.out & 
echo ^^ port 8000

echo FOR SMART USER:
echo nohup python flask_wag.py > nohup_flask_wag.out &


def alg_list_wag_concepts():
    global EC
    #wagtail
    cwd=LOCAL_PATH
    wag_concepts=EC.call_venv_function('wagtail1','AUTO_wag_scripts','interface_list_concepts',cwd=cwd)
    meta={}
    return wag_concepts,meta


# TWO:  chatgpt

    sers\jon\envs\wagtail1\Scripts \a ctivate.bat && python -c "from AUTO_wag_scripts import interface_list_concepts; print(interface_list_concept
    cmd="call c:/Users/jon/envs/"+workon+"/Scripts/activate.bat && "
    cmd+="cd "+cwd+" && "
    cmd+="set OPENAI_API_KEY=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 && "
    cmd+=""python -c "from ""+script_py+"" import ""+function_name+""; print(""+function_name+""())" ""

"""
