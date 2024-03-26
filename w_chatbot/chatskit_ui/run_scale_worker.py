import sys,os
import re
import json
import time
import copy
import uuid
import datetime

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"

sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")

from tools.dev_tools import iter_dir_documents

from ystorage.ystorage_handler import Storage_Helper
from web_crawler import auto_crawl_domain
from web_crawler import get_friendly_name

from alg_wraps.gptindex_indexing import interface_create_index
from alg_wraps.gptindex_indexing import interface_load_index
from alg_wraps.gptindex_indexing import interface_ping_vector_db
from alg_wraps.gptindex_indexing import interface_iter_indexes


if os.getenv('OPENAI_API_KEY') is None:
    # The environment variable is defined
    print("[init misssing] OPENAI_API_KEY see SETUPENV.sh")
    stopp=no_API_KEY
    

#0v3#  JC  Apr 17, 2023  Iter indexes
#0v2#  JC  Feb 16, 2023  Update for multiples
#0v1#  JC  Jan 17, 2023


###################################################
#   BOT INTERFACE   (manage multi from MANAGE_CHATGPT)
###################################################
#

#Storage=Storage_Helper(storage_dir=LOCAL_PATH+"../storage_dbs")
#Storage.init_db('history')



class Data_Lake_Storage(object):
    ## Larger then Storage_Helper db
    #- optional s3
    #- optional local files
    def __init__(self):
        self.Storage=Storage_Helper(storage_dir=LOCAL_PATH+"data_lake_dbs")
        return
    
    def init_Storage(self,storage_db_name):
        # ? check if exists or init anyways?
        self.Storage.init_db(name=storage_db_name)
        db_size=self.Storage.size(storage_db_name)
        return db_size

class Abstract_Target(object):
    def __init__(self,id='default1'):
        self.id=id
        self.config={}
        return
    
    def dump_config(self):
        self.config['id']=self.id
        return self.config

class Website_Crawler(object):
    #archive.org, commoncrawl, yacy, httrack,
    def __init__(self):
        return

class Scale_Worker(object):
    def __init__(self):
        # worker storage for config
        self.Worker_Storage=Storage_Helper(storage_dir=LOCAL_PATH+"worker_dbs")
        
        # data lake storage for data lake
        self.Data_Lake=Data_Lake_Storage()

        self.worker_db_name='worker_configs'
        self.Worker_Storage.init_db(self.worker_db_name)
        return
    
    def validate_system(self):
        errors=[]
        print ("> system is distributed.")
        print ("> test. boot")
        print ("> test vector database is online")
        is_online=interface_ping_vector_db()

        return errors

    def index_target(self):
        return
    
    def shutdown(self):
        return
    
    def source2raw(self):
        # website to raw?
        # local documents to raw?
        return

    def check_data_lake(self,domain=None):
        ## Get config from crawler
        self.domain=domain
        config=auto_crawl_domain(domain=self.domain,b=['get-config'])
        self.storage_db_name=config['db_name']
        
        db_size=self.Data_Lake.init_Storage(self.storage_db_name)
        print ("[info] db size: "+str(self.storage_db_name)+": "+str(db_size)+' records')

        return db_size,self.storage_db_name
    
    def iter_documents(self,config={}):
        
        ## METHOD 2:  files in local file directory
        if config.get('text_directory_source',''):
            if not os.path.exists(config['text_directory_source']): stopp=no_files

            manual_cont=False
            for ppath,the_text in iter_dir_documents(ddir=config['text_directory_source']):
                ppath=str(ppath)
                
                ## logic if manual cont
                if manual_cont:
                    if ppath=='C:/scripts-22/chatgpt/scale_worker/../the_data_lake/docs_building_science/CP-9907_Measured_Air_Changeadee.txt':
                        manual_cont=False
                if manual_cont:
                    print ("[info] manual skip: "+str(ppath))
                    continue

                yield ppath, the_text, {}
        else:
            ## METHOD 1:  files in sqlite
            db_size=self.Data_Lake.init_Storage(self.storage_db_name)
            if db_size:
                for idx in self.Data_Lake.Storage.iter_database(self.storage_db_name):
                    record=self.Data_Lake.Storage.db_get(idx,'crawl',name=self.storage_db_name)
                    the_text=record.get('the_text','')
                    if the_text:
                        #* idx or doc_id is stored in index I believe
                        yield idx,the_text,{}
        
        return
    
    def load_index(self):
        return
    
    def store_config(self,config):
        # run id? session id?
        self.Worker_Storage.db_put(config['run_id'],'config',config,name=self.worker_db_name)
        print ("[info] stored config at run_id: "+str(config['run_id']))
        return
    
    def load_config(self,run_id):
        record=self.Worker_Storage.db_get(run_id,'config',name=self.worker_db_name)
        return record

    def iter_configs(self):
        for idx in self.Worker_Storage.iter_database(self.worker_db_name):
            record=self.Worker_Storage.db_get(idx,'config',name=self.worker_db_name)
            if record:
                yield record
        return

def get_run_id(pre_config={}):
    ## Just wrap get_config but makes cleaner
    #[ ] or, only when run_id exists?
    config=get_config(pre_config=pre_config)
    
    #TODO:  check if exists
    exists=True
    return config['run_id'],exists

def get_config(pre_config={}):
    print ("[x] snapshot save config settings on each run for backwards compat")

    config=pre_config

    ## 1/
    config['version']='v5'  #mostly for vector db but affects run_id

    ## 2/
    ## FRIENDLY NAME  (ie/ project name without versions)
    if config.get('friendly_name',''):
        pass
    elif not config.get('friendly_name','') and config.get('base_url',''):
        config['friendly_name']=get_friendly_name(config['base_url'])
    else:
        print ("[error]: "+str(config))
        stopp=missing_name_friendly_name

    #i)  patch friendly must be capitalized
    config['friendly_name']=config['friendly_name'][0].upper()+config['friendly_name'][1:]
    
    
    ## 3/
    ## NOTE LOGICAL IMPACTS OF CHANGING VERSION:
    #i)  changing version will point to different vector db class
    config['vector_db_friendly_name']=config['friendly_name']+"_"+config['version']

    config['run_id']=config['vector_db_friendly_name']  #**optional session name
    
    
#    config['source_type']='full_website'
#    config['target_type']='sqlite'
    
    ## Use for variations on an index ie.
    config['embedding_model_name']='sentence_transformers_all_mpnet_base_v2'
    
    ## Version control across various components
    
    ### SOME DEFAULTS:
    config['base_url']=config.get('base_url','')
    config['vector_db_notes']=['stored on truthkit in weaviate persistent directory']
        
    return config


def top_scale_worker(config={},b=[]):
    
    if not b:
        b=['get_index']
        b=['create_data_lake']
        b=['create_index']
        b=['preview_documents']

    print ("[info] running top_scale_worker with options: "+str(b))
    
    meta={}
    start_time=time.time()
    
    ## FORCE NEW TRIAL
    config=get_config(pre_config=config)


    Worker=Scale_Worker()
    Worker.validate_system()
    db_size,friendly_name=Worker.check_data_lake(domain=config.get('base_url',''))

    #=====================================================
    ##############################
    #  CREATE DATA LAKE CORPUSES
    ##############################
    if 'create_data_lake' in b and config.get('base_url',''):
        print ("[info] auto crawling: "+str(config['base_url']))
        auto_crawl_domain(domain=config['base_url'],b=['do_full_domain_crawl'])
        
        
    #=====================================================
    db_size,friendly_name=Worker.check_data_lake(domain=config.get('base_url',''))
    
    if 'preview_documents' in b:
        for doc_id,txt,meta in Worker.iter_documents(config=config):
            print ("TxT: "+str(txt))
            print ("="*40)
    
    ###########################
    #  CREATE INDEX
    ###########################
    count_indexed=0
    if 'create_index' in b:
        ### FIRST PASS
        friendly_name=config['vector_db_friendly_name']
        index_filename,count_indexed=interface_create_index(friendly_name,Worker,config=config,embedding_name=config['embedding_model_name'])
        
        print ("Index created via "+str(count_indexed)+" docs at: "+str(index_filename))
        
    ###########################
    #  SAVE CONFIG
    ###########################
    b=['store_config']
    if 'store_config' in b and db_size or count_indexed and index_filename:
        config['meta']={}
        config['meta']['index_filename']=index_filename
        config['meta']['runtime']=time.time()-start_time
        config['meta']['count_indexed']=count_indexed
        config['meta']['data_lake_db_size']=db_size
        config['meta']['the_date']=str(datetime.datetime.now())

        Worker.store_config(config)


    print ("[info] done top_scale_worker")
    return


def top_use_index():
    
    ## CONFIG
    config={}
    config['base_url']='https://www.portstoronto.com/'
    
    config=get_config(pre_config=confit)

    ## LOAD INDEX
    friendly_name=config['vector_db_friendly_name']
    index,embed_model=interface_load_index(friendly_name)
    
    ## QUERY INDEX
    #** see gptindex_wrap
    
    query="Can I swim in the harbour?"
    query="What's the longest I can park on the street?"
    query="What are common public park bylaws?"
    query="Are there any private cemetaries in Toronto?"
    query="Where can I scuba dive?"

    response_mode='default'    # can be many
    response_mode='minquery'   #Only 1 or 2

    print ("[info] got index")
    print ("[info] doing query...")
    #print ("** if KeyError: 0 then likely being rate limited")
    #response = index.query(query, mode='default',embed_model=embed_model,response_mode=response_mode,verbose=True) 
    
    #similarity at vector
    response = index.query(query, similarity_top_k=5,mode='default',embed_model=embed_model,response_mode=response_mode,verbose=True) 
    
    print ("RESPONSE: "+str(response))

    return


def plan_full_run(pre_config={},branches=[]):

    errors=[]
    
    if not branches:
        b=[]
        b=['check_setup']
        b=['create_index']
        b=['run_query']
    else:
        b=branches
    print ("[info] plan_full_run at branches: "+str(b))
        
    if not pre_config:
        ### REDO BUILDING SCIENCE DOCUMENTS
        pre_config={}
        pre_config['friendly_name']='BuildingScienceCom' #Title for now
        pre_config['text_directory_source']=LOCAL_PATH+"../the_data_lake/docs_building_science"
        query="What causes the most heat loss in a room?"
    

    if 'check_setup' in b:
        pre_config['base_url']='https://www.portstoronto.com/'
    
        config=get_config(pre_config=pre_config)
        print ("BASE CONFIG: "+str(config))
        
        Worker=Scale_Worker()
        errors+=Worker.validate_system()
        db_size,friendly_name=Worker.check_data_lake(domain=config['base_url'])
        print ("[info] current document count for: "+str(config['friendly_name'])+": "+str(db_size))
    
    
    if 'create_index' in b:
        
        ## dev
        b=['preview_documents']
        b=[]
        b=['create_index']
        b+=branches #Allow ask for data lake early
        top_scale_worker(config=pre_config,b=b)
        
    if 'run_query' in b:

        config=get_config(pre_config=pre_config)

        print ("*beware, index + query == memory error via huggingface embeddings model")
        embedding_name=config['embedding_model_name']
        friendly_name=config['vector_db_friendly_name']
        index,embed_model=interface_load_index(friendly_name, embedding_name=embedding_name)
        

        response_mode='default'    # can be many
        response_mode='minquery'   #Only 1 or 2
        top_k=3 #note: minquery won't do 3rd

        response = index.query(config['query'], similarity_top_k=top_k,mode='default',embed_model=embed_model,response_mode=response_mode,verbose=True) 
    
        print ("RESPONSE: "+str(response))

    return



def load_preconfig(topic):
    #** SET THESE FOR EACH??
    b=[topic]
    pre_config={}
    
    ## DEFAULT
    pre_config['friendly_name']=topic

    if 'buildingscience' in b:
        pre_config['friendly_name']='BuildingScienceCom' #Title for now
        pre_config['text_directory_source']=LOCAL_PATH+"../the_data_lake/docs_building_science"
        pre_config['query']="What causes the most heat loss in a room?"

    if 'myupp' in b:
        pre_config['friendly_name']=topic
    return pre_config


class Bot_Interface(object):
    ## Mostly for flask api
    def __init__(self,topic='buildingscience'):
        self.topic=topic
        self.index=None
        self.embed_model=None
        return
    
    def get_name(self):
        return self.topic
    
    def test_query(self):
        text_response,meta=self.handle_query('hello world')
        if not text_response:
            stopp=hard_fail_no_text_response
        return text_response
    
    def load(self):
        ## Preconfig
        self.pre_config=load_preconfig(self.topic)
        self.config=get_config(pre_config=self.pre_config)
        
        ## Big model pieces
        print ("[debug] loading index & embedder...")
        
        embedding_name=self.config['embedding_model_name']
        friendly_name=self.config['vector_db_friendly_name']

        try:
            self.index,self.embed_model=interface_load_index(friendly_name, embedding_name=embedding_name)
        except Exception as e:
            if 'No connection' in str(e):
                print ("[error] can't load index (connect to weaviate maybe)")
                stopp=no_index
            else:
                self.index,self.embed_model=interface_load_index(friendly_name, embedding_name=embedding_name)

        print ("[debug] loaded.")

        return
    
    def handle_query(self,query, params={}):
        ## params are raw params passed from streamlit example_chatbot.py
        
        response_mode='default'    # can be many
        response_mode='minquery'   #Only 1 or 2
        top_k=3 #note: minquery won't do 3rd

        response = self.index.query(query, similarity_top_k=top_k,mode='default',embed_model=self.embed_model,response_mode=response_mode,verbose=True) 
        
        #??dict response?? /indecies/response/schema/
        text_response=str(response)
        text_response=re.sub(r'\\n','',text_response)
        
#        text_response+=" "+str(params)
  
        return text_response,{}
    
def interface_iter_known_topics():
    # topic + config + filename??
    # {'friendly_name': 'BuildingScienceCom', 'text_directory_source': 'C:\\scripts-22\\chatgpt\\scale_worker/../the_data_lake/docs_building_science', 'version': 'v5', 'vector_db_friendly_name': 'BuildingScienceCom_v5', 'run_id': 'BuildingScienceCom_v5', 'embedding_model_name': 'sentence_transformers_all_mpnet_base_v2', 'base_url': '', 'vector_db_notes': ['stored on truthkit in weaviate persistent directory'], 'meta': {'runtime': 770.2069473266602, 'count_indexed': 289, 'data_lake_db_size': 0, 'the_date': '2023-01-18 10:32:47.952132'}}
    Worker=Scale_Worker()
    for config in Worker.iter_configs():
        #print ("FO: "+str(config))
        topic=config.get('topic','')
        if not topic:
            topic=config.get('friendly_name','')
        if topic:
            yield topic,config

    return

def sample_run_stack():
    ## TOP DIRECTION
    pre_config={}
    
    ## TOPIC
    pre_config['topic']='nexusenergycanada'
    b=[pre_config['topic']]
    b=['buildingscience']
    b=['portauthority']
    
    

    ## TOP FUNCTIONS
    branches=['create_index','create_data_lake']
    branches=['run_query']
                                                        #
    #####################################################


    if 'buildingscience' in b:
        pre_config['friendly_name']='BuildingScienceCom' #Title for now
        pre_config['text_directory_source']=LOCAL_PATH+"../the_data_lake/docs_building_science"
        pre_config['query']="What causes the most heat loss in a room?"
    
    if 'portauthority' in b:
        pre_config['base_url']='https://portstoronto.com/'

    if 'nexusenergycanada' in b:
        pre_config['base_url']='https://nexusenergycanada.com'

    plan_full_run(pre_config=pre_config,branches=branches)
    
    return

def interface_chatbot():
    return

def interface_load_chatbot(name):
    Bot=Bot_Interface(topic=name)
    Bot.load()
    # text_response,meta=Bot.handle_query(query, params={})
    return Bot

def interface_chatbot_create_index_from_domain(name,domain):
    print ("[ ] save config with index!")
    if not 'http' in domain: domain='https://'+domain
    econfig={}
    econfig['topic']=name
    econfig['friendly_name']=name
#    econfig['text_directory_source']=''
    econfig['base_url']=domain

    branches=[]
    branches+=['create_data_lake']
    branches+=['create_index']
    top_scale_worker(config=econfig,b=branches)

    return

def dev_interface_chatbot():
    print ("Try creating external")

    econfig={}
    econfig['topic']='myupp'
    econfig['friendly_name']='myupp'
#    econfig['text_directory_source']=''
    econfig['base_url']="https://myupp.ca"
        
        
    b=['view_documents']
    b=['create_from_scratch']
    b=['basic_query']
    
    if 'create_from_scratch' in b:
        ###########################
        # CREATE FROM SCRATCH
        branches=[]
        branches+=['create_data_lake']
        branches+=['create_index']
    
        top_scale_worker(config=econfig,b=branches)
        
    if 'basic_query' in b:
        branches=[]
        branches+=['run_query']
        econfig['query']='What are some goals for 2023?' #[x]
        econfig['query']='Who are some of the UPP members?'
        plan_full_run(pre_config=econfig,branches=branches)
        
    if 'view_documents' in b:
        branches=[]
        branches+=['preview_documents']
        top_scale_worker(config=econfig,b=branches)
        
    
    return

def dev_usage():
    query='What is ESG?'

    name='myupp'
    Bot=interface_load_chatbot(name)
    text_response,meta=Bot.handle_query(query, params={})
    print ("RES: "+str(text_response))
    
    return


def dev_multiple_indexes():
    ##  
    return


def test_endpoint_query():
    q='Do I need a new furnace to be green certified?'

    print ("[test] query")

    Bot=Bot_Interface()
    Bot.load()

    print ("QUERY: "+str(q))
    rr,dd=Bot.handle_query(q)
    print ("RESPONSE: "+str(rr))

    return

if __name__=='__main__':
#    a=good_port_authority_index

    branches=['call_scale_worker']

    branches=['top_use_index']

    branches=['top_scale_worker']

    branches=['plan_full_run']

    branches=['sample_run_stack']

    branches=['test_endpoint_query']

    branches=['dev_interface_chatbot']

    branches=['dev_usage']


    for b in branches:
        globals()[b]()
        
        
        

        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
