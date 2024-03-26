name_of_file=__file__.split('/')[-1]
print ("python -m streamlit run "+name_of_file+" --server.port 8082")

import os,sys
import time
import re
import requests

import html
import uuid

import streamlit as st   #pip install streamlit
from streamlit_chat import message

from streamlit_feedback import streamlit_feedback

import configparser as ConfigParser

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)



#localhost:8082/case/case_1/chat


#1v1# JC  Nov 30, 2023  New v1
#1v0# JC  Nov 18, 2023  add .streamlit/config.toml  > disallow dark theme (safari)
#0v9# JC  Nov 12, 2023  Integrate pip install streamlit-feedback
#0v8# JC  Nov 10, 2023  Migrate to fast_main
#0v7# JC  Nov  1, 2023  Various UI layout adjustments (bigger chat and better spacing)
#0v6# JC  Sep 26, 2023  js to main page
#0v5# JC  Sep 14, 2023  INSTALL REQUIREMENTS:
#                               pip install streamlit_chat==0.0.2.1 
#                               NOT pip install streamlit_chat==0.1.1
#0v4# JC  Sep 14, 2023  Option for WT.
#0v3# JC  Apr 14, 2023  Step through normal run and upgrade to 1.21
#0v2# JC  Feb  9, 2023  Config + fix clearing of input


#NOTES:
#- recall, this is run on every input so global session state variable only
# https://chatbot.epventures.co?case_id=chase_S3_A&amp;session_id=wfrix&amp;user_id=wo0sd8

#REF:
# 
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

## Hardcode AVATARS
BOT_AVATAR='https://core.epventures.co/static/wt_logo_blue_transparent.png'
USER_AVATAR='https://core.epventures.co/static/1x1.png'


COLLECT_FEEDBACK=True
ON_LIVE_SERVER=True
if os.name=='nt': ON_LIVE_SERVER=False

### CHAT_SUPPORT_ENDPOINT
CHAT_SUPPORT_ENDPOINT='https://core.epventures.co' #<-- migrate wt_flask_handle to fast_main
if not ON_LIVE_SERVER:
    CHAT_SUPPORT_ENDPOINT='127.0.0.1:8008' #<-- migrate wt_flask_handle to fast_main
print ("[CHAT_SUPPORT_ENDPOINT (for streamlit)] at: "+str(CHAT_SUPPORT_ENDPOINT))

## Patch
if not re.search(r'^http',CHAT_SUPPORT_ENDPOINT,flags=re.I):
    CHAT_SUPPORT_ENDPOINT='http://'+CHAT_SUPPORT_ENDPOINT

##########################


def optional_patches():
    nott=calledd
        # Hide header banner and hamburger
        #st.markdown(""" <style> 
        ##MainMenu {visibility: hidden;}
        #footer {visibility: hidden;}
        #</style> """, unsafe_allow_html=True)
    return

def apply_patches():

    ###1/   SET PAGE TITLE & ICON
    if False: #must be called first and conflicts with streamlit-feedback
        st.set_page_config(
            page_title="WTKit",
            page_icon=None
        )

    if not 'nt' in os.name: #patch bug (? which?)
        #    page_icon=":robot:"
        ##  st.header("WatchTower Bot")
        ##  st.markdown("[Homepage](https://watchtower.ca)")
        pass

    ###2/   Remove made with streamlit
    hide_streamlit_style = """
                <style>
                #MainMenu {visibility: hidden;}
                footer {visibility: hidden;}
                </style>
                """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True) 
    
    ###3/   Hide red linear gradient at top of window
    hide_decoration_bar_style = '''
    <style>
        header {visibility: hidden;}
    </style>
    '''
    st.markdown(hide_decoration_bar_style, unsafe_allow_html=True)
    
    ###4/   Font family
    # Define and inject custom font-family styling
    st.markdown("""
    <style>
        body, h1, h2, h3, h4, h5, p, li, label {
            font-family: "Inter", Sans-serif !important;
        }
    </style>
    """, unsafe_allow_html=True)

    ###5/   Hide both bot icons (can turn off user but bottt remains so hide)
    #[ ] does not work maybe cause dynamic?
    st.markdown("""
        <style>
        img[alt="profile"] {
            display: none !important;
        }
        </style>
        """, unsafe_allow_html=True)

    #6/   Retry on newer streamlit
    st.markdown("""
        <style>
        .avatar {
            display: none !important;
        }
        </style>
        """, unsafe_allow_html=True)


    ##7/  Remove excess white space at top of chat window
    # left at 5rem is 80px?
    st.markdown("""
        <style>
               .block-container {
                    padding-top: 1rem;
                    padding-bottom: 0rem;
                    padding-left: 10%;
                    padding-right: 10%;
                }
        </style>
        """, unsafe_allow_html=True)

    ##8/  Move chat box up to top (there's a strange stVerticalBlock with 1rem gap but 5px gap is better)
    st.markdown("""
    <style>
        [data-testid="stVerticalBlock"] {
            gap: 5px !important;
        }
    </style>
    """, unsafe_allow_html=True)

    ##9/  More space after input box  (was shrunk because of #7)
    st.markdown("""
    <style>
        .stTextInput {
            padding-bottom: 30px !important;
        }
    </style>
    """, unsafe_allow_html=True)

    return
    
#iframe    st.markdown('<script>alert("Hello")</script>', unsafe_allow_html=True)

apply_patches()


#https://discuss.streamlit.io/t/injecting-js/22651/5
#https://stackoverflow.com/questions/67977391/can-i-display-custom-javascript-in-streamlit-web-app
def run_javascript(source: str) -> None:
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
"""+"alert('Hello');"
#run_javascript('alert("Hello");')
#run_javascript(longjs)



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
print ("[debug] streamlit query params: "+str(params))

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

    input_text = st.text_input("You ask: ","", key=KEY) #on_change
    
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

def query_wt_chat_handler(query,params={}):
    global CHAT_SUPPORT_ENDPOINT
    response={}

    print ("[debug] query: "+str(query)+" params: "+str(params))

    do_query=True
    
    if query in ['Every time?','Hello, how are you?']: do_query=False

    output={}
    output['generated_text']='Still ready for a question...'
    
    if do_query:
        #flask_endpoint='http://10.8.18.29:5005'
        #flask_endpoint='http://192.168.0.25:5005'
        #url=flask_endpoint+"/ask?query="+query
        #url=flask_endpoint+"/ask?query="+query&topic=buildingscience
        
        if params:
            # Nov 10; new format to fast_main.py
            # http://127.0.0.1:8008/api/v1/case/case_atm_locations/square
            params_urlencoded=''
            for kkey in params:
                params_urlencoded+='&'+str(kkey)+'='+str(params[kkey])
            url=CHAT_SUPPORT_ENDPOINT+"/api/v1/case/"+params.get('case_id','')+"/ask?query="+query+params_urlencoded
        else:
            url=CHAT_SUPPORT_ENDPOINT+"/ask?query="+query

        ## Pass streamlist parameters to flask handler  (allow it to do ALL routing)
        if params:
            for kkey in params:
                url+='&'+str(kkey)+'='+str(params[kkey])

        with st.spinner("Thinking..."):
            retries=2
            got_response=False
            while retries>0 and not got_response:
                retries-=1
                try:
                    response = requests.get(url) #, headers=headers, json=payload)
                    got_response=True
                except Exception as e:
                    print("[warning] could not query streamlit flask handler... (immediate retry): "+str(e))
            
            try:
                dd=response.json()
            except Exception as e:
                #DEV# logging.warning("[non json back from flask: "+str(response))
                dd={}
    
        ## Local patch, possible list [{}]
        if isinstance(dd,list):
            #print ("[debug] raw got: "+str(dd))
            dd=dd[0]

        try:

            output['generated_text']=dd.get('generated_text',"Oops, I've lost connection to the server: "+str(response.text))
            #extra=' [debug] url: '+str(url)
            #output['generated_text']+=extra
        except:
            output['generated_text']=dd.get('generated_text',"Oops, I've lost connection to the server")

    print ("[streamlit output: "+str(output))
    return output


#########################
#  ON USER INPUT
#########################
#
if user_input:
    output=query_wt_chat_handler(user_input,params=params)
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
#  COLLECT FEEDBACK
###############################
#def _submit_feedback(*args,**kwargs): #user_response, emoji=None):
#print ("SESSION STATE: "+str(st.session_state))

#** broken won't call so manually look at session state
def _submit_feedback(user_response):
    """_summary_
    _submit_feedback:
    """
    print ("HANDLE FEEDBACK: "+str(user_response))
    stopp=isgood
    return
    st.toast(f"Feedback submitted: {user_response}", icon=emoji)
    return user_response.update({"some metadata": 123})

## CUSTOM EXTRACT!
def parse_feedback_from_session_state():
    feedback_data = []

    # Get the last question and answer, if available
    last_question = st.session_state.get('past', [])[-1] if 'past' in st.session_state and st.session_state['past'] else None
    last_answer = st.session_state.get('generated', [])[-1] if 'generated' in st.session_state and st.session_state['generated'] else None

    # Iterate through each item in the session state
    for key, value in st.session_state.items():
        # Check if the key contains feedback data
        if isinstance(value, dict) and 'type' in value and value['type'] == 'thumbs':
            # Extract the thumbs value and optional text
            thumbs_icon = value.get('score')
            optional_text = value.get('text')

            # Convert the thumbs icon to a numerical value: 1 for thumbs up, 0 for thumbs down
            thumbs_value = 1 if thumbs_icon == '👍' else 0 if thumbs_icon == '👎' else None

            # Append the feedback data to the list along with question and answer
            feedback_data.append({
                'key': key, 
                'thumbs': thumbs_value, 
                'text': optional_text, 
                'question': last_question, 
                'answer': last_answer
            })


    return feedback_data

# Example usage:
feedback_results = parse_feedback_from_session_state()
print ("CUSTOM FEEDBACK: "+str(feedback_results))

def submit_user_feedback(feedback, params={}):
    global CHAT_SUPPORT_ENDPOINT
    response = {}

    # Extract case_id from params and construct the feedback submission URL
    case_id = params.get('case_id', '')
    if case_id:
        url = f"{CHAT_SUPPORT_ENDPOINT}/api/v1/case/{case_id}/submit_feedback"
    else:
        # Fallback URL if case_id is not provided
        url = f"{CHAT_SUPPORT_ENDPOINT}/api/v1/submit_feedback"

    # Additional URL parameters (excluding case_id)
    additional_params = {k: v for k, v in params.items() if k != 'case_id'}
    if additional_params:
        params_urlencoded = '&'.join([f'{key}={value}' for key, value in additional_params.items()])
        url += f"?{params_urlencoded}"

    # Prepare the payload with feedback
    payload = {'feedback': feedback}

    # Attempt to send the feedback to the server
    try:
        response = requests.post(url, json=payload)
        #no# response = requests.request("POST",url,json=payload)
        response.raise_for_status()  # Raise an exception for HTTP errors
        return response.json()  # Return the server's response as JSON
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except Exception as e:
        print(f"Error occurred while submitting feedback: {e}")

    return {'error': 'Failed to submit feedback'}

if feedback_results:
    submit_user_feedback(feedback_results, params=params)
    

###############################
#  REFRESH STATE OF MESSAGES
##############################
#
## Recreate message flow
# STYLES: https://dicebear.com/styles
# https://github.com/AI-Yash/st-chat/blob/8ac13aa3fdf98bacb971f24c759c3daa16669183/streamlit_chat/__init__.py#L24

if 'generated' in st.session_state:
    c=-1
    for i in range(len(st.session_state['generated'])-1, -1, -1):  #Step in reverse
        c+=1

        #, logo='https://raw.githubusercontent.com/dataprofessor/streamlit-chat-avatar/master/bot-icon.png') #bottts

        if ON_LIVE_SERVER:
            ## SERVER STREAMLIT VERSION accepts logo url!
    
            ## 1/  BOT
            message(st.session_state["generated"][i], key=str(i), avatar_style=None, logo=BOT_AVATAR) #Bot
            if c==0 and COLLECT_FEEDBACK:
                feedback = streamlit_feedback(
                    feedback_type="thumbs",
                    optional_text_label="[Optional] Please provide an explanation",
                    key=str(uuid.uuid4()),
            #broke so custom#                    on_submit=_submit_feedback
                )
            ## 2/  USER
            message(st.session_state['past'][i], is_user=True, key=str(i) + '_user',avatar_style=None, logo=USER_AVATAR) # USER
        else:

            ## 1/  BOT
            message(st.session_state["generated"][i], key=str(i), avatar_style=None)
            if c==0 and COLLECT_FEEDBACK:
                feedback = streamlit_feedback(
                    feedback_type="thumbs",
                    optional_text_label="[Optional] Please provide an explanation",
                    key=str(uuid.uuid4()),
            #broke so custom#                    on_submit=_submit_feedback
                )
            ## 2/  USER
            message(st.session_state['past'][i], is_user=True, key=str(i) + '_user',avatar_style=None) #adventurer



## OPTIONS FOR SESSIONS (use get_query_params instead)
#import streamlit as st
#from streamlit_javascript import st_javascript
#url = st_javascript("await fetch('').then(r => window.parent.location.href)")
#st.write(url)
#
#SESSION params are maybe (_session_mgr not future proof
#        import streamlit as st
#        import urlib.parse
#        sessions = st.runtime.get_instance()._session_mgr.list_active_sessions()
#        req = st.runtime.get_instance()._session_mgr.get_active_session_info(sessions[0]).request
#        joinme = (req.protocol, req.host, "", "", "", "")
#        my_url = urllib.parse.urlunparse(joinme)
#        )
#
