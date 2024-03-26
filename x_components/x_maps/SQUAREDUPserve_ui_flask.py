import os
import sys
import codecs
import json
import re

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")
from w_mindstate.mindstate import Mindstate


from flask import Flask, render_template, send_from_directory, request
from flask_cors import CORS

from get_logger import setup_logging
logging=setup_logging()


#0v1# JC  Oct  4, 2023  Init

"""
    CENTRALIZED UI COMPONENTS
    - for use in various dashboards views
    - for use in various widgets
    
  NOTES:
  - timeline + chatbot are stand-alone not included here

"""

### CONFIG
config_file=LOCAL_PATH+'../'+'w_config_dashboard.json'
def load_config():
    global config_file
    DASH={}
    with open(config_file, 'r') as fp:
        CONFIG = json.load(fp)
    DASH=CONFIG['dashboards']['square']
    return CONFIG,DASH
CONFIG,DASH=load_config()
print("dashboard:", DASH)
PORT=int(DASH['port'])
app = Flask(__name__, static_url_path='/nonexistentstatic', static_folder='static', template_folder='templates')
CORS(app)  #Allow CORS so that parent html can adjust iframe height

@app.route('/square')
def index():
    return render_template('square1.html')

@app.route('/static/<path:filename>')
def serve_static(filename):
    print("Serving:", filename)
    if filename.endswith('.js'):
        response = send_from_directory('static', filename)
        response.headers['Content-Type'] = 'application/javascript'
        return response
    return send_from_directory('static', filename)

def local_load_multimodal(case_id):
    ## Can access via api or module
    Mind=Mindstate()
    sesh,session_id,is_created=Mind.start_or_load_session(case_id=case_id)
    
    answer_dict=Mind.get_field(session_id,'last_answer_meta')

    return Mind,session_id,answer_dict

@app.route('/dynamic_square')
def dynamic_html():
    html='No html found - empty Square'

    ## Case + auth
    case_id = request.args.get('case_id')
    session_id = request.args.get('session_id')
    print ("CASE: "+str(case_id))

    
    ## Load from cache (mind state)
    Mind,session_id,answer_dict=local_load_multimodal(case_id)
    
    try: html=answer_dict.get('multimodal',{}).get('html','')
    except: html=''
    
    if not html:
        html="" #"- at session_id: "+str(session_id)
    
    return render_template('square_jinja1.html', dynamic_content=html)


sample_html_component="""
 <p><table class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th style = "background-color: #FFFFFF;font-family: Century Gothic, sans-serif;font-size: medium;color: #305496;text-align: left;border-bottom: 2px solid #305496;padding: 0px 20px 0px 0px;width: auto">Transaction Date</th>
      <th style = "background-color: #FFFFFF;font-family: Century Gothic, sans-serif;font-size: medium;color: #305496;text-align: left;border-bottom: 2px solid #305496;padding: 0px 20px 0px 0px;width: auto">Sender Name</th>
      <th style = "background-color: #FFFFFF;font-family: Century Gothic, sans-serif;font-size: medium;color: #305496;text-align: left;border-bottom: 2px solid #305496;padding: 0px 20px 0px 0px;width: auto">Transaction Amount</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td style = "background-color: #D9E1F2;font-family: Century Gothic, sans-serif;font-size: medium;text-align: left;padding: 0px 20px 0px 0px;width: auto">2021-12-01</td>
      <td style = "background-color: #D9E1F2;font-family: Century Gothic, sans-serif;font-size: medium;text-align: left;padding: 0px 20px 0px 0px;width: auto">Integrated Call Center Solutions</td>
      <td style = "background-color: #D9E1F2;font-family: Century Gothic, sans-serif;font-size: medium;text-align: left;padding: 0px 20px 0px 0px;width: auto">3000000.0</td>
    </tr>
    <tr>
      <td style = "background-color: white; color: black;font-family: Century Gothic, sans-serif;font-size: medium;text-align: left;padding: 0px 20px 0px 0px;width: auto">2021-12-02</td>
      <td style = "background-color: white; color: black;font-family: Century Gothic, sans-serif;font-size: medium;text-align: left;padding: 0px 20px 0px 0px;width: auto"></td>
      <td style = "background-color: white; color: black;font-family: Century Gothic, sans-serif;font-size: medium;text-align: left;padding: 0px 20px 0px 0px;width: auto">0.35</td>
    </tr>
    <tr>
      <td style = "background-color: #D9E1F2;font-family: Century Gothic, sans-serif;font-size: medium;text-align: left;padding: 0px 20px 0px 0px;width: auto">2021-12-07</td>
      <td style = "background-color: #D9E1F2;font-family: Century Gothic, sans-serif;font-size: medium;text-align: left;padding: 0px 20px 0px 0px;width: auto">Integrated Call Center Solutions</td>
      <td style = "background-color: #D9E1F2;font-family: Century Gothic, sans-serif;font-size: medium;text-align: left;padding: 0px 20px 0px 0px;width: auto">1500000.0</td>
    </tr>
    <tr>
      <td style = "background-color: white; color: black;font-family: Century Gothic, sans-serif;font-size: medium;text-align: left;padding: 0px 20px 0px 0px;width: auto">2021-12-08</td>
      <td style = "background-color: white; color: black;font-family: Century Gothic, sans-serif;font-size: medium;text-align: left;padding: 0px 20px 0px 0px;width: auto">Integrated Call Center Solutions</td>
      <td style = "background-color: white; color: black;font-family: Century Gothic, sans-serif;font-size: medium;text-align: left;padding: 0px 20px 0px 0px;width: auto">7500000.0</td>
    </tr>
    <tr>
      <td style = "background-color: #D9E1F2;font-family: Century Gothic, sans-serif;font-size: medium;text-align: left;padding: 0px 20px 0px 0px;width: auto">2021-12-08</td>
      <td style = "background-color: #D9E1F2;font-family: Century Gothic, sans-serif;font-size: medium;text-align: left;padding: 0px 20px 0px 0px;width: auto">JPMorgan Chase Bank NA</td>
      <td style = "background-color: #D9E1F2;font-family: Century Gothic, sans-serif;font-size: medium;text-align: left;padding: 0px 20px 0px 0px;width: auto">502094.95</td>
    </tr>
  </tbody>
</table></p>
"""
if __name__ == "__main__":
    app.run(host='0.0.0.0',debug=True, port=PORT)
    

"""

"""
