import os,sys
import re
import json
from flask import Flask, send_from_directory, render_template, request


LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"

sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")
sys.path.insert(0,LOCAL_PATH+"../../")
sys.path.insert(0,LOCAL_PATH+"../../../")

from w_utils import am_i_on_server

#0v1# JC Oct 27, 2023  Setup


"""
    LEAN FLASK for d3 dev
    - but, also deploy to server option so use ocnfig

"""

ON_LIVE_SERVER=False
if am_i_on_server():
    ON_LIVE_SERVER=True

## CONFIG FOR BROADCASTS
config_file=LOCAL_PATH+'../../../'+'w_config_dashboard.json'
def load_config():
    global config_file
    with open(config_file, 'r') as fp:
        CONFIG = json.load(fp)
    return CONFIG
CONFIG=load_config()


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
    
    
    ## POINT TO NEW API CORE
    if ON_LIVE_SERVER:
        data_url='https://core.epventures.co/api/v1/case/'+case_id+'/timeline_data'
    else:
        data_url='http://127.0.0.1:'+str(CONFIG['dashboards']['api_core']['port'])+'/api/v1/case/'+case_id+'/timeline_data'

    return render_template('index.html',data_url=data_url)


"""
run_obs.py ->> active timeline
- @ /*?case_id=xx
- recall, passed case_id + session_id
- loads mindstate
- formats or resolves keys
- adjusts titles
- preps data format for observable
- renders to observable template!

"""

@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)

if __name__ == "__main__":
    app.run(debug=True,port=5011)
    

"""
http://127.0.0.1:8008/api/v1/case/timeline/ColinFCB1/timeline_data

	
records	
0	
t	
filename_page_num	1
transaction_date	"2020-01-17"
account_number	"0010640417308"
transaction_amount	445.61
section	"Checks Paid"
label	"Transaction"
statement_id	"ColinFCB1-2020-01-01-0010640417308-Management-Properties-v-Brusko-Copy-of-First-Citizens-Bank-Checks-2020.pdf"
transaction_description	"Check No. 01-17"
account_id	"ColinFCB1-0010640417308"
filename	"Management-Properties-v-Brusko-Copy-of-First-Citizens-Bank-Checks-2020.pdf"
case_id	"ColinFCB1"
id	"ccbf71dc502d898ce8b4dad0d17d69e73343f0e590e1218516d30547c9d14fe8"
1	
t	
filename_page_num	1
transaction_date	"2020-01-14"
account_number	"0010640417308"
transaction_amount	639.56
section	"Checks Paid"
label	"Transaction"
statement_id	"ColinFCB1-2020-01-01-0010640417308-Management-Properties-v-Brusko-Copy-of-First-Citizens-Bank-Checks-2020.pdf"
transaction_description	"Check No. 10124"
account_id	"ColinFCB1-0010640417308"
filename	"Management-Properties-v-Bru

"""


"""

    function placeCirclesSIDEOVERLAP(group, direction) {
        let indices = d3.range(group.length)
            .sort((a, b) => d3.ascending(group[a].priority, group[b].priority));
        indices.forEach((index, order) => (group[index].order = order));

        for (let index of indices) {
            let intervals = [];
            let circle = group[index];
            for (let step of [-1, 1])
                for (let i = index + step; i > -1 && i < group.length; i += step) {
                    let other = group[i];
                    let dist = Math.abs(circle.x - other.x);
                    let radiusSum = circle.r + other.r;
                    if (dist > circle.r + Math.max(circle.r, other.r)) break;
                    if (other.y === Infinity || dist > radiusSum) continue;
                    let offset = Math.sqrt(radiusSum * radiusSum - dist * dist);
                    intervals.push([other.y - offset, other.y + offset]);
                }
            let y = 0;
            if (intervals.length) {
                intervals.sort((a, b) => d3.ascending(a[0], b[0]));
                let candidate = 0;
                for (let [lo, hi] of intervals) {
                    if (direction > 0 && candidate + circle.r + 1 <= lo) break;
                    if (direction < 0 && candidate - (circle.r + 1) >= hi) break;
                    if (direction > 0 && hi >= 0) candidate = hi + 1;
                    if (direction < 0 && lo <= 0) candidate = lo - 1;
                }
                y = candidate;
            }
            group[index].y = y;
        }

        let maxRadiusCircle = group.find(circle => circle.r === d3.max(group, d => d.r));
        let referenceLineY;

        let maxRadius = d3.max(group, d => d.r);
        const gap = maxRadius + 18;
        for (let circle of group) {
            circle.y += direction * gap;
        }

        return gap;

    }

"""