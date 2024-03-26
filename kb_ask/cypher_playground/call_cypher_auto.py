import os
import sys
import codecs
import time
import json
import re

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")
sys.path.insert(0,LOCAL_PATH+"../../")

from cypher_auto import generate_neo4j_field_samples

from get_logger import setup_logging

logging=setup_logging()


#0v1# JC  Oct 17, 2023  Init

"""
"""


def call_cypher_auto_update():
    generate_neo4j_field_samples()
    return

if __name__=='__main__':
    branches=['call_cypher_auto_update']
    for b in branches:
        globals()[b]()

