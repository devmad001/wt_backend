import os
import sys
import codecs
import json
import re

from sqlalchemy.orm import Session

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")
sys.path.insert(0,LOCAL_PATH+"../..")

from c_macros.m_cypher.macro_butterfly_waterfall import interface_get_waterfall
from c_macros.m_cypher.macro_butterfly_waterfall import interface_get_butterfly

from service_test_data.chart_case_data_v1 import get_butterfly_data_sample
from service_test_data.chart_case_data_v1 import get_waterfall_data_sample

from get_logger import setup_logging
logging=setup_logging()


        
#0v1# JC Nov 23, 2023  Setup


"""
    NEW GRAPH DATA ENDPOINTS
    - butterfly
    - waterfall
   *recall, pending a bit on full account resolution 
   
   See files for more details:
   - grabs:  Entity -- DEBIT_FROM --> transaction -- CREDIT_TO --> Entity

"""

def generate_waterfall_graph_data(case_id):
    if case_id=='case_chart_data_v1':
        return get_waterfall_data_sample(case_id),{}

    data,meta=interface_get_waterfall(case_id)
    
    return data,meta

def generate_butterfly_graph_data(case_id):
    if case_id=='case_chart_data_v1':
        return get_butterfly_data_sample(case_id),{}
    data,meta=interface_get_butterfly(case_id)
    return data,meta


if __name__=='__main__':
    branches=['dev1']
    for b in branches:
        globals()[b]()

