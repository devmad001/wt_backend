import os
import sys
import codecs
import json
import re
import time

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")


#0v1# JC  Sep 11, 2023  Setup


"""
    BACKGROUND PIPELINE RUN
    - ie/ called from server
    - SEE:  sim_user.py for standard entrypoints
"""


def run_pipeline_background(case_id):
    print("Running pipeline in background: "+str(case_id))
    time.sleep(60)
    return

    ## Typically calling pipeline requires job (agent) help
    if case_id:
        print ("[debug] calling: interface_call_agent_handle_case_request")
        from a_agent.run_iagent import interface_call_agent_handle_case_request
        interface_call_agent_handle_case_request(case_id=case_id)

    return


def main(args):
    #0: script name (this)
    #1: function
    #2: argument
    print(f"Received argument: {args}")

    if len(args)>2:
        if args[1]=='run_pipeline':
            run_pipeline_background(args[1])
        else:
            print ("[debug] odd arg: "+str(args[0]))
    else:
        print ("[debug] not enough args")

    return


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Please provide an argument.")
        sys.exit(1)
    main(sys.argv)


        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
