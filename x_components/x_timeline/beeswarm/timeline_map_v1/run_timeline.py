import os,sys
import re
import json
from flask import Flask, send_from_directory, render_template, request

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"

sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")
sys.path.insert(0,LOCAL_PATH+"../../")
sys.path.insert(0,LOCAL_PATH+"../../../")


#0v1# JC Jan  8, 2024  Shared timeline


"""
    LEAN VIEW OF STAND ALONE TIMELINE
"""

app = Flask(__name__, static_folder='.', static_url_path='')


@app.route('/')
def index():
    case_id = request.args.get('case_id')
    session_id = request.args.get('session_id')
    print ("CASE: "+str(case_id))
    if not case_id:
        case_id='65858e0c198ceb69d5058fc3' #well_fargo_1_10.pdf
    
    ## POINT TO NEW API CORE
    if True: #ON_LIVE_SERVER:
        data_url='https://core.epventures.co/api/v1/case/'+case_id+'/timeline_data'
    else:
        data_url='http://127.0.0.1:'+str(CONFIG['dashboards']['api_core']['port'])+'/api/v1/case/'+case_id+'/timeline_data'

    timeline_version='timeline_index_v1.html'
    return render_template(timeline_version,data_url=data_url)


@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)

if __name__ == "__main__":
    app.run(debug=True,port=5177) #5177 opened for cors
    