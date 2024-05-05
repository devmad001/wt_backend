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

import langchain
from llm_interfaces import OpenAILLM


#0v1# JC  Jan 15, 2024  Stand-alone


"""
    'TEST' for LLM
    - [ ] migrate to unit test once features confirmed
"""

## Unit test
class TestLLM(unittest.TestCase):
    
    def test_langchain_version(self):
        lanchain_version=langchain.__version__
        # requirements_dev:  langchain==0.0.287
        # Jon local dev:       VERSION: 0.0.305
        # Test that <= 0.0.305
        # Suggest why version less
        self.assertTrue(lanchain_version <= "0.0.305", "langchain version is less than 0.0.305 (frozen about Sept 2023)")
        
        return

    def test_basic_llm_query(self):
        given="Hello, how are you?"
        LLM=OpenAILLM(model_name='gpt-4')
        response=LLM.prompt(given,try_cache=False)
        
        self.assertTrue(response)

        print ("LLM TEST GIVEN: "+str(given))
        print (" response> "+str(response))
        
        return

    ### llm_interfaces
    ## Test openai config
    ## Test langchain version
    ## Test llm_interface query
    ## Test llm_interface query with cache
    


def dev1():

    ## UNUSED
    given="Hello, how are you?"
    LLM=OpenAILLM(model_name='gpt-4')
    response=LLM.prompt(given,try_cache=False)
    
    print ("LLM TEST GIVEN: "+str(given))
    print (" response> "+str(response))

    LLM.refresh_llm()

    print ("LLM TEST GIVEN: "+str(given))
    print (" response> "+str(response))

    
    return


def dev2():
    print ("Test langchain libraries etc.")
    lanchain_version=langchain.__version__
    print ("VERSION: "+str(lanchain_version))
    # requirements_dev:  langchain==0.0.287
    # Jon local dev:       VERSION: 0.0.305
    
    # Test that <= 0.0.305
    assert lanchain_version <= "0.0.305"
    
    return

if __name__=='__main__':
    if False:
        branches=['dev2']
        for b in branches:
            globals()[b]()
    else:
        unittest.main()






