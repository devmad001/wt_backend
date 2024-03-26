import os
import sys
import codecs
import copy
import json
import re
import threading  #future multi

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")

from w_utils import util_get_modified_keys
from w_storage.gstorage.gneo4j import Neo

from get_logger import setup_logging
logging=setup_logging()

from schemas.SCHEMA_kbai import gold_schema_definition


#0v2# JC  Oct  7, 2023  Remove keyword because search works fine out-of-the-box
#0v1# JC  Sep 28, 2023  Init

"""
    CYPHER QUERY MARKUP
    ** easier to NOT use versioning but better for tracking! -- see samples with & without
    - since answers are cypher, why not leverage cypher on kb update
    - afterall, if you can't answer question, maybe you can ask it to update
"""


def NOT_NEEDED_CYPHER_add_keyword_chemical(**vars):
    """
        CYPHER QUERY MARKUP
        - self-contained query AND update
        - follow versioning for modified fields though
        - kb_update -> dev_cypher_update()
    """
    meta={}
    
    #a_query...
    # usedby dev_cypher_update():  cypher=cypher_add_fields_to_node_VERSIONS(node_label,properties, record[id_property_name], version=markup_version, id_property_name=id_property_name)
    """
        RECALL:  sample cypher update across 3 fields with corresponding meta data fields
            MATCH (n:Person {id: '12345'}) SET n.versions_metadata = '{"name": "v1.1", "age": "v1.1", "city": "v1.1"}', n.name = 'John Doe', n.age = 30, n.city = 'New York'
    """
    
    ## NON-VERSIONED:
    """
        MATCH (n:Transaction)
            WHERE toLower(n.transaction_description) CONTAINS 'chemical' AND n.case_id = 'YOUR_CASE_ID'
            SET n.has_keyword_chemical = true
            RETURN n
    """
    
    ## VERSIONED:
    
    b=['chemical']

    case_id=vars['case_id']
    version=vars['markup_version']

    if 'chemical' in b:
        keyword='chemical'
        new_field='has_keyword_chemical'
    
    if []:
        ## DEV
        # airport, ammo
        keyword='airport'
        new_field='has_keyword_airport'

        keyword='ammo'
        new_field='has_keyword_ammo'


    cypher="""
        // SELECT
        MATCH (n:Transaction)
            WHERE EXISTS(n.transaction_description)
                  AND toLower(n.transaction_description) CONTAINS '"""+keyword+"""'
                  AND n.case_id = '""" + str(case_id) + """'
            
            
            
        // CALCULATION
        SET n."""+new_field+""" = true
        
        
        // VERSIONING
            WITH n
            , CASE
                WHEN EXISTS(n.versions_metadata) THEN apoc.convert.fromJsonMap(n.versions_metadata)
                ELSE {}
            END AS versionsMap
            
            // VERSION
            WITH n, versionsMap
            SET versionsMap."""+new_field+""" = '""" + str(version) + """',
                n.versions_metadata = apoc.convert.toJson(versionsMap)
            RETURN n

    """
    logging.info("[cypher_markup]:  "+str(cypher))

    for rr in Neo.iter_stmt(cypher,verbose=True):
        print ("[cypher] result: "+str(rr)) #Non on inser
    
    
    cypher_view="""
        MATCH (n:Transaction)
            WHERE n.has_keyword_chemical = true AND n.case_id = '""" + str(case_id) + """'
            RETURN n;
        """
    count_records_with_keywords=0
    for rr in Neo.iter_stmt(cypher_view,verbose=True):
        print ("[keyword "+str(keyword)+"] result: "+str(rr)) #Non on inser
        count_records_with_keywords+=1

    logging.info("[records with keyword '"+str(keyword)+"'] count: "+str(count_records_with_keywords))
    meta['count_records_changed']=count_records_with_keywords

    return meta


def do_cypher_markup(*args,**vars):
    ### RECALL:
    #** follow do_logic_markup flow
    
    ## GIVEN RECALL:
    # markup_goals == which alg here to run
    # Records      == bite sized list of dumped records from KB to markup!
    # schema       == essentially a bunch of parameters
    #                 ^^^*** separate logical tweaks from this routine!
    #                     ^^^ ie/ schema regex examples to apply when
    #                             looking for check number. default here tweaks there.
    # meta_doc     == other meta not available in raw transaction "Records"
    
    ## Recall, cypher update & field versions are handled external call_kbai.py
    #- version tracking  (like do_llm_markup) #- cypher update     (like do_llm_markup)
    meta={}
    finished_records=[]
    unfinished_records=[]
    
    """
        dd={}
        dd['case_id']=ptr['case_id']
        dd['schema']=ptr['schema']
        dd['Records']=Records
        dd['markup_goals']=ptr['markup_goals']
        dd['meta_doc']=meta_doc
        dd['DEFAULT_LLM_GROUP_SIZE']=options['DEFAULT_LLM_GROUP_SIZE']  #10 a big 
        dd['markup_version'] ** cause doing update to db
    """
    
    ## Map back to va
    # touch givens
    vars['markup_goals']=vars['markup_goals'] #ie/ alg to run
    

    ### LOOKUP CYPHER BRANCH
    #- recall, set during mapping (call_kbai.py -> map_question_need_to_alg_offer))
    
    if True:
        pass

#remove#    elif False and 'CYPHER_add_keyword_chemical' in vars['markup_goals']:
#remove#        ## DO direct manipulation or via pass back records?
#remove#        #- recall versioning maybe include it here
#remove#        cypher_meta=CYPHER_add_keyword_chemical(**vars)
#remove#        meta.update(cypher_meta) #<-- count_records_changed

    else:
        raise Exception("Unknown markup_goals: %s" % vars['markup_goals'])

    logging.info("[finished cypher markup] count changed/matched: "+str(meta.get('count_records_changed','')))

    return finished_records,unfinished_records,meta



if __name__=='__main__':
    branches=['do_markup_alg_logic']
    for b in branches:
        globals()[b]()



"""
    LOGIC ROUTINE IDEAS:
        main_account=''
        print ("Yeah, is main account withdrawl or deposit -- seems like an easy question")
"""

"""
SAMPLE:  search for keyword including field versioning update

NO VERSIONING:
MATCH (n:Transaction)
WHERE toLower(n.transaction_description) CONTAINS 'chemical' AND n.case_id = 'YOUR_CASE_ID'
SET n.has_keyword_chemical = true
RETURN n

WITH VERSIONING:


You want to select nodes with the label Transaction that have a non-null transaction_description attribute containing the word 'chemical' (case-insensitive). If such nodes are found, you intend to set a has_keyword_chemical attribute to true and update the versions_metadata attribute with the version v1.3 for has_keyword_chemical. Below is an example query that implements this logic:

MATCH (n:Transaction)
WHERE EXISTS(n.transaction_description)
      AND toLower(n.transaction_description) CONTAINS 'chemical'
      AND n.case_id = '"" + str(case_id) + ""'

// Calculation
WITH n, true AS hasChemical,
     CASE
         WHEN EXISTS(n.versions_metadata) THEN apoc.convert.fromJsonMap(n.versions_metadata)
         ELSE {}
     END AS versionsMap

// Set
SET n.has_keyword_chemical = hasChemical

WITH n, versionsMap, hasChemical
// VERSION
SET versionsMap.has_keyword_chemical = '"" + str(version) + ""',
    n.versions_metadata = apoc.convert.toJson(versionsMap)
RETURN n
Explanation:
MATCH Clause: Selects nodes with the label Transaction.
WHERE Clause: Filters nodes that have a non-null transaction_description containing the word 'chemical' (case-insensitive) and with a case_id equal to a specified value.
WITH Clause: Processes the nodes to calculate hasChemical (set to true) and to handle versions_metadata.
SET Clause: Updates the has_keyword_chemical attribute and versions_metadata for selected nodes.
Notes:
Ensure to replace str(case_id) and str(version) with actual values or variables.
Adjust the version identifier (str(version)) to 'v1.3' or whatever version identifier you need.
Be cautious when updating data, and consider backing up your database or working on a non-production dataset first.

"""