import os, sys
import time
import json
import requests
import datetime

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")

sys.path.insert(0,LOCAL_PATH+"../../")
from w_mindstate.abstract_FE import WORKFLOW_load_init_data


#0v4# JC Feb 21, 2024  Quick patch hardcode type for butterfly & waterfall
#0v3# JC Jan 16, 2024  Add basic test + transaction/record/token counter
#0v2# JC Dec  3, 2023  Encapsulate FE data model for front-end to control format
#0v1# JC Nov 29, 2023


"""
    FORMAL DEV FOR wsprotocol
    > test_ws_service.py for basic request format check

"""

class FEDashboard:
    def __init__(self):
        self.msg = {'action': 'init_data', 'meta': {}}
        self.dash = {'dsettings': {}, 'components': []}
        self.init_meta()

    def init_meta(self):
        self.msg['meta']['dashboard_types'] = [
            'ChatComponent', 'TimelineComponent', 'SquareComponent', 'IFRAMEComponent', 
            'WaterfallComponent', 'ButterflyComponent', 'BarchartComponent']
        self.msg['meta']['layout_types'] = ['view_standard_1', 'view_standard_2']

    def set_layout(self, layout_type='view_standard_1', custom_layout=None):
        self.dash['dsettings']['layout_type'] = layout_type
        self.dash['dsettings']['custom_layout'] = custom_layout or {}

    def set_datahash(self,datahash):
        return self.dash['dsettings'].update({'datahash':datahash})

    def set_credits_used(self,credits_used):
        return self.dash['dsettings'].update({'credits_used':credits_used})

    def set_case_id(self,case_id):
        return self.dash['dsettings'].update({'case_id':case_id})

    def add_component(self, component_type, id, position, component_name, datahash, is_main, src=None):
        component = {
            'type': component_type,
            'id': id,
            'position': position,
            'component_name': component_name,
            'src': src,
            'datahash': datahash,
            'is_main': is_main
        }
        self.dash['components'].append(component)

    def get_message(self):
        self.msg['data'] = self.dash
        return self.msg


def request_init_data(case_id='',session_id='', user_id='',target='default', force_datahash_change=False,layout_type='view_standard_1'):
    # target:  default is normal, dev is jc view
    # ** In fact, this single request can be loaded always even if redundant
    credits_used=0

    ASSUME_butterfly_always_layout_2=True  # Hardcode layout for now

    if not case_id:
        raise Exception("ERROR: no case id!")

    #[ ] user_id + 

    ## Get state and data view from abstract_FE
    the_data,meta=WORKFLOW_load_init_data(case_id,session_id='',user_id='',target=target)
    
    credits_used=meta.get('credits_used',0)
    
    if False:
        #**beware text encodings
        print ("RAW D: "+str(json.dumps(the_data)))
        print ("RAW D: "+str(json.dumps(meta)))
    
    #** view_standard_2 is full_right on timeline (though not tested)
    dashboard = FEDashboard()
    dashboard.set_layout(layout_type=layout_type)
    dashboard.set_case_id(case_id)
    
    is_chat_main=False
    dashboard.add_component('chat', 'chat_1', 'bottom_left', 'ChatComponent', '123',is_chat_main,'https://chatbot.epventures.co?case_id='+case_id+'&session_id=wfrix')
    
    
    datahash=''
    for component_label in the_data:

        component_data=the_data[component_label]
        component_type=component_data['component_type']
        component_id=component_data['component_id']
        component_position=component_data['component_position']
        component_name=component_data['component_name']
        component_src=component_data['component_src']
        component_main=component_data.get('is_main_component',False)
        
        #0v4# Feb 21, 2024 hardcode quick patch for demo asap request [ ] ideally this set upstream
        #[ ] no effect since not button force related
        if component_src and '/butterfly' in component_src: component_type='butterfly'
        if component_src and '/waterfall' in component_src: component_type='waterfall'

        if force_datahash_change:
            component_hash=datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")
        else:
            component_hash=component_data['component_hash']

        dashboard.add_component(component_type, component_id, component_position, component_name, component_hash, component_main, component_src)
        
        ## Screen datashash is any of the compoent hashes
        if component_hash:
            datahash=component_hash

    dashboard.set_datahash(datahash)
    dashboard.set_credits_used(credits_used)


#    dashboard.add_component('timeline', 'timeline_1', 'top_full', 'WaterfallComponent','123')
#    dashboard.add_component('square', 'square_1', 'bottom_right', 'SquareComponent','123')

    init_data=dashboard.get_message()
    return init_data


def HARDCODED_request_init_data():
    #** view_standard_2 is full_right on timeline (though not tested)
    raise Exception("HARDCODED_request_init_data() is deprecated")
    dashboard = FEDashboard()
    dashboard.set_layout()
    dashboard.add_component('timeline', 'timeline_1', 'top_full', 'WaterfallComponent','123')
    dashboard.add_component('square', 'square_1', 'bottom_right', 'SquareComponent','123')
    dashboard.add_component('chat', 'chat_1', 'bottom_left', 'ChatComponent', '123','https://chatbot.epventures.co?case_id=chase_S3_A&session_id=wfrix')
    return dashboard.get_message()


def request_data_refresh(datahash,case_id=''):
    msg={
        "action": "request_data_refresh",
        "data": {
            "datahash": datahash,
        }
    }
    if case_id:
        msg['data']['case_id']=case_id
    return msg

def request_component_refresh(component_id):
    msg={
        "action": "request_component_refresh",
        "data": {
            "component_id": component_id,
            "key": datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")
        }
    }
    return msg


def request_set_iframe_url(component_id,iframe_source=''):
    #   "iframe_source": 'https://core.epventures.com/api/v1/get_chat?case_id=1'
    msg={
        "action": "request_iframe_url",
        "data": {
            "component_id": "timeline_1",
            "iframe_source": iframe_source
        }
    }
    return msg

def request_set_main(component_data):
    #   "iframe_source": 'https://core.epventures.com/api/v1/get_chat?case_id=1'
    msg={
        "action": "request_iframe_url",
        "data": { **component_data} 
    }
    return msg

def client_request_init_data():
    msg={}
    msg['action']='request_init_data'
    return msg

def client_ping():
    msg={}
    msg['action']='request_ping'
    return msg

def client_pong():
    ## Pong back to clients' ping request
    msg={}
    msg['action']='response_pong'
    return msg


def dev_dump_ws_protocol():
    
    ## Layout section

    ## Component section

    ## Actions section
    
    ## Connection section

    return



def step_1_initial_ws_connection():
    
    ## ws connection
    user_id=''
    case_id=''
    fin_session_id=''

    endpoint='https://core.epventures.co/api/v1/ws'      # post or 
    params='?&case_id=...&fin_session_id=...&user_id=...'
    
    ## ws connected response:
    msg={}
    msg['case_id']=case_id
    msg['fin_session_id']=fin_session_id
    msg['status']='ws_connected'
    
    connect_request='get '+endpoint+params

    return connect_request



def echo_all_ws_samples_v1():
    lnn=30

    print ("-"*lnn)
    print ("CLIENT CONNECTION VIA:")
    print (str(json.dumps(step_1_initial_ws_connection(),indent=4)))

    print ("")
    print ("-"*lnn)
    print ("INIT DATA SENT ON REQUEST")
    print ("*possible to add get endpoint too if also convenient")
    print (str(json.dumps(request_init_data(),indent=4)))

    print ("")
    print ("-"*lnn)
    print ("SERVER REQUESTS REFRESH OF COMPONENT")
    print (str(json.dumps(request_component_refresh('timeline_1'),indent=4)))

    print ("")
    print ("-"*lnn)
    print ("SERVER REQUESTS SET IFRAME URL")
    print (str(json.dumps(request_set_iframe_url('timeline_1','https://core.epventures.com/api/v1/get_chat?case_id=1'),indent=4)))

    print ("")
    print ("-"*lnn)
    print ("CLIENT OPTIONAL REQUEST INIT DATA")
    print (str(json.dumps(client_request_init_data(),indent=4)))

    print ("")
    print ("-"*lnn)
    print ("CLIENT OPTIONAL PING")
    print (str(json.dumps(client_ping(),indent=4)))


    return
    
def request_data_refresh(datahash):
    msg={
        "action": "request_refresh",
        "data": {
            "key": datahash
        }
    }
    return msg

def dev_ws_protocol():
    case_id='case_atm_location'
    b=['init_data']
    b=['data_refresh']
    b=['iframe_set_main']

    if 'init_data' in b:
        ##### DYNAMIC init_data !!
        
        ## Get state from multimodal + component map
        init_data=request_init_data(case_id=case_id, session_id='', user_id='',target='dev')
        print ("GOT INIT MSG: "+str(init_data))
        
        ## DYNAMIC MESSAGE DATA
        #> add datahash 
        
    if 'data_refresh' in b:
        init_data=request_init_data(case_id=case_id, session_id='', user_id='',target='dev')
        data_hash=init_data['data']['dsettings']['datahash']
        msg=request_data_refresh(data_hash,case_id=case_id)
        print ("GOT refresh MSG: "+str(msg))
        
    if 'iframe_set_main' in b:
        init_data=request_init_data(case_id=case_id, session_id='', user_id='',target='dev')
        for component in init_data['data']['components']:
            if component.get('is_main',False):
                msg=request_set_main(component)
                print ("GOT MAIN: "+str(msg))

    return


"""
    NOTES ON WS PROTOCOL
    i) ws_connection, init_data
    ii) [request_data_refresh]: expect key sent to (timeline,square) component as param for refresh as change
    iii) [iframe url]: expect timeline url + key sent to (timeline) component 


"""



if __name__ == "__main__":
    #dev1()
#    echo_all_ws_samples_v1()
    dev_ws_protocol()


"""
rn msg

def request_component_refresh(component_id):
    msg={
        "action": "request_component_refresh",
        "data": {
            "component_id": component_id,
            "key": datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")
        }
    }
    return msg


def request_set_iframe_url(component_id,iframe_source=''):
    #   "iframe_source": 'https://core.epventures.com/api/v1/get_chat?case_id=1'
    msg={
        "action": "request_iframe_url",
        "data": {
            "component_id": "timeline_1",
            "iframe_source": iframe_source
        }
    }
    return msg

"""

"""
def ORG_dev_request_init_data():
    #[ ] delete since now go through dashboard class to keep clean
    ## NOTES:
    #- view_standard_1:  regular
    #- view_standard_2:  tall

    msg={}

    msg['action']='init_data'

    msg['meta']={}
    msg['meta']['dashboard_types']=['ChatComponent','TimelineComponent','SquareComponent','IFRAMEComponent','WaterfallComponent','ButterflyComponent','BarchartComponent']
    msg['meta']['layout_types']=['view_standard_1','view_standard_2'] #view_standard_1 
    
    dash={}
    dash['dsettings']={}
    
    ## Dashboard layout:
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
    
    ## Square def
    component_square={}
    component_square['type']='square'
    component_square['id']='square_1'
    component_square['position']='bottom_right'
    component_square['component_name']='SquareComponent'
    component_square['src']=None
    dash['components'].append(component_square)
    
    ## Chat def
    component_chat={}
    component_chat['type']='chat'
    component_chat['id']='chat_1'
    component_chat['position']='bottom_left'
    #component_chat['component_name']='IFRAMEComponent'
    component_chat['component_name']='ChatComponent'
    component_chat['src']='http://core.epventures.com/api/v1/get_chat?case_id=1'
    component_chat['src']='https://chatbot.epventures.co?case_id=chase_S3_A&session_id=wfrix'
    ## Load chat endpoint from config file

    dash['components'].append(component_chat)
    
    msg['data']=dash

    return msg


"""
