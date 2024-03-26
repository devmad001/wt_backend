import os
import sys
import codecs
from datetime import datetime
import json
import re

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")

from flask import Flask, render_template, send_from_directory, request, jsonify
from flask_cors import CORS

sys.path.insert(0,LOCAL_PATH+"../../")
from w_mindstate.mindstate import Mindstate
from w_utils import get_priority_keys
from help_format_timeline import help_add_colors


from get_logger import setup_logging
logging=setup_logging()


#0v3# JC  Oct 11, 2023 Include geo map (view here because 'timeline' widget area)
#0v2# JC  Oct  4, 2023 Pass data via parenty front-end or now, direct during generation
#0v1# JC  Sep 25, 2023 Init

"""
    OBSERVABLE DROP-IN FOR MAIN TIMELINE
    ++ MAP!
    - watch doing self-servered static files
"""

### CONFIG
dashboard_name='Timeline'
config_file=LOCAL_PATH+'../../'+'w_config_dashboard.json'

def load_config():
    global config_file
    DASH={}
    
    with open(config_file, 'r') as fp:
        CONFIG = json.load(fp)
    DASH=CONFIG['dashboards']['timeline'] # Timeline

    return CONFIG,DASH

CONFIG,DASH=load_config()

print("dashboard:", DASH)
PORT=int(DASH['port'])

app = Flask(__name__, static_url_path='/nonexistentstatic', static_folder='static', template_folder='templates')

CORS(app)  #Allow CORS so that parent html can adjust iframe height


# Function to format date
def format_date(record, date_key=''):
    """
    Format date to 'dd-mmm-yy'. Accepts str or datetime.
    """
    ## STEP 1:  choose date key
            
    if date_key in record:
        date=record[date_key]
        if isinstance(date, datetime):
            try: the_date=date.strftime('%d-%b-%y')
            except:
                logging.info("[warning] could not understand datetime: "+str(date))
                the_date=date
            return the_date
        elif isinstance(date, str):
            try:
                # Attempt to parse string to datetime and format
                return datetime.strptime(date, '%Y-%m-%d %H:%M:%S').strftime('%d-%b-%y')
            except ValueError:
                # Handle other date string formats if necessary
                print(f"Warning: Could not parse date string {date}")
                return date  # Or return a default value/format
        else:
            print(f"Warning: Unexpected date type {type(date)} for date {date}")
            return str(date)  # Or return a default value/format
    else:
        return ''

@app.route('/')
def index():
    ## Upgrade to accept case_id and session_id
    # Set by app_parenty.py loaded in parenty index.html
    # similar to square (serve_ui_flask), accessible here to pass forwards
    
    case_id = request.args.get('case_id')
    session_id = request.args.get('session_id')
    print ("CASE: "+str(case_id))
    
    ## Load multimodal response for Mind
    
    ### LOAD DATA FOR TIMELINE
    #- fields are specific to expected format for UI.
    #- requires mapping for now
    Mind=Mindstate()
    sesh,session_id,is_created=Mind.start_or_load_session(case_id=case_id)
    
    last_answer_meta=Mind.get_field(session_id,'last_answer_meta')
    # logging.info("GOT: "+str(last_answer_meta.get('multimodal',{}).get('timeline',{})))
    tdata=[]
    if last_answer_meta:
        try:
            tdata=last_answer_meta.get('multimodal',{}).get('timeline',{})
        except:
            logging.info("[no multimodal for timeline]: "+str(last_answer_meta))
    
    """
     [{'transaction_date': Timestamp('2021-12-02 00:00:00'), 'filename_page_num': 1, 'case_id': 'case_o3_case_single', 'transaction_description': 'Cash Concentration Transfer Credit From Account 000000659097338 Trn: | 0.35 | 0037720300Xf', 'versions_metadata': '{"transaction_method": "llm_markup-transaction_type_method-", "transaction_type": "llm_markup-transaction_type_method-"}', 'transaction_type': 'book_transfer', 'algList': ['create_ERS'], 'statement_id': 'case_o3_case_single-2021-12-01-000000373171278-Continuum Chase statement 1278 Dec 2021.pdf', 'transaction_method': 'other', 'account_id': 'case_o3_case_single-000000373171278', 'account_number': '000000373171278', 'id': 'ae836b3e6ae849de15534241df4c74c37b9f6bc09a47ed31e45a823a54155b54', 'section': 'Deposits and Credits', 'filename': 'Continuum Chase statement 1278 Dec 2021.pdf', 'transaction_amount': 0.35}]
     """
     
    ### RAW MAP
    
    ### SOURCE PRIORITY FIELDS (generic way)
    date_key,amount_key,name_key=get_priority_keys(tdata)
    logging.info("[priority keys] date_key: "+str(date_key)+" amount_key: "+str(amount_key)+" name_key: "+str(amount_key))

    timeline_data=[]
    for record in tdata:
        keep_it=True

        # Re-map the fields in each record
        # Parse the transaction_date string into a datetime object
        # Reformat the transaction_datetime to your desired format
        org_date=record.get(date_key,'')
        formatted_date = format_date(record,date_key=date_key)
        
        ## Format amount
        try:
            amount = record.get(amount_key, 0)
            #patch remove $
            if isinstance(amount, str):
                amount = amount.replace('$', '')
            amount_float = float(amount) if isinstance(amount, str) and amount.replace('.', '', 1).isdigit() else amount
            formatted_amount = f"${amount_float:.2f}"

            if int(amount_float)==0:
                logging.info("[info] skip zero amount")
                keep_it=False

        except Exception as e:
            logging.error("[warning] could not format amount for timeline given record: "+str(record)+' err: '+str(e))
            formatted_amount=0

        name_key_value = record.get(name_key, '')
        
        # Check if any word in name_key_value is longer than 20 characters
        ## *** patch avoid any keys as title
        if any(len(word) > 30 for word in name_key_value.split()):
            name_key_value = ''
#D1        logging.info("USING name key value: "+str(name_key_value))

        
        rr = {
            "Bank Name, City, State": f"{name_key_value}, Elkhart, KS",
            "Closing Date": formatted_date,  # You might need to format this date
            "Approx. Asset (Millions)": formatted_amount,
            "Press Release (PR)": "PR-058-2023",
            "Approx. Deposit (Millions)": "$130.00",  # Add logic for mapping this field
            "Acquirer & Transaction": f"Dream First Bank, National Association, to assume all deposits and xxx assets.",
            name_key: name_key_value
        }

        ## KEEP IT?
        #- if not serializable and amount is 0 then skip
        try: json.dumps(rr)
        except:
            logging.info("[info] skip row not json serializeable: "+str(rr)+" ORG DATE: "+str(org_date))
            keep_it=False

        #ALT    formatted_date=str(formatted_date) #json serializeable
        if str(formatted_amount)=="0" or str(formatted_amount)=="$.0.00":
            logging.info("[info] skip zero amount")
            keep_it=False

        if not keep_it:
            continue

        print ("DDD: "+str(formatted_date)+" am: "+str(formatted_amount))

        # Add the processed record to timeline_data
        timeline_data.append(rr)
        
    ### Add colors to timeline data
    timeline_data=help_add_colors(timeline_data,name_key,amount_key,date_key)
    #^^ record['color']='#d2d2d2'

    print ("SERVING COUNT: "+str(len(timeline_data)))
    print ("SERVING COUNT: "+str(timeline_data))

    
    # Dummy timeline_data dictionary (Replace this with your actual data)
    timeline_data_ORG = [
        {
            "Bank Name, City, State": "REALTIME TEST DATA PASSED Heartland Tri-State Bank, Elkhart, KS",
            "Press Release (PR)": "PR-058-2023",
            "Closing Date": "28-Jan-23",
            "Approx. Asset (Millions)": "$139.00",
            "Approx. Deposit (Millions)": "$130.00",
            "Acquirer & Transaction": "Dream First Bank, National Association, to assume all deposits and assets.",
        },
        # ... other records
    ]

    # Convert the Python dictionary to a JSON string
    timeline_data_json = json.dumps(timeline_data)

    # Passing case_id, session_id, and timeline_data to the template
    return render_template('index.html', case_id=case_id, session_id=session_id, timeline_data=timeline_data_json)




@app.route('/static/<path:filename>')
def serve_static(filename):
    print("Serving:", filename)

    if filename.endswith('.js'):
        response = send_from_directory('static', filename)
        response.headers['Content-Type'] = 'application/javascript'
        return response
    return send_from_directory('static', filename)

########################
#  MAP
########################
#- see x_maps/flask_serve_map.py

@app.route("/map/get_pois")
@app.route("/get_pois")
def get_pois():
    case_id = request.args.get('case_id')
    session_id = request.args.get('session_id')
    print ("CASE: "+str(case_id))
    
    ## Load multimodal response for Mind
    
    ### LOAD DATA FOR TIMELINE
    #- fields are specific to expected format for UI.
    #- requires mapping for now
    Mind=Mindstate()
    sesh,session_id,is_created=Mind.start_or_load_session(case_id=case_id)
    
    last_answer_meta=Mind.get_field(session_id,'last_answer_meta')
    # logging.info("GOT: "+str(last_answer_meta.get('multimodal',{}).get('timeline',{})))
    mdata=[]
    if last_answer_meta:
        try:
            mdata=last_answer_meta.get('multimodal',{}).get('map',{})
        except:
            logging.info("[no multimodal for map]: "+str(last_answer_meta))
    
    """
     [{'Latitude':0,'Longitude':0,'Name':'','Info':''}]
     """
    print ("[debug raw mdata]: "+str(mdata))

    poi_data = {
        'type': 'FeatureCollection',
        'features': [
            {
                'type': 'Feature',
                'geometry': {
                    'type': 'Point',
                    'coordinates': [-123.115898, 49.295868] # Example coordinates
                },
                'properties': {
                    'title': 'POI 1',
                    'description': 'Description for POI 1'
                }
            },
            #... Add more POIs as necessary
        ]
    }
    poi_data['features']=[]
    for point in mdata:
        print ("GIVEN: "+str(point))
        dd={}
        dd['type']='Feature'
        dd['geometry']={}
        dd['geometry']['type']='Point'
        dd['geometry']['coordinates']=[point['Longitude'],point['Latitude']]
        dd['properties']={}
        dd['properties']['title']=point.get('Name','')
        dd['properties']['description']=point.get('Info','')
        
        poi_data['features'].append(dd)
        
    # front checks if data, if non it won't try to plot map
    if not poi_data['features']:
        poi_data={}

    return jsonify(poi_data)
 
     
     
@app.route("/map")
def map_view():
    case_id = request.args.get('case_id')
    session_id = request.args.get('session_id')
    return render_template("index_here_map_async.html", case_id=case_id, session_id=session_id)



if __name__ == "__main__":
    app.run(host='0.0.0.0',debug=True, port=PORT)







