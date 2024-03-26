import time
import os
import sys
import codecs
import json
import re
import datetime

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"..")

from get_logger import setup_logging
logging=setup_logging()


#0v1# JC  Sep  2, 2023  Init


"""
"""

## NOTES:
#- don't make too abstract OR specific
#- see gen_records.py

"""
Record class
- store multiple versions of each field
- store strategy used to fill each field
- store timestamp of each field
- store version of each field
- store value of each field
- store parameters used to fill each field

"""

import datetime

class AI_Record:
    """
    A class to represent a record with ability to store multiple versions of each field,
    the strategy used to fill each field, timestamp of each field, version of each field,
    value of each field, and parameters used to fill each field.
    """

    def __init__(self, id):
        """
        Initializes the AI_Record with the given id.

        :param id: The id of the AI_Record
        """
        self.id = id
        self.fields = {}

    def init_fields(self, ifields):
        """
        Initializes the fields with the given initial fields.

        :param ifields: A dictionary of initial fields
        """
        self.fields.update(ifields)

    def identify_needs(self):
        """
        Identifies the fields that need to be filled.

        :return: A list of field names that need to be filled
        """
        needs_list = []
        for key, field_info in self.fields.items():
            if isinstance(field_info, str):
                continue
            elif not field_info:
                needs_list.append(key)
                continue
            elif isinstance(field_info,list) and not field_info[-1]['value']:
                needs_list.append(key)
                continue
            # Add version mismatch check here if needed
        return needs_list

    def fill_needs(self, strategies, mega={},force_needs=[]):
        """
        Fills the identified needs using the provided strategies.

        :param strategies: A dictionary of strategies to fill the needs
        :param force_needs: A list of needs that have to be filled forcefully
        :param mega:  full meta data set
        """
        needs = self.identify_needs() + force_needs
        seen = {}
        print ("[info] fill_needs: "+str(needs))
        for need in needs:
            if need in seen:
                continue
            seen[need] = True
            if need in strategies:
                strategies[need].fill(self, need,mega)

    def update_field(self, field_name, value, strategy, parameters=None):
        """
        Updates the field with the given value, strategy, and parameters.

        :param field_name: The name of the field to update
        :param value: The new value of the field
        :param strategy: The strategy used to fill the field
        :param parameters: The parameters used to fill the field
        """
        field = self.fields[field_name]
        strategy_name = strategy.__class__.__name__
        if not field or field[-1]['value'] != value or field[-1]['strategy_version'] != strategy.version:
            timestamp = datetime.datetime.now().isoformat()
            field.append({
                'value': value,
                'timestamp': timestamp,
                'strategy_version': strategy.version,
                'strategy_name': strategy_name,
                'parameters': parameters,
            })

    def manual_set_field(self, field_name, value):
        """
        Manually sets the field with the given value.

        :param field_name: The name of the field to update
        :param value: The new value of the field
        """
        if field_name not in self.fields:
            self.fields[field_name] = []
        timestamp = datetime.datetime.now().isoformat()
        entry = {
            'value': value,
            'timestamp': timestamp,
            'strategy_version': None,
            'strategy_name': 'Manual',
            'parameters': None,
        }
        self.fields[field_name].append(entry)

    def to_dict(self):
        """
        Converts the AI_Record to a dictionary.

        :return: A dictionary representation of the AI_Record
        """
        return vars(self)

    def latest_values(self):
        """
        Retrieves the latest values of all fields.

        :return: A dictionary of the latest values of all fields
        """
        return {key: value[-1]['value'] if value else None for key, value in self.fields.items()}

    def get(self, field):
        """
        Retrieves the latest value of the specified field.

        :param field: The name of the field
        :return: The latest value of the field or None if the field does not exist
        """
        try:
            value = self.fields[field][-1]['value']
        except KeyError:
            value = None
        return value




def dev1():
    id='test'
    Record=AI_Record(id=id)
    return

if __name__=='__main__':
    branches=['dev1']
    for b in branches:
        globals()[b]()




"""
"""
