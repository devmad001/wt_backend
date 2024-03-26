import sys,os
import re
import json
import copy
import uuid

from flask import Flask, request, Response, jsonify, send_file
from flask_cors import CORS

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)

from wt_brains import Bot_Interface

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

#CORS(app) 

#gunicorn_logger = logging.getLogger("gunicorn.error")
#app.logger.handlers = gunicorn_logger.handlers
#app.logger.setLevel(gunicorn_logger.level)


#0v3#  JC  Nov  1, 2023  **moved into fast_main & bot_router.py
#0v2#  JC  Oct  4, 2023  Other UX handler: button, etc
#0v1#  JC  Sep 14, 2023  WT option


"""
"""

@app.route('/case/<case_id>/view/submit', methods=['POST', 'GET'])
#@login_required
def handle_submit(case_id):
    """
    BUTTON CLICK OR SUBMIT HANDLER
    - Handles submissions for specific case_ids
    """
    output = {}
    
    # Authorization check: Ensure current user has access to case_id
#    if not user_has_access_to_case(current_user, case_id):
#        abort(403)  # Forbidden: The user doesn't have access to the resource

    query_param = request.args.get('query', default=None, type=str)

    if query_param:
        output['response'] = f'Received query parameter: {query_param} for case ID: {case_id}'
        Bot=Bot_Interface()
        Bot.set_case_id(case_id)
        output['generated_text'],meta=Bot.handle_bot_query(query_param, params=None)
        
    else:
        output['error'] = 'No query parameter provided'

    return jsonify(output)

def user_has_access_to_case(user, case_id):
    """
    Function to check if a user has access to a specific case_id.
    Implement your authorization logic here.
    """
    # Example: Check if user is the owner of the case or has admin privileges
    # This is just a placeholder. You need to implement the actual check based on your requirements.
    return user.is_admin or user.owns_case(case_id)


#@app.route('/ask', methods=['POST','GET']) #Remove slash
@app.route('/<path:path>', methods=['POST','GET'])
def handle_ask(path):
    """
        STANDARD CHATBOT QUESTION HANDLER
    """
    
    #[ ] authenticate user
    #[ ] authenticate case_id (session etc)

    ## Watch larger loads?
    Bot=Bot_Interface()

    query=''
    
#    if not user_has_access_to_case(current_user, case_id):
#        abort(403)  # Forbidden: The user doesn't have access to the resource

    params={}
    params=request.args.to_dict()
#    for kkey in request.args:
#        if not kkey=='query':
#            params[kkey]=request.args.get(kkey)

    path=re.sub(r'^\/','',path)
    path=re.sub(r'\/ask','',path)


    query=request.args.get('query','')

    print ("GOT PATH: "+str(path))
    print ("GOT params: "+str(params))
    print ("GOT query: "+str(query))
    
    session_id=params.get('session_id',None)
    case_id=params.get('case_id',None)
    
    if case_id:
        Bot.set_case_id(case_id)
    
    output={}
    if query and case_id:
        output['generated_text'],meta=Bot.handle_bot_query(query, params=params)
        try:
            pass
#            output['generated_text'],meta=Bot.handle_bot_query(query, params=params)
        except Exception as e:
            print ("[handle_bot_query openai maybe error]: "+str(e))
            if 'auth_subrequest_error' in str(e):
                output['generated_text']='auth_subrequest_error'
            else:
                output['generated_text']='Internal error 1008'
    else:
        output['generated_text']="You forgot to ask properly."

    print ("[done handle ask]: "+str(output))
    return jsonify(output)
                   


if __name__ == '__main__':
    # debug false cause large load
    PORT=5005
    app.run(host='0.0.0.0', port=PORT, debug=True)
        


"""
"""        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
