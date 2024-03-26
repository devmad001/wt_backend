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

from ideal_answers.ideal_g20 import GET_tip_regex_description

from get_logger import setup_logging
logging=setup_logging()


#0v1# JC  Nov  7, 2023  Init



"""
    IDEAL ANSWER FLOW
    - guiding answers, prompts, and cypher
    - iterative refinements, and user feedback

    - The current kb_ask flows is fine (ie checks if empty vars.  But better to acknowledge (here) all opportunities for refinement.
    )

"""


class Ideal_Answer():
    ## Flow to get ideal answer
    def __init__(self):
        self.question=''
        return
    
    def set_question(self,question):
        self.question=question
        return
    
    def run_standard_QnA_flow(self):
        return
    
    def thumbs_up_down(self,answer_id='',thumbs_up=None):
        return
    
    def llm_prompt_additions_bullets(self):
        given_keyword_to_schema_name_suggestions=[]
        data_frequency_suggestions=[]  #most related to main_account node (node account counts)

        return

    def llm_prompt_additions_cypher(self):
        related_question_cypher_answers=[]
        return
    
    def get_cypher_from_prompt(self):
        # prompt -> LLM -> cypher
        return
    def get_cypher_from_function(self):
        ## NOTE USED BUT COULD ie:
        # do_description_regex('TERM')
        return
    
    def q50_list_questions(self):
        return
    def question_to_50q_matches(self):
        # 50Q
        return
    def q50_list_human_thought_process(self):
        # how would a human answer this
        return
    def q50_get_written_cypher(self,q50_id,include_sample_answer=False):
        return
    
    def evaluate_response(self):
        return

    def decision_redo_flow(self,suggest_path=[]):
        # Try again but more guilded answer flow
        return
    
    def user_set_specific_question(self,question='',meta={}):
        return
    
    def user_list_questions(self):
        return
    
    def manage_db_storage(self):
        #sql etc.
        return
    
    def manage_multimodal(self):
        # barchart
        # chart title (axis + legends + colors)
        return
    
    def get_tips(self):
        tips={}
        tips['regex_description']=GET_tip_regex_description() # bullet points str
        return tips
    
    ## TWO-STAGE QUERIES ie: short query and retry longer if not found  (ie/ expect recursive flow)


def dev_ideal_answer():
    ## Stand alone useage
    #- apply to specific case.
    IA=Ideal_Answer()
    ## Current endpoint ping
    ## Route through this branch
    
    return

def dev_local_Bot_Interface(question,case_id):
    from w_chatbot.wt_brains import Bot_Interface
    
    allow_cached=False
    Bot=Bot_Interface()
    Bot.set_case_id(case_id)
    answer,answer_dict=Bot.handle_bot_query(question,params={},allow_cached=allow_cached)

    return answer,answer_dict

def call_ideal_answer():
    ## Recall Bot_Interface
    case_id='case_atm_location'
    question='How many transactions?'

    print ("> answer via normal branch")
    print ("CASE ID: "+str(case_id))
    print ("QUESTION: "+str(question))
    answer,answer_dict=dev_local_Bot_Interface(question,case_id)
    print ("ANSWER: "+str(answer))

    print ("> answer via ideal answer   ?watch context transfer")

    return

def dev2():
    print ("1.  qq dictionary   question_table") #<-- boring but important

    print ("2.  Programattic memory and suggestions:  have gpt self evaluate + know when its' a hard question etc.  And, even write its own cypher query")
    print ("3.  Thumbs up/down for 3rd party tuning")
    

    print ("misc recall challenge:  understanding the main_account node")

    ## ALL THE WAYS TO EXTEND ANSWER UNDERSTANDING (capture below but)::
    
    ## FOR EACH 50Q QUESTION:
    
    # ID,ORG_DESC,[variations on question text],[question_id_tag], [llm helpers] [cypher_query], [evaluate answer], [recursive refine]
    
    qq={}
    qq['id']='q1'
    qq['org_desc']='How many transactions?'
    qq['variations']=['How many transactions?','How many transactions','How many transactions are there?']
    qq['question_id_tag']='q1_how_many_t'
    qq['llm_helpers']=['[llm_prompt] inject prompt bullets','[llm_prompt] inject Q&A cypher samples'] 
    qq['cypher_query']='match (n:main_account) return count(n)'
    qq['cypher_query_samples']=['match (n:main_account) return count(n)','match (n:main_account) return count(n) limit 1']
    qq['answer_score']=0.50
    qq['answer']='There are 100 transactions'
    qq['multimodal']={}

    #[1]   Collect X ways to ask the same question free text
    #[2]   Have questioin ID -> 50Q lookup?
    
    ### (this captured elsewhere but...)
    ## Pre-written cypher query
    ## LLM suggestive prompts

    #.
    #.
    #.
    #--> cypher query


    #> Collect X ways to answer the same question ??

    return


def dev1():
    
    ### CURRENT Q&A FLOW IS FINE
    ### ENCHANCED FLOW BECOMES STATE MACHINE OR OWN ABSTRACT CLASS
    #- easy to track and run alone
    #- 
    
    
    ## Related TASKS:
    tasks=[]
    tasks+=['add title to charts (via llm)']
    tasks+=['shivam do we use user id']
    
    ## QA
    qa_qa_tracking=[]
    qa_qa_tracking+=['easy query all Q&A']
    qa_qa_tracking+=['estimate quality or performance']
    qa_qa_tracking+=['thumbs up/down for feedback on quality']

    
    ### ACTION FOCUSED ON ANSWER HELPERS:
    top_answer_helpers=[]
    top_answer_helpers+=['match to known question (50Q)']
    top_answer_helpers+=['check response and retry']
    top_answer_helpers+=['[llm_prompt] inject prompt bullets']
    top_answer_helpers+=['[llm_prompt] inject Q&A cypher samples']
    top_answer_helpers+=['spawn aside alg']
    
    ### GUILDED ANSWER FLOW  (partial match 50q)
    match_thoughts=[]
    match_thoughts+=['jon to list cypher query for each question']
    match_thoughts+=['UI for user help to select or guilde their question']

    
    ## The single question
    user_free_text_question=''
    all_possible_questions=[]
    q50_target_questions=[]
    
    advanced_paths=[]

    ##  NORMAL PATH
    normal_path=['question','llm_prompt','llm','cypher_exe','llm_summary','multi_modal']
    

    ## ADVANCED PATH
    #[a]  Does question match existing 50q target question?
    advanced_paths+=['Does given question match 50q target question?']
    advanced_paths+=['Does match have a human interpreted thought process?']
    advanced_paths+=['Does match have a sample|direct cypher query and response? (for injection)']
    

    ### BIGGEST INSIGHT RESOLUTION IS:  question > cypher > response

    ## LLM PROMPT STANDARD
    #- just the schema
    #- default  bullet points

    ## LLM PROMPT AUGMENTATION
    #- via bullet points
    #- via sample question with response
    #- via sample data (ie/ main_account involvements)

    advanced_paths+=['Can we augment the cypher prompt via (x,y,z)']
    advanced_paths+=['cypher augment [x]: if alternate keyword then rephrase to known schema ie: outflows == main_account debit']
    

    ## ADVANCED PATH:  CHECK RESPONSE DOES IT MAKE SENSE
    advanced_paths+=['Does response make sense?']
    advanced_paths+=['Redo response decision point']


    return




if __name__=='__main__':
    branches=['dev1']
    branches=['call_ideal_answer']

    for b in branches:
        globals()[b]()


"""
"""
