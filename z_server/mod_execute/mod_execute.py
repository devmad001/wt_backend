from __future__ import division
import sys
import re
import os
import subprocess
import time

import json
#import simplejson as json #support for single quotes
import ast

## 
LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
from executor import Execute_Command


#0v3# JC Apr 18, 2023  Integrate back to mods + ehub
#0v2# JC Apr 17, 2023  Add venv call
#0v1# JC Apr  2, 2020  CLEAN

## Recall
#- originally performance, then executor, now, mode_execute
#- issues with capturing ALL output stream (esp when fast), and cross platform


## TODO:
#[ ] run_command_iter needs to return sys.stderr if command fails (instead of nothing)


class The_Execute_Command(Execute_Command):
    def __init__(self):
        self.is_windows=True
        if 'linux' in sys.platform: self.is_windows=False
        super(The_Execute_Command,self).__init__()
        return

    def is_running(self,regex,kill_if_running=False,verbose=False):
        # direct call
        #? works linkux??
        return super(The_Execute_Command,self).is_running(regex,kill_if_running=kill_if_running,verbose=verbose)
    
    def execute(self,cmd,cwd='',workon='',visible=True,background=False):
        if not cwd: cwd=LOCAL_PATH
        if self.is_windows and background:
            self.run_windows_background(cmd,cwd,workon=workon,visible=visible)
        else:
            raise Exception("Not supported exe (only windows + background)")
        return
    
    def run_command_iter(self,cmd,echo=False,python_path='',cwd='',background=False,spawn=False,workon='',verbose=False):
        #> used in phantom call for debug
        for liner in super(The_Execute_Command,self).run_command_iter(cmd,echo=echo,python_path=python_path,cwd=cwd,background=background,spawn=spawn,workon=workon,verbose=verbose):
            yield liner
        return

    ## Experimental (via TK_CHATSKIT)
    def call_venv_function(self,workon,script_py,function_name,cwd='',extra_cmds=[],echo=False, args=[], kwargs={}):
        #[ ]** beware will fail on error so optional check via direct import or xxx?
        if not cwd:
            cwd=LOCAL_PATH

        cmd=""

        if workon:
            cmd+="call c:/Users/jon/envs/"+workon+"/Scripts/activate.bat && "
        if cwd:
            cmd+="cd "+cwd+" && "

        for ecmd in extra_cmds:
            cmd+=ecmd+" && "

        ## Clean
        script_py=re.sub(r'\.py$','',script_py,flags=re.I)

        if not args and not kwargs:
            cmd+="""python -c "from """+script_py+""" import """+function_name+"""; print("""+function_name+"""())" """
        else:
            args_str=[]
            for arg in args:
                args_str.append("'"+str(arg)+"'")
                args_str=','.join(args_str)
            
            if kwargs:
                kwargs_str = ' '.join([f"{key}='{value}'" for key, value in kwargs.items()])

            ## Special handling parameters
            if args and not kwargs:
                #Join list of args as quoted strings
                cmd+="""python -c "from """+script_py+""" import """+function_name+"""; print("""+function_name+"""("""+args_str+"""))" """

            elif kwargs and not args:
                # These could be run?key1=val1&key2=val2
                #print ("JSON: "+str(kwargs_str))
                cmd+="""python -c "from """+script_py+""" import """+function_name+"""; print("""+function_name+"""("""+kwargs_str+"""))" """
            elif kwargs and args:
                both=args_str+','+kwargs_str
                cmd+="""python -c "from """+script_py+""" import """+function_name+"""; print("""+function_name+"""("""+both+"""))" """
                pass
            else:
                raise Exception("Not supported")

        if echo:
            print ("[echo] "+str(cmd) )
        print ("[echo] "+str(cmd) )

        results=[]
        for liner in self.run_command_iter(cmd,echo=False):
            liner_obj=[]
            ## Load it
            try:
                liner_obj=json.loads(liner) #no single quotes!
            except:
                try:
                    liner_obj=ast.literal_eval(liner)
                except:
                    try: liner_obj=str(liner) #or encode
                    except: liner_obj=liner

            ## Normalize it
            if isinstance(liner_obj,dict):
                liner_obj=[liner_obj]
            elif not isinstance(liner_obj,list):
                try: liner_obj=[liner_obj.strip()]  #no /r
                except:
                    liner_obj=[liner_obj]
    
            if liner_obj:
                results+=liner_obj

        return results

## Sample from ai_flask for running arbitrary LOCALLY visible function directly within this space
##@app.route('/<library>/<function>')
#@app.route('/<library>/<function>/<path:args>')
#def run_library_function(library, function, args):
#    try:
#        lib = importlib.import_module(library)
#    except:
#        install_package(library)
#        lib = importlib.import_module(library)
#    func = getattr(lib, function)
#
#    arg_list = [arg for arg in args.split('/')]
#    query_args = {k: v for k, v in request.args.items()}
#    dtype = query_args.get('dtype', 'float')
#    arg_list = [convert_type(arg, dtype) for arg in arg_list]
##    result = func(*arg_list, **query_args)
#    return str(result)
    


def is_process_running_linux(process_name):
    # ** ignore vi opened files
    # DEV:  Sep 27, 2023
    if not process_name.strip(): return False

    try:
        # Run a command to get the list of process IDs that have process_name
        proc = subprocess.Popen(['pgrep', '-af', process_name], stdout=subprocess.PIPE)
        # Read from the pipe
        out, err = proc.communicate()

        # Convert the output to a string and split into a list of lines
        process_list = out.decode().split('\n')

        # Iterate over the lines and print them
        for process in process_list:
            if process:
                if process_name in process and not ' vi ' in str(process):
                    print(f'Process "{process_name}" is running: {process}')
                    return True
        print(f'Process "{process_name}" is not running')
        return False
    except Exception as e:
        print(f'Error occurred while checking for "{process_name}" process: {e}')
        return False

def is_script_running_with_arg(script_name, arg):
    # Example Usage
    #is_script_running_with_arg("running1.py", "argumentA")

    if not script_name.strip() or not arg.strip(): return False

    try:
        # Run a command to get the list of Python process IDs and script names with arguments
        proc = subprocess.Popen(['pgrep', '-af', 'python'], stdout=subprocess.PIPE)
        # Read from the pipe
        out, err = proc.communicate()

        # Convert the output to a string and split into a list of lines
        process_list = out.decode().split('\n')

        # Iterate over the lines to find the script with the specific argument
        for process in process_list:
            if script_name in process and arg in process:
                print(f'Script "{script_name}" with argument "{arg}" is running: {process}')
                return True
                
        print(f'Script "{script_name}" with argument "{arg}" is not running')
        return False
    except Exception as e:
        print(f'Error occurred while checking for "{script_name}" script with argument "{arg}": {e}')
        return False



def sample_modes():
    if False:
        self.run_windows_background('echo Hello World flash then close','.',workon='python3',visible=True)

    if False:
        wd="./bot_utilities"
        script_py="bot_sleep.py"
        for line in Exe.run_python_iter(script_py,cwd=wd,allow_multiple_instances=False,kill_if_running=True,background=True,spawn=True):
            pass
    return
    
         
def dev1():
    Exe=The_Execute_Command()
    #Exe.execute('')
    #Exe.run_windows_background('echo Hello World flash then close','.',workon='python3',visible=True)
    Exe.is_running('bot_sleep',kill_if_running=True,verbose=True)
    
    print ("Done dev1")
    return
    

if __name__=='__main__':
    branches=['dev1']

    for b in branches:
        globals()[b]()
