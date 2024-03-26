import os
import sys
import codecs
import json
import re
import time
import threading

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")

#from w_storage.ystorage.ystorage_handler import Storage_Helper

## Include REAL connections
from w_utils import am_i_on_server

## ws
from starlette.testclient import TestClient
#D# from z_apiengine.fast_ws_v1 import app  # Import your FastAPI app

from mindstate import get_dashboard_data
from kb_ask.kb_answer_multimodal import control_load_decision
from config_views import config_get_map_view_url

from get_logger import setup_logging
logging=setup_logging()


#0v3# JC  Jan 24, 2024  Read dashboard view types from 'config' file
#0v2# JC  Jan 24, 2024  JC:  moved but consider comverging features
#0v1# JC  Nov 30, 2023  Init


ON_SERVER=am_i_on_server()

"""
    ABSTRACT FRONT-END VIEW
    - as more logic offloaded to backend (to keep FE 'simple')
    - keep stateless
    - part of test suite as well
    
    - Actual view endpoints (ie/ map & timeline)
"""

if ON_SERVER:
    BASE_ENDPOINT='https://core.epventures.co'
else:
    BASE_ENDPOINT='http://127.0.0.1:8008'
BASE_ENDPOINT+='/'+'api/v1'+"/case/"
    


def local_get_ws_init_data(case_id='case_test_A'):
    LOCAL_ENDPOINT='/ws'
    logging.info("[ws] connection to fetch init data")
    response={}
    client = TestClient(app)
    with client.websocket_connect(LOCAL_ENDPOINT+'?case_id='+case_id+'&fin_session_id=test_session') as ws:
        try:
            # Attempt to send and receive a message
            ws.send_json({'action': 'request_init_data'})
            response = ws.receive_json()
        except:
            response = {}
    return response


class Abstract_FE():
    def __init__(self):
        self.name='Abstract_FE'
        self.capabilities=[]
        
    def preload_capabilities(self):
        
        self.capabilities=[]
        self.capabilities+=['buttons']
        self.capabilities+=['faqs']
        self.capabilities+=['dashboard.timeline']
        self.capabilities+=['dashboard.chat']
        self.capabilities+=['dashboard.square']

        self.capabilities+=['html_page']            #[ ] load page
        self.capabilities+=['ws.component_admin']
        self.capabilities+=['ws.component']

        return
    
    def load_dashboard(self):
        return
    
    def load_object(self,name):
        if 'buttons'==name:
            #* [ ] see your original button definition
            pass
        if 'faqs'==name:
            #* FAQ content hosted by Shivram at xxx
            pass
        return
    
    def load_ws(self,command):
        rr={}
        if command=='init_data':
            rr=local_get_ws_init_data() #case_id=
        return rr


def dev_abstract_FE():

    FE=Abstract_FE()
    FE.preload_capabilities()
    FE.load_dashboard()
    
    entrypoints=[]
    entrypoints+=['full_dashboard_load']
    entrypoints+=['default_pushes_button']
    entrypoints+=['user_pushes_button']
    entrypoints+=['user_visits_faqs']
    entrypoints+=['user_asks_in_chat']   #<-- actual exciting part!
    
    if False:
        entrypoints+=['user_add_edits_button']
        entrypoints+=['system_add_edits_button']
        entrypoints+=['system_add_edits_faq']
        entrypoints+=['user_resizes_components']
        
        
    if 'full_dashboard_load' in entrypoints:
        print ("full_dashboard_load")

        print ("--> [ ] load buttons")
        FE.load_object('buttons')

        print ("--> [ ] load faqs")
        FE.load_object('faqs')
        print ("--> [ ] load ws.init_data") # do data calls

        init_data=FE.load_ws('init_data')


    return

def run_simulation():
    logging.info("[FE simulation]")

    b=['fetch_init_data']
    b=['broadcast_to_FE']

    if 'fetch_init_data' in b:
        logging.info("[FE simulation]:: FETCH INIT DATA")
        FE=Abstract_FE()
        FE.preload_capabilities()
        init_data=FE.load_ws('init_data')
        logging.info("[raw init_data]: "+str(init_data))
        
    if 'broadcast_to_FE' in b:
        print ("RECALL FULL BROADCAST:  for case.. does broadcast_to...uses mindstate...can call now")
        print ("[ ] need map to ws action commands")
        print ("[ ] set hash on content to send for each target component")
        
        print ("[existing broadcast_listener gets case_id, session_id, message ] ")
        print ("[^comes when mindstate is updated")
                
        print ("MINDSTATE updated with multimodal, do broadcast")
        print ("MAP MULTIMODAL TO COMPONENT DEF VIA ws message")
            


    return

def local_check_flow():
    case_id='case_atm_location'
    
    #? force broadcast call via question entry
    #? dump active multimodal
    #? map multimodal to ws action including full urls
    
#    from w_mindstate.mindstate import Mindstate
#> get last answer meta!!
#    sesh,sesh_id,is_created=self.Mind.start_or_load_session(case_id=case_id)
    
#    force_show_decision=''
#    Dashboard,multimodal=get_dashboard_data(case_id,force_show_decision=force_show_decision)

    
    case_id='case_atm_location'
    Dashboard,multimodal=get_dashboard_data(case_id)
    
    print ("M: "+str(multimodal))

    return

###  RECALL:
# Dashboard=The_Dashboard()
#    Dashboard.set_last_answer_meta(last_answer_meta)
#    Dashboard.prepare_multimodal_insights(case_id,session_id='',force_show_decision=force_show_decision)
#    multimodal=Dashboard.dump_multimodal_insights()
#


def dev1():

    ###
    # from services.ws_service import request_init_data, request_component_refresh, request_set_iframe_url, client_ping, client_pong
    ws_action_types=[] # fast_ws_v1.py
    #init data
    # component_refresh( component_id ) (hash data or time)
    # set_iframe_url( component_id )
    
    ###
    #
    b=['update_square_data']
    
    case_id='case_atm_location'
    Dashboard,multimodal=get_dashboard_data(case_id)
    print ("Data hash( via jsonl 2000 chars): "+str(multimodal['data_hash']))

    #> multimodal. barchart, timeline, xxx
    
    #^the_dashboard.py

# {'features': {'has_lat_lng': False, 'is_timelineable': True, 'is_barchartable': True}, 'column_names_map': {'latitude': None, 'longitude': None, 'timeline_date_col': 'transaction_date', 'timeline_amount_col': 'transaction_amount', 'barchart_category_col': 'is_wire_transfer', 'barchart_value_col': 'transaction_amount'}, 'show_decision': 'timeline_dynamic'}

    if 'update_square_data' in b:
        print ("[LOGIC 1]  Always show square. Hash data to show if changed")
        print ("[ ] load square data to plot and do hash")
        print ("[ ] send hash to FE which will update if it has changed")
        print ("Multimodal: "+str(multimodal['multimodal'].keys()))
        print ("Data hash: "+str(multimodal['data_hash']))


    return

def alg_case2datahash(case_id):
    from w_mindstate.mindstate import get_dashboard_data
    Dashboard,multimodal=get_dashboard_data(case_id)
    data_hash=multimodal.get('data_hash','') #Old cache may not have it
    return data_hash

def alg_case2_ws_update_msg(case_id):
    from z_apiengine.services.ws_service import request_data_refresh
    datahash=alg_case2datahash(case_id)
    msg=request_data_refresh(datahash)
    return msg


def call_dev():
    case_id='case_atm_location'
    datahash=alg_case2datahash(case_id)
    print ("Data hash for case_id: "+str(case_id)+" is: "+str(datahash))
    
    print ("ws update msg: "+str(alg_case2_ws_update_msg(case_id)))
    return

"""
    msg={}
    msg['meta']={}
    msg['meta']['dashboard_types']=['ChatComponent','TimelineComponent','SquareComponent','IFRAMEComponent','WaterfallComponent','ButterflyComponent','BarchartComponent']
    msg['meta']['layout_types']=['view_standard_1','view_standard_2'] #view_standard_1 
    
    dash={}
    ## Dashboard layout:
    dash['dsettings']={}
    dash['dsettings']['layout_type']='view_standard_1'  #view_standard_3'  #main timeline, bottom two
    dash['dsettings']['custom_layout']={}               # maximize window state, etc.
    
    ## Components:
    dash['components']=[]
    
    ## Timeline def
    component_timeline={}
    component_timeline['type']='timeline'
    component_timeline['id']='timeline_1'
    component_timeline['position']='top_full'
    component_timeline['component_name']='WaterfallComponent'
    component_timeline['src']=None
    dash['components'].append(component_timeline)

""" 


def map_multi_to_full_dashboard():
    print ("FORMAL VISIBILITY TO USER DASHBOARD STATE")

    #> Recall you have Dashboard class but also multimodal + new FE now

    ## ws v1 (react) requires full specification on data updates
    
    #[1]  dashboard level  (layout choice etc)
    
    #[2]  component level  (type, source, data, position)
    
    #[3]  data level       (hash, data, refresh, etc)
    
    #[4]  styling          (x-axis/y-axis, color, titles)
    #     - done upstream in multimodal
    

    ### LOGIC AT MAIN 'TIMELINE' COMPONENT VIEW TYPE
    #- RECALL SHARED data_init spec in ws_service.py
    
    ## DECISION FIELDS
    fields=['ws_msg_type','component_name','layout_type','src','datahash']

    show_decision=''

    details={}
    #msg['meta']['dashboard_types']=['ChatComponent','TimelineComponent','SquareComponent','IFRAMEComponent','WaterfallComponent','ButterflyComponent','BarchartComponent']
    #details['component_name']='IFRAMEComponent' #|
    #if 'map show decision to component type details' in []:
    #    pass
    
    ### CHECK GIVENs + STATE
    show_decision=''
    

    ## NOTES ON MAJOR FLOWS:
    #[A]  initialize data
    #[B]  specifically show component  (ie/ show_decision dictates settings)
    #[C]  update data  (ie/ broadcast listener requests latest hash state)
    

    ## [B] DETAILS

    #- show_decision in: timeline_nodes, timeline_butterfly, timeline_waterfall, timeline_barchart, timeline_iframe 

    #[ ] add show decision logic update upstream or clear mapping here because logic of which is tbd.
    

    if 'datahash' in fields:
        pass

    if 'src' in fields:
        pass

    if 'layout_type' in fields:
        pass

    if 'component_name' in fields:
        pass

    if 'ws_msg_type' in fields:
        pass

    return



def local_validate_show_decision(show_decision):
    ## Control variable raise otherwise
    
    #> kb_answer_multimodal.py -> prepare_multimodal_insight_dict -> show_decision
    show_decision_names=[]
    if not show_decision in show_decision_names:
        raise Exception("show_decision: "+str(show_decision)+" not in: "+str(show_decision_names))

    return

def dev_which_main_to_show():
    ## NOTES:
    #- this is top decision passing to organize dashboard components  (data not forwarded here)
    #- recall, there is generally a component view choice THEN...a data load choice.
    #- ideally decision logic is upstream
    
    print ("TARGET:  WHAT TO SHOW IN MAIN COMPONENT  (which can be array of various components)")
    
    show={}
    show['react']={}  # Full application
    show['dev']={}    # Jon controllable
    

    print ("** FULL NODE HAS DIFFERENT FEATURES THE main.tsx (local) ")
    target_capabilities=['NOT_butterfly','NOT_waterfall']

    
    case_id='case_atm_location'
    Dashboard,multimodal=get_dashboard_data(case_id)
        
    ## CHECK GIVEN DATA
    print ("AT multimodal: "+str(list(multimodal['multimodal'].keys())))
    print ("AT idict: "+str(multimodal['multimodal']['idict']))

    show_decision=multimodal['multimodal']['idict']['show_decision']
    datahash=multimodal['data_hash']
    
    ## Check show_decision
    control_load_decision(show_decision) #/ timeline, timeline_dynamic,map,barchart
    
    show['show_decision']=show_decision
    

    MAIN_OPTIONS=['timeline_nodes', 'timeline_butterfly', 'timeline_waterfall', 'timeline_barchart', 'timeline_iframe','timeline_map']
    
    ## Steering logic
    #was_it_multimodal_logic_show_decision=None
    #was_it_force_show_decision_from_button_etc=None
    
    #######################################
    ## Description of main options
    
    ## [ ] x.  timeline_dynamic
    print ("timeline_dynamic is jon nodes for FULL transaction chart (AI written query)")

    ## [ ] x.  timeline_barchart
    print ("Barchart is dynamic content (AI written data)")

    ## [ ] x.  timeline_map
    print ("Map is dynamic content (AI written data)")

    ## [ ] x.  timeline_waterfall
    print ("timeline_waterfall is balance over time. Custom query to generate") 

    ## [ ] x.  timeline_butterfly
    print ("timeline_butterfly is entity debit/credit custom query to generate")

    ## [ ] x.  timeline_iframe
    #[ ] data vs view.
    print ("timeline_iframe is undefined but flexible content")
    
    #######################################
    ## CHOICE LOGIC + MAP FOR MAIN TO SHOW
    
    component={}
    if True or 'use show_decision from multimodal':

        print ("[case]: "+str(case_id)+"decision: "+str(show_decision))
        component=map_decision2component(show_decision,target='default')
        component_dev=map_decision2component(show_decision,target='dev')

    #elif:: allow force show like butterfly when requested directly (see routing)
    
    ########################################
    ## USE FULL DICT to guide output then trim at VERY end


    return

def get_component_iframe_src(show_decision,target):
    ## Load from config
    return

def map_env2square_component(case_id,target='default',datahash=''):
    global BASE_ENDPOINT
    ## Must match ws_service.py requirement (pulls keys)

    component={}
    component['component_position']='bottom_right'
    component['component_type']='square'
    if target=='dev':
        component['component_name']='IFRAMEComponent'
        component['component_src']=BASE_ENDPOINT+case_id+'/square'
        component['component_position']='bottom_right'
    else:
        component['component_name']='SquareComponent'
        component['component_src']=None
        component['component_position']='bottom_right'
    component['component_id']=component['component_name']+'_1'
    component['component_hash']=datahash
    return component


def map_decision2component(case_id,show_decision,session_id='',user_id='',target='default',datahash=''):
    global BASE_ENDPOINT
    ## Must match ws_service.py requirement (pulls keys) [it raise err otherwise]

    ## 'default' expects the normal target react space (**external views required)
    ## 'dev'     expects the main.tsx for dev control
    
    component={}
    component['is_main_component']=True  # for ie/ set iframe (of main)
    component['show_decision']=show_decision
    component['component_position']='top_full' #Unless inflow/outflow butterfly then full_right
        
    if show_decision=='timeline':
        component['component_type']='timeline'
        if target=='dev':
            component['component_name']='IFRAMEComponent'
            component['component_src']=BASE_ENDPOINT+case_id+'/timeline'  
        else:
            component['component_name']='IFRAMEComponent'
            component['component_src']=BASE_ENDPOINT+case_id+'/timeline'  

    elif show_decision=='timeline_dynamic':
        component['component_type']='timeline'
        if target=='dev':
            component['component_name']='IFRAMEComponent'
            component['component_src']=BASE_ENDPOINT+case_id+'/timeline_dynamic'
        else:
            component['component_name']='IFRAMEComponent'
            component['component_src']=BASE_ENDPOINT+case_id+'/timeline_dynamic'

    elif show_decision=='barchart':
        component['component_type']='barchart'
        if target=='dev':
            component['component_name']='IFRAMEComponent'
            component['component_src']=BASE_ENDPOINT+case_id+'/barchart'
        else:
            ## External barchart so iframe
            component['component_name']='IFRAMEComponent'
            component['component_src']=assemble_barchart_source_url(case_id,include_session=False)

    elif show_decision=='map':
        component['component_type']='map'
        if target=='dev': #get config will determine if local maps
            component['component_name']='IFRAMEComponent'
            component['component_src']=config_get_map_view_url(case_id,session_id=session_id,user_id=user_id)
        else:
            component['component_name']='IFRAMEComponent'
            component['component_src']=config_get_map_view_url(case_id,session_id=session_id,user_id=user_id)

    else:
        raise Exception("show_decision: "+str(show_decision)+" not mapped to component")
        
    print ("[ ] raw component: "+str(component))

    
    component['component_id']=component['component_type']+'_1'
    
    print ("[ ] add react_waterfall, react_butterfly")

    component['component_hash']=datahash

    ## HARDCODE Feb 21
    if component['component_src'] and '/butterfly' in component['component_src']: component['component_type']='butterfly'
    if component['component_src'] and '/waterfall' in component['component_src']: component['component_type']='waterfall'
    
    return component
    

def assemble_barchart_source_url(case_id,include_session=True,fin_session_id="A34838448fec8",user_id="manurian2344"):
    """
    ** user_id and fin_session_id need to be set to SOMETHING
    https://nets.epventures.co/6579c53c0c64027a3b9f2f34/barchart?fin_session_id=A34838448fec8&user_id=manurian2344
    
    """
    base_endpoint="https://nets.epventures.co/"
    extra=''

    if include_session:
        #Assumes set properly!
        extra="?fin_session_id="+fin_session_id+"&user_id="+user_id

    url=base_endpoint+case_id+"/barchart"
    url+=extra
    return url



def dev_review_all_iframe_src():
    global BASE_ENDPOINT

    srcs={}
    
    case_id='case_atm_location'

    ON_SERVER=am_i_on_server()

    print ("THIS WAS in main.tsx but want backend controllable")
    print (">> load dashboard config json")
    
    def load_config():
        config_file=LOCAL_PATH+'../'+'w_config_dashboard.json'
        with open(config_file, 'r') as fp:
            CONFIG = json.load(fp)
        return CONFIG
    CONFIG=load_config()
    
    if ON_SERVER:
        BASE_ENDPOINT='https://core.epventures.co'
    else:
        BASE_ENDPOINT='http://127.0.0.1:8008'
        
    ## Add API
    BASE_ENDPOINT+='/'+'api/v1'+"/case/"+case_id+"/"
    
    ## See routing for base view (may need to use v0 ?)
    
    #** recall, is in config but hardcode here ok cause no ports anymore (8008 core.)

    ## node timeline iframe
    #*recall: timeline loads ALL transactions vs dynamic is last question result
    srcs['timeline_dynamic']=BASE_ENDPOINT+'timeline_dynamic'  #** should give same as static
    srcs['timeline']=BASE_ENDPOINT+'timeline'  #** should give same as static

    ## node map
    srcs['map']=BASE_ENDPOINT+'map/view' 

    ## node barchart BUT ORG because via core.
    srcs['barchart']=BASE_ENDPOINT+'barchart'
    
    print ("SOURCES: "+str(srcs))
    
    return srcs



def dev_descriptive_components():

    """
    SERVER SIDE OPTIONS  (react d3.js components)
    - barchart
    - waterfall
    - butterfly

    IFRAME SOURCED OPTIONS  (original jon)

    """

    return



def local_load_state(case_id):
    show={}
    Dashboard,multimodal=get_dashboard_data(case_id)
    ## CHECK GIVEN DATA

    print ("AT multimodal: "+str(list(multimodal['multimodal'].keys())))
    print ("AT idict: "+str(multimodal['multimodal']['idict']))

    if not 'show_decision' in multimodal['multimodal']['idict']:
        raise Exception("show_decision not in multimodal['multimodal']['idict']")
        logging.warning("No show decision -- use 'timeline'")
        show_decision='timeline'
        show_decision=multimodal['multimodal']['idict']['show_decision']=show_decision
    else:
        show_decision=multimodal['multimodal']['idict']['show_decision']

    datahash=multimodal['data_hash']
    ## Check show_decision
    control_load_decision(show_decision) #/ timeline, timeline_dynamic,map,barchart

    show['show_decision']=show_decision
    show['datahash']=datahash
    
    ## MAP OTHER The_Dashboard fields
    show['credits_used']=multimodal.get('credits_used',0)
    return show
    
def ENTRY_get_init_data():
    """
        get ws init_data for rendering in jon dev env
        - uses org html square (so type of square is IFRAMEComponent)
        - uses 127.0.0.1 and local charts (not react_butterfly, not react_waterfall, not react_barchart)
        - show decision still decides main timeline
    """

    return


def WORKFLOW_load_init_data(case_id='',session_id='',user_id='',target='default'):
    #: target: default|dev
    the_data={}
    meta={}

    show=local_load_state(case_id)
    datahash=show['datahash']
    meta['credits_used']=show['credits_used']

    the_data['main_component']=map_decision2component(case_id,show['show_decision'],target=target,datahash=datahash,session_id=session_id,user_id=user_id)
    the_data['square_component']=map_env2square_component(case_id,target=target,datahash=datahash)
    
    ## Assemble init_data (per spec)
    #> current endpoint (pass through validate_init_data routine for formatting)
    #from services.ws_service import request_init_data, request_component_refresh, request_set_iframe_url, 
    
    ### Keys should map to ws_service requirement (pushed through class)

    return the_data, meta



if __name__=='__main__':

    branches=['dev_abstract_FE']
    branches=['run_simulation']
    branches=['local_check_flow']
    branches=['dev1']
    branches=['call_dev']

    branches=['map_multi_to_full_dashboard']
    branches=['dev_which_main_to_show']

    branches=['dev_review_all_iframe_src']


    for b in branches:
        globals()[b]()
        


print ("**square original html view")



"""

"""










