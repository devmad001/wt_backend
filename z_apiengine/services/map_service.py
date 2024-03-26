import os
import sys
import codecs
import json
import re

from fastapi import FastAPI

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")

sys.path.insert(0,LOCAL_PATH+"../..")

from w_mindstate.mindstate import Mindstate


from get_logger import setup_logging
logging=setup_logging()


        
#0v1# JC Nov  5, 2023  Setup


"""
    MAP     SERVICES
"""

def remove_words_more_then_20_chars(text):
    text = re.sub(r'\b\w{20,}\b', ' ', text)
    text=re.sub(r'\|', ',', text)  #replace pipe with comma
    text=re.sub(r', ,', ',', text)
    text=re.sub(r'[\s]+', ' ', text)
    return text

def load_map_poi_features(case_id):
    
    # Load multimodal response for Mind
    Mind = Mindstate()
    sesh, session_id, is_created = Mind.start_or_load_session(case_id=case_id)
    
    last_answer_meta = Mind.get_field(session_id, 'last_answer_meta')
    mdata = []
    if last_answer_meta:
        try:
            mdata = last_answer_meta.get('multimodal', {}).get('map', {})
        except:
            logging.info("[no multimodal for map]: " + str(last_answer_meta))

#D2    print("[debug raw mdata]: " + str(mdata))

    poi_data = {
        'type': 'FeatureCollection',
        'features': []
    }

    for point in mdata:
#D2        print("GIVEN: " + str(point))
        
        ## CLEAN MAP DATA
        description=point.get('Info','')
        description=remove_words_more_then_20_chars(description)
        
        dd = {
            'type': 'Feature',
            'geometry': {
                'type': 'Point',
                'coordinates': [point['Longitude'], point['Latitude']]
            },
            'properties': {
                'title': point.get('Name', ''),
                'description': description
            }
        }
        poi_data['features'].append(dd)
    
    # If no features, return empty response
    if not poi_data['features']:
        logging.info("[map_service] no features found for case_id: " + str(case_id))
        poi_data = {}

    return poi_data

#def load_map_html_view(case_id):
#    return html_view
    
if __name__=='__main__':
    branches=['dev1']
    for b in branches:
        globals()[b]()


"""
"""