name_of_file=__file__.split('/')[-1]
FLASK_ENDPOINT='127.0.0.1:5005'

print ("python -m streamlit run "+name_of_file+" --server.port 8082")
print ("*assume flask at: "+str(FLASK_ENDPOINT))

import os,sys
import time
import re

import streamlit as st   #pip install streamlit
from streamlit_chat import message
import requests

import html
import uuid


import configparser as ConfigParser

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)

#localhost:8082/case/case_1/chat

#0v6# JC  Sep 26, 2023  js to main page
#0v5# JC  Sep 14, 2023  INSTALL REQUIREMENTS:
#                               pip install streamlit_chat==0.0.2.1 
#                               NOT pip install streamlit_chat==0.1.1

#0v4# JC  Sep 14, 2023  Option for WT.
#0v3# JC  Apr 14, 2023  Step through normal run and upgrade to 1.21
#0v2# JC  Feb  9, 2023  Config + fix clearing of input


#NOTES:
#- recall, this is run on every input so global session state variable only
#

#REF:
#    https://github.com/AI-Yash/st-chat
#    https://share.streamlit.io/ai-yash/st-chat/main/examples/chatbot.py
#    API_URL = "https://api-inference.huggingface.co/models/facebook/blenderbot-400M-distill"
#    #https://docs.streamlit.io/knowledge-base/tutorials/build-conversational-apps#build-a-simple-chatbot-gui-with-streaming

#NOTES:
###########################
### Parameters and url paths
## BASE URL CONFIG:
##~/streamlit/config.toml:
##[server]
##baseUrlPath = "/tool/streamlit"
### Normalize path since var1=value turns into var1=[value]
#
##D1# ## Wildcard routes
##D1# #Define app routes
##D1# routes = {
##D1#     '/option_a': option_a,
#

##########################
## CONFIGS
#Config = ConfigParser.ConfigParser()
#Config.read(LOCAL_PATH+"config_chatgpt.ini")
#flask_service=Config.get('main_server','flask_service')
#flask_port=Config.get('main_server','flask_port')

## Patch
if not re.search(r'^http',FLASK_ENDPOINT,flags=re.I):
    FLASK_ENDPOINT='http://'+FLASK_ENDPOINT

##########################
def apply_patches():

    ### SET PAGE TITLE & ICON
    if not 'nt' in os.name: #patch bug
        st.set_page_config(
            page_title="WTKit",
            page_icon=":robot:"
        )
        ##  st.header("WatchTower Bot")
        ##  st.markdown("[Homepage](https://watchtower.ca)")

    ### Remove made with streamlit
    hide_streamlit_style = """
                <style>
                #MainMenu {visibility: hidden;}
                footer {visibility: hidden;}
                </style>
                """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True) 
    return
    
#iframe    st.markdown('<script>alert("Hello")</script>', unsafe_allow_html=True)

apply_patches()

#https://discuss.streamlit.io/t/injecting-js/22651/5
def javascript(source: str) -> None:
    div_id = uuid.uuid4()

    st.markdown(f"""
    <div style="display:none" id="{div_id}">
        <iframe src="javascript: \
            var script = document.createElement('script'); \
            script.type = 'text/javascript'; \
            script.text = {html.escape(repr(source))}; \
            var div = window.parent.document.getElementById('{div_id}'); \
            div.appendChild(script); \
            div.parentElement.parentElement.parentElement.style.display = 'none'; \
        "/>
    </div>
    """, unsafe_allow_html=True)

# Call the function to execute JavaScript
longjs="""
alert("Hello2");
"""
#javascript('alert("Hello");')
javascript(longjs)




##########################
# PARAMETERS AND STATE
##########################
#
def get_query_parameters():
    params={}
    temp_params = st.experimental_get_query_params()
    for kkey in temp_params:
        params[kkey]=temp_params[kkey][0] #Assume take first
    print ("[debug got query: "+str(params))
    return params
params=get_query_parameters()

if 'generated' not in st.session_state:
    st.session_state['generated'] = []

if 'past' not in st.session_state:
    st.session_state['past'] = []


#########################
#  HANDLE USER INPUT
#########################
def get_text():
    ## Recall, called on every input so increment key to allow clearing & new input prompt
    #- counter for tracking

    if not 'counter' in st.session_state:
        KEY=st.session_state.counter=0
    else:
        st.session_state.counter+=1
        
    ## Patch
    try:
        KEY=st.session_state.counter
    except:
        st.session_state.counter=0
        KEY=0

    input_text = st.text_input("You: ","", key=KEY) #on_change
    
    if KEY>0:
        input_text=st.session_state[KEY-1]
    else:
        input_text=''
#
    return input_text 

user_input = get_text()


#########################
#  QUERY HANDLER
#########################
#
def query_UNUSED(payload):
    response = requests.post(API_URL, headers=headers, json=payload)
    if response:
        try:
            rr=response.json()
        except Exception as e:
            rr={'error':'bad_response_1003'}
    else:
        rr={'error':'bad_response_from_internal_flask_query_endpoint'}
    return rr

def query_wt_chat_handler(query):
    global FLASK_ENDPOINT

    print ("[debug] query: "+str(query))
    do_query=True
    
    if query in ['Every time?','Hello, how are you?']: do_query=False

    output={}
    output['generated_text']='Still ready for a question...'
    
    if do_query:
        #flask_endpoint='http://10.8.18.29:5005'
        #flask_endpoint='http://192.168.0.25:5005'
        #flask_endpoint='https://ask.chatskit.com/buildingscience'
        #url=flask_endpoint+"/ask?query="+query
        #url=flask_endpoint+"/ask?query="+query&topic=buildingscience
        
        url=FLASK_ENDPOINT+"/ask?query="+query
        ## Pass streamlist parameters to flask handler  (allow it to do ALL routing)
        if params:
            for kkey in params:
                url+='&'+str(kkey)+'='+str(params[kkey])

        response = requests.get(url) #, headers=headers, json=payload)
        
        try:
            dd=response.json()
        except Exception as e:
            #logging.warning("[non json back from flask: "+str(response))
            dd={}
    
        output['generated_text']=dd.get('generated_text',"Oops, I've lost connection to the server.")

    print ("[streamlit output: "+str(output))
    return output


#########################
#  ON USER INPUT
#########################
#
if user_input:
    output=query_wt_chat_handler(user_input)
#    output = query({
#        "inputs": {
#            "past_user_inputs": st.session_state.past,
#            "generated_responses": st.session_state.generated,
#            "text": user_input,
#        },"parameters": {"repetition_penalty": 1.33},
#    })

    ## Add to below session
    st.session_state.past.append(user_input)
    st.session_state.generated.append(output["generated_text"])
    

###############################
#  REFRESH STATE OF MESSAGES
###############################
#
## Recreate message flow
# STYLES: https://dicebear.com/styles
# https://github.com/AI-Yash/st-chat/blob/8ac13aa3fdf98bacb971f24c759c3daa16669183/streamlit_chat/__init__.py#L24

if 'generated' in st.session_state:
    for i in range(len(st.session_state['generated'])-1, -1, -1):
        print ("[debug] call at: "+str(i))

        message(st.session_state["generated"][i], key=str(i), avatar_style="bottts")
        message(st.session_state['past'][i], is_user=True, key=str(i) + '_user',avatar_style="adventurer")




