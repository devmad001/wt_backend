import os
import sys
import codecs
import uuid
import requests
import json
import re
import time
import pickle
import base64

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")

from w_storage.ystorage.ystorage_handler import Storage_Helper
from w_utils import am_i_on_server

import configparser as ConfigParser

from the_dashboard import The_Dashboard

from get_logger import setup_logging
logging=setup_logging()



#0v2# JC  Nov  3, 2023  new broadcast_to for react
#0v1# JC  Sep 27, 2023  Setup


"""
    MINDSTATE
    - tracks session, discussion, state across devices or widgets
    - case_id to session_id lookup for continued?
    - basic broadcast to listening processes (front-end)

"""


ON_LIVE_SERVER=False
if am_i_on_server():
    ON_LIVE_SERVER=True


## CONFIG FOR BROADCASTS
config_file=LOCAL_PATH+'../'+'w_config_dashboard.json'
def load_config():
    global config_file
    with open(config_file, 'r') as fp:
        CONFIG = json.load(fp)
    return CONFIG
CONFIG=load_config()


### ROOT CONFIG
RootConfig = ConfigParser.ConfigParser()
RootConfig.read(LOCAL_PATH+"../w_settings.ini")

FRAUDWS_PORT=RootConfig.get('services','fraudws_port')
FRAUDWS_subdomain=RootConfig.get('services','fraudws_subdomain')
FRAUDWS_domain=RootConfig.get('services','fraudws_domain')

if ON_LIVE_SERVER:
    WS_ENDPOINT='https://'+FRAUDWS_subdomain+"."+FRAUDWS_domain
else:
    WS_ENDPOINT='http://127.0.0.1:'+str(FRAUDWS_PORT)



def validate_message_format(message=''):
    # If URL is not set it will do a direct reload of existing
    is_valid=True
    ACCEPTED_MSG_KEYS=['RELOAD_TIMELINE_IFRAME_URL','RELOAD_SQUARE_IFRAME_URL']
    ACCEPTED_MSG_KEYS+=['session_id','case_id','message']
    
    for mkey in message:
        if not mkey in ACCEPTED_MSG_KEYS:
            is_valid=False
            raise Exception("[validate_message_format]  Invalid message key: "+str(mkey))
            break
    return is_valid


def local_get_last_answer_meta(case_id):
    Mind=Mindstate()
    sesh,session_id,is_created=Mind.start_or_load_session(case_id=case_id)
    last_answer_meta=Mind.get_field(session_id,'last_answer_meta')
    return last_answer_meta

def get_dashboard_data(case_id,force_show_decision=''):

    last_answer_meta=local_get_last_answer_meta(case_id)

    Dashboard=The_Dashboard()
    Dashboard.set_last_answer_meta(last_answer_meta)
    Dashboard.prepare_multimodal_insights(case_id,session_id='',force_show_decision=force_show_decision)
    multimodal=Dashboard.dump_multimodal_insights()

    return Dashboard,multimodal

def broadcast_to(case_id,session_id='',message={},force_show_decision=''):
    global WS_ENDPOINT

    ## Require session_id
    #- optionally load from session db OR allow it to be looked at from the front-end

    ## May need to load from session db (or assume found from front-end)

    full_endpoint=WS_ENDPOINT+"/broadcast_listener"

    logging.info("Broadcasting to: "+case_id+" at: "+str(full_endpoint))
    
    ## Check message content
    is_valid=validate_message_format(message=message)
            
    data={}
    data['case_id']=case_id
    data['session_id']=session_id
    data['message']=message
    
    
    Dashboard,multimodal=get_dashboard_data(case_id,force_show_decision=force_show_decision)

    ## DESTINED FOR FRONT-END
    data['multimodal']=multimodal['multimodal']

    #multimodal['multimodal']['timeline_view_type'] & ['timeline_view_url']
    # ^^ timeline type wants extra parameters like width

    # .idict.
    #  {'features': {'has_lat_lng': False, 'is_timelineable': True, 'is_barchartable': True}, 'column_names_map': {'latitude': None, 'longitude': None, 'timeline_date_col': 'Date', 'timeline_amount_col': 'Amount', 'barchart_category_col': 'Date', 'barchart_value_col': 'Amount'}, 'show_decision': 'timeline'}
    
    show_decision=multimodal['multimodal']['idict']['show_decision']
    
    logging.info("[dashboard] show main timeline view: "+str(show_decision)+" URL: "+str(multimodal['multimodal']['timeline_view_url']))

    ## Dump (including df)
    the_json={}
    the_json['data']={}
    the_json['data']=data

    if 'validate serialization' in []:
        try:
            the_json=json.dumps(the_json)
        except Exception as e:
            raise Exception("[mindstate] could not json dump: "+str(e)+": "+str(the_json))

    ## Pre-check base endpoint?
    try:
        response = requests.post(full_endpoint, json=the_json,timeout=5)
        is_sent=True
    except Exception as e:
        logging.info("[mindstate] could not post to: "+str(full_endpoint)+" error: "+str(e))
        is_sent=False
    logging.info ("SENT: "+str(is_sent))
   
    return is_sent



class Mindstate:
    ## Session mind
    def __init__(self):
        self.session_id=None
        self.Storage=Storage_Helper(storage_dir=LOCAL_PATH+"../w_datasets")
        self.Storage.init_db('mindstate_case2sesh')
        self.Storage.init_db('mindstate_sessions')
        return
    
    def start_or_load_session(self,case_id=''):
        sesh=None
        session_id=''
        is_created=False
        if case_id:
            dd=self.Storage.db_get(case_id,'lookup',name='mindstate_case2sesh')
            if not dd:
                ## Create new session
                sesh=self._create_session(case_id=case_id)
                is_created=True
            else:
                sesh=self.Storage.db_get(dd['session_id'],'sesh',name='mindstate_sessions')
                if not sesh:
                    raise Exception("Session not found at: "+str(dd))
            if sesh:
                session_id=sesh['session_id']
        return sesh,session_id,is_created
    
    def _create_session(self,case_id=''):
        session_id=str(uuid.uuid4())
        dd={}
        dd['case_id']=case_id
        dd['session_id']=session_id
        dd['created']=time.time()
        
        ## Create lookup
        self.Storage.db_put(dd['case_id'],'lookup',dd,name='mindstate_case2sesh')
        
        ## Create session
        sesh={}
        sesh['session_id']=session_id
        sesh['case_id']=case_id
        sesh['created']=time.time()
        sesh['state']={}
        self.Storage.db_put(dd['session_id'],'sesh',dd,name='mindstate_sessions')
        
        return sesh
    
    def set_session_id(self,session_id):
        self.session_id=session_id
        return
    def get_session_id(self):
        return self.session_id

    def update_field(self,session_id,field,value,broadcast=False):
        sesh=self.Storage.db_get(session_id,'sesh',name='mindstate_sessions')
        if sesh:
            if not 'state' in sesh: sesh['state']={}
            sesh['state'][field]=value
            sesh['state'][field+"-timestamp"]=int(time.time())
            self.Storage.db_put(session_id,'sesh',sesh,name='mindstate_sessions')
            
        if broadcast:
            self.dev_broadcast(sesh['case_id'],sesh['session_id'])
        return

    def get_field(self,session_id,field):
        field_value=None
        sesh=self.Storage.db_get(session_id,'sesh',name='mindstate_sessions')
        if sesh:
            field_value=sesh.get('state',{}).get(field,None)
            
        ### SPECIAL CASE DECODE
        if field=='last_answer_meta':
            if field_value:
                decoded_df = base64.b64decode(field_value)
                field_value= pickle.loads(decoded_df)
            else:
                field_value={} #None
        
        return field_value
    
    ## FULL NAMING BUT KEEPS A BIT MORE FIRM
    def MIND_store_last_question(self,ask,session_id):
        # broadcast as a demo to see graph update
        self.update_field(session_id,'last_question',ask,broadcast=False)
        return
    def MIND_store_last_answer(self,answer,session_id):
        self.update_field(session_id,'last_answer',answer)
        return
    def MIND_store_last_answer_meta(self,vvalue,session_id):
        #* meta from answer
        
        # Serialize the DataFrame
        serialized_df = pickle.dumps(vvalue)
        encoded_df = base64.b64encode(serialized_df).decode('utf-8') #Not as bytes
        
        ## Includes dataframe etc so can't be pickled!
        logging.info("[dev] broadcast answer now that it's stored (to front-end ie)")
        self.update_field(session_id,'last_answer_meta',encoded_df,broadcast=True)

        return

    def MIND_store_last_parenty_post(self,vvalue):
        self.update_field(session_id,'last_parenty_post',vvalue)
        
    def dev_broadcast(self,case_id,session_id):
        #broadcast_to(target='api_services',message={'session_id':session_id,'case_id':case_id})
        message={'session_id':session_id,'case_id':case_id}
        broadcast_to(case_id,session_id=session_id,message=message)
        return
    

def dev_load_test_sesssion():
    case_id='case_default2'
    #session_id=str(uuid.uuid4())

    Mind=Mindstate()
    sesh,session_id,is_new=Mind.start_or_load_session(case_id=case_id)
    print ("LOADED SESSION NEW: "+str(is_new))
    print ("RAW SESH: "+str(sesh))
    
    return Mind,sesh,session_id,is_new

def dev1():
    Mind,sesh,session_id,is_new=dev_load_test_sesssion()
    Mind.update_field(session_id,'field1','value1')
    return

def dev_broadcast_change():
    ## Message to all X
    #- for now, do http internal post to fastapi API_services (that talks with front-end)

    case_id='case_schoolkids'
    case_id='template_case'
    case_id='case_o3_case_single'
    check=devonly

    Mind=Mindstate()

    sesh,session_id,is_new=Mind.start_or_load_session(case_id=case_id)

    print ("LOADED SESSION NEW: "+str(is_new))

    Mind.update_field(session_id,'field1','value1')
    
    message={'hello':'world'}
    

    ## Update field with broadcast intent
    #Mind.update_field(session_id,'field1','value1',broadcast=['api_services']

#    Mind.set_session_id(session_id)  #absolute setting (because deliberate about where & when)

    Mind.dev_broadcast(case_id,session_id)

    return


if __name__=='__main__':
    branches=['dev1']
    branches=['dev_broadcast_change']
    for b in branches:
        globals()[b]()



        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
