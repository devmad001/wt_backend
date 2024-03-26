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

sys.path.insert(0,LOCAL_PATH+"..")

from llm_interfaces import OpenAILLM


#0v1# JC  Jan 15, 2024  Stand-alone


"""
    'TEST' for LLM
    - [ ] migrate to unit test once features confirmed
"""

## Unit test
class TestLLM(unittest.TestCase):

    def test_basic_llm_query(self):
        given="Hello, how are you?"
        LLM=OpenAILLM(model_name='gpt-4')
        response=LLM.prompt(given)
        
        self.assertTrue(response)

        print ("LLM TEST GIVEN: "+str(given))
        print (" response> "+str(response))
        
        return


def dev1():
    given="Hello, how are you?"
    LLM=OpenAILLM(model_name='gpt-4')
    response=LLM.prompt(given)
    
    print ("LLM TEST GIVEN: "+str(given))
    print (" response> "+str(response))

    LLM.refresh_llm()

    print ("LLM TEST GIVEN: "+str(given))
    print (" response> "+str(response))

    
    return

if __name__=='__main__':
    if False:
        branches=['dev1']
        for b in branches:
            globals()[b]()
    unittest.main()






