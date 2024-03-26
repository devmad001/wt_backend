import os
import sys
import codecs
import json
import re

from fastapi import FastAPI

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")

from get_logger import setup_logging
logging=setup_logging()


#0v3# JC                [ ] migrate to SCHEMA_kbai.py
#0v2# JC  Sep 21, 2023  Indexes
#0v1# JC  Sep 19, 2023  Init

"""
    **managed in SCHEMA_kbai (gold schema def)
    GRAPH SCHEMA
"""

GRAPH_SCHEMA={}
GRAPH_SCHEMA['node2id_name']={}
GRAPH_SCHEMA['node2id_name']['Transaction']='id'

### DEFINE INDEXES required on Labels!
GRAPH_INDEXES={}
GRAPH_INDEXES['Transaction']={}
GRAPH_INDEXES['Transaction']['id']=True #CREATE INDEX FOR (n:Transaction) ON (n.id)
GRAPH_INDEXES['Entity']={}
GRAPH_INDEXES['Entity']['id']=True #CREATE INDEX FOR (n:Entity) ON (n.id)

def dev1():
    return

if __name__=='__main__':
    branches=['dev1']
    for b in branches:
        globals()[b]()

"""
from neo4j import GraphDatabase

def create_schema(driver, schema):
    with driver.session() as session:
        for label, properties in schema["NodeLabels"].items():
            for property in properties["Properties"]:
                session.run(f"CREATE INDEX ON :{label}({property})")
        
        for relationship, details in schema["RelationshipTypes"].items():
            # Add any logic needed to create relationships

# Initialize the Neo4j driver
driver = GraphDatabase.driver("neo4j://localhost:7687", auth=("neo4j", "password"))

# Create the schema
create_schema(driver, schema)

"""
