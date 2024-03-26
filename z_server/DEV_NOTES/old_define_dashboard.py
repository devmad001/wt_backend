import os
import sys
import codecs
import json
import re

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")


from get_logger import setup_logging
logging=setup_logging()



#0v3# JC  Oct 27, 2023  Add formal API (swagger) + alt d3 timeline
#0v2# JC  Sep 28, 2023  Add live endpoints
#0v1# JC  Sep 25, 2023  Init


"""
    DEFINE ORIGINAL JSON DASHBOARD CONFIG
    - ideally, not overly config based but url + ports will swap
"""


CONFIG_FILENAME=LOCAL_PATH+'../'+'w_config_dashboard.json'


def define_dashboard_config():
    print ("Admin config creation -- formalize it a bit")

    dash={}
    dash['base_url']="http://3.20.195.157"
    dash['local_url']="http://127.0.0.1"
    dash['LOCAL_DEV']=True
    dash['CHATBOT_ONLINE']=True

    dash['dashboards']={}

    ## PARENT at index 0
    #- main window handler
    dashboard={}
    dashboard['id']='parenty'
    dashboard['live']='dashboard.epventures.co'


    dashboard['port']=5000
    dashboard['server_start_cmd']='python app_parenty.py'
    dashboard['server_dir']='/w_zoid'
    dash['dashboards'][dashboard['id']]=dashboard

    ## ADMIN
    dashboard={}
    dashboard['id']='admin' #Admin
    dash['dashboards'][dashboard['id']]=dashboard

    ## FRAUDAPI
    dashboard={}
    dashboard['id']='fraudapi'
    dashboard['name']='fraudapi'
    dashboard['live']='fraudapi.epventures.co'
    dashboard['rel_url']='/'
    dashboard['port']=8008
    dashboard['sample_call']=dash['base_url']+":"+str(dashboard['port'])+dashboard['rel_url']
    dashboard['server_dir']=''
    dashboard['server_start_cmd']=''
    dashboard['notes']=['alg_generate_pdf_hyperlink thinks storage.']
    dash['dashboards'][dashboard['id']]=dashboard

    ## TIMELINE
    dashboard={}
    dashboard['id']='timeline'
    dashboard['name']='Timeline'
    dashboard['live']='timeline.epventures.co'
    dashboard['rel_url']='/'
    dashboard['port']=5003
    dashboard['sample_call']=dash['base_url']+":"+str(dashboard['port'])+dashboard['rel_url']
    dashboard['server_dir']='/x_timeline/bank_failures'
    dashboard['server_start_cmd']='python run_obs.py'
    dash['dashboards'][dashboard['id']]=dashboard

    dashboard={}
    dashboard['id']='map'
    dashboard['name']='map'
    dashboard['live']='timeline.epventures.co'
    dashboard['rel_url']='/map'
    dashboard['port']=5003
    dashboard['sample_call']=dash['base_url']+":"+str(dashboard['port'])+"/get_pois"
    dashboard['server_dir']=''
    dashboard['server_start_cmd']=''
    dash['dashboards'][dashboard['id']]=dashboard
    
    ## Chat bot
    dashboard={}
    dashboard['id']='chatbot'
    dashboard['name']='chatbot'
    dashboard['live']='chatbot.epventures.co'
    dashboard['rel_url']='/'

    dashboard['port']=8082
    dashboard['sample_call']=dash['base_url']+":"+str(dashboard['port'])+dashboard['rel_url']
    dashboard['server_dir']='/w_chatbot'
    dashboard['server_start_cmd']='python -m streamlit run wt_streamlit.py --server.port '+str(dashboard['port'])
    #dashboard['server_start_cmd']='python -m streamlit run c:\scripts-23\watchtower\wcodebase\w_chatbot\wt_streamlit.py --server.port '+str(dashboard['port'])

    dash['dashboards'][dashboard['id']]=dashboard

    ## Chat bot ENDPOINT
    dashboard={}
    dashboard['id']='chatbot_api'
    dashboard['name']='chatbotapi'
    dashboard['live']='chatbotapi.epventures.co'
    dashboard['rel_url']='/'
    dashboard['port']=5005
#    dashboard['sample_call']=dash['base_url']+":"+str(dashboard['port'])+dashboard['rel_url']
    dashboard['server_dir']='/w_chatbot'
    dashboard['server_start_cmd']='python wt_flask_handle.py'

    dash['dashboards'][dashboard['id']]=dashboard


    ## Square
    dashboard={}
    dashboard['id']='square'
    dashboard['name']='square'
    dashboard['live']='square.epventures.co'
    dashboard['rel_url']='/dynamic_square'

    dashboard['port']=8081  #Hard coded in pyfiledrop.py [ ]
    dashboard['sample_call']=dash['base_url']+":"+str(dashboard['port'])+dashboard['rel_url']
    dashboard['server_dir']='/x_components'
    dashboard['server_start_cmd']='python serve_ui_flask.py'

    dash['dashboards'][dashboard['id']]=dashboard

    ## Upload 
    dashboard={}
    dashboard['id']='upload'
    dashboard['name']='upload'
    dashboard['live']='upload.epventures.co'
    dashboard['rel_url']='/'

    dashboard['port']=8084  #Hard coded in pyfiledrop.py [ ]
    dashboard['sample_call']=dash['base_url']+":"+str(dashboard['port'])+dashboard['rel_url']
    dashboard['server_dir']='/w_ui/file_manager'
    dashboard['server_start_cmd']='python pyfiledrop.py'

    dash['dashboards'][dashboard['id']]=dashboard

    ## API Hub
    dashboard={}
    dashboard['id']='api_services'
    dashboard['name']='api_services'
    dashboard['live']='api.epventures.co'

    dashboard['rel_url']='/'

    dashboard['port']=8083  #Hard coded in pyfiledrop.py [ ]
    dashboard['sample_call']=dash['base_url']+":"+str(dashboard['port'])+dashboard['rel_url']+"ping"
    dashboard['server_dir']='/w_api'
    dashboard['server_start_cmd']='python api_services.py'

    dash['dashboards'][dashboard['id']]=dashboard

#special api#    ## API Core (Swagger)
#special api#    dashboard={}
#special api#    dashboard['id']='api_core'
#special api#    dashboard['name']='api_core'
#special api#    dashboard['live']='core.epventures.co'
#special api#
#special api#    dashboard['rel_url']='/'
#special api#
#special api#    dashboard['port']=8008  
#special api#    dashboard['sample_call']=dash['base_url']+":"+str(dashboard['port'])+dashboard['rel_url']+"ping"
#special api#    dashboard['server_dir']='/z_apiengine'
#special api#    dashboard['server_start_cmd']='python fast_main.py' #uviconrn fast_main:app --reload
#special api#
#special api#    dash['dashboards'][dashboard['id']]=dashboard

    ## API D3  (experiments or timeline A?)
    dashboard={}
    dashboard['id']='d3'
    dashboard['name']='d3'
    dashboard['live']='d3.epventures.co'

    dashboard['rel_url']='/'

    dashboard['port']=5011
    dashboard['sample_call']=dash['base_url']+":"+str(dashboard['port'])+dashboard['rel_url']+"ping"
    dashboard['server_dir']='/x_timeline/beeswarm/bee_2_better'
    dashboard['server_start_cmd']='python flaskd3.py' #uviconrn fast_main:app --reload

    dash['dashboards'][dashboard['id']]=dashboard

#    # ..unused...below...
#    dashboard['flaskpath']='/x_timeline/bank_failures/run_obs.py'
#    dashboard['start_cmd']='python run_obs.py'
#    dashboard['is_relative']=True
#
#
#    dashboard['css']={}
#    dashboard['css']['position']='absolute'
#    dashboard['css']['top']='10px'
#    dashboard['css']['left']='10px'
#    dashboard['css']['width']='300px'
#    dashboard['css']['height']='200px'
#    dashboard['responsive']=True
#    dashboard['type']='iframe'
    
    
    ## WRITE
    fp=open(CONFIG_FILENAME,'w')
    json.dump(dash,fp,indent=4)
    fp.close()

    print (str(json.dumps(dash,indent=4)))
    print ("[updated]: "+str(CONFIG_FILENAME))

    return


if __name__=='__main__':
    branches=['define_dashboard_config']
    for b in branches:
        globals()[b]()


"""

"""
