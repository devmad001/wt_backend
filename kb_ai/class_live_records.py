import os
import sys
import codecs
import json
import re
import random
from copy import deepcopy


LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")

from get_logger import setup_logging
logging=setup_logging()

#0v1# JC  Sep 14, 2023  Init

"""
    LIVE RECORDS
    - ideally just iterate over all
    - facilitate sub-record processing
"""

"""
- ideally just use as normal record
- option to break down randomly or by group
- option to dump records with fewer fields just for processing
- use virtual_id so all records in a group are incremental (ie/ llm likes it)
"""

"""
The Live_Records class provides a structured framework for handling and processing batches of data records. The main intent behind this class is to offer a convenient way to segment records, process them in chunks, and then update their statuses accordingly.

Flexible Record Management: Store and manage records with optional fields inclusion or exclusion.
Batch Processing: With the built-in grouping mechanisms, users can process records in specific group sizes, in halves, or randomize their processing order. This is especially useful for operations that need batch processing or limited-resource scenarios.
Virtual ID System: To ease the processing and ensure records' uniqueness during operations, Live_Records assigns a virtual ID to each record. This virtual ID is transparent to the user and gets mapped back to the real ID once processing is complete.
Status Tracking: Every record comes with a status that gets updated throughout its lifecycle. This makes it easier to track which records have been processed, which are pending, and which encountered errors.
"""

class Live_Records:
    
    def __init__(self, meta=None, group_size=None):
        self.meta = meta if meta else {}
        self.data_records = {}
        self.group_size = group_size or 0
        self.record_status = {}

        # To track fields for inclusion/exclusion
        self.only_use_these_fields = []
        self.exclude_fields = []
        self.virtual_to_real_id={}

        # Extra mta
        self.record_type=''

    def sample_record(self):
        # For checking schema/transaction_id/etc.
        if self.data_records:
            for kkey in self.data_records:
                return self.data_records[kkey]
        else:
            return {}

    def list_field_names(self):
        ## All or one
        if self.data_records:
            for kkey in self.data_records:
                return list(self.data_records[kkey].keys())
        else:
            return []

    def set_record_type(self, record_type):
        ## should be schema approved
        #- assumes all records are of this type
        self.record_type = record_type
        return

    def set_records(self, records, only_use_these_fields=[], exclude_fields=[]):
        ## .exclude_fields:  Exclude fields during group dumps (fields preserved till end dump)
        self.only_use_these_fields = only_use_these_fields
        self.exclude_fields = exclude_fields
        
        if not self.group_size: self.group_size=len(records)  #default full

        for i, record in enumerate(records):
            record_copy = deepcopy(record)
            if 'id' in record_copy:
                record_copy['idd'] = record_copy.pop('id')
            
            record_copy['id'] = str(i)
            self.data_records[record_copy['id']] = record_copy
            self.record_status[record_copy['id']] = "unprocessed"

    def _get_next_group(self, size, specific_ids=[]):
        group = []

        if specific_ids:
            # ie/ randomized and passed as specific_ids
            for record_id in specific_ids:
                if self.record_status[record_id] == "unprocessed" and len(group) < size:
                    self.record_status[record_id] = "processing"
                    group.append(record_id)
        else:
            ## Sequential walk
            for record_id, record in self.data_records.items():
                if self.record_status[record_id] == "unprocessed" and len(group) < size:
                    self.record_status[record_id] = "processing"
                    group.append(record_id)

        return group

    def _half_group(self):
        self.group_size = max(1, self.group_size // 2)
        return self._get_next_group(self.group_size)

    def _randomize_remaining_records_to_process(self):
        unprocessed_ids = [record_id for record_id, status in self.record_status.items() if status == "unprocessed"]
        random.shuffle(unprocessed_ids)
        return self._get_next_group(self.group_size,specific_ids=unprocessed_ids)

    def _first_x_items(self, x):
        return self._get_next_group(x)

    def dump_all_records(self):
        # Recall, could iter + update but better to pass around!
        #- recall, id is internal to Record for organizing
        all_records=[]
        #for id in self._get_next_group(len(self.data_records)):
        all_records=self.dump_sub_records(group_size=len(self.data_records),method='all')
        return all_records

    def dump_sub_records(self, group_size=None, method='default'):
        # Warning mechanism for records still in "processing"
        self.virtual_to_real_id = {}

        processing_records = [record_id for record_id, status in self.record_status.items() if status == "processing"]
        if processing_records:
            print(f"Warning: There are {len(processing_records)} records still in 'processing' state. Consider using 'process_failed' or 'process_and_update_records' to update their status.")
    
        if group_size:
            self.group_size = group_size
        group_ids = []

        if method == 'half_group':
            group_ids = self._half_group()
        elif method == 'randomize':
            group_ids = self._randomize_remaining_records_to_process()
        elif method == 'first_x':
            group_ids = self._first_x_items(group_size)
        elif method == 'all':
            group_ids = self._get_next_group(len(self.data_records))
        else:  # default method
            group_ids = self._get_next_group(self.group_size)
    
        # Filter fields and assign virtual id for the dump
        group = []
        virtual_id = 1
        for record_id in group_ids:
            record = deepcopy(self.data_records[record_id])
            if self.only_use_these_fields:
                record = {k: record[k] for k in self.only_use_these_fields if k in record}
            else:
                for field in self.exclude_fields:
                    record.pop(field, None)
                    
            record['id'] = str(virtual_id)  # Assign the virtual id
            self.virtual_to_real_id[str(virtual_id)] = record_id  # Store the mapping
            virtual_id += 1
    
            group.append(record)
    
        ##  only_use_these_fields=schema.get('only_use_these_fields',[]) #['transacti
        return group

    def process_failed(self, failed_records, reasons=[]):
        # unused reasons for now
        for record in failed_records:
            virtual_id = record['id']
            real_id = self.virtual_to_real_id.get(virtual_id)
            if not real_id:
                raise ValueError(f"Virtual ID {virtual_id} not found in mapping.")
                
            if real_id in self.data_records:
                self.record_status[real_id] = "unprocessed"
            else:
                raise ValueError(f"Record with ID {real_id} not found.")

    def process_and_update_records(self, updated_records):
        for record in updated_records:
            virtual_id = record['id']
            real_id = self.virtual_to_real_id.get(virtual_id)
            if not real_id:
                print ("[debug] raw map: "+str(self.virtual_to_real_id))
                raise ValueError(f"Virtual ID {virtual_id} not found in mapping.")
    
            if real_id in self.data_records:
                # Update the main record with the changes from the updated record
                self.data_records[real_id].update(record)
                self.record_status[real_id] = "processed"
            else:
                raise ValueError(f"Record with ID {real_id} not found.")

    def check_all_succeeded(self):
        return all(status == "processed" for status in self.record_status.values())

    def list_failures(self):
        return [record for record_id, record in self.data_records.items() if self.record_status[record_id] != "processed"]

    def size(self):
        return len(self.data_records)
    
    def count_processed(self):
        count_processed = sum(1 for status in self.record_status.values() if status == "processed")
        return count_processed

    def count_unprocessed(self):
        count_processed = sum(1 for status in self.record_status.values() if status == "processed")
        unprocessed=len(self.record_status)-count_processed
        return unprocessed

    def FINALLY_get_all_records(self,raise_pending_error=False):
        # Error mechanism if there are records in "processing"
        processing_records = [record_id for record_id, status in self.record_status.items() if status == "processing"]
        if processing_records:
            if raise_pending_error:
                raise RuntimeError(f"Error: There are {len(processing_records)} records still in 'processing' state. Ensure all records are processed before calling this method.")
            else:
                logging.info(f"Warning: There are {len(processing_records)} records still in 'processing' state. Ensure all records are processed before calling this method.")

        processed = []
        unprocessable = []
        
        for record_id, record in self.data_records.items():
            record_copy = deepcopy(record)
            if 'idd' in record_copy:
                record_copy['id'] = record_copy.pop('idd')
            
            if self.record_status[record_id] == "processed":
                if 'idd' in record_copy:
                    del record_copy['idd']  # Remove internal tracking 'id', not the original 'id'
                processed.append(record_copy)
            else:
                unprocessable.append(record_copy)
        
        return processed, unprocessable



def dev1():

    b=['std']
    b=['exclude']

    if 'exclude' in b:

        # 1. Create an instance of Live_Records
        #live_records = Live_Records(group_size=5) # assuming a group size of 5 for this example
        live_records = Live_Records()
        live_records = Live_Records(group_size=3)
        
        # 2. Set initial records
        initial_records = [{'id': '1', 'data': 'Data_A'}, {'id': '2', 'data': 'Data_B'}, {'id': '3', 'data': 'Data_C'}, {'id': '4', 'data': 'Data_D'}, {'id': '5', 'data': 'Data_E'}, {'id': '6', 'data': 'Data_F'}, {'id': '7', 'data': 'Data_G'}, {'id': '8', 'data': 'Data_H'}, {'id': '9', 'data': 'Data_I'}, {'id': '10', 'data': 'Data_J'}]
        print ("[GIVEN] "+str(initial_records))

        live_records.set_records(initial_records,exclude_fields=['data'])
        
        # 3. Dump sub-records using default method
        fetched_records = live_records.dump_sub_records()

        print ("SUB: "+str(fetched_records))

        live_records.process_and_update_records(fetched_records)

        final_good,final_unprocessed=live_records.FINALLY_get_all_records()

        print ("FINAL: "+str(final_good))
        print ("FINAL un: "+str(final_unprocessed))



    if 'std' in b:
    
        # Assuming the Live_Records class is defined as above...
        
        # 1. Create an instance of Live_Records
        live_records = Live_Records(group_size=5) # assuming a group size of 5 for this example
        
        # 2. Set initial records
        initial_records = [{'id': '1', 'data': 'Data_A'}, {'id': '2', 'data': 'Data_B'}, {'id': '3', 'data': 'Data_C'}, {'id': '4', 'data': 'Data_D'}, {'id': '5', 'data': 'Data_E'}, {'id': '6', 'data': 'Data_F'}, {'id': '7', 'data': 'Data_G'}, {'id': '8', 'data': 'Data_H'}, {'id': '9', 'data': 'Data_I'}, {'id': '10', 'data': 'Data_J'}]
        live_records.set_records(initial_records)
        
        # 3. Dump sub-records using default method
        fetched_records = live_records.dump_sub_records()
        
        # 4. Simulate processing: let's assume that even ID records fail and odd ID records succeed
        failed_group = [record for record in fetched_records if int(record['idd']) % 2 == 0]
        good_group=[record for record in fetched_records if record not in failed_group]
    
        # 'status'
        live_records.process_failed(failed_group) #<-- changes from processing to unprocessed
        live_records.process_and_update_records(good_group)
        
        # 5. Dump sub-records using the 'half_group' method
        next_group = live_records.dump_sub_records(method='half_group')
    
        ##  assume all good good
        live_records.process_and_update_records(next_group)
        
        # 6. At the end, retrieve all records, separated into processed and unprocessable
        processed_records, unprocessable_records = live_records.FINALLY_get_all_records()
        
        # Print the results
        print("Processed Records:", processed_records)
        print("Unprocessable Records:", unprocessable_records)
        

    return

def dev_sample_sub_groups():
    if 'small group experiments' in []:
        ## Small group
        Records.set_records(all_transactions,only_use_these_fields=[],exclude_fields=['idd','case_id'])
    
        sub_records=Records.dump_sub_records(group_size=3,method='default')
        print ("SUB REC 1: "+str(sub_records))
    
        ## Assume process and all good
        #**ack is key otherwise will reprocess!
        Records.process_and_update_records(sub_records)
    
        sub_records=Records.dump_sub_records(group_size=3,method='default')
        print ("SUB REC 2: "+str(sub_records))
        Records.process_and_update_records(sub_records)
    
        sub_records=Records.dump_sub_records(group_size=2,method='default')
        print ("SUB REC 3: "+str(sub_records))
    
    
    return

if __name__=='__main__':
    branches=['dev1']
    for b in branches:
        globals()[b]()

"""
SAMPLE:
import unittest

class TestLiveRecords(unittest.TestCase):

    def setUp(self):
        self.records = [{"id": str(i)} for i in range(1, 11)]
        self.meta = {}
        self.lr = Live_Records(self.records, self.meta)

    def test_default_iteration(self):
        group = self.lr.iter_records_group_size()
        self.assertEqual(len(group), 10)  # Should fetch all records since default group size is set to length of records

    def test_half_group_iteration(self):
        self.lr.group_size = 8
        group = self.lr.iter_records_group_size(method='half_group')
        self.assertEqual(len(group), 4)  # Should fetch half of the set group size

    def test_randomize_iteration(self):
        group = self.lr.iter_records_group_size(method='randomize')
        self.assertEqual(len(group), 10)  # Should fetch all records in randomized order

    def test_first_x_items(self):
        group = self.lr.iter_records_group_size(group_size=5, method='first_x')
        self.assertEqual(len(group), 5)  # Should fetch first 5 records

    def test_process_success_and_failure(self):
        group = self.lr.iter_records_group_size()
        self.lr.process_failed(group[:5])  # First 5 records marked as failed
        self.lr.process_succeeded(group[5:])  # Last 5 records marked as succeeded

        self.assertFalse(self.lr.check_all_succeeded())
        self.assertEqual(len(self.lr.list_failures()), 5)

    def test_all_success(self):
        group = self.lr.iter_records_group_size()
        self.lr.process_succeeded(group)
        self.assertTrue(self.lr.check_all_succeeded())


if __name__ == '__main__':
    unittest.main()
"""