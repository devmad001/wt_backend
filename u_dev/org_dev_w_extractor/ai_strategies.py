import time
import os
import sys
import codecs
import json
import re

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"..")

from get_logger import setup_logging
logging=setup_logging()


#0v1# JC  Sep  2, 2023  Init


"""
IMPORT ALGS AS REQUIRED

"""

class FillStrategy:
    version = 1.0
    @staticmethod
    def fill(record, needs, mega):
        raise NotImplementedError()

class RecordTypeStrategy(FillStrategy):
    version = 1.0

    @staticmethod
    def fill(record, needs,mega):
        if False and needs == 'type':
            if not record.fields['email']:
                value = 'Unknown'
            elif record.fields['email'][-1]['value'] == 'default@example.com':
                value = 'Generic'
            else:
                value = 'Specific'
            record.update_field('type', value, RecordTypeStrategy)

class TransactionsFillStrategy(FillStrategy):
    version = 1.0
    """
        Transaction extraction strategy v1.0
        NEED:  if not transactions or last value version < active version
        LOGIC:
        - given schema for a transaction
        - for each pdf page
        - ask llm to extract transactions from page
        - include section of page that transaction was found in
        - don't do further classification ie/ "is cash"
        - [ ] add absolute field checking vs schema
    """

    @staticmethod
    def fill(record, needs,mega):

        ## LOCAL NEEDS PREVIEW
        local_needs=[]
        if not record.fields['transactions']:
            local_needs+=['extract_transactions']
        if 'extract_transactions' in needs:
            local_needs+=['extract_transactions']

        ## FULFILLMENT
        if 'extract_transactions' in local_needs:
            print ("FILLING TRANSACTIONS")
            ## Apply logic

        if False and needs == 'type':
            if not record.fields['email']:
                value = 'Unknown'
            elif record.fields['email'][-1]['value'] == 'default@example.com':
                value = 'Generic'
            else:
                value = 'Specific'
            record.update_field('type', value, RecordTypeStrategy)


def record_to_json(record, filename):
    with open(filename, 'w') as f:
        json.dump(record.to_dict(), f)


def record_from_json(filename):
    with open(filename, 'r') as f:
        data = json.load(f)
        record = record(data['name'])
        record.fields = data['fields']
        return record



if __name__=='__main__':
    branches=['dev1']
    for b in branches:
        globals()[b]()




"""
"""
