import os, sys
import time
import requests


LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")


from z_apiengine.database import SessionLocal
from database_models import Button

from w_utils import get_base_endpoint
from w_utils import get_ws_endpoint

# Interface to LLM (at bot_service -- also possible further down)
#* will spawn ws message to FE

from z_apiengine.services.bot_service import handle_question


from get_logger import setup_logging
logging=setup_logging()

WS_ENDPOINT=get_ws_endpoint()



#0v3# JC Dec 28, 2023  Push query to question handler
#0v2# JC Dec 11, 2023  ...start actually today
#0v1# JC Dec  8, 2023  **start coding today on LAST day (time to integrate)


"""
    BUTTON HUB
    - more exciting then it sounds
    - connect various systems together
    - ideally pub/sub style but for now just keep basic msg passing (even internally is fine)
    
    - Simulation mode?
    - sources and targets?
    - registration, modes, expand, connect, imports, etc.
    - worflows?
    
    *given no time, base around light_workflow_functions
    > light_channel_send_download_request_to_FE()
    
    http://127.0.0.1:5173/case/case_test_loc/run
    
    > services/button_service list_buttons, delete_button, create_set_button


"""


"""
    BUTTON SCHEMA
    action:xxx
    name:
    msg:xxx
    dd:{...}
"""

MODE='dev'

## GIVEN:
#1]  From FE_case_view -> button_handler
# inputs_dict = {
#        "case_id": case_id,
#        "fin_session_id": fin_session_id,
#        "button_label": button_label,
#        "button_action": button_action,
#        "button_id": button_id,
#        **additional_params }



####################################################################
####################################################################
def interface_button_hub(*args,**kwargs):
    ## Kwargs from FE_case_view.py -> /button_handler -> inputs_dict

    ## Call from?  well, button_handler to begin
    print ("[debug] at interface_button_hub given: "+str(kwargs))

    Hub=Button_Hub()
    
    button_id=kwargs.get('button_id',None)
    case_id=kwargs.get('case_id','')
    fin_session_id=kwargs.get('fin_session_id','a3483aff')  #
    user_id=kwargs.get('user_id','manuri3221')  #<-- for now hard code

    if button_id:

        ## Lookup or hard code
        if str(button_id)=='1': ## Download Excel
            print ("[debug] button hub -- download excel!")
            Hub.OUT_spawn_download_excel(case_id)
            
        ##[ ] 2: Accounts Chart, 3: Balance Chart, 4: sample but >10k query
        
        elif str(button_id)=='2': # butterfly /Accounts / Entities
            #  "view_standard_1", is standard
            #  "view_standard_2" is tall ie/ for butterfly
            layout_type='view_standard_2'

            url=assemble_butterfly_source_url(case_id,user_id=user_id,fin_session_id=fin_session_id)
            msg=prepare_ws_force_timeline_url_msg(case_id,url,user_id=user_id,fin_session_id=fin_session_id,layout_type=layout_type)
            logging.info("[debug] butterfly/accounts request message is: "+str(msg))
            Hub._broadcast_ws_msg(case_id,msg,branch='')
        
        elif str(button_id)=='3': # waterfall / Balance over time

            url=assemble_waterfall_source_url(case_id,user_id=user_id,fin_session_id=fin_session_id)
            msg=prepare_ws_force_timeline_url_msg(case_id,url,user_id=user_id,fin_session_id=fin_session_id)
            Hub._broadcast_ws_msg(case_id,msg,branch='')

        else:
            ## Try to execute (requires query to be populated otherwise skip)
            #Get button or pass
            with SessionLocal() as db:
                button=db.query(Button).filter(Button.id==button_id).first()
                if button:
                    if button.query:
                        ## Does downstream ws message push
                        Hub.execute_button_query(case_id,button_id=button_id,button=button)
                    else:
                        logging.info("[warning] no query found for button_id: "+str(button_id))

                else:
                    logging.info("[debug] no button found for id: "+str(button_id))
        

    
    return
####################################################################
####################################################################


class Button_Hub:

    def __init__(self):
        return
    
    def execute_button_query(self,case_id,button_id='',button=None):
        if not button:
            button=self.get_button_by_id(button_id)
        if button:
            if button.query:
                logging.info("[button initiated query] "+str(button.query)+"...")
                handle_question(button.query,case_id,params={})
            else:
                print ("[warning] no query found for button_id: "+str(button_id))
        return
    
    def get_button_by_id(self,button_id):
        with SessionLocal() as db:
            button=db.query(Button).filter(Button.id==button_id).first()
        return button
    
    def OUT_spawn_download_excel(self,case_id):
        #** wrap in here for now
        
        ## MSG
        url=assemble_excel_source_url(case_id)
        msg=prepare_ws_spawn_download_msg(case_id,url)
        # {'action': 'spawn_download', 'url': 'http://127.0.0.1:8008/api/v1/case/case_test_loc/generate_excel'}
        self._broadcast_ws_msg(case_id,msg,branch='spawn_download')
        return
    
    def _broadcast_ws_msg(self,case_id,msg,branch='spawn_download'):
        #** case_id is target channel
        #** recall fast_ws_v1 & broadcast_listener
        #local_broadcast_endpoint=get_base_endpoint()+'/api/v1/case/'+case_id+'/broadcast'

        # Sending the POST request
        broadcast_endpoint=WS_ENDPOINT+"/broadcast_listener"

        response = requests.post(broadcast_endpoint, json=msg)
        
        # Printing the response (for debugging purposes)
        if False:
            print(response.status_code)
            print(response.json())

        return



def dev1():

    Hub=Button_Hub()
    
    ## OPEN BUTTON TASKS
    #( may not need to be here but need to enqueue somewhere)
    

    ## PHASE:  trial basic buttons
    button={}
    button['name']='auto submit question to chatbot: how many transactions are there'

    ## PHASE:  trial download buttons (ws)
    button={}
    button['name']='route download excel request to FE'
    
    ## PHASE:  use an edited button
    ## PHASE:  auto create a button

#ok    ## PHASE:  hook up macros
#ok    button={}
#ok    button['name']='hook up butterfly query'
#ok    button={}
#ok    button['name']='hook up waterfall query'

    return



def assemble_butterfly_source_url(case_id,fin_session_id="A34838448fec8",user_id="manurian2344"):
    """
    https://nets.epventures.co/6579c53c0c64027a3b9f2f34/butterfly?fin_session_id=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2NTcxYjg2YTg4MDYxNjEyYWEyZmM4YjciLCJlbWFpbCI6InNoaXZhbUBzaGl2YW1wYXRlbHMuY29tIiwiaWF0IjoxNzAyNDc3MzY0LCJleHAiOiIyMDIzLTEyLTE0VDAyOjIyOjQ0LjAwMFoifQ.5db7a4f757358edfb23782f7b75bf9e7474a26c2b8704c36bb8cf806e9dc99d2&user_id=6571b86a88061612aa2fc8b7
    """
    base_endpoint="https://nets.epventures.co/"
    extra="?fin_session_id="+fin_session_id+"&user_id="+user_id

    url=base_endpoint+case_id+"/butterfly"
    url+=extra
    return url

def assemble_waterfall_source_url(case_id,fin_session_id="A34838448fec8",user_id="manurian2344"):
    """
    https://nets.epventures.co/6579c53c0c64027a3b9f2f34/waterfall?fin_session_id=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2NTcxYjg2YTg4MDYxNjEyYWEyZmM4YjciLCJlbWFpbCI6InNoaXZhbUBzaGl2YW1wYXRlbHMuY29tIiwiaWF0IjoxNzAyNDc3MzY0LCJleHAiOiIyMDIzLTEyLTE0VDAyOjIyOjQ0LjAwMFoifQ.5db7a4f757358edfb23782f7b75bf9e7474a26c2b8704c36bb8cf806e9dc99d2&user_id=6571b86a88061612aa2fc8b7
    
    """
    base_endpoint="https://nets.epventures.co/"
    extra="?fin_session_id="+fin_session_id+"&user_id="+user_id

    url=base_endpoint+case_id+"/waterfall"
    url+=extra
    return url
    

def assemble_excel_source_url(case_id):
    url_source='/api/v1/case/'+case_id+'/generate_excel'
    base_endpoint=get_base_endpoint()
    url=base_endpoint+url_source
    return url

def prepare_ws_spawn_download_msg(case_id,url,session_id='123',layout_type='view_standard_1'):
    #  "view_standard_1", is standard,  "view_standard_2" is tall ie/ for butterfly
    #[ ] migrate to ws_servcie
    #[ ] check for 200?
    ## Per expected broadcast_listener
    msg = {
    "data": {
        "case_id": case_id,
        "session_id": session_id,
        "update_type": 'spawn_download',
        "force_datahash_change": False,
        "action": "spawn_download", 
        "layout_type": layout_type,
        "url": url
        }
    }

    return msg

def dev2():
    ## EXCEL
    """
    general_router-> generate_excel
     {'action': 'spawn_download', 'url': 'http://127.0.0.1:8008/api/v1/case/case_test_loc/generate_excel'}
    """
    
    case_id='case_test_loc'

    ## ASSEMBLE
    url=assemble_excel_source_url(case_id)
    method='ws_spawn_download'
    print ("URL: "+str(url))
    
    msg=prepare_ws_spawn_download_msg(case_id,url,session_id='123')
    print ("MSG: "+str(msg))

    return


def AUTOMATE_button_cap():
    #** running if connected ws should see update.
    #http://127.0.0.1:5173/case/case_test_loc/run
    
    Hub=Button_Hub()
    Hub.OUT_spawn_download_excel('case_test_loc') #<-- locally if ws listening/connected

    return


#############################
# BUTTON SERVICE ENDPOITNS:
#
#> button_service.py
#############################

def LIST_known_buttons():
    #* see button_service.py for general CRUD

    case_id='case_test_loc'
    #?by username? by case?
    
    with SessionLocal() as db:
        buttons=db.query(Button).all()
        for button in buttons:
            print (str(button.id)+" >> "+str(button))

    return


def dev_chart_buttons():

    """
    https://nets.epventures.co/6579c53c0c64027a3b9f2f34/butterfly?fin_session_id=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2NTcxYjg2YTg4MDYxNjEyYWEyZmM4YjciLCJlbWFpbCI6InNoaXZhbUBzaGl2YW1wYXRlbHMuY29tIiwiaWF0IjoxNzAyNDc3MzY0LCJleHAiOiIyMDIzLTEyLTE0VDAyOjIyOjQ0LjAwMFoifQ.5db7a4f757358edfb23782f7b75bf9e7474a26c2b8704c36bb8cf806e9dc99d2&user_id=6571b86a88061612aa2fc8b7

    https://nets.epventures.co/6579c53c0c64027a3b9f2f34/waterfall?fin_session_id=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2NTcxYjg2YTg4MDYxNjEyYWEyZmM4YjciLCJlbWFpbCI6InNoaXZhbUBzaGl2YW1wYXRlbHMuY29tIiwiaWF0IjoxNzAyNDc3MzY0LCJleHAiOiIyMDIzLTEyLTE0VDAyOjIyOjQ0LjAwMFoifQ.5db7a4f757358edfb23782f7b75bf9e7474a26c2b8704c36bb8cf806e9dc99d2&user_id=6571b86a88061612aa2fc8b7
    
    """
    
    case_id='6579c53c0c64027a3b9f2f34'
    
    butt=assemble_butterfly_source_url(case_id)
    fall=assemble_waterfall_source_url(case_id)
    
    print ("BUTTON: "+str(butt))
    print ("FALL: "+str(fall))
    
    return



def prepare_ws_force_timeline_url_msg(case_id,url,user_id='6232393',fin_session_id='123',layout_type='view_standard_1'):
    #[ ] migrate to ws_servcie
    #[ ] check for 200?
    ## Per expected broadcast_listener
    msg = {
    "data": {
        "case_id": case_id,
        "session_id": fin_session_id,
        "update_type": 'force_timeline_url',  #<-- for handler
        "force_datahash_change": True,    
        "action": "init_data",                #<-- for FE
        "layout_type": layout_type,           #<-- for FE
        "url": url
        }
    }

    return msg


def dev_force_timeline_url():
    ## Pass message to broadcast_listener
    #- listener will get init_data but will enforce a new url for timeline
    #**also possibly change datahash to ensure its' refreshed?
    
    ## See fast_ws_v1.py
    
    Hub=Button_Hub()

    case_id='6579c53c0c64027a3b9f2f34'
    user_id='manuri3221'
    fin_session_id='A34838448fec8'

    if False:
        url=assemble_waterfall_source_url(case_id,user_id=user_id,fin_session_id=fin_session_id)
    
        url=assemble_butterfly_source_url(case_id,user_id=user_id,fin_session_id=fin_session_id)
        
        msg=prepare_ws_force_timeline_url_msg(case_id,url,user_id=user_id,fin_session_id=fin_session_id)
    
        Hub._broadcast_ws_msg(case_id,msg,branch='')
        print ("Did butterfly")
        
        
    if 'butterfly_always':
        case_id='65858e0c198ceb69d5058fc3' #local jon

        url=assemble_butterfly_source_url(case_id,user_id=user_id,fin_session_id=fin_session_id)
        msg=prepare_ws_force_timeline_url_msg(case_id,url,user_id=user_id,fin_session_id=fin_session_id,layout_type='view_standard_2')
        print ("MSG: "+str(msg))
        Hub._broadcast_ws_msg(case_id,msg,branch='')
        

    return



def dev_sim_button_handler_click():
    """
    WORKS:
    http://127.0.0.1:8008/api/v1/case/6579c53c0c64027a3b9f2f34/button_handler?button_id=3&case_id=6579c53c0c64027a3b9f2f34&user_id=manuri3221&fin_session_id=A34838448fec8
    http://127.0.0.1:8008/api/v1/case/6579c53c0c64027a3b9f2f34/button_handler?button_id=2&case_id=6579c53c0c64027a3b9f2f34&user_id=manuri3221&fin_session_id=A34838448fec8
    """
    
    case_id='6579c53c0c64027a3b9f2f34'
    user_id='manuri3221'
    fin_session_id='A34838448fec8'
    
    ## Create url params?case_id=...
    url="?case_id="+case_id+"&user_id="+user_id+"&fin_session_id="+fin_session_id
    url+="&button_id=2"

    url='/button_handler'+url
    
    url='http://127.0.0.1:8008/api/v1/case/'+case_id+url
    
    print ("TRY: "+str(url))

    return


def dev_sim_button_query():
    print ("Simulating button query...")
    button_id=4 #Known to have query at this point even though dynamic
    Hub=Button_Hub()
    Hub.execute_button_query('case_test_loc',button_id=button_id)
    return

if __name__ == "__main__":
    #dev1()
    #dev2()
#    AUTOMATE_button_cap()
#    LIST_known_buttons()
#    dev_chart_buttons()

#    dev_sim_button_handler_click()
#    dev_sim_button_query()
    dev_force_timeline_url()




"""
"""



