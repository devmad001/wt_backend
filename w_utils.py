import os
import sys
import codecs
import json
import re
import copy

import configparser as ConfigParser

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")



#0v1# JC  Sep 26, 2023  Init

"""
    COMMON UTILITIES
"""


def levenshtein(s1, s2):
    if len(s1) < len(s2):
        return levenshtein(s2, s1)

    # len(s1) >= len(s2)
    if len(s2) == 0:
        return len(s1)

    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    
    return previous_row[-1]

def similarity_string(s1, s2):
    # Normalize to lowercase
    s1=copy.deepcopy(s1).lower()
    s2=copy.deepcopy(s2).lower()
    lev_distance = levenshtein(s1, s2)
    max_length = max(len(s1), len(s2))
    try: similarity_percent = (1 - lev_distance / max_length)
    except: similarity_percent=0
    return similarity_percent

def util_get_modified_keys(original_dict, modified_dict):
    """
    This function identifies the keys of the top-level items that were modified 
    from the original_dict to the modified_dict.
    
    Parameters:
    original_dict (dict): The original dictionary.
    modified_dict (dict): The dictionary after modifications.

    Returns:
    list: A list of keys of modified top-level items in the dictionary.
    """
    modified_keys = []

    # Check for modified and deleted keys
    for key in original_dict:
        if key not in modified_dict or original_dict[key] != modified_dict[key]:
            modified_keys.append(key)

    # Check for newly added keys
    for key in modified_dict:
        if key not in original_dict:
            modified_keys.append(key)

    return modified_keys


def am_i_on_server():
    # Check for nt in os
    if os.name=='nt':
        return False
    else:
        return True
    
def get_base_endpoint():
    if am_i_on_server():
        base_domain='https://core.epventures.co'
    else:
        base_domain='http://127.0.0.1:8008'
    return base_domain

def get_ws_endpoint():
    #** ideally config loading is NOT in utils but easy global
    ### ROOT CONFIG
    RootConfig = ConfigParser.ConfigParser()
    RootConfig.read(LOCAL_PATH+"w_settings.ini")
    
    FRAUDWS_PORT=RootConfig.get('services','fraudws_port')
    FRAUDWS_subdomain=RootConfig.get('services','fraudws_subdomain')
    FRAUDWS_domain=RootConfig.get('services','fraudws_domain')
    
    if am_i_on_server():
        WS_ENDPOINT='https://'+FRAUDWS_subdomain+"."+FRAUDWS_domain
    else:
        WS_ENDPOINT='http://127.0.0.1:'+str(FRAUDWS_PORT)
    return WS_ENDPOINT


def get_priority_keys(jsonl):
    ## Date
    ## Amount or total
    #** assume generally that field is accessible across
    date_key=None
    amount_key=None
    name_key=None
    
    priority_amounts = ['amount', 'total']
    priority_names = ['transaction_type', 'name']
    priority_dates = ['date']

    if jsonl:
        record = jsonl[0]
        print("[debug] record: {}".format(record))
    
        # Case amount: Identify potential amount keys based on priority
        potential_amount_keys = [key for key in record if any(amount in key.lower() for amount in priority_amounts)]
        print ("POT A: "+str(potential_amount_keys))
    
        # Assign amount_key based on priority
        amount_key = next((key for amount in priority_amounts for key in potential_amount_keys if amount in key.lower()), '')
        print ("POT A: "+str(amount_key))
    
        # Case date: Assign date_key based on priority
        date_key = next((key for date in priority_dates for key in record if date in key.lower()), '')
    
        # Case node name: Assign name_key based on priority, excluding date_key and amount_key
        name_key = next((key for name in priority_names for key in record if name in key.lower() and key != date_key and key != amount_key), None)
        
        # If no priority names match, assign to a key that isn't date_key or amount_key
        if name_key is None:
            name_key = next((key for key in record if key != date_key and key != amount_key), None)
            #if not name_key: name_key=amount_key

    ## Default empty
    if date_key is None: date_key = ''
    if amount_key is None: amount_key = ''
    if name_key is None: name_key = ''
    
    return date_key, amount_key, name_key


def dev_priority_fields():
    return

def test_am_i_on_server():
    print("am_i_on_server: {}".format(am_i_on_server()))
    return

if __name__=='__main__':
    branches=['dev_manage_services']
    branches=['dev_priority_fields']
    branches=['test_am_i_on_server']

    for b in branches:
        globals()[b]()

