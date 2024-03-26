import os
import sys
import codecs
import json
import re

from fastapi import FastAPI

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")

sys.path.insert(0,LOCAL_PATH+"../..")

from w_mindstate.mindstate import Mindstate
from a_agent.interface_manager import Manager_Interface

from w_ui.api_helper import UX_Helper

from w_ui.sim_user import interface_get_job_status  #For job start


from get_logger import setup_logging
logging=setup_logging()


        
#0v1# JC Nov  2, 2023  Setup


"""
    VARIOUS COMMAND SERVICES
    - 
"""


#MIND=Mindstate()

MANAGER=Manager_Interface()

def get_execution_log_html(case_id):
    global MANAGER

    liners: List[str] = []
    
    # Check debug log
    fname, debug_log = MANAGER.dump_latest_log(case_id)
    liners.append(f"<p>Case log filename: {fname}</p>")
    
    liners.append('<p>RAW LOG:</p>')
    liners.append('<pre>' + "\n".join(debug_log.split('\n')) + '</pre>')

    
    # Construct HTML content

    #### STATUS 2 line statu#s
    # QUERY via api_services.py OR directly to api_helper
 
    
    # Construct HTML content
    
    html_content = """
        <html>
        <head>
            <style>
                p {
                    margin-top: 1px;
                    margin-bottom: 1px;
                }
                 body,
        html {
             margin: 15 0 15 15;
             line-height: 1.5;
             /*padding: 0; */
            /* background-color: #f2f2f2;*/
            /* height: 100%;  removes scrollbars great*/
            /* basic beige */
            /* background-color: #f0f9ff; /* watchtower light blue */
    
            font-family: "Inter", Sans-serif;
            font-size: 17px;
            /* This is the base font-size for the page */
            font-weight: 400;
            /* This sets the default weight to regular */
            font-style: normal;
            /* This sets the default style to normal */
            overflow-y:auto;
            /* overflow: hidden; */
    
        }

            </style>
        </head
        <body>
        """
        
    if True:
        html_content += f"<h1>Execution Log for Case: {case_id}</h1>"
        for line in liners:
            html_content += f"<p>{line}</p>"
            
    ## NEW STATUS


    UX=UX_Helper()
    # ['is_case_ready_to_query', 'case_files', 'is_case_running', 'estimated_case_running_time_remaining_m', 'case_status_sub_word', 'case_status_word']
    

    umeta=UX.dump_user_ux_meta(case_id=case_id)
    html_content += f"<h1>Case Status</h1>"
    html_content += f"<br>"
    html_content += f"<p>State: "+str(umeta['case_status_word'])+"</p>"  # Ready for query etc..
    html_content += f"<br>"
    html_content += f"<p>"+str(umeta['case_status_sub_word'])+"</p>"     # Active Files: , etc.

    html_content += "</body></html>"
    
    return html_content


def get_process_state_html(case_id):
    global MANAGER

    liners: List[str] = []
    
    # ALL case states
    cases_running = MANAGER.which_cases_are_running()
    liners.append(f"<p>[debug view remove] call active cases running: {cases_running}</p>")
    
    # CASE STATE
    simple_case_state = MANAGER.what_is_the_last_state_of_case(case_id)
    liners.append(f"<p>[case state]: {simple_case_state} for: {case_id}</p>")
    
    # Check debug log
    fname, debug_log = MANAGER.dump_latest_log(case_id)
    liners.append(f"<p>Case log filename: {fname}</p>")
    
    liners.append('<p>RAW LOG:</p>')
    liners.append('<pre>' + "\n".join(debug_log.split('\n')) + '</pre>')


    
    # Construct HTML content

    #### STATUS 2 line statu#s
    # QUERY via api_services.py OR directly to api_helper
 
    
    # Construct HTML content
    
    html_content = """
        <html>
        <head>
            <style>
                p {
                    margin-top: 1px;
                    margin-bottom: 1px;
                }
                 body,
        html {
             margin: 15 0 15 15;
             line-height: 1.5;
             /*padding: 0; */
            /* background-color: #f2f2f2;*/
            /* height: 100%;  removes scrollbars great*/
            /* basic beige */
            /* background-color: #f0f9ff; /* watchtower light blue */
    
            font-family: "Inter", Sans-serif;
            font-size: 17px;
            /* This is the base font-size for the page */
            font-weight: 400;
            /* This sets the default weight to regular */
            font-style: normal;
            /* This sets the default style to normal */
            overflow-y:auto;
            /* overflow: hidden; */
    
        }

            </style>
        </head
        <body>
        """
        
    if False: #Org debug view
        html_content += f"<h1>(*development view...in-progress)  Process Status for Case: {case_id}</h1>"
        for line in liners:
            html_content += f"<p>{line}</p>"
            
    ## NEW STATUS


    UX=UX_Helper()
    # ['is_case_ready_to_query', 'case_files', 'is_case_running', 'estimated_case_running_time_remaining_m', 'case_status_sub_word', 'case_status_word']
    

    umeta=UX.dump_user_ux_meta(case_id=case_id)
    html_content += f"<h1>Case Status</h1>"
    html_content += f"<br>"
    html_content += f"<p>State: "+str(umeta['case_status_word'])+"</p>"  # Ready for query etc..
    html_content += f"<br>"
    html_content += f"<p>"+str(umeta['case_status_sub_word'])+"</p>"     # Active Files: , etc.

    html_content += "</body></html>"
    
    return html_content


def get_process_start_html(case_id):
    global MANAGER
    """
    a_agent/interface_manager.py Manager_interface
    : start background which cases running, last case and state, last state,
    : 
        w_ui/sim_user.py  interface_get_job_status

    """

    liners=[]
    
    ## CASE STATE
    simple_case_state=MANAGER.what_is_the_last_state_of_case(case_id)
    liners+=["[case state]: "+str(simple_case_state)+" for: "+str(case_id)]
    
    ## Active cases running
    cases_running=MANAGER.which_cases_are_running()
    liners+=["[cases running (before start)]: "+str(cases_running)]
    
    ## Job state
    #- does not check for running background job
    job_status=interface_get_job_status(case_id)
    # {'is_case_running_in_background': False, 'is_job_running': False, 'has_job_ever_finished': True, 'age_of_last_active_m': 2510.15, 'age_since_started_m': 2522.7591921448707, 'job_raw_page_count': 4, 'estimated_time_remaining': 0}
   

    ## Start
    started_new_job=False
    if not case_id in cases_running:
        liners+=["[STARTED NEW BACKGROUND JOB FOR CASE]: "+str(case_id)]
        started_new_job=True
        MANAGER.start_long_running_job_process_in_background(case_id)
    else:
        liners+=["BACKGROUND JOB ALREADY RUNNING!"]
    
    # Construct HTML content
    html_content = """
        <html>
        <head>
            <style>
                p {
                    margin-top: 1px;
                    margin-bottom: 1px;
                }
                 body,
        html {
             margin: 15;
             line-height: 1.5;
             /*padding: 0; */
            /* background-color: #f2f2f2;*/
            height: 100%;
            overflow: hidden;
            /* basic beige */
            /* background-color: #f0f9ff; /* watchtower light blue */
    
            font-family: "Inter", Sans-serif;
            font-size: 17px;
            /* This is the base font-size for the page */
            font-weight: 400;
            /* This sets the default weight to regular */
            font-style: normal;
            /* This sets the default style to normal */
    
        }

            </style>
        </head>
        <body>
        """
    
    #        Estimated time remaining: """+str(int(job_status.get('estimated_time_remaining','')))+""" minutes
    
    html_content += "<h1>Active Case Analysis Info</h1>"
    
    html_content += """
    <div id="infoview">
        <table style="border-collapse: collapse; width: 100%;">
            <tr>
                <td style="width: 20%; padding: 5px; border: none;">Active Case id:</td>
                <td style="width: 80%; padding: 5px; border: none;">""" + str(case_id) + """</td>
            </tr>
            <tr>
                <td style="width: 20%; padding: 5px; border: none;">Time since started:</td>
                <td style="width: 80%; padding: 5px; border: none;">""" + str(int(job_status.get('age_since_started_m',0))) + """ minutes</td>
            </tr>
    """
    
    if started_new_job:
        html_content += """
            <tr>
                <td style="width: 20%; padding: 5px; border: none;">Last state:</td>
                <td style="width: 80%; padding: 5px; border: none;">STARTING NEW CASE ANALYSIS...</td>
            </tr>
        """
    else:
        html_content += """
            <tr>
                <td style="width: 20%; padding: 5px; border: none;">Last state:</td>
                <td style="width: 80%; padding: 5px; border: none;">Case '""" + str(case_id) + """' is already running in the background.</td>
            </tr>
        """
    
    html_content += """
        </table>
    </div>
    """
    html_content += "<br>"
    html_content += "<h2>Other Cases:</h2>"
    html_content += "**tbd: user cases manager view"
    


#    ### THIS STATUS
#    for line in liners:
#        html_content += f"<p>{line}</p>"

    html_content += "</body></html>"

    return html_content


def get_process_admin_html(case_id):
    global MANAGER

    liners=[]
    
    ## CASE STATE
    simple_case_state=MANAGER.what_is_the_last_state_of_case(case_id)
    liners+=["[case state]: "+str(simple_case_state)+" for: "+str(case_id)]
    
    ## Active cases running
    cases_running=MANAGER.which_cases_are_running()
    liners+=["[cases running (before start)]: "+str(cases_running)]

    ## Start
    if not case_id in cases_running:
        liners+=["[STARTED NEW BACKGROUND JOB FOR CASE]: "+str(case_id)]
        MANAGER.start_long_running_job_process_in_background(case_id)
    else:
        liners+=["BACKGROUND JOB ALREADY RUNNING!"]
    
    # Construct HTML content
    html_content = """
        <html>
        <head>
            <style>
                p {
                    margin-top: 1px;
                    margin-bottom: 1px;
                }
            </style>
        </head>
        <body>
        """

    html_content += f"<h1>Process START request for Case: {case_id}</h1>"

    for line in liners:
        html_content += f"<p>{line}</p>"
    html_content += "</body></html>"

    return html_content
    

if __name__=='__main__':
    branches=['dev1']
    for b in branches:
        globals()[b]()


"""
"""