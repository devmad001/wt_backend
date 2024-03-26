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


    ## Marners
    data_url='https://core.epventures.co/api/v1/case/MarnerHoldingsB/timeline_dynamic_data?user_id=6571b44088061612aa2fc807&fin_session_id=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2NTcxYjQ0MDg4MDYxNjEyYWEyZmM4MDciLCJlbWFpbCI6ImJpc2RldnQwMEBnbWFpbC5jb20iLCJpYXQiOjE3MDg0MzUzODQsImV4cCI6IjIwMjQtMDItMjFUMDE6MjM6MDQuMDAwWiJ9.6b2dca1cb1be314cb62abfdf7ed2472a58d2d2cccf88848194b6302a460c6641'

    
    ## Nav Case:
    data_url='https://core.epventures.co/api/v1/case/65a8168eb3ac164610ea5bc2/timeline_dynamic_data?user_id=6571b44088061612aa2fc807&fin_session_id=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2NTcxYjQ0MDg4MDYxNjEyYWEyZmM4MDciLCJlbWFpbCI6ImJpc2RldnQwMEBnbWFpbC5jb20iLCJpYXQiOjE3MDg0MzUzODQsImV4cCI6IjIwMjQtMDItMjFUMDE6MjM6MDQuMDAwWiJ9.6b2dca1cb1be314cb62abfdf7ed2472a58d2d2cccf88848194b6302a460c6641'

    data_url='http://127.0.0.1:8008/api/v1/case/65a8168eb3ac164610ea5bc2/timeline_dynamic_data?user_id=6571b44088061612aa2fc807&fin_session_id=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2NTcxYjQ0MDg4MDYxNjEyYWEyZmM4MDciLCJlbWFpbCI6ImJpc2RldnQwMEBnbWFpbC5jb20iLCJpYXQiOjE3MDg0MzUzODQsImV4cCI6IjIwMjQtMDItMjFUMDE6MjM6MDQuMDAwWiJ9.6b2dca1cb1be314cb62abfdf7ed2472a58d2d2cccf88848194b6302a460c6641'
    
    
    return render_template('timeline_index_v3.html',data_url=data_url)


@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)

if __name__ == "__main__":
    app.run(debug=True,port=3000)
    


"""
"""