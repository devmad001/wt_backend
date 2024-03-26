import os,sys
import re
import json
from flask import Flask, send_from_directory, render_template, request


LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"

sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")
sys.path.insert(0,LOCAL_PATH+"../../")
sys.path.insert(0,LOCAL_PATH+"../../../")

#from w_utils import am_i_on_server

#0v1# JC Nov 16, 2023  Setup


"""
"""

ON_LIVE_SERVER=False
#if am_i_on_server(): ON_LIVE_SERVER=True

## CONFIG FOR BROADCASTS
config_file=LOCAL_PATH+'../../../'+'w_config_dashboard.json'
def load_config():
    global config_file
    with open(config_file, 'r') as fp:
        CONFIG = json.load(fp)
    return CONFIG
CONFIG=None#load_config()


#app = Flask(__name__, static_url_path='')
app = Flask(__name__, static_folder='.', static_url_path='')

def local_case2data(case_id):
    global CONFIG
    #** unlick run_obs.py the formatted data comes directly from API core
    #- however, recall mindstate needs to be on API core side!
    #data_file=LOCAL_PATH+'../../../'+'w_data/'+case_id+'/case_data.json'
    #with open(data_file, 'r') as fp:
    #    data = json.load(fp)
    return data

@app.route('/')
def index():
    global CONFIG,ON_LIVE_SERVER
     
    case_id = request.args.get('case_id')
    session_id = request.args.get('session_id')
    print ("CASE: "+str(case_id))
    
    if not case_id:
        case_id='ColinFCB1'
    
    data_url='http://127.0.0.1:5012/static/state-population-2010-2019.tsv'
    data_url='http://127.0.0.1:5012/static/butterfly_mock_data.csv' #3 column csv name,neg amount, pos amount

    return render_template('index_fisheye_1.html',data_url=data_url)


@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)

if __name__ == "__main__":
    app.run(debug=True,port=5012)
    


"""
"""