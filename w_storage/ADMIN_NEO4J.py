import os
import sys
import codecs
import json
import re
import time

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")

from a_query.cypher_helper import cypher_add_fields_to_node
from a_query.cypher_helper_neo4j import cypher_add_fields_to_node_VERSIONS
from a_query.cypher_helper import cypher_create_node
from a_query.cypher_helper import cypher_create_relationship
from a_query.cypher_helper import cypher_add_create_relationship

from w_storage.gstorage.gneo4j import Neo
from kb_ai.schemas.SCHEMA_graph import GRAPH_SCHEMA
from kb_ai.schemas.SCHEMA_graph import GRAPH_INDEXES

from get_logger import setup_logging
logging=setup_logging()


#0v1# JC  Sep 21, 2023  Init


"""
    NEO4J requires indexes on common node id etc.
    - ultimately, depends on schema
"""


def create_indexes_in_graph_db():
    b=['destroy_nonuniques']
    b=['create_indexes']

    if 'destroy_nonuniques' in b:
        check=sureee
        ## Also does relationships!
        query="""
        MATCH (t:Transaction)
        WITH t.id AS id, COLLECT(t) AS nodes
        WHERE SIZE(nodes) > 1
        FOREACH (n IN TAIL(nodes) | 
          DETACH DELETE n
        );
        """
        print ("!!!!! DESTROYING TRANSACTION NODE (nonunique) in 10s...")
#        time.sleep(5)
        for rr in Neo.run_stmt(query,verbose=True):
            try: print("enforce unique response: "+str(rr.data()))
            except: print("enforce unique response: "+str(rr))
        query="""
        MATCH (t:Entity)
        WITH t.id AS id, COLLECT(t) AS nodes
        WHERE SIZE(nodes) > 1
        FOREACH (n IN TAIL(nodes) | 
          DETACH DELETE n
        );
        """
        print ("!!!!! DESTROYING ENTITY      NODE (nonunique) in 10s...")
        time.sleep(5)
        for rr in Neo.run_stmt(query,verbose=True):
            try: print("enforce unique response: "+str(rr.data()))
            except: print("enforce unique response: "+str(rr))


    if 'create_indexes' in b:
        print ("[dev] creating indexes on graph db")
        for label, properties in GRAPH_INDEXES.items():
            for property in properties:
                ## CONSTRAINT == INDEX
                #query = f"CREATE INDEX FOR (n:{label}) ON (n.{property})"
                query=f"CREATE CONSTRAINT ON (n:{label}) ASSERT n.{property} IS UNIQUE"
                print ("[dev] create index query: "+str(query))
                try:
                    for rr in Neo.run_stmt(query,verbose=True):
                        print("create index response: "+str(rr))
                except Exception as e:
                    print ("> "+str(e))
    return


if __name__=='__main__':
    branches=['create_indexes_in_graph_db']
    for b in branches:
        globals()[b]()