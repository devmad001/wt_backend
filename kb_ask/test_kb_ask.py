import time
import os
import sys
import codecs
import copy
import json
import re
import unittest

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")


from kb_ask.kb_ask import KB_AI_Agent 
from kb_ask.kb_ask import AI_handle_kb_question


#0v1# JC  Mar  8, 2024  Stand-alone


"""
    Local test for kb_ask
    (ideally move into test section but not yet ready)

"""

class TestKBASK(unittest.TestCase):

    def test_kb_ask_query(self):
        return



def dev1():

    ## VIA class:
    Agent=KB_AI_Agent()
    
    #> question to cypher
    #** fix bug where cypher response is NOT a string if openai fails
    case_id='case_atm_location' #Hardcode
    question="How many transactions are there?"
    cypher,llm_query,meta=Agent.question_to_cypher(question,case_id)
    
    print ("GOT cypher: "+str(cypher))


    if False:
        ## Via interface:
        #Agent = KB_AI_Agent()
        answer,meta,Agent=AI_handle_kb_question(question,case_id,Agent=None)
    
    return



if __name__=='__main__':
    if True:
        branches=['dev1']
        for b in branches:
            globals()[b]()
    else:
        unittest.main()






