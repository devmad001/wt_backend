import os
import sys
import time
import codecs
import json
import re
import uuid
import pandas as pd
import hashlib

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity


LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")

from w_storage.gstorage.gneo4j import Neo

from w_storage.ystorage.ystorage_handler import Storage_Helper
from w_llm.embeddings_model import Embeddings_Model

from get_logger import setup_logging
logging=setup_logging()

Storage=Storage_Helper(storage_dir=LOCAL_PATH+"../w_datasets")
Storage.init_db('guided_questions')

print ("[ ] TODO:  Pandas depreciation warning: @  self.guides = self.guides.append({'id': id, 'vector': vector}, ignore_index=True)")


#0v2# JC  Jan 10, 2024  Possible quota error now caught
#0v1# JC  Nov 11, 2023  Base


"""
    TEST ANSWERING
    - place into prompt after first attempt!
    - make the response route obvious
    - extend to decide on UI kind (timeline|map|barchart) view in multimodal
"""

### Notes on similarity
#- a rather nonsense question may have 0.74 similarity


def test_answering_objects():
    logging.info("[classes]")


    logging.info("> kb_ask.py --> KB_AI_Agent()")
    logging.info("    ^-> question to cypher, imports all below")
    logging.info("    ^-> Mindstate, Ideal_Answer, ")

    logging.info("> mindstate:  session state memory")

    logging.info("> kb_router.py handle_special_question_routing")
    logging.info("    ^-> special question to specific query (q13_total_inflows)")

    logging.info("> MultiModal_Response()")
    logging.info("   imports: QA_Session_Answers()")

    ## DO IMPORTS
    
    KBAI=KB_AI_Agent()
    
    print ("NOV 11:  New kb_answering_multimodal:  backend decides on UI kind (timeline|map|barchart) view in multimodal")

    
    return

def generate_hash(text):
    # Create a SHA-256 hash object
    sha256 = hashlib.sha256()
    # Update the hash object with the bytes-like object (text in bytes format)
    sha256.update(text.encode())
    # Return the hexadecimal representation of the hash
    return sha256.hexdigest()
    

class Question_Guide:
    global Storage

    def __init__(self):
        self.EM=Embeddings_Model()
        self.guides= pd.DataFrame(columns=['id', 'vector'])
        return
        
    def text2vector(self,text):
        try:
            embedding=self.EM.get_embedding(text)
        except:
            logging.error("[embeddings_model.py] Quota error at get embeddings")
            embedding=None
        return embedding
        
    def set_train_flavor1(self,qq):
        logging.info("set_train_flavor1")
        
        qq['v']=1  # question, better_question, cypher
        qq['id']=generate_hash(qq['question']+qq.get('better_question',''))
        if not 'question' in qq:
            raise Exception("Missing id|question|better_question: "+str(qq))
        
        ## Get or push
        org_qq=Storage.db_get(qq['id'],'train',name='guided_questions')

        vector=[]
        if org_qq:
            vector=org_qq.get('vector','')
            ## Pass as updates.
            org_qq.update(qq)
            qq=org_qq

        if not vector:
            vector=self.text2vector(qq['question'])
            
        if vector:
            qq['vector']=vector
            Storage.db_put(qq['id'],'train',qq,name='guided_questions')
        
        return
    
    def preload_guides(self):
        ## Load all guides
        ## Reverse index or, for now, just iterate
        for id in Storage.iter_database('guided_questions'):
            dd=Storage.db_get(id,'train',name='guided_questions')
            vector=dd['vector']
            # Append the vector and id to the DataFrame
            self.guides = self.guides.append({'id': id, 'vector': vector}, ignore_index=True)
        return


    def search_guide(self, text):

        # Convert the input text to a vector
        input_vector_list = self.text2vector(text) #Possible quota error downstream
        if not input_vector_list:
            return None,0

        input_vector = np.array(input_vector_list).reshape(1, -1)

        if self.guides is not None:
            # Prepare guide vectors for cosine similarity
            guide_vectors = np.array(self.guides['vector'].tolist())

            # Calculate cosine similarity with each guide vector
            similarities = cosine_similarity(guide_vectors, input_vector)

            # Find the index of the most similar guide
            most_similar_index = np.argmax(similarities)

            # Get the ID of the most similar guide
            similar_guide_id = self.guides.iloc[most_similar_index]['id']

            # Retrieve the data from storage using the ID
            similar_guide_data = Storage.db_get(similar_guide_id, 'train', name='guided_questions')
            
            sim_value=similarities[most_similar_index]
            logging.info("[better_question]  SIM VALUE: "+str(sim_value))

            return similar_guide_data, sim_value

        return None,0


def test_dev_question_guide():
    print ("Recall existing: kb_router [keyword]  handle_special_question_routing()")

    user_question=''
    
    ## Write direct Cypher match
    top_50q=[(['commonly_asked'],['better_asked'],['ideal_cypher'])]

    ## Also, ideal_answer approach
    
    phases=[]
    phases+=['one_match_freetext_to_commonly_asked'] #[ ] build this
    
    Guide=Question_Guide()
    
    return


def dev1():
    Guide=Question_Guide()
    
    b=[]
    b+=['touch_active_code']
    
    if 'touch_active_code' in b:
        print ("> kb_ask.ideal_answer.py -> framework for management")
        print ("> kb_router.py handle_special_question_routing")
        print ("     ^^ given keyword, run query?")

    return

def ALG_question2better_question(question,Guide=None):
    meta={}
    meta['start_time']=time.time()

    Guide=Question_Guide()
    Guide.preload_guides()
    dd,sim_value=Guide.search_guide(question)
    better_question=dd.get('better_question','')

    meta['run_time']=time.time()-meta['start_time']
    meta['sim_value']=sim_value
    return better_question,Guide,meta

def call_guided_question():

    question='blaaa, blaa nonsense and bad spelling?' #0.74 similarity
    question='where are the transactions?'
    question='List all the payee names with amounts'

    if 'local logic trial' in []:
        Guide=Question_Guide()
        Guide.preload_guides()
    
        dd,sim_value=Guide.search_guide(question)
        dd.pop('vector',None) #shh
        print ("GOT: "+str(dd))
        print ("FOR question: "+str(question))

    better_question,Guide,meta=ALG_question2better_question(question)

    print ("QUESTION: "+str(question))
    print ("BETTER QUESTION: "+str(better_question))
    print ("guided question>> "+str(meta))

#    better_question,Guide,meta=ALG_question2better_question(question,Guide=Guide)
#    print ("QUESTION: "+str(question))
#    print ("BETTER QUESTION: "+str(better_question))
#    print (">> "+str(meta))
#
    return
    

#####################################################
#  BETTER QUESTION  restatement
#####################################################
def ENTRYPOINT_train_guided_questions():
    
    #### RECALL:
    #- formal list of q50 is in given_q50.py -- add detailed notes there or specific question re-writing here
    
    
    ## - bullets are injected into the query prompt as general rules
    ## - better_questions are included at the end to more narrowly give a 'one shot style of example'
    ## - cypher   ""
    
    Guide=Question_Guide()
    
    case_id='case_X'
    
    ## Transactions for timeline
    qq={}
    qq['question']='show me the transactions'
    qq['better_question']='Show me all transactions including amount and date'
    qq['cypher']="MATCH (n:transaction { case_id: '"+case_id+"'}) RETURN n"
    Guide.set_train_flavor1(qq)

    ## Map locations?
    qq={}
    qq['question']="Show me where the ATMs are"
    qq['bullets']=['Transaction location is in the Processor.lat and Processor.lng']
    qq['cypher']="""MATCH (Transaction:Transaction {case_id: 'case_atm_location', transaction_method: 'atm'})-[:PROCESSED_BY]->(Processor:Processor)
    RETURN Processor.lat as ATM_Latitude, Processor.lng as ATM_Longitude"""
    Guide.set_train_flavor1(qq)

    ## Transaction locations are part of the Processor
    qq={}
    qq['question']="Show me where the transactions are on a map"
    qq['better_question']="Show me the Processor.lat and Processor.lng for all transactions"
    Guide.set_train_flavor1(qq)
    
    ### JON MANUAL TRAINING NOV 12, 2023
    #[ ] see ideal_g20 because should search with (?i) pattern so cypher suggestion is better
    qq={}
    qq['question']="List all payments to the IRS"
    qq['better_question']="List all transactions and total amounts where Payee.name CONTAINS 'IRS' or Transaction.transaction_description CONTAINS 'IRS'"
    Guide.set_train_flavor1(qq)
    
    ### Nov 18
    #    List all the sources of funds
    #Who sent money?
    #List the name of all Sender entities

    qq={}
    qq['question']="List all the sources of funds"
    qq['better_question']="List the name and amount of all Sender Entities"
    Guide.set_train_flavor1(qq)

    qq={}
    qq['question']="Who sent money?"
    qq['better_question']="List the name and amount of all Sender Entities"
    Guide.set_train_flavor1(qq)

    qq={}
    qq['question']="What is the payment ID on zelle transfers?"
    qq['better_question']="What is the Entity.id of the Payee with Payee name contains Zelle?"
    Guide.set_train_flavor1(qq)
    
    qq={}
    qq['question']="List all the payee names with the amounts"
    qq['better_question']="List all Entity.name that received funds"
    Guide.set_train_flavor1(qq)
    
    ## Strange one
    qq={}
    qq['question']="Show me the names of all payees and amounts"
    qq['better_question']="Show me the names of all payees and amount"   # !! SINGULAR! [ ] may need to include this in org prompt for amount hint
    Guide.set_train_flavor1(qq)

    ## Who sent money?
    

    ## GOOD QUESTIONS:
    #[ ] consider compiling good vs issue somewhere else.
    #G1 Show me the names of all payees and amounts where amount total is >20000
    
    #G2 Show me all transactions where money was sent to Armindo Freitas
    
    #G3 What are the total inflows
    # MATCH (Transaction:Transaction {case_id: 'MarnerHoldingsB', is_credit: True}) RETURN sum(Transaction.transaction_amount) as total_inflows
    
    #G4 Are there any recurring regular transaction amounts
    #>> frequency of amounts


    ## SOSO QUESTIONS:
    # WHere where the transactions -- does lat + long but may want full transaction details along with lat lng
    # [ ] also want hyperlinks on map

    
    logging.info("[done storing training data]")

    return


def local_run_query(query,case_id):
    rr,meta=Neo.run_query(query)
    print ("GOT: "+str(rr))
    return

def dev2():
    case_id='case_atm_locations'
    case_id='chase_3_66_5ktransfer'
    return


def try_qna():
    #Dev various
    from ideal_answers.ideal_g20 import dev_try_single_question
    
    #http://127.0.0.1:8008/api/v1/case/chase_3_66_5ktransfer/pdf/Chase%20Statements%203%2012.pdf?page=1&key=0da450fb3141c2097d1b60398886459aff428fe302cc3157f85d3599495fe956
    case_id='chase_3_66_5ktransfer'

    question='What is the total number of outflows via check?'
    question="What are the total inflows?"
    question="List the total outflows via wire transfer"

    question="Show me the names of all payees and amounts"

    dev_try_single_question(question=question,case_id=case_id)

    return



if __name__=='__main__':

    branches=['test_answering_objects']
    branches=['dev2']


    branches=['call_guided_question']

    branches=['try_qna']
    branches=['ENTRYPOINT_train_guided_questions']

    for b in branches:
        globals()[b]()








