import os
import sys
import codecs
import json
import re

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")

from pypher import __, Pypher
from w_storage.gstorage.gneo4j import Neo
from w_llm.llm_interfaces import OpenAILLM

from get_logger import setup_logging
logging=setup_logging()


#0v1# JC  Sep  6, 2023  Init


class LLM_Query_Engine:
    # Use LLM and neo4j connection
    def __init__(self):
        self.LLM=OpenAILLM()
        return

    def ask_graph(self,prompt,verbose=False):
        response=self.prompt(prompt)
        if verbose:
            print ("Response: "+str(response))
        ## Inter response
        for dd in Neo.iter_stmt(response):
            ## Auto clean
            if isinstance(dd,list) and len(dd)==1:
                dd=dd[0]
            yield dd
        return

    def prompt(self,prompt):
        response=self.LLM.prompt(prompt)
        response=self._auto_clean_response(response)
        return response

    def _auto_clean_response(self,response):
        ## ie/ ````
        cleaned=[]
        state_opened=False
        state_closed=False
        pattern=r'\`\`\`'
        for liner in response.split('\n'):
            if re.search(pattern,liner) and state_opened:
                state_closed=True
                break
            elif re.search(pattern,liner) and not state_opened:
                state_opened=True #don't capture first line
            elif state_opened:
                cleaned.append(liner)
            else:
                pass
    
        resp=''
        if cleaned and state_closed:
            cleaned='\n'.join(cleaned)
        else:
            cleaned=response
        return cleaned


def dev1():
    prompt=""" Write a cypher query to find all nodes with a given label """
    prompt=""" Write a cypher query to find all nodes where parameter case='case_1' """
    """
    R: MATCH (n:Node)
    WHERE n.case = 'case_1'
    RETURN n
    """
    prompt=""" Write a cypher query to find all nodes the node parameter 'case' has value 'case_1' """

    LLM=OpenAILLM()
    response=LLM.prompt(prompt,try_cache=True)

    print ("R: "+str(response))

    ## Inter nodes
    for dd in Neo.iter_stmt(response):
        print ("cypher insert response> "+str(dd))


    return

def dev2():
    prompt=""" Write a cypher query to find all nodes the node parameter 'case' has value 'case_1' """
    prompt=""" Write a cypher query iterate over all nodes"""

    prompt=""" Can you provide a Cypher query to retrieve all nodes with a case_id of 'case_1'? """
    """
    Response: MATCH (n)
    WHERE n.case_id = 'case_1'
    RETURN n
    """

    break_at=10
    LQE=LLM_Query_Engine()
    c=0
    for dd in LQE.ask_graph(prompt,verbose=True):
        c+=1
        print ("> "+str(dd))
        if c>break_at:
            break
    return

if __name__=='__main__':
    branches=['dev1']
    branches=['dev2']
    for b in branches:
        globals()[b]()


"""
  ## CLEAN (get from quotes)
    cleaned=[]
    state_opened=False
    state_closed=False
    pattern=r'\`\`\`'
    for liner in response.split('\n'):
        if re.search(pattern,liner) and state_opened:
            state_closed=True
            break
        elif re.search(pattern,liner) and not state_opened:
            state_opened=True #don't capture first line
        elif state_opened:
            cleaned.append(liner)
        else:
            pass

    resp=''
    if cleaned and state_closed:
        cleaned='\n'.join(cleaned)
    else:
        cleaned=response
    return cleaned
"""
