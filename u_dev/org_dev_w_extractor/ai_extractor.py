import time
import os
import sys
import codecs
import json
import re

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"..")

from w_storage.ystorage.ystorage_handler import Storage_Helper
from get_logger import setup_logging

from ai_record import AI_Record
from ai_strategies import *
from ai_strategies import TransactionsFillStrategy

from w_pdf.pdf_process import iter_query_documents #Dev import

logging=setup_logging()


#0v1# JC  Sep  2, 2023  Init

# Use mega{} dict to store all data for given id "doc"


"""
    Model after need based class extraction set
    - mega variable
    - iterative, storage, tracking

"""

## REF:
#- meta{} record tracks all target fields (via schema)
#- strategies implement logic for fulfilling need of each field

Storage=Storage_Helper(storage_dir=LOCAL_PATH+"../w_datasets")
Storage.init_db('mega_records')


def iter_documents():
    # Part dev
    for Doc in iter_query_documents():
        yield Doc.id,Doc
    return


strategies = {
    'extract_transactions': TransactionsFillStrategy()
}

def entry_run_extraction():
    not_strategies = []

    for id,Doc in iter_documents():
        logging.info("Processing document: %s", Doc.dump())

        record_data = Storage.db_get(id, 'mega', name='mega_records')
        if not record_data:
            record_data = {
                'id': id,
                'doc': Doc.dump(),
                'fields': {}
            }

        # Initialize AI_Record object
        Record = AI_Record(id)
        Record.init_fields(record_data.get('fields', {}))

        print ("[debug] fields: "+str(Record.fields))

        # Fulfill needs
        force_needs=['extract_transactions']
        Record.fill_needs(strategies, mega=record_data, force_needs=force_needs)

        # Update record_data fields
        record_data['fields'] = Record.fields

        # Update record in database
        Storage.db_put(id, 'mega', record_data, name='mega_records')


        break
    
    logging.info("Done processing documents")
    return



def dev1():
    ok=later
    r1=AI_Record('1234')
    strategies={'record_type':RecordTypeStrategy}
    r1.fill_needs(strategies)

    # Dump the person's dictionary to JSON
    record_to_json(r1, f"{r1.name}.json")

    # Load the person object back from the saved JSON
    loaded_person = record_from_json("John Doe.json")
    print(loaded_person.latest_values())

    return

if __name__=='__main__':
    branches=['entry_run_extraction']
    for b in branches:
        globals()[b]()




"""
"""
