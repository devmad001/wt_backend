import time
import os
import sys
import codecs
import json
import re

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"..")

from get_logger import setup_logging


from w_llm.llm_interfaces import OpenAILLM

logging=setup_logging()



#0v1# JC  Sep  2, 2023  Init


"""
    VALIDATE CYPHER AND COMMON MODS
"""

CYPHER_SAMPLE_1="""
    MERGE (z:Payer {name:"Zelle", id:"case_1_Zelle", case_id:"case_1"})
MERGE (r1:Recipient {name:"Lil Bro Alex", id:"case_1_Lil Bro Alex", case_id:"case_1"})
CREATE (z)-[p1:PAYMENT_TO {
    case_id: "case_1",
    transaction_id: "Jpm674243402",
    transaction_description: "Zelle Payment To Lil Bro Alex Jpm674243402",
    transaction_amount: 200.00,
    transaction_date: date("2021-08-09")
}]->(r1)

MERGE (r2:Recipient {name:"Remote Online Deposit", id:"case_1_Remote Online Deposit", case_id:"case_1"})
CREATE (z)-[p2:PAYMENT_TO {
    case_id: "case_1",
    transaction_id: "1",
    transaction_description: "Remote Online Deposit",
    transaction_amount: 200.00,
    transaction_date: date("2021-08-26")
}]->(r2)
"""

def mod_cypher_add_node_property(given,add_dict,overwrite=True):
    meta={}
    new=''
    raise Exception("Not implemented since id merge with name in sample")

    ## Assumptions:
    #1)  defined on one complete line
    if not ')' in given:
        return new,meta
    #2) no nested parenthesis
    #3) don't overwrite
    if not overwrite: raise Exception("Not implemented no overwrite")

    # Using a regex pattern to identify key-value pairs
    pattern = r'(?P<key>\w+): "(?P<value>[^"]+)"'

    matches = re.findall(pattern, liner)
    if matches:
        # Converting matches into a dictionary
        dd = {key: value for key, value in matches}

        ## ADD id to node
        if not 'id' in dd:
            if dd.get('name',''):
                dd['id']=case_name+"_"+dd.get('name','')
            else:
                dd['id']=case_name+"_"+str(uuid.uuid4())  #Randomize or base on description
#D                print("D: " + str(dd))

        ## ADD case_id to node
        dd['case_id']=case_name

        ## UPDATE NODE DEFINITION DICT

        cypher_no_quote_keys_str=', '.join([f'{key}:"{value}"' for key, value in dd.items()])

        new_liner=re.sub(r'\{.*','',liner)+"{"+cypher_no_quote_keys_str+"}"+")"

    return given

def dev1():
    samp=CYPHER_SAMPLE_1
    new=mod_cypher_add_node_property(samp)
    return

if __name__=='__main__':
    branches=['dev1']

    for b in branches:
        globals()[b]()




"""
"""
