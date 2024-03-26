import os
import sys
import codecs
import json
import re
import requests
from configparser import ConfigParser

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")
sys.path.insert(0,LOCAL_PATH+"../../")

from w_utils import am_i_on_server

from w_chatbot.wt_brains import Bot_Interface

#0v1# JC Nov 24, 2023  Setup

"""
    TODO:  ADD THIS TO FORMAL TESTS
    
    FUNCTIONAL STYLE OF TEST FOR QUESTIONT TO META CACHE
    - doing this as part of adding html_data which also needs to be cached

"""




def test_question_to_cache():
    
    case_id='chase_3_66_5ktransfer' #[x] 
    case_id='MarnerHoldingsB'
    
    
    question='Show me all transactions'
    
    ## Via BOT  [ ] so is this a bot test?
    
    Bot=Bot_Interface()
    Bot.set_case_id(case_id)
    output,meta=Bot.handle_bot_query(question)
    
    #  dict_keys(['run_id', 'question', 'case_id', 'rating', 'cypher', 'llm_query_make_cypher', 'data_response', 'df', 'data_response_token_length', 'run_time', 'multimodal', 'response', 'the_date'])
    print ("META KEYS: "+str(meta.keys()))

    # MULTIMODAL KEYS: dict_keys(['human_readible', 'jsonl', 'df', 'df_filtered', 'chatbot', 'barchart', 'timeline', 'html', 'html_data', 'map', 'idict'])
    print ("MULTIMODAL KEYS: "+str(meta['multimodal'].keys()))
    
    # Check html_data
    if not 'html_data' in meta['multimodal']:
        raise Exception("ERROR: NO HTML DATA")
    
    print ("[html_data]: "+str(meta['multimodal']['html_data']))

    return



if __name__=='__main__':
    branches=['test_question_to_cache']
    
    for b in branches:
        globals()[b]()


"""

"""
