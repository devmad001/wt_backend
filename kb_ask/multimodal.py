import os
import sys
import time
import codecs
import datetime
import json
import re
import uuid

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")

from w_storage.gstorage.gneo4j import Neo
from w_storage.ystorage.ystorage_handler import Storage_Helper
from kb_answer import QA_Session_Answers

from get_logger import setup_logging
logging=setup_logging()


#0v3# JC  Jan 28, 2024  Allow transaction id in dynamic timeline response
#0v2# JC  Oct 11, 2023  Map data
#0v1# JC  Oct  3, 2023  Init

"""
    Allow to respond in multimodal
    - 
    Normal flow: Bot_Interface() -> kb_ask.py interface_kb_ask()

    Multi flow:
    - get cypher response as normalized df
    - split into various dict flavors of response
    (org see kb_answer.py for dev options)
    
    Approach:
    - kb_ask imports this state

"""

## GENERAL PRIVATE
#[ ] combine with kb_answer.py -> HIDE_SPECIAL_HEADERS
PRIVATE_REGEX=[r'entity.*id',r'versions.*metadata',r'account.*id']
PRIVATE_REGEX+=[r'case.*id',r'Alg.*List']
PRIVATE_REGEX+=[r'Alg List']
PRIVATE_REGEX+=[r'algList']
#need id for check merge# PRIVATE_REGEX+=[r'^id$']
#need id for check merge# PRIVATE_REGEX+=[r'\.id$']


class MultiModal_Response():
    #** similar to KB_AI_Agent() but focused on multimodal

    ## keep simple like dict
    def __init__(self):
        self.QA_Answers=QA_Session_Answers()
        self.responses={}
        self.cypher_used=None
        return
    
    def remove_private_data_headers(self,jsonl):
        global PRIVATE_REGEX
        # Compile the regular expressions into a single regex pattern for efficiency
        
        # Iterate through the list of dictionaries and filter each one
        cleaned_jsonl = []
        for record in jsonl:
            cleaned_record={}
            for kkey in record:
                keep_key=True
                for reg in PRIVATE_REGEX:
                    if re.search(reg,str(kkey),flags=re.I):
                        keep_key=False
                if keep_key:
                    cleaned_record[kkey]=record[kkey]
            cleaned_jsonl+=[cleaned_record]
        return cleaned_jsonl

    def remove_private_df_headers(self,df):
        global PRIVATE_REGEX
        if df is None: return df
        # Combine the regular expressions into a single regex
        combined_regex = '|'.join(PRIVATE_REGEX)
        
        if df is not None:
            # Filter the DataFrame's columns based on the combined regex
            columns_to_drop = df.filter(regex=re.compile(combined_regex, re.I), axis=1).columns
            print ("[debug] dropping columns: ",columns_to_drop)
            print ("[debug] all      columns: ",df.columns)
            # Drop the identified columns and return the result
            return df.drop(columns=columns_to_drop)
        else:
            return df
    
    def note_cypher_used(self,cypher):
        self.cypher_used=cypher
        return
    
    def set_data_response(self,data_response):
        # Recall:  Neo.run_stmt_to_data
        self.responses['jsonl']=data_response
        return

    def set_df_response(self,df):
        # From new Neo.run_stmt_to_normalized   
        self.responses['df']=df
        return
    
    def set_human_readible_response(self,human_readible):
        ## Typically, an error message for chat
        self.responses['human_readible']=human_readible
        return
    
    def set_chatbot_response(self,chatbot_txt):
        self.responses['chatbot']=chatbot_txt
        return
    
    def get_multimodal_response(self):
        #[ ] beware: long processing time (10s for NAV)
        logging.info("[info] at get_multimodal_response()")

        ## return dict of responses
        dd={}
        dd['human_readible']=self.responses.get('human_readible',None)
        dd['jsonl']=self.responses.get('jsonl',[])
        dd['df']=self.responses.get('df',None)

        #[x] fast
        dd['df_filtered']=self.remove_private_df_headers(self.responses.get('df',None))
        dd['chatbot']=self.responses.get('chatbot',None)  #set during end of responses
        
        ## Data frame to output format translator
        #[ ] beware long
        stimer=time.time()
        answers=QA_Session_Answers().dump_answers(dd['df'],dd['df_filtered'])
        print ("[debug] time to dump answers: ",time.time()-stimer)

        # Direct map so obvious
        dd['barchart']=answers.pop('barchart','')
        dd['timeline']=answers.pop('timeline','')
        dd['html']=answers.pop('html','')
        dd['html_data']=answers.pop('html_data','')
        dd['map']=answers.pop('map','')
        
        ## CHECK ALL DUMPED
        answers.pop('df','') #Don't want unless maybe json
        if answers:
            logging.info("[info] missed answers: %s",answers.keys())
        
        #self.responses.update(dd)
        
        #>> see kb_ask.py
        return dd
    
    def broadcast_multimodal_response(self):
        ## Broadcast to all listeners (aka mind state)
        #* recall, output is passed as answer dict through wt_brain -> Bot_interface & cached there for broadcast!
        response=self.get_multimodal_response()
        
        return


def dev1():
    return

if __name__=='__main__':
    branches=['dev1']

    for b in branches:
        globals()[b]()


"""
"""
