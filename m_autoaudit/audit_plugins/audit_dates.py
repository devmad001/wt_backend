import os
import sys
import json
import re
import time


LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")

from auto_auditor import An_Incident
from auto_auditor import register_plugin



#0v1# JC  Mar 17, 2023  Setup



"""
    AUDIT PLUGINS:  Dates
    - Recall:  audit doesn't necessarily have the power to fix, but can suggest.  It logs!
    - Recall:  if have specific example -- add gold test.

"""

"""
SAMPLE RAW (recall jon_cypher_fix_data)
   from a_query.queryset1 import delete_transaction_node
    case_id = '65caaffb9b6ff316a779f525' #<-- ashford park MANY
    
    THINKS 2024 but 2023?!


    # Query to find and update transactions
        MATCH (n:Transaction)
        WHERE n.case_id='{}' AND n.transaction_date>'2025-01-01'
        SET n.transaction_date = REPLACE(n.transaction_date, '5958', '2022')
        SET n.transaction_date = REPLACE(n.transaction_date, '2028', '2022')
        RETURN n
"""



def dev_dates_in_future():
    return

def dev_dates_not_within_statement_period():
    return



if __name__=='__main__':
    branches=['dev_dates_in_future']
    for b in branches:
        globals()[b]()



"""

"""








