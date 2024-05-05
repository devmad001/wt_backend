import os
import sys
import codecs
import json
import re
from decimal import Decimal

#from pypher import Pypher, __  #pip install pypher_cypher

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")

from get_logger import setup_logging
logging=setup_logging()

from w_storage.gstorage.gneo4j import Neo
from cypher_helper import escape_string


#0v1# JC  Sep 18, 2023  Init

"""
Like cypher_helper.py but, queries neo4j for real-time feild updates

"""

def query_get_versions_dict(node_type, node_id, tx='', id_property_name='id', node_var='n'):
    #if not tx: tx=Neo.open_session()

    query = f"""
        MATCH ({node_var}:{node_type} {{{id_property_name}: '{node_id}'}})
        RETURN {node_var}.versions_metadata AS versions_metadata
        """

    #result = tx.run(query).single()
    result,tx = Neo.run_stmt(query) #tx.run(query).single()
    result=result.single()

    versions_metadata = result['versions_metadata']

    #print ("[dev] got current versions: "+str(versions_metadata))

    if versions_metadata:
        return json.loads(versions_metadata)
    else:
        return {}

### PROPERTY UPDATES
def cypher_add_fields_to_node_VERSIONS(node_type, properties, node_id, version, id_property_name='id', node_var='n'):
    """
    node_type: The type of the node you want to update.
    properties: The properties you want to add or update.
    node_id: The unique identifier for the specific node you want to update.
    id_property_name: The name of the property you use as an identifier (default is 'id').
    node_var: The variable name you want to use for the node in your Cypher query.
    versions:  dict with keys as fields for latest version tracking
    """
    
    ## Bug catch on id with spaces or odd escapes?
    if ' ' in properties.get(id_property_name, ''):
        logging.warning("Bad node id has a space?: "+str(properties.get(id_property_name, '')))
    if "\'" in properties.get(id_property_name, ''):
        logging.warning("Bad node id has an escape?: "+str(properties.get(id_property_name, '')))

    current_versions = query_get_versions_dict(node_type, node_id, id_property_name=id_property_name, node_var=node_var)

    # Update the versions with the properties and versions provided
    for key, value in properties.items():
        if version:
            current_versions[key] = version

    updated_versions = json.dumps(current_versions)

    set_statements = [f"{node_var}.versions_metadata = '{updated_versions}'"]
    for key, value in properties.items():
        if isinstance(value, (float, int, Decimal)):
            set_statements.append(f"{node_var}.{key} = {value}")
        else:
            escaped_value = escape_string(str(value))
            set_statements.append(f"{node_var}.{key} = '{escaped_value}'")

    props_str = ', '.join(set_statements)

    query = f"MATCH ({node_var}:{node_type} {{{id_property_name}: '{node_id}'}}) SET {props_str}"

    return query



def dev1():
#      def _get_versions_dict(tx, node_type, node_id, id_property_name='id', node_var='n'):
#  
#    query_get_versions_dict()
    return

if __name__=='__main__':
    branches=['dev1']
    for b in branches:
        globals()[b]()


"""
"""
