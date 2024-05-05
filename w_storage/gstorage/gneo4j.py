import sys,os
import re
import logging
import abc
import copy
import uuid
import time
import threading
#from multiprocessing import Lock # Alt where _lock=Lock() instead of threading

from neo4j import GraphDatabase  ## neo4j-4.1.1  # workon gret36

try: import ConfigParser
except: import configparser as ConfigParser


LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)

import logging as logger

# Options for auto start
from neo4j_service import Manage_Neo4j_Service
from normalize_graph import graph_to_df

Config = ConfigParser.ConfigParser()
Config.read(LOCAL_PATH+"neo4j_settings.ini")

SERVER_USERNAME=Config.get('neo4j_local','username')
SERVER_PASSWORD=Config.get('neo4j_local','password')

Config = ConfigParser.ConfigParser()
Config.read(LOCAL_PATH+"../../w_settings.ini")

SERVER_IP=Config.get('neo4j','neo4j_address')
SERVER_IP_LOCAL=Config.get('neo4j','neo4j_address_local')
SERVER_BOLT_PORT=Config.get('neo4j','neo4j_bolt')


#1v0# JC  Nov  7, 2023  Check use of tx.commit(), tx.close() after run_stmt
#0v9# JC  Nov  6, 2023  [ ] run_stmt swap '' -> \'  (cypher should accept '' but nope)
#0v8# JC  Sep 28, 2023  Only connect at first usage
#0v7# JC  Sep 21, 2023  Auto get_schema() per neo4j_graph (langchain)
#0v6# JC  Sep 18, 2023  New singleton pattern for importing
#0v5# JC  Sep 12, 2023  Keep query interface lean (few assumptions)
#0v4# JC  Sep  6, 2023  defunc/query retry
#0v3# JC  Sep  5, 2023  Migrate from gret

TRY_LOCAL_NEO4J=False

def interface_get_neo4j():
    #0v2# Update to no connection until first usage
    Neo = Neo4j_Interface()
    return Neo

### GLOBAL NEO CONNECTION
Neo=None #Below call!

## FOR SCHEMA (ref: neo4j_graph @langchain)
node_properties_query = """
CALL apoc.meta.data()
YIELD label, other, elementType, type, property
WHERE NOT type = "RELATIONSHIP" AND elementType = "node"
WITH label AS nodeLabels, collect({property:property, type:type}) AS properties
RETURN {labels: nodeLabels, properties: properties} AS output

"""

rel_properties_query = """
CALL apoc.meta.data()
YIELD label, other, elementType, type, property
WHERE NOT type = "RELATIONSHIP" AND elementType = "relationship"
WITH label AS nodeLabels, collect({property:property, type:type}) AS properties
RETURN {type: nodeLabels, properties: properties} AS output
"""

rel_query = """
CALL apoc.meta.data()
YIELD label, other, elementType, type, property
WHERE type = "RELATIONSHIP" AND elementType = "node"
UNWIND other AS other_node
RETURN "(:" + label + ")-[:" + property + "]->(:" + toString(other_node) + ")" AS output
"""


class Neo4j_Interface(object):

    _instance = None
    _lock = threading.Lock()  # Add this line for thread lock

    def __init__(self):
        self.driver=None
        self.schema=""
        return

    def __new__(cls):
        with cls._lock:  # Acquire the lock
            if cls._instance is None:
                cls._instance = super(Neo4j_Interface, cls).__new__(cls)
                # Initialize any other attributes you want here if needed
        return cls._instance
    
    def connect(self,username='',password='',ip=''):
        global SERVER_USERNAME,SERVER_PASSWORD,SERVER_IP, SERVER_BOLT_PORT
        global SERVER_IP_LOCAL
        global TRY_LOCAL_NEO4J

        with self._lock:  # Acquire the lock

            # If already connected, just return
            if self.driver is None or not self.is_connected():
    
                if not username: username=SERVER_USERNAME
                if not password: password=SERVER_PASSWORD
                if not ip: ip=SERVER_IP
                
                ## Try local access to neo4j via bolt first
                if TRY_LOCAL_NEO4J:
                    try:
                        self.graph_endpoint = "bolt://"+SERVER_IP_LOCAL+":"+SERVER_BOLT_PORT
                        print("[debug] Starting neo4j graph at: "+str(self.graph_endpoint))
                        local_driver = GraphDatabase.driver(self.graph_endpoint, auth=(username, password), connection_timeout=10)
                        self.driver = local_driver
                        return
                    except:
                        self.graph_endpoint = "bolt://"+ip+":"+SERVER_BOLT_PORT
                        # Don't set self.driver to None here
        
                try:
                    self.graph_endpoint="bolt://"+ip+":"+SERVER_BOLT_PORT
                    print ("[debug] Starting neo4j graph at: "+str(self.graph_endpoint))
                    self.driver = GraphDatabase.driver(self.graph_endpoint, auth=(username, password),connection_timeout=10) #default 30 timeout
        
                except Exception as e:
                    logger.error("Could not connect to graph db: "+str(e))
                    logger.info("Try to auto start graph service..")
                    Neo=Manage_Neo4j_Service()
                    Neo.start_service()
                    logger.info("<pause 5 minutes> BEWARE!")
                    time.sleep(60*5)
                    self.driver = GraphDatabase.driver(self.graph_endpoint, auth=(username, password),connection_timeout=10) #default 30 timeout
        
                logger.info("Connected to neo4j at: "+self.graph_endpoint)
        return

    def is_connected(self):
        if not self.driver:
            return False
        try:
            with self.driver.session() as session:
                session.run('RETURN 1').single()
            return True
        except:
            return False

    def disconnect(self):
        if self.driver:
            self.driver.close()
        return

#temp    def query(self, query: str, params: dict = {}) -> List[Dict[str, Any]]:
#temp        """Query Neo4j database. REF: neo4j_graph langchain"""
#temp        from neo4j.exceptions import CypherSyntaxError
#temp
#temp        with self.driver.session(database=self._database) as session:
#temp            try:
#temp                data = session.run(query, params)
#temp                return [r.data() for r in data]
#temp            except CypherSyntaxError as e:
#temp                raise ValueError(f"Generated Cypher Statement is not valid\n{e}"

    def get_schema(self):
        if not self.schema:
            self.refresh_schema()
        return self.schema


    def refresh_schema(self) -> None:
        """
        ** requires apoc!!
        Refreshes the Neo4j graph schema information.
        REF:  neo4j_graph.py (langchain) for Graph QA
        """
        node_properties,tx = self.run_stmt(node_properties_query)
        relationships_properties,tx = self.run_stmt(rel_properties_query)
        relationships,tx = self.run_stmt(rel_query)

        node_properties = list(map(lambda x: x['output'], node_properties.data()))
        relationships_properties = list(map(lambda x: x['output'], relationships_properties.data()))
        relationships = list(map(lambda x: x['output'], relationships.data()))

        # Dump as computable but filter at 'output'
        self.schema=(node_properties,relationships_properties,relationships)

        #self.schema = f"""
        #Node properties are the following:
        #{[el['output'] for el in node_properties]}
        #Relationship properties are the following:
        #{[el['output'] for el in relationships_properties]}
        #The relationships are the following:
        #{[el['output'] for el in relationships]}
        #"""

    def _auto_start_session(foo):
        def magic(self, stmt, tx=None, parameters=None, verbose=False):
            if parameters is None:
                parameters = {}
            if tx is None or not tx:
                if self.driver is None or not self.is_connected():
                    self.connect()  # Ensures a driver is initialized and connected
                tx = self.open_session()  # This should now be safe
            return foo(self, stmt, tx=tx, parameters=parameters, verbose=verbose)
        return magic

    def open_session(self):
        if self.driver is None:
            raise AttributeError("Driver not initialized. Call connect() method first.")
        return self.driver.session()

    def close_session(self,tx):
        tx.close()
        return
    
    def process_element(self,element):
        """
        Function to process a single element (node or relationship) dynamically
        """
        if hasattr(element, 'labels'):  # Check if the element is a Node
            return {
                'id': element.id,
                'labels': list(element.labels),
                'properties': element.data()
            }
        elif hasattr(element, 'type'):  # Check if the element is a Relationship
            return {
                'id': element.id,
                'type': element.type,
                'properties': element.data(),
                'start_node_id': element.start_node.id,
                'end_node_id': element.end_node.id
            }
        else:
            return element.data() if hasattr(element, 'data') else element  # Handle scalar values and others
        
    def run_stmt_to_normalized(self,stmt,tx='',parameters={},verbose=False):
        meta={}
        jsonl=[]
        for record in self.run_stmt_to_data(stmt,tx=tx,parameters=parameters,verbose=verbose):
            jsonl+=[record]
        df,meta=graph_to_df(jsonl)
        return jsonl,df,tx,meta
        
    @_auto_start_session
    def run_stmt_to_data(self,stmt,tx='',parameters={},auto_close=True,verbose=False):
        ## Handle generic data
        #> likes iter_stmt but upgraded to handle generic data
        results,tx=self.run_stmt(stmt,tx=tx,parameters=parameters,verbose=verbose)
        processed_data = []
        for record in results:
            processed_record = self.process_element(record)  # process_record is your record processing function
            processed_data.append(processed_record)
            yield processed_record
        return# processed_data


    def _patch_stmt(self, stmt):
        # Replace '' that do not follow whitespace and are not followed by a comma or the end of the string with \'
        stmt = re.sub(r"(?<!\s)''(?![,])", r"\'", stmt)
        return stmt

    @_auto_start_session
    def run_stmt(self,stmt,tx='',parameters={},auto_close=True,verbose=False):
        #https://neo4j.com/docs/api/python-driver/current/transactions.html
        # USE: for result in results: print(result.data())
        #** default is max 100 connections
        #[ ] commit changes
        
        stmt=self._patch_stmt(stmt)
        
        try: 
            results=tx.run(stmt,parameters=parameters) ## Timeout if many? 
        except Exception as e:
            logger.info("[warning] exception on stmt run means reconnect (max 100 connections): "+str(e))
            logger.info("[warning] given parameters: "+str(parameters))
            #^^ not just re open session
            self.close_session(tx)

            self.disconnect()
            self.connect()
            tx=self.open_session()
            results=tx.run(stmt,parameters=parameters) ## Timeout if many?

        #      results.data() !
        return results,tx
    
    def clean_cypher_exceptions(self,stmt):
        # If stmt fails try for common pitfalls

        #   \ at end of inner query
        stmt=re.sub(r'\\\n','\n',stmt) # Looks ok for \\n at end of line mod to \n
#        for liner in re.split('\n',stmt): print (">"+str(liner)+"<")

        # Singl quotes within stmt??
        #stmt = """MERGE (n:Entity {id: '6578e48c20668da6f77cd052-322c7hbB'}) ON CREATE SET n += {entity_id: '322c7hbB', case_id: '6578e48c20668da6f77cd052', id: '6578e48c20668da6f77cd052-322c7hbB', account_holder_name: 'ARGOT SERRANO', account_number: '322c7hbB', account_holder_address: 'PALM D DATE ''0/ ﬂ ; ZO?P', bank_name: 'JPMorgan chase Bank', bank_address: 'MEMO PO BOX 1755 | 90/7162 | Al SERT, CA92261-1735', label: 'Entity'} ON MATCH SET n += {entity_id: '322c7hbB', case_id: '6578e48c20668da6f77cd052', id: '6578e48c20668da6f77cd052-322c7hbB', account_holder_name: 'ARGOT SERRANO', account_number: '322c7hbB', account_holder_address: 'PALM D DATE ''0/ ﬂ ; ZO?P', bank_name: 'JPMorgan chase Bank', bank_address: 'MEMO PO BOX 1755 | 90/7162 | Al SERT, CA92261-1735', label: 'Entity'}"""
        corrected_stmt = re.sub(r"(?<=\w)'(?=\w)", "\\\\'", stmt)

        return stmt

    @_auto_start_session
    def iter_stmt(self,stmt,tx='',verbose=False, auto_close=True,expect_EXTRACT=False,parameters={}):
        ##** see run_stmt_to_data for generic ^^
        ## Upgrade to check for summary stats
        #Expects query to have dicts in output
        # ** timeout potential? neo4j.exceptions.ClientError: {code: None} {message: None}
        ## ** lazy fetch at results but possible to timeout

        ## Exceptions:
        #1)  Timeout
        #2)  Failed to read from defunct connection
        #     - if 'Failed to read from defunct connection' in str(e):
        #3) \\n escaping \n in statement is bad

#        try: print ("[debug] possible timeout at tx.run: "+str(stmt))
#        except: pass

        stmt=self._patch_stmt(stmt)

        yielded=0
        retries=2
        is_done=False
        is_error=False

        stats={}

        while not is_done and retries:
            retries-=1

            valid_first=False
            try:
                result = tx.run(query=stmt, parameters=parameters)
                valid_first=True
            except Exception as e:
                print ("[error at cypher stmt]: "+str(stmt))
                print ("[error at cypher stmt]  ^^^above")
                print ("[error] gneo4j.py exception: "+str(e))
                stmt=self.clean_cypher_exceptions(stmt)

            try:
                ## Do query and iter later (so can chck summary vars)

                if not valid_first:
                    result = tx.run(query=stmt, parameters=parameters)

                #** BEWARE:  list(result) clears results!
        
                # Yield results one-by-one
                for record in result:
                    if verbose:
                        print ("[verbose gneo4j] record: "+str(record))
                    dict_list = self._Resp2dictlist(record)
                    yield dict_list
                    yielded+=1
                
                if not list(result)==[] and not yielded:
                    print ("[debug gneo4j] no results but NOT yielded?")
        
                # After all results have been yielded, consume the result to get the summary
                summary = result.consume()
        
                # Check if any nodes were created
                #- note more options below
                if summary.counters.nodes_created:
                    if verbose: print(f"[debug gneo4j] {summary.counters.nodes_created} nodes were created.")
                    stats['count_nodes_created']=summary.counters.nodes_created
        
                is_done=True
            except Exception as e:
                print ("[error at cypher stmt]: "+str(stmt))
                print ("[error at cypher stmt]  ^^^above")
                print ("[error] gneo4j.py exception: "+str(e))
                raise RuntimeError("[error] gneo4j.py exception: "+str(e))
                # timeout?
                # Failed to read from defunct connection?
                print ("[dev] just try running query again... Total yielded: "+str(yielded))

        #D# if verbose: print ("[debug] ^^ done tx.run")

        tx.close()
        return
    
    def _Resp2dictlist(self,Resp,verbose=False):
        tups=[]
        #org# the_obj=Resp.data()  #Proper way but...
        
        is_node=False
        is_edge=False
        
        edge_dict={}
        for kkey,vv in Resp.items():
            if verbose: logger.info("--->> "+str(kkey)+" values: "+str(vv))
            #n values: <Node element_id='42265' labels=frozenset({'Recipient'}) properties={'name': 'Kevin', 'case_id': 'case_1', 'id': 'case_1_Kevin'}>

            if False:
                node={}
                if kkey=='n':
                    node['labels']=vv.labels
                    node['id']=vv.id
                    node['properties']=dict(vv)

            if isinstance(vv,int) or isinstance(vv,float):
                tups+=[vv]  #t='MATCH (n) RETURN COUNT(n) as TotalNodes;'
            elif not hasattr(vv,'nodes') and re.search(r'^type\(',kkey):
                #Assume edge type
                tups+=[vv]
                is_edge=True
            elif not hasattr(vv,'nodes'): #not hasattr(vv,'type'):
                ## STANDARD NODE ENTRY
                is_node=True
                node=dict(vv)
                if 'labels' in vv:
                    node['labels']=list(vv.labels)
                tups+=[node]

            elif hasattr(vv,'nodes'): #vv.type=='link':
                is_edge=True
                edge_dict=dict(vv)
                tups+=[edge_dict]
                
                if False:
                    ## Validate raw id -> id matches expected edge id
                    start_node=vv.start_node
                    end_node=vv.end_node

                    logger.info("[rel has node_start raw id: "+str(start_node.id)+" labels: "+str(start_node.labels))
                    for label in start_node.labels:
                        logger.info("lab: "+str(label))
                    logger.info("Length: "+str(len(start_node.labels)))
                    
                    for aa in start_node:
                        logger.info("OK: "+str(aa))
            else:
                stopp_unk=nown_type

        return tups
    
    def _record_node_obj2record_meta(self,node_obj_dict):
        checkk=olld
        labels=list(node_obj_dict.keys()) #[]
        return node_obj_dict['id'],labels
#        logger.info("RECORD LABEL: "+str(node_obj_dict))
#        logger.info("RECORD LABEL: "+str(node_obj_dict.labels)) #frozen set
        #logger.info("RECORD LABEL: "+str(set(node_obj_dict.labels))) #frozen set
        #logger.info("RECORD LABEL: "+str(node_obj_dict['labels']))
        for term in set(node_obj_dict.labels):
            labels+=[term]
        return node_obj_dict.id,labels
    
    def create_id(self):
        return str(uuid.uuid1())
    
    ## index https://www.quackit.com/neo4j/tutorial/neo4j_create_an_index_using_cypher.cfm
    
    ## constraint A constraint allows you to place restrictions over the data that can be entered against a node or a relationship.
    
    ## get prop  payload=node.properties.get('payload','')
    


def dev1():
    b=['basic']
    b=['timeout_query']

    Neo=Neo4j_Interface()
    Neo.connect()
    
    if 'timeout_query' in b:
        stmt="""MATCH (n { idx:'https://www.studioamelia.com'}) RETURN n"""
        for dd in Neo.iter_stmt(stmt):
            print ("> "+str(dd))
    
    else:
        stmt='hello'
        Neo.run_stmt(stmt)

    Neo.disconnect()
    logger.info("[done dev1]")
    return

def dev_try_remote_server():
    Neo=Neo4j_Interface()
    #ok#Neo.connect(username='neo4j',password='xxxxxxxxxxxxxxx',ip='3.20.195.157')
    Neo.connect()
    return


def dev_check_connections():
    print ("**enterprise edition only")
    Neo=Neo4j_Interface()
    Neo.connect()

    def list_connections(tx):
        result = tx.run("CALL dbms.listConnections()")
        return [record.data() for record in result]

    driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "password"))
    tx=Neo.open_session() # tx = self.driver.session()

    with Neo.driver.session() as session:
        connections = session.read_transaction(list_connections)

    for connection in connections:
        print(connection)

#    driver.close()

    return


### GLOBAL Neo
#- depends on class so call at end
Neo=interface_get_neo4j()

def dev_sample_explicit_session_management():
    ## COMMENTS:
    #- Explicitn session open will ensure session closed neatly
    #- Recall, use tx if want to use same session + the custom code
    
    global Neo
    case_id='case_atm_location'
    stmt="""
    MATCH (t:Transaction)
    WHERE t.case_id='"""+str(case_id)+"""'
    return t
    """
    
    Neo.connect()

    with Neo.open_session() as session:
        #session.write_transaction(create_and_return_greeting, "Alice", "Bob")
        #jsonl,df,tx,meta=Neo.run_stmt_to_normalized(stmt)
        
        ## DIRECT RUN
        records=[]
        for record in session.run(stmt):
            records.append(record['t'])
        print ("Size of records session.run: "+str(len(records)))
            
        ## Pass session
        jsonl,df,tx,meta=Neo.run_stmt_to_normalized(stmt,tx=session)
        print("Size of records passed: "+str(len(jsonl)))

        ## Assume handles session
        jsonl,df,tx,meta=Neo.run_stmt_to_normalized(stmt)
        print("Size of records passed: "+str(len(jsonl)))
    
    return


if __name__=='__main__':

    branches=['dev1']
    branches=['dev_try_remote_server']
    branches=['dev_check_connections']
    branches=['dev_sample_explicit_session_management']

    for b in branches:
        globals()[b]()
        
        
        
"""

OPTIONAL:
result = tx.run(query=stmt, parameters=parameters)

for record in result:
    node = record['n']  # Assuming your query has "RETURN n"
    
    # Extracting properties
    properties = dict(node)
    
    # Extracting labels
    labels = list(node.labels)

    print(properties)
    print(labels)


Statement & Parameters:

summary.statement: The Cypher statement that was executed.
summary.parameters: The parameters that were passed to the Cypher statement.
Query Execution Time:

summary.result_available_after: The time it took until the result was available (in milliseconds).
summary.result_consumed_after: The time it took to consume the result (in milliseconds).
Notifications:

summary.notifications: Returns a list of notifications produced while executing the statement. These can provide hints about how to optimize the query.
Statistics:

summary.counters: Provides statistics about what the query did, such as the number of nodes created, relationships deleted, properties set, etc.

Some of the methods available on the counters object are:

nodes_created()
nodes_deleted()
relationships_created()
relationships_deleted()
properties_set()
labels_added()
labels_removed()
indexes_added()
indexes_removed()
constraints_added()
constraints_removed()
... and many more.
Server Info:

summary.server: Information about the Neo4j server where the statement was executed. It has properties like:
address: The server address.
version: The version of Neo4j.
Database Info:

summary.database: Information about the database on which the statement was executed. It provides properties like:
name: Name of the database.
Plan & Profile:

summary.plan: Returns the plan for the executed statement, if available.
summary.profile: Returns the profile for the executed statement, if available. This can help you understand the performance characteristics of the query.
Query Type:

summary.query_type: Provides an insight into the type of statement executed (e.g., READ_ONLY, SCHEMA_WRITE, etc.).
"""        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        

