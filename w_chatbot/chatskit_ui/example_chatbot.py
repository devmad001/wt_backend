print ("streamlit run example_chatbot.py --server.port 8082")
import os,sys
import time

import streamlit as st
from streamlit_chat import message
import requests

import configparser as ConfigParser

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)


#0v4# JC  Sep 14, 2023  Option for WT.
#0v3# JC  Apr 14, 2023  Step through normal run and upgrade to 1.21
#0v2# JC  Feb  9, 2023  Config + fix clearing of input


# NOTES:
#- recall, this is run on every input so global session state variable only


#REF
    #https://github.com/AI-Yash/st-chat
    #https://share.streamlit.io/ai-yash/st-chat/main/examples/chatbot.py
    #API_URL = "https://api-inference.huggingface.co/models/facebook/blenderbot-400M-distill"

USE_LOCAL_FLASK=True

## CONFIGS
Config = ConfigParser.ConfigParser()
Config.read(LOCAL_PATH+"../config_chatgpt.ini")
flask_service=Config.get('main_server','flask_service')
flask_port=Config.get('main_server','flask_port')

## FLASK
#- recall:  python flasK_chat.py
if USE_LOCAL_FLASK:
    pass
FLASK_ENDPOINT=flask_service+":"+flask_port



if not 'nt' in os.name: #patch bug
    st.set_page_config(
        page_title="ChatsKit",
        page_icon=":robot:"
    )
    ##  st.header("BuildingScience.ca Bot")
    ##  st.markdown("[Homepage](https://buildingscience.ca)")
    
## Parameters and url paths
# BASE URL CONFIG:
#~/streamlit/config.toml:
#[server]
#baseUrlPath = "/tool/streamlit"

## Normalize path since var1=value turns into var1=[value]
params={}
temp_params = st.experimental_get_query_params()
for kkey in temp_params:
    params[kkey]=temp_params[kkey][0] #Assume take first
print ("[debug got query: "+str(params))


## Remove made with streamlit
hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True) 


if 'generated' not in st.session_state:
    st.session_state['generated'] = []

if 'past' not in st.session_state:
    st.session_state['past'] = []


### ** comment out sub / routes and use parameters instead
#D1# ## Get path for internal logic
#D1# # Get query parameters from URL
#D1# params = st.experimental_get_query_params()
#D1# # Get path from query parameters
#D1# path = params.get('path', ['/'])[0]
#D1# print ("GOT PATH: "+str(path))
#D1# 
#D1# def option_a():
#D1#     #DEMO
#D1#     return
#D1# 
#D1# ## Wildcard routes
#D1# #Define app routes
#D1# routes = {
#D1#     '/option_a': option_a,
#D1#     '/': lambda: st.write('Main page'),
#D1#     '/(.*)': lambda path: st.write(f'At path: {path}')
#D1#     #'/(.*)': lambda path: st.write(f'Path not found: {path}')
#D1# }


def query(payload):
    response = requests.post(API_URL, headers=headers, json=payload)
    if response:
        try:
            rr=response.json()
        except Exception as e:
            rr={'error':'bad_response_1003'}
    else:
        rr={'error':'bad_response_from_internal_flask_query_endpoint'}
    return rr

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


def query_chatskit(query):
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
        
        dd=response.json()
    
        output['generated_text']=dd['generated_text']

    return output

if user_input:

    output=query_chatskit(user_input)
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
    

## Recreate message flow
# STYLES: https://dicebear.com/styles
# https://github.com/AI-Yash/st-chat/blob/8ac13aa3fdf98bacb971f24c759c3daa16669183/streamlit_chat/__init__.py#L24

if 'generated' in st.session_state:

    for i in range(len(st.session_state['generated'])-1, -1, -1):
        message(st.session_state["generated"][i], key=str(i), avatar_style="bottts")
        message(st.session_state['past'][i], is_user=True, key=str(i) + '_user',avatar_style="adventurer")








