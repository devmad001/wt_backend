import os
import sys
import codecs
import json
import re

from fastapi import FastAPI

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")

from w_storage.gstorage.gneo4j import Neo

from get_logger import setup_logging
logging=setup_logging()


#0v3# JC  Feb 12, 2024  Hitting 4096 token limit (gpt-4) require reduction (extra schema caused issue)
#0v2# JC  Oct 11, 2023  Extend for PROCESSED_BY
#0v1# JC  Sep 21, 2023  Init


"""
    >>
"""



def dev1():
    print ("ASK KB")
    print ("-> english to cypher conversion")
    print ("-> recall prompts")
    print ("-> recall Langchain")
    print ("-> LLMs:  Bison can be fine tuned")

    """
    Google bison stuff
    https://cloud.google.com/blog/topics/partners/build-intelligent-apps-with-neo4j-and-google-generative-ai
    https://github.com/neo4j-partners/neo4j-generative-ai-google-cloud 
    """

    return


def get_graph_schema_str():
    ## Dump schema from db!
    # recall:  this is langchain tested dump
    schema=Neo.get_schema()
    """
     Node properties are the following:
[{"properties": [{"property": "id", "type": "STRING"}, {"property": "case_id", "type": "STRING"}, {"property": "bank_name", "type": "STRING"}, {"property": "account_holder_name", "type": "STRING"}, {"property": "account_holder_address", "type": "STRING"}, {"property": "account_number", "type": "STRING"}, {"property": "name", "type": "STRING"}], "labels": "Account"}, {"properties": [{"property": "transaction_type", "type": "STRING"}, {"property": "transaction_description", "type": "STRING"}, {"property": "versions_metadata", "type": "STRING"}, {"property": "transaction_method", "type": "STRING"}, {"property": "payer_id", "type": "STRING"}, {"property": "statement_id", "type": "STRING"}, {"property": "section", "type": "STRING"}, {"property": "receiver_id", "type": "STRING"}, {"property": "transaction_date", "type": "STRING"}, {"property": "filename", "type": "STRING"}, {"property": "transaction_amount", "type": "STRING"}, {"property": "case_id", "type": "STRING"}, {"property": "id", "type": "STRING"}, {"property": "filename_page_num", "type": "STRING"}, {"property": "algList", "type": "LIST"}, {"property": "transaction_reference", "type": "STRING"}, {"property": "account_id", "type": "STRING"}, {"property": "amount", "type": "STRING"}, {"property": "account_number", "type": "STRING"}], "labels": "Transaction"}, {"properties": [{"property": "id", "type": "STRING"}, {"property": "case_id", "type": "STRING"}, {"property": "entity_id", "type": "STRING"}, {"property": "bank_name", "type": "STRING"}, {"property": "account_holder_name", "type": "STRING"}, {"property": "account_holder_address", "type": "STRING"}, {"property": "account_number", "type": "STRING"}, {"property": "bank_address", "type": "STRING"}, {"property": "name", "type": "STRING"}, {"property": "type", "type": "STRING"}, {"property": "role", "type": "STRING"}], "labels": "Entity"}]
Relationship properties are the following:
[{"type": "DEBIT", "properties": [{"property": "date", "type": "STRING"}, {"property": "amount", "type": "FLOAT"}]}, {"type": "CREDIT", "properties": [{"property": "date", "type": "STRING"}, {"property": "amount", "type": "STRING"}]}, {"type": "DEBIT_FROM", "properties": [{"property": "date", "type": "STRING"}, {"property": "amount", "type": "STRING"}]}, {"type": "CREDIT_TO", "properties": [{"property": "date", "type": "STRING"}, {"property": "amount", "type": "STRING"}]}]
Relationship are the following:
["(:Account)-[:DEBIT_FROM]->(:Transaction)", "(:Account)-[:DEBIT]->(:Transaction)", "(:Transaction)-[:DEBIT_FROM]->(:Transaction)", "(:Transaction)-[:CREDIT_TO]->(:Entity)", "(:Transaction)-[:CREDIT_TO]->(:Transaction)", "(:Transaction)-[:CREDIT_TO]->(:Account)", "(:Entity)-[:DEBIT_FROM]->(:Transaction)"]
    """

    schema_str=''

    node_properties=schema[0]
    relationship_properties=schema[1]
    relationships=schema[2]

    labels = [item['labels'] for item in node_properties]
    unique_labels = list(set(labels))
    
    #    print ("[debug known labels]: "+str(unique_labels))

    ## TOP-LEVEL FILTER

    #[A]  "LABEL" / NODE TYPE FILTER
    keep_only_labels=['Transaction','Entity']
    keep_only_labels+=['Processor']
    keep_only_labels+=['BankStatement']
    node_properties = [item for item in node_properties if item['labels'] in keep_only_labels]

    #[B]  "RELATION TYPE" FILTER
    # List of relationships to keep
    keep_only_rels = ['DEBIT_FROM', 'CREDIT_TO']
    keep_only_rels+= ['PROCESSED_BY']
    keep_only_rels+= ['HAS_TRANSACTION']

    # REGEX  Filtering relationships
    relationships = [rel for rel in relationships if any(re.search(keep_rel, rel) for keep_rel in keep_only_rels)]
    #keep_only_rels += [r'Transaction.*Transaction']  #Invalid in db quick patch

    filter_rels=[r'Transaction.*Transaction']
    filter_rels+=[':Account']
    relationships = [item for item in relationships if not any(re.search(filter_rel, item) for filter_rel in filter_rels)]

    #[C]  Filter node properties
    #    keep_only = ['transaction_type']
    #filtered_data = [{'labels': item['labels'], 'properties': [prop for prop in item['properties'] if prop['property'] in keep_only]} for item in data]
    filter_out = ['algList']
    filter_out+=['location'] #Using lat + lng
    filter_out+=['label'] # Transaction, etc.

    node_properties = [{'labels': item['labels'], 'properties': [prop for prop in item['properties'] if prop['property'] not in filter_out]} for item in node_properties]
    node_properties_str=str(json.dumps(node_properties))
    ## Token reduction
    node_properties_str=re.sub('STRING','STR',node_properties_str)

    #[D]  Filter relations properties
    filter_out = []
    relationship_properties = [{'type': item['type'], 'properties': [prop for prop in item['properties'] if prop['property'] not in filter_out]} for item in relationship_properties]
    relationship_properties_str=str(json.dumps(relationship_properties))
    relationship_properties_str=re.sub('STRING','STR',relationship_properties_str)
    
    ## STR FORMAT
    schema_str+="Node properties are the following:\n"
    schema_str+=node_properties_str+"\n"
    schema_str+="Relationship properties are the following:\n"
    schema_str+=relationship_properties_str+"\n"
    schema_str+="Relationship are the following:\n"
    schema_str+=str(json.dumps(relationships))+"\n"

    if False:
        print ("[known labels] : "+str(labels)) # [known labels] : ['Account', 'Transaction', 'Entity']
        print ("SCHEMEE: "+str(schema_str))

    return schema_str

"""
schema version?
CYPHER_GENERATION_PROMPT

"""

def call_get_graph_schema_str():
    print (">> RECALL SAMPLES in cypher_snapshot!!")
    schema_str=get_graph_schema_str()
    print ("OK: "+str(schema_str))
    return schema_str

if __name__=='__main__':
    branches=['call_get_graph_schema_str']

    for b in branches:
        globals()[b]()



"""
fine tune Bison-text for cypher 100 smples
the text-bison base model can be tuned to generate more accurate Cypher. Lets see how to adapter tune it. We will try to tune the model with some Cypher statements. The model achieves some Cypher generation capability but could be better. It is suggested to try with at least a few hundred statements. You should aim for more quality training data.

Question: What other fund managers are investing in same companies as Vanguard?
Answer: MATCH (m1:Manager) -[:OWNS]-> (c1:Company) <-[o:OWNS]- (m2:Manager) WHERE toLower(m1.managerName) contains "vanguard" AND elementId(m1) <> elementId(m2) RETURN m2.managerName as manager, sum(DISTINCT o.shares) as investedShares, sum(DISTINCT o.value) as investmentValue ORDER BY investmentValue LIMIT 10

Question: What are the top investors for Apple?
Answer: MATCH (m1:Manager) -[o:OWNS]-> (c1:Company) WHERE toLower(c1.companyName) contains "apple" RETURN distinct m1.managerName as manager, sum(o.value) as totalInvested ORDER BY totalInvested DESC LIMIT 10

Question: What are the other top investments for fund managers investing in Apple?
Answer: MATCH (c1:Company) <-[:OWNS]- (m1:Manager) -[o:OWNS]-> (c2:Company) WHERE toLower(c1.companyName) contains "apple" AND elementId(c1) <> elementId(c2) RETURN DISTINCT c2.companyName as company, sum(o.value) as totalInvested, sum(o.shares) as totalShares ORDER BY totalInvested DESC LIMIT 10

Question: What are the top investors in the last 3 months?
Answer: MATCH (m:Manager) -[o:OWNS]-> (c:Company) WHERE date() > o.reportCalendarOrQuarter > o.reportCalendarOrQuarter - duration({{months:3}}) RETURN distinct m.managerName as manager, sum(o.value) as totalInvested, sum(o.shares) as totalShares ORDER BY totalInvested DESC LIMIT 10

Question: What are top investments in last 6 months for Vanguard?
Answer: MATCH (m:Manager) -[o:OWNS]-> (c:Company) WHERE toLower(m.managerName) contains "vanguard" AND date() > o.reportCalendarOrQuarter > date() - duration({{months:6}}) RETURN distinct c.companyName as company, sum(o.value) as totalInvested, sum(o.shares) as totalShares ORDER BY totalInvested DESC LIMIT 10

Question: Who are Apple's top investors in last 3 months?
Answer: MATCH (m:Manager) -[o:OWNS]-> (c:Company) WHERE toLower(c.companyName) contains "apple" AND date() > o.reportCalendarOrQuarter > date() - duration({{months:3}}) RETURN distinct m.managerName as investor, sum(o.value) as totalInvested, sum(o.shares) as totalShares ORDER BY totalInvested DESC LIMIT 10

Question: Which fund manager under 200 million has similar investment strategy as Vanguard?
Answer: MATCH (m1:Manager) -[o1:OWNS]-> (:Company) <-[o2:OWNS]- (m2:Manager) WHERE toLower(m1.managerName) CONTAINS "vanguard" AND elementId(m1) <> elementId(m2) WITH distinct m2 AS m2, sum(distinct o2.value) AS totalVal WHERE totalVal < 200000000 RETURN m2.managerName AS manager, totalVal*0.000001 AS totalVal ORDER BY totalVal DESC LIMIT 10

Question: Who are common investors in Apple and Amazon?
Answer: MATCH (c1:Company) <-[:OWNS]- (m:Manager) -[:OWNS]-> (c2:Company) WHERE toLower(c1.companyName) contains "apple" AND toLower(c2.companyName) CONTAINS "amazon" RETURN DISTINCT m.managerName LIMIT 50

Question: What are Vanguard's top investments by shares for 2023?
Answer: MATCH (m:Manager) -[o:OWNS]-> (c:Company) WHERE toLower(m.managerName) CONTAINS "vanguard" AND date({{year:2023}}) = date.truncate('year',o.reportCalendarOrQuarter) RETURN c.companyName AS investment, sum(o.value) AS totalValue ORDER BY totalValue DESC LIMIT 10

Question: What are Vanguard's top investments by value for 2023?
Answer: MATCH (m:Manager) -[o:OWNS]-> (c:Company) WHERE toLower(m.managerName) CONTAINS "vanguard" AND date({{year:2023}}) = date.truncate('year',o.reportCalendarOrQuarter) RETURN c.companyName AS investment, sum(o.shares) AS totalShares ORDER BY totalShares DESC LIMIT 10

Question: Which managers own FAANG stocks?
Answer: MATCH (m:Manager)-[o:OWNS]->(c:Company) WHERE toLower(c.companyName) IN [toLower("Facebook"),toLower("Apple"),toLower("Amazon"),toLower("Netflix"),toLower("Google")] RETURN m.managerName as manager, collect(distinct c.companyName) as companies

Question: {question}
Answer: 
"""
