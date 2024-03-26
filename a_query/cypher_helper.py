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


#0v2# JC  Sep 23, 2023  Number support (float, decimal, int)
#0v1# JC  Sep  7, 2023  Init

## REF:
# https://github.com/emehrkay/Pypher



## Rare options for cleaning (but usually only when fails)
def try_clean_cypher(cypher):
    #0v1# Very basic and only on error, consider combining with escape_str
    #*** CENTRALIZE THIS!
    ## Only run when cypher fails since should be rare
    #1/  \$ must be \\$
    cypher=re.sub(r'\\\$', '\\\\$', cypher)
    cypher=cypher.replace(' \\$', ' \\\\$') # " \$"

    #2 double left right specials
    cypher = cypher.replace('“', '\"').replace('”', '\"')

    #3/ optional
    #cypher = cypher.encode('ascii', 'ignore').decode('ascii') #back to str

    #4/ apostrophe within ' this can't ' to  ' this can\'t '
    cypher= re.sub(r"(\w)'(\w)", r"\1\\'\2", cypher)


    return cypher


def escape_string(value):
    #0v3#
    #Assumes string


    # Ensure value is a string
    if not isinstance(value, (str, bytes)):
        # Convert value to string if it's not None; otherwise, set it to an empty string
        value = str(value) if value is not None else ''

    # Normalize any already escaped single quotes
    value = re.sub(r"''", "'", value)
    
    # Escape single quotes by doubling them up for Cypher
    value = value.replace("'", "''")

    # Assume that dollar signs prefixed with a backslash should be unescaped
    value = re.sub(r'\\\$','$', value)
    
    # Replace 'â€œ' and 'â€' with a standard double quote
    value = value.replace('â€œ', '\"').replace('â€', '\"')

    return value


def sample_cypher():
    #TBD as not easy to work with
    # Example
    node_data = {
        'type': 'Person',
        'properties': {
            'name': 'John Doe',
            'age': 25
        }
    }
    
    cypher_query = build_cypher_from_dict(node_data)
    print ("[dev] from: "+str(node_data)+" ==> "+str(cypher_query))


    p = build_cypher_from_dict(node_data)
    print("Parameterized Query:", p)
    print("Parameters:", p.bound_parameters)
    
    # Interpolate parameters into query (not recommended for execution, but okay for debugging):
    full_query = str(p)
    for param_name, param_value in p.bound_parameters.items():
        full_query = full_query.replace(f"${param_name}", str(param_value))
    
    print("Full Query:", full_query)

    return



def cypher_create_node(node_type, properties, node_var='n'):
    props_list = []
    if 'label' in properties:
        raise ValueError("The 'label' property is reserved for use by the Cypher query builder.")
    properties['label']=node_type

    for key, value in properties.items():
        if isinstance(value, (float, int, Decimal)):
            props_list.append(f"{key}: {value}")
        else:
            escaped_value=escape_string(value)
            props_list.append(f"{key}: '{escaped_value}'")
    props_str = ', '.join(props_list)
    return f"MERGE ({node_var}:{node_type} {{{props_str}}})\n"

def cypher_create_update_node(node_type, properties, unique_property='id', node_var='n'):
    #[ ] beware utf-8 fault possible if printed to screen
    if 'label' in properties:
        raise ValueError("The 'label' property is reserved for use by the Cypher query builder.")
    properties['label']=node_type
    unique_value = properties[unique_property]
    if isinstance(unique_value, (float, int, Decimal)):
        unique_prop_str = f"{unique_property}: {unique_value}"
    else:
        unique_prop_str = f"{unique_property}: '{unique_value}'"

    props_list = []
    for key, value in properties.items():
        if isinstance(value, (float, int, Decimal)):
            props_list.append(f"{key}: {value}")
        else:
            escaped_value=escape_string(value)
            props_list.append(f"{key}: '{escaped_value}'")
            
    props_str = ', '.join(props_list)
    set_str = f"{node_var} += {{{props_str}}}"

    query = (
        f"MERGE ({node_var}:{node_type} {{{unique_prop_str}}}) "
        f"ON CREATE SET {set_str} "
        f"ON MATCH SET {set_str}"
    )
    return query


def cypher_create_relationship(source_type, target_type, rel_type, source_props, target_props, from_node_var='a', to_node_var='b'):
    if len(source_props.keys())>1 or len(target_props.keys())>1:
        raise ValueError("Only one property per node is supported for now.")
    
    #0v2# number support
    source_props_str_list = []
    for key, value in source_props.items():
        if isinstance(value, (float, Decimal, int)):
            source_props_str_list.append(f"{key}: {value}")
        else:
            escaped_value=escape_string(value)
            source_props_str_list.append(f"{key}: '{escaped_value}'")
    source_props_str = ', '.join(source_props_str_list)
    
    target_props_str_list = []
    for key, value in target_props.items():
        if isinstance(value, (float, Decimal, int)):
            target_props_str_list.append(f"{key}: {value}")
        else:
            target_props_str_list.append(f"{key}: '{value}'")
    target_props_str = ', '.join(target_props_str_list)
    
    return f"MATCH ({from_node_var}:{source_type} {{{source_props_str}}}), ({to_node_var}:{target_type} {{{target_props_str}}}) MERGE ({from_node_var})-[r:{rel_type}]->({to_node_var}) RETURN r"

#D def VAR_ONLY_cypher_add_create_relationship(rel_type, rel_props={}, rel_var='r', from_node_var='a', to_node_var='b'):
#D     ## To be used if nodes where just created so vars a and b exist
#D     rel_props_str = ', '.join([f"{key}: {value!r}" for key, value in rel_props.items()])
#D     #return f"MERGE ({from_node_var})-[r:{rel_type} {{{rel_props_str}}}]->({to_node_var}) RETURN r"
#D     return f"MERGE ({from_node_var})-[{rel_var}:{rel_type} {{{rel_props_str}}}]->({to_node_var})"+"\n"

#0v2# Sep 23, 2023  Add float support (not just as strings)
#[ ] add documentation but essentially allows various vars or ids to be passed
#    ^ though may have removed that requirement.  better to create nodes first completely
def cypher_add_create_relationship(rel_type, **kwargs):
    cypher = ""

    #0v2#  Convert the relationship properties dict to Cypher format
    rel_props_list = []
    for key, value in kwargs['rel_props'].items():
        if isinstance(value, (float, Decimal,int)):
            rel_props_list.append(f"{key}: {value}")
        else:
            escaped_value=escape_string(value)
            rel_props_list.append(f"{key}: '{escaped_value}'")
    
    rel_props_cypher = "{" + ", ".join(rel_props_list) + "}"

    # Check if we are matching using a variable for the 'from' node (e.g., sender12) or an id
    if 'from_node_var' in kwargs:
        from_node = kwargs['from_node_var']
    elif 'from_node_id' in kwargs and 'from_node_label' in kwargs:
        from_node = kwargs['from_node_label'].lower()  # Using lowercase variable name to avoid conflicts
        cypher += f"MATCH ({from_node}:{kwargs['from_node_label']}{{id: '{kwargs['from_node_id']}'}})\n"
    else:
        raise ValueError("Either 'from_node_var' or 'from_node_id' and 'from_node_label' must be provided.")
    
    # Check if we are matching using a variable for the 'to' node (e.g., receiver12) or an id
    if 'to_node_var' in kwargs:
        to_node = kwargs['to_node_var']
    elif 'to_node_id' in kwargs and 'to_node_label' in kwargs:
        to_node = kwargs['to_node_label'].lower()  # Using lowercase variable name to avoid conflicts
        cypher += f"MATCH ({to_node}:{kwargs['to_node_label']}{{id: '{kwargs['to_node_id']}'}})\n"
    else:
        raise ValueError("Either 'to_node_var' or 'to_node_id' and 'to_node_label' must be provided.")
    
    # Create the relationship
    relationship = f"{kwargs['rel_var']}:{rel_type} {rel_props_cypher}"
    cypher += f"MERGE ({from_node})-[{relationship}]->({to_node})\n"
    
    return cypher


### PROPERTY UPDATES
#- NON-VERSIONS SUPPORT
#     ^ for  _VERSIONS support (requires neo4j fetch see cypher_helper_neo4j.py)
def cypher_add_fields_to_node(node_type, properties, node_id, id_property_name='id', node_var='n'):
    """
    node_type: The type of the node you want to update.
    properties: The properties you want to add or update.
    node_id: The unique identifier for the specific node you want to update.
    id_property_name: The name of the property you use as an identifier (default is 'id').
    node_var: The variable name you want to use for the node in your Cypher query.
    """
    
    props_list = []
    for key, value in properties.items():
        if isinstance(value, (float, Decimal,int)):
            props_list.append(f"{node_var}.{key} = {value}")
        else:
            escaped_value=escape_string(value)
            props_list.append(f"{node_var}.{key} = '{escaped_value}'")
    
    props_str = ', '.join(props_list)
    
    # Here's where you specify the unique identifier for the node you want to update.
    return f"MATCH ({node_var}:{node_type} {{{id_property_name}: '{node_id}'}}) SET {props_str}" + "\n"


## Example usage
#node_creation_str = "CREATE (a:Account {name: 'mainAccount'}), (b:Transaction {description: 'Transfer to Zelle'}) "
#relationship_str = cypher_create_relationship(
#    rel_type="DEBIT",
#    rel_props={"amount": 1000}
#)


def dev1():
    node_data = {
        'node_type': 'Person',
        'properties': {
            'name': 'John Doe',
            'age': 25
        }
    }
    cypher=cypher_create_node(**node_data)

    print ("{dev1} from: "+str(node_data)+" ==> "+str(cypher))

    relationship_data = {
        'source_type': 'Person',
        'target_type': 'Company',
        'rel_type': 'WORKS_FOR',
        'source_props': {'name': 'John Doe'},
        'target_props': {'name': 'TechCorp'}
    }
    cyp=cypher_create_relationship(**relationship_data)
    print ("{dev1} from: "+str(relationship_data)+" ==> "+str(cyp))
    return



if __name__=='__main__':
    branches=['do_query']
    branches=['sample_cypher']
    branches=['dev1']
    branches=['debug_creation']
    for b in branches:
        globals()[b]()


"""
def cypher_create_relationship(source_type, target_type, rel_type, source_props, target_props, rel_props={}, from_node_var='a', to_node_var='b'):
    def format_props(props):
        return ', '.join([f"{key}: '{value}'" for key, value in props.items()])

    source_props_str = format_props(source_props)
    target_props_str = format_props(target_props)
    rel_props_str = format_props(rel_props)

    return (
        f"MATCH ({from_node_var}:{source_type} {{{source_props_str}}}),"
        f"({to_node_var}:{target_type} {{{target_props_str}}})"
        f"MERGE ({from_node_var})-[r:{rel_type} {{{rel_props_str}}}]->({to_node_var})"
        f"RETURN r"
    )

# Example usage
cypher_query = cypher_create_relationship(
    source_type="Account",
    target_type="Transaction",
    rel_type="DEBIT",
    source_props={"name": "mainAccount"},
    target_props={"description": "Transfer to Zelle"},
    rel_props={"amount": 1000}
)

"""