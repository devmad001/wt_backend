import os
import sys
import codecs
import json
import re
import ast
import math

from collections import OrderedDict

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")

from w_llm.llm_interfaces import OpenAILLM

from algs_extract import alg_resolve_to_date
#from a_query.cypher_helper import cypher_create_node
from a_query.cypher_helper import cypher_create_update_node
from a_query.cypher_helper import cypher_create_relationship

from w_storage.gstorage.gneo4j import Neo

from kb_ai.schemas.SCHEMA_kbai import gold_schema_definition

from get_logger import setup_logging
logging=setup_logging()


#0v5# JC  Feb 17, 2024  nan value getting through to neo4j cypher causes error
#0v4# JC  Feb 13, 2024  Catch exception on weird account name (Bad check formats?)... log error though
#0v3# JC  Oct  3, 2023  Upgrade: Statement node type
#0v2# JC  Sep 20, 2023  Create account via schema
#0v1# JC  Sep  8, 2023  Init

"""
    Create DB nodes and relationships from smart_extract_fields
"""
 
def local_run_query(stmt):
    results=[]
    for dd in Neo.iter_stmt(stmt,verbose=True):   #response to dict  ** catch exception!
        print ("cypher response> "+str(dd))
        results+=[dd]
    return results


def local_create_account_node(chunk,ptr):
    #### DEFINE ACCOUNT NODE:
    #- statement?
    #- main account?
    #- is entity

    #print ("[ ] watch don' update at every page cause may be error??")

    schema_entity=gold_schema_definition['nodes']['Entity']

    """ ptr:
{'case_id': 'SGM BOA', 'chunk_id': 'SGM BOA-page-SGM BOA statement december 2021.pdf-1', 'page_num': 1, 'filename': 'SGM BOA statement december 2021.pdf', 'account_number': '3250 7713 0099', 'account_holder_name': 'SKYVIEW CAPITAL GROUP MANAGEMENT LLC', 'account_holder_address': '2000 AVE OF STARS  810N, LOS ANGELES, CA  90067-4700', 'statement_period': '2021-12-01 to 2021-12-31', 'bank_name': 'Bank of America, N.A.', 'bank_address': 'P.O. Box 25118, Tampa, FL 33622-5118', 'statement_date': '2021-12-01', 'statement_page_number': 1}
    """

    NODE_TYPE='Entity'
    node={}
    node['entity_id']=ptr.get('account_number','')

    if node['entity_id']:
        node['case_id']=ptr['case_id']
        node['id']=ptr['case_id']+"-"+ptr['account_number'] #[ ] referencebed by transaction.account_id

        ## Map a bund of fields
        fields=['account_holder_name','account_number','account_holder_address','bank_name','bank_address']
        for field in fields:
            if ptr.get(field,''):
                node[field]=ptr[field]
                
        ## Patch no single quotes -- cause double singles causing problem
        #[ ] move to patch raw data
        if 'account_holder_address' in node:
            # account_holder_address: 'PALM D DATE ''0/ ﬂ ; ZO?P', b
            node['account_holder_address']=re.sub(r"'"," ",node['account_holder_address'])

        ## Map custom?

        ## Create cypher programmatically
        #cypher=cypher_create_node(NODE_TYPE,node)


        ## #0v5#  Patch fix? nan value on closing_balance and opening_balance
        #> long way but avoid nan (numpy non)
        if 'closing_balance' in node:
            # Check if the value is a string 'nan' or a float math.nan
            if node['closing_balance'] == 'nan' or (isinstance(node['closing_balance'], float) and math.isnan(node['closing_balance'])):
                node['closing_balance'] = ''
        if 'opening_balance' in node:
            # Check if the value is a string 'nan' or a float math.nan
            if node['opening_balance'] == 'nan' or (isinstance(node['opening_balance'], float) and math.isnan(node['opening_balance'])):
                node['opening_balance'] = ''
        #^end patch
        

        ## Only set/update nodes with values
        update_node={}
        for field in node:
            if node[field]:  #ignore None, "", etc. and won't overwrite
                update_node[field]=node[field]

        
        #JC: possible try-except
        # [ ] happened again with bad check scan name. do catch and log error
        cypher=cypher_create_update_node(NODE_TYPE,node,unique_property='id')   #Allow for update of fields if exists
        
        #0v4#
        try:
            results=local_run_query(cypher)
        except:
            logging.error("[could not create account name] "+str(node)+" at cypher: "+str(cypher))
            logging.dev("[could not create account name] "+str(node)+" at cypher: "+str(cypher))

    return


def local_create_statement_node(chunk,ptr):
    #[ ] add to graph_schema def + watch tracking on neo4j schema dump for Q & A.

    schema_entity=gold_schema_definition['nodes']['Entity']
    # Graph schema too?
    schema_statement=gold_schema_definition['nodes']['BankStatement']
    NODE_TYPE='BankStatement'

    """ ptr:
{'case_id': 'SGM BOA', 'chunk_id': 'SGM BOA-page-SGM BOA statement december 2021.pdf-1', 'page_num': 1, 'filename': 'SGM BOA statement december 2021.pdf', 'account_number': '3250 7713 0099', 'account_holder_name': 'SKYVIEW CAPITAL GROUP MANAGEMENT LLC', 'account_holder_address': '2000 AVE OF STARS  810N, LOS ANGELES, CA  90067-4700', 'statement_period': '2021-12-01 to 2021-12-31', 'bank_name': 'Bank of America, N.A.', 'bank_address': 'P.O. Box 25118, Tampa, FL 33622-5118', 'statement_date': '2021-12-01', 'statement_page_number': 1}
    """

    NODE_TYPE='BankStatement'
    print ("PTR: "+str(ptr))
#    if ptr['page_num']==3: a=kkk

    node={}
    node['id']=ptr['statement_id']
    
    if node['id']:
        node['case_id']=ptr['case_id']

        ## Map a bund of fields
        fields=['account_holder_name','account_number','account_holder_address','bank_name','bank_address']
        fields+=['statement_period','statement_date']
        fields+=['opening_balance','closing_balance'] ## Per: smart_extract()

        for field in fields:
            if ptr.get(field,''):  #Don't overwrite with blank
                node[field]=ptr[field]

        ## Patch no single quotes -- cause double singles causing problem
        #[ ] move to patch raw data
        if 'account_holder_address' in node:
            # account_holder_address: 'PALM D DATE ''0/ ﬂ ; ZO?P', b
            node['account_holder_address']=re.sub(r"'"," ",node['account_holder_address'])


        #[ ] jc possible try-except
        cypher=cypher_create_update_node(NODE_TYPE,node,unique_property='id')   #Allow for update of fields if exists

        #0v4#
        try:
            results=local_run_query(cypher)
        except:
            logging.error("[could not create statement node] at cypher: "+str(cypher))
            logging.dev("[could not create statement node] at cypher: "+str(cypher))
        
#        if results:
#            raise Exception("ERROR: "+str(results))

    return


def smart_store_fields(page_level_record,chunk,ptr):
    # chunk: likely page level stats
    # ptr:   current state of where we are (page, statement, etc)

    ## Immediately create nodes and relationships in neo4j
    #- do further assumptions and augmentation once base data exists
    #     (for example, linking to transactions)

    branches=[]
    branches=[]
    branches+=['create_account_node']
    branches+=['create_statement_node']

    if 'create_account_node' in branches:
        local_create_account_node(chunk,ptr)  # Formatting issue on holder name ie/ bad check scan!

    if 'create_statement_node' in branches:
        local_create_statement_node(chunk,ptr)

    return


def dev1():
    return

if __name__=='__main__':
    branches=['dev1']
    for b in branches:
        globals()[b]()


"""
"""
