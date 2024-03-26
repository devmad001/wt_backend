import os
import sys
import codecs
import json
import re
import psutil

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")


#0v1# JC  Sep 11, 2023  Setup


"""
    HANDLER FOR BACKGROUND TASKS WILL SPAWN run_background_tasks.p
"""


def check_if_process_running(process_name):
    '''Check if there is any running process that contains the given name.'''
    try:
        for proc in psutil.process_iter():
            pinfo = proc.as_dict(attrs=['pid', 'name', 'cmdline'])
            if process_name.lower() in pinfo['name'].lower():
                # Checking by process name
                return True
            if pinfo['cmdline'] and process_name in ' '.join(pinfo['cmdline']):
                # Checking by arguments if the process name isn't found
                return True
        return False
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
        return False


def check_if_process_argument_running(process_name, argument):
    '''Check if there is any running process that contains the given name and argument.'''
    try:
        for proc in psutil.process_iter():
            pinfo = proc.as_dict(attrs=['pid', 'name', 'cmdline'])
            
            # Check process name
            if process_name.lower() not in pinfo['name'].lower():
                continue

            # Check arguments
            if pinfo['cmdline'] and argument in ' '.join(pinfo['cmdline']):
                return True
                
        return False
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
        return False

def dev_background():
    # Check if 'run.py' is running
    cmd='python run_background_tasks.py'
    process_name='run_background_tasks.py'
    argument='case_1'

    cmd+=" "+argument

    #if not check_if_process_running(process_name):
    if not check_if_process_argument_running(process_name,argument):
        print ("STARTING: "+cmd)
        os.system(cmd)

    else:
        print("'run.py' is already running.")

    return

def call_run_pipeline_background(case_id):
    ## Import and run this
    ## ideally submitted as job to request queue but ok in background

    cmd='python run_background_tasks.py'
    process_name='run_background_tasks.py'

    method='run_pipeline'
    argument=case_id

    cmd+=" "+method
    cmd+=" "+argument

    #if not check_if_process_running(process_name):
    is_started=False
    if not check_if_process_argument_running(process_name,argument):
        print ("STARTING: "+cmd)
        os.system(cmd)
        is_started=True

    else:
        print(process_name+" is already running.")

    return is_started,{}

if __name__=='__main__':
    branches=['dev1']
    branches=['dev_background']
    for b in branches:
        globals()[b]()
        


"""
"""
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
