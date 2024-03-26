import os
import sys
import codecs
import uuid
import json
import re
import time
import hashlib

import pandas as pd
from collections import Counter


import configparser as ConfigParser

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")


from get_logger import setup_logging
logging=setup_logging()

from kb_ask.kb_answer_multimodal import prepare_multimodal_insight_dict
from config_views import config_get_map_view_url


#0v3# JC  Jan 24, 2024  Centralize view urls into config_views
#0v2# JC  Jan 16, 2024  Add credits used option
#0v1# JC  Nov 13, 2023  Setup


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

FRAUDAPI_PORT=RootConfig.get('services','fraudapi_port')
FRAUDAPI_subdomain=RootConfig.get('services','fraudapi_subdomain')
FRAUDAPI_domain=RootConfig.get('services','fraudapi_domain')


ON_LIVE_SERVER=True
if os.name=='nt': ON_LIVE_SERVER=False

if ON_LIVE_SERVER:
    BASE_ENDPOINT='https://'+FRAUDAPI_subdomain+"."+FRAUDAPI_domain
else:
    BASE_ENDPOINT='http://127.0.0.1:'+str(FRAUDAPI_PORT)




"""
    DASHBOARD "proxy"
    - similar to mindstate but replicate what front-end dashboard should see
    - also be obvious on which views are being shown
    - tie into last step of broadcast to

"""


## Patch:  Possible for df to have multiple named columns, so do: Name1, Name2, etc.


def generate_hash(text):
    # Create a SHA-256 hash object
    sha256 = hashlib.sha256()
    # Update the hash object with the bytes-like object (text in bytes format)
    sha256.update(text.encode())
    # Return the hexadecimal representation of the hash
    return sha256.hexdigest()
    
def normalize_df(df):
    # Timestamp() dates can't be serialized!
    df = df.applymap(lambda x: x.strftime('%Y-%m-%d %H:%M:%S') if isinstance(x, pd.Timestamp) else x)
    
    # NaT to None
    
    # Replace NaT with None
    df = df.where(pd.notna(df), None)

    return df

# Do it for jsonl too:

def serialize_dicts_with_timestamps(dicts_list):
    #[ ] optionally upstream
    for d in dicts_list:
        for key, value in d.items():
            
            if isinstance(value, pd._libs.tslibs.nattype.NaTType):
                d[key] = None

            if isinstance(value, pd.Timestamp):
                # Convert Timestamp to string
                d[key] = value.strftime('%Y-%m-%d %H:%M:%S')
    """
    from datetime import date
       if isinstance(value, pd.Timestamp) or isinstance(value, date):
                # Convert to string
                d[key] = value.strftime('%Y-%m-%d')
    """
    return dicts_list
    
def rename_duplicate_columns(df):
    col_count = {}
    new_columns = []

    for col in df.columns:
        if col in col_count:
            col_count[col] += 1
            new_col_name = f"{col}_{col_count[col]}"
            new_columns.append(new_col_name)
        else:
            col_count[col] = 0
            new_columns.append(col)

    df.columns = new_columns
    return df



class The_Dashboard:
    def __init__(self):
        self.last_answer_meta={}
        self.idict={}
        
        self.explain=[]
        return

    def set_last_answer_meta(self,last_answer_meta):
        self.last_answer_meta=last_answer_meta
        return
    

#    def load_multimodal_state(self,case_id,session_id=''):
#        return
#
    def prepare_multimodal_insights(self,case_id,session_id='',user_id='',force_show_decision=''):
        ## Essentially use function that decides what to show
        #dd['multimodal']['idict']=self.idict   #*possibly exists already but from same method
        self.case_id=case_id
        self.user_id=user_id #[ ] pass + check

        question=''
        meta={}
        if not self.last_answer_meta:
            logging.warning("[warning] no last_answer_meta at: "+str(case_id))
        else:
#            print ("GIVEN AT KEYS: "+str(self.last_answer_meta.keys()))
            self.idict=prepare_multimodal_insight_dict(self.last_answer_meta['multimodal'],question=question,case_id=case_id,meta=meta,force_show_decision=force_show_decision)
            
            print ("[idict]: "+str(self.idict))

        return
    
    def dump_multimodal_insights(self):
        
        ##[1]  Include idict with answer_meta (may have refreshed based on rules/state)
        dd=self.last_answer_meta
        if not 'multimodal' in dd:
            logging.info("[debug] dump multimodal but none at last answer meta: "+str(dd))
            dd['multimodal']={} #Patch if never had question
        dd['multimodal']['idict']=self.idict   #*possibly exists?
        
        ##[2]  Set target timeline view
        dd=self.include_main_timeline_component_url(self.case_id,dd,session_id='',user_id=self.user_id)
        

        ######################################
        ### Ensure json serializeable
        
        ## Dataframes:
        for block in dd['multimodal']:
            # If df then normalize
            if isinstance(dd['multimodal'][block],pd.DataFrame):
                dd['multimodal'][block]=normalize_df(dd['multimodal'][block])
                
        if dd['multimodal'].get('barchart',[]):
            dd['multimodal']['barchart']=serialize_dicts_with_timestamps(dd['multimodal']['barchart'])
        if dd['multimodal'].get('timeline',[]):
            dd['multimodal']['timeline']=serialize_dicts_with_timestamps(dd['multimodal']['timeline'])

        if dd['multimodal'].get('df',None) is not None:
            try:
                dd['multimodal']['df']=rename_duplicate_columns(dd['multimodal']['df']).to_json(orient='records')
            except Exception as e:
                logging.error("[could not serialize] : "+str(e)+" AT DATA: "+str(dd['multimodal']['df']))
                dd['multimodal']['df']=dd['multimodal']['df'].to_json(orient='records')
    
            dd['multimodal']['df_filtered']=rename_duplicate_columns(dd['multimodal']['df_filtered']).to_json(orient='records')
        else:
            dd['multimodal']['df_filtered']=None
        
        #[ ] ideally move this normalization up
        ## -> normalize yes, but better to do grossly above.
        ### To string for barchart + timeline data
        for item in dd['multimodal'].get('barchart',[]):
            if 'Date' in item:
                if item['Date'] is None:
                    item['Date']=''
                elif isinstance(item['Date'],str):
                    pass #? check format?
                else:
                    item['Date']=item['Date'].strftime('%Y-%m-%d')

        for item in dd['multimodal'].get('timeline',[]):
            if 'Date' in item:
                # May be string already
                if item['Date'] is None:
                    item['Date']=''
                elif isinstance(item['Date'],str):
                    pass
                else:
                    item['Date']=item['Date'].strftime('%Y-%m-%d')
                
        # If dd['df'] is dataframe then serialize it
        if dd.get('df',None) is not None:
            if isinstance(dd['df'],pd.DataFrame):
                dd['df']=dd['df'].to_json(orient='records')

        ## Precheck json serializeable?
        try:
            temp=json.dumps(dd)
            
            ## Auto data hash for front-end change detection
        except Exception as e:
            print ("COULD NOT SERIALIZE: "+str(dd))
            
            ## Local debug check for df or unserializeable
            print (str(e))
            print ("="*30)

            ### DEBUG WHERE IN DATA?
            for block in dd['multimodal']:
                try:
                    json.dumps(dd['multimodal'][block])
                except:
                    print ("BAD: "+str(dd['multimodal'][block])+" AT BLOCK: "+str(block))
                    print ("BAD BLOCK: "+str(block))
                print ("="*30)

            for block in dd:
                try:
                    json.dumps(dd[block])
                except:
                    print ("BAD: "+str(dd[block])+" AT BLOCK: "+str(block))
                print ("="*30)
                
            raise Exception("BAD DATA (SEE RAW DATA DUMPS ABOVE)")
    
        ## Calculate data hash
        dd['data_hash']=self._data_hash(dd)  #For front-end change detection
        dd['credits_used']=self.calculate_credits_used(dd)

        return dd
    
    def calculate_credits_used(self,dd):
        ## Dev initial (recall used really once on creation)
        # 'jsonl', 'df', 'df_filtered',
        credits_used=0
        try:
            credits_used=len(dd['multimodal'].get('jsonl',[]))
        except:
            try:
                credits_used=len(dd['multimodal'].get('df',[]))
            except:
                pass
        return credits_used
    
    def _data_hash(self,dd):
        max_string=2000
        content=''
        if not 'jsonl' in dd['multimodal']:
            print ("NO DATA FOR HASH FOR: "+str(dd['multimodal']))
            logging.info("[debug] no jsonl data for hash")
            content=''
            #NO DATA FOR HASH FOR: {'idict': {}, 'timeline_view_type': 'timeline', 'timeline_view_url': '', 'df_filtered': None}
        else:
    
            for idict in dd['multimodal']['jsonl']:
                try:line_str=str(idict)
                except: line_str=''
                content+=line_str
                if len(content)>max_string:
                    break
        data_hash=generate_hash(content)
        return data_hash
    
    def include_main_timeline_component_url(self,case_id,dd,session_id='',user_id=''):
        ## Depends on decision
        show_decision=''

        if 'show_decision' in dd['multimodal']['idict']:
            show_decision=dd['multimodal']['idict']['show_decision']
        
        if not show_decision:
            logging.warning("[debug] no show_decision (use timeline) at: "+str(dd['multimodal']['idict']))
            show_decision='timeline'
            dd['multimodal']['idict']['show_decision']=show_decision
            dd['multimodal']['timeline_view_type']=show_decision

        else:

            dd['multimodal']['timeline_view_type']=show_decision
        
        urls=get_timeline_urls(case_id,session_id=session_id,user_id=user_id)

        dd['multimodal']['timeline_view_url']=urls.get(show_decision,'')
        
        if not dd['multimodal']['timeline_view_url']:
            logging.warning("[unknown timeline_view_url]")

        self.explain+=['Dashboard main view is: '+str(dd['multimodal']['timeline_view_url'])]
        return dd
    

def get_timeline_urls(case_id,session_id='',user_id=''):
    global BASE_ENDPOINT
    #[ ] possible remove because covered in abstract_FE
    
    logging.info("[debug] ok .get_timeline_urls() but now in abstract_FE map_decision2component)")
    
    # (square http://127.0.0.1:8008/api/v1/case/case_atm_locations/square)
    
    urls={}
    
    ## Add API
    url=BASE_ENDPOINT+'/api/v1/timeline/'+case_id
    
    ## Map view
    #http://127.0.0.1:8008/api/v1/case/case_atm_locations/map/view
    #urls['map']=BASE_ENDPOINT+'/api/v1/case/'+case_id+'/map/view'
    urls['map']=config_get_map_view_url(case_id,session_id=session_id,user_id=user_id)
    
    ## Timeline
    # const apiUrl = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8008';
    # const defaultUrl = `${apiUrl}/api/v1/case/${caseId}/timeline?maxWidth=${maxWidth}&maxHeight=${enforcedMaxHeight}`;
    urls['timeline_dynamic']=BASE_ENDPOINT+'/api/v1/case/'+case_id+'/timeline_dynamic'
    
    ## Barchart
    #http://127.0.0.1:8008/api/v1/case/case_atm_locations/barchart'
    urls['barchart']=BASE_ENDPOINT+'/api/v1/case/'+case_id+'/barchart'

    return urls


def dev1():
    print ("Resolve target urls (for dashboard auto load)")
    
    base_url=''
    
    #timeline url
    #map url
    #barchart url

    return



if __name__=='__main__':
    branches=['dev1']
    for b in branches:
        globals()[b]()





        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
