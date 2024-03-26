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

#from w_storage.gstorage.gneo4j import Neo
#from dev_kb_ask import get_graph_schema_str
#from multimodel import Multimodal_Response
#from w_storage.ystorage.ystorage_handler import Storage_Helper

from w_llm.llm_interfaces import LazyLoadLLM
from multimodal import MultiModal_Response

from get_logger import setup_logging
logging=setup_logging()



#0v1# JC  Oct  3, 2023  Setup

"""
    SPECIAL HANDLING OF QUESTIONS
    - predefined questions / answers
    - fallback?

"""

def dev1():
    return

def handle_non_topical_or_short_question(question):
    LLM = LazyLoadLLM.get_instance()  # Assuming LazyLoadLLM is a singleton class
    prompt="""
    You are an AI business analyst analyzing bank statement transactions.
    You are being asked a single question but believe that it is non-topical or too short to answer.
    Provide some default guildance to the user:
    - "Consider asking me to: list all transactions by date and amount"
    - "Consider asking me to: give you the total of all transactions"
    
    The question: """+str(question)+"""
    """
    logging.info("[dev] basic question prompt: "+str(prompt))
    txt_response = LLM.prompt(prompt)
    return txt_response


def handle_special_question_routing(question,case_id,Agent=None):
    is_done=False
    answer='[special question handling]'
    answer_dict={}
    #answer_dict['multimodal']=None #Multimodal.get_multimodal_response()
    Agent=None
    
    word_count_of_question=len(question.split(' '))

    ###
    
    if 'q13_total_inflows' in question:
        logging.info("[info]  SPECIAL QUESTION ROUTING:  q13_total_inflows")
        ## Hard code question
        ## Hard code answer source
        from v_questions.q30_questions import q13_total_inflows
        jsonl,df,qq,out_meta=q13_total_inflows(case_id=case_id)
        
        ## Gather answer into multimodal!
        Multimodal=MultiModal_Response()
        Multimodal.set_data_response(jsonl)
        Multimodal.set_df_response(df)
        
        answer='hard coded q13 response but this is stand-alone text'
        Multimodal.set_df_response(df)
        
        answer_dict['multimodal']=Multimodal.get_multimodal_response()

        is_done=True

    elif word_count_of_question<3:
        logging.info("[info]  SPECIAL QUESTION ROUTING:  TOO FEW WORDS: "+str(question))
        answer=handle_non_topical_or_short_question(question)
        # No multimodal
        is_done=True
        answer_dict={}

    

    return is_done,answer,answer_dict,Agent


def ENTRYPOINT_dev_force_question(question='',case_id='',Agent=None):
    # See v_ux/ux_user_frontend.py for normal flows
    is_done,answer,answer_dict,Agent=handle_special_question_routing(question,case_id,Agent=Agent)

    return is_done,answer,answer_dict,Agent


def dev_call_entrypoint():
    
    case_id='case_o3_case_single'
    question='q13_total_inflows'
    is_done,answer,answer_dict,Agent=ENTRYPOINT_dev_force_question(question=question,case_id=case_id)
    
    print ("ANSWER DICT: ",answer_dict)
    print ("="*40)
    print ("ANSWER HTML: ",answer_dict['multimodal']['html'])
    
    ## DEV FORCE UPDATE MIND STATE FOR FRONT-END VIEWS!
    from w_mindstate.mindstate import Mindstate
    Mind=Mindstate()
    sesh,session_id,is_created=Mind.start_or_load_session(case_id=case_id)
    
    #** answer_dict is not serializable with df so pickled downstream!
    Mind.MIND_store_last_answer_meta(answer_dict,session_id)
    
    print ("*dev: stored answer dict at session id: "+str(session_id))
    
    ## Load it back
    answer_dict=Mind.get_field(session_id,'last_answer_meta')
    
    print ("GOT BACK: "+str(answer_dict))

    return

if __name__=='__main__':
    branches=['dev1']
    branches=['dev_call_entrypoint']

    for b in branches:
        globals()[b]()




