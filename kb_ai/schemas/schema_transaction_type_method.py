import os
import sys
import codecs
import json
import re

from fastapi import FastAPI

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")

from get_logger import setup_logging
logging=setup_logging()
from schemas.SCHEMA_kbai import gold_schema_definition


#0v3# JC  Feb  2, 2024  Add amount_sign to schema only fields (cause checks no meta otherwise)
#0v2# JC  Oct  7, 2023  Get transaction method id via llm as well! ie/ Check id, zelle id, wire transfer id, 
#                          ^ these will feed the PROCESSED_BY node id
#0v1# JC  Sep 17, 2023  Init


"""
    NOTES ON TRANSACTION TYPE + METHOD
    - see SCHEMA_kbai.py gold top
"""

"""
TRANSACTION RECORD SAMPLE JAN 24
 {'transaction_date': '2021-09-24', 'filename_page_num': 194, 'is_credit': False, 'account_number': '3340 4918 5630', 'transaction_amount': 0.55, 'section': 'Withdrawals and other debits', 'label': 'Transaction', 'statement_id': '65a8168eb3ac164610ea5bc2-2021-09-01-3340 4918 5630-72d85b81-c416-4ffd-950c-f0c1fd62f251.pdf', 'transaction_description': 'AMERICAN EXPRESS DES:AXP DISCNT ID:0000019109 INDN:PLANET SMOOT5104512413 CO ID:1134992250 CCD', 'account_id': '65a8168eb3ac164610ea5bc2-3340 4918 5630', 'filename': '72d85b81-c416-4ffd-950c-f0c1fd62f251.pdf', 'amount_sign': '-', 'case_id': 'test_default_65a8168eb3ac164610ea5bc2_194', 'id': 'test_default_65a8168eb3ac164610ea5bc2_194-d4aeec2cc09ed62a4420e3f929fdda8ff43b904a48456eb4321106d96552506c'}
"""

"""
GOLD DEF SAMPLE ONLY:
"examples": {
 SAMPLE ONLY!   "transaction_type": ["withdrawal", "deposit", "book_transfer","loan_disbursement", "loan_repayment", "transfer", "payment", "reversal", "refund", "fee", "interest_received", "interest_paid", "Venmo", "other"],
  SAMPLE ONLY!                "transaction_method": ["ATM", "wire_transfer", "check", "cash", "fed_wire", "debit_card", "credit_card", "online_payment", "mobile_payment", "other"]
            }
"""

### Load examples from gold schema!
## From SCHEMA_kbai.py (or import)
transaction_type_examples=[]
transaction_method_examples=[]
for node_type in gold_schema_definition['nodes']:
    node=gold_schema_definition['nodes'][node_type]
    if node_type=='Transaction':
        for field_name in node['examples']:
            if field_name=='transaction_type':
                transaction_type_examples=node['examples'][field_name]
                transaction_method_examples=node['examples']['transaction_method']


#############################################
#  STANDARDIZE!
# inner schema version 1.4
#_ validate on
#############################################
schema={}
schema['kind']='transaction_type_method_goals'
#schema['version']=1.4
schema['version']=1.5# Oct 17 1.4 -> 1.5 is_cash_involved, is_wire_transfer
schema['source_node_label']='Transaction'  #Update field
schema['kb_update_type']='field_update' 
schema['fields_to_update']=['transaction_type','transaction_method','is_cash_involved','is_wire_transfer']
#Feb 2, 2024schema['only_use_these_fields']=['transaction_description','section']  #For input
schema['only_use_these_fields']=['transaction_description','section','amount_sign']  #For input

#OTHER2# NON JSON RETURNED: schema['header']="""For each bank statement deposit transaction provided in the JSON data, add the sender_entity_name and sender_entity_type. The sender_entity_name & souce_entity_type should be inferred from the description & section. Return the response in valid JSON format."""

#OTHER2#  schema['header']="""For each bank statement deposit transaction provided in the JSON data, add the sender_entity_name and sender_entity_type. The sender_entity_name & souce_entity_type should be inferred from the description & section. Return the response in valid JSON format (don't explain it)."""

schema['header']="""For each bank statement deposit transaction provided in the JSON data add the:  transaction_type, transaction_method, transaction_method_id, is_cash_involved and is_wire_transfer. The values can be inferred from the transaction description & section. The transaction method id includes things like: the check number, zelle id, wire transfer id,etc. Return the response in valid JSON format (don't explain it)."""

schema['bullets']=[]

schema['bullets']+=['- Typical transaction_types: '+', '.join(transaction_type_examples)]
schema['bullets']+=['- Typical transaction_methods: '+', '.join(transaction_method_examples)]
schema['bullets']+=['- Typical is_cash_involved: True, False']
schema['bullets']+=['   * is_cash_involved=False if debit_card purchase']
schema['bullets']+=['- Typical is_wire_transfer: True, False']

schema['examples']=[]
schema['examples']+=[
            {
                "transaction_description": "Zelle Withdrawl To main account Jpm671584743",
                "section": "Electronic Withdrawl",
                "transaction_type":"withdrawl",
                "transaction_method": "zelle",
                "transaction_method_id": "Jpm671584743",
                "is_cash_involved": False,
                "is_wire_transfer": True,
                "id": 1
            }
            ]
#dynamic# schema['examples']+=[
#dynamic#             {
#dynamic#                 "transaction_description": "Reversal: Orig CO id:American Express",
#dynamic#                 "section": "Deposits and Additions",
#dynamic#                 "transaction_type":"reversal",
#dynamic#                 "transaction_method": "other",
#dynamic#                 "transaction_method_id": "unknown",
#dynamic#                 "id": 2
#dynamic#             }
#dynamic#             ]

schema['examples']+=[
            {
                "transaction_description": "Remote Online Deposit",
                "section": "Deposits and Additions",
                "transaction_type":"deposit",
                "transaction_method": "online_payment",
                "transaction_method_id": "unknown",
                "is_cash_involved": False,
                "is_wire_transfer": False,
                "id": 2
            }
            ]
schema['examples']+=[
            {
                "transaction_description": "ACCOUNT TRANSFER TRSF FROM 000245202689 2106527124",
                "section": "Deposits and Additions",
                "transaction_type":"transfer",
                "transaction_method": "other",
                "transaction_method_id": "2106527124",
                "is_cash_involved": False,
                "is_wire_transfer": True,
                "id": 2
            }
            ]
schema['examples']+=[
              {
        "transaction_description": "PAYCHEX - RCX    DES:PAYROLL    ID:95475300004896X  INDN:SKYVIEW\nCAPITAL GROUP   CO ID:1161124166 CCD",
        "section": "Transactions",
        "transaction_type":"deposit",
        "transaction_method": "online_payment",
        "transaction_method_id": "95475300004896X",
        "is_cash_involved": False,
        "is_wire_transfer": True,
        "id": "5"
        }
        ]

### DYNAMICS ARE INCLUDED FIRST IN EXAMPLES LIST
#- field specific examples based on document text context OR data to process text
#- given_data matches applied first, then doc-wide, then generic examples
#- e.g. 
schema['dynamics']=[]

schema['dynamics']+=[('given_data',r'Reversal',
            {
                "transaction_description": "Reversal: Orig CO id:American Express",
                "section": "Deposits and Additions",
                "transaction_type":"reversal",
                "transaction_method": "other",
                "transaction_method_id": "unknown",
                "is_cash_involved": False,
                "is_wire_transfer": False,
                "id": 2
            }
            )]
# Beware, doc_text can be very long
schema['dynamics']+=[('doc_text',r'Reversal',
            {
                "transaction_description": "Reversal: Orig CO id:American Express",
                "section": "Deposits and Additions",
                "transaction_type":"reversal",
                "transaction_method": "other",
                "transaction_method_id": "unknown",
                "is_cash_involved": False,
                "is_wire_transfer": False,
                "id": 2
            }
            )]



def dev1():
    print(generate_cypher_from_schema(schema_definition))
    return

if __name__=='__main__':
    branches=['dev1']
    for b in branches:
        globals()[b]()

"""
"""
