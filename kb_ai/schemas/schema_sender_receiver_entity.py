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


#0v2# JC  Nov  1, 2023  Include transaction_type to guild direction of sender/receiver
#0v1# JC  Sep 13, 2023  Init

"""
    SCHEMA FOR DEFINING CREATION OF SENDER AND RECEIVER ENTITY
"""

"""
REF:
- NODE BASED!
- see dev_add_nodes.py
"""


schema={}
schema['kind']='sender_receiver_entity'
schema['version']=1.0
schema['kb_update_type']='node_create'

schema['source_node_label']='Transaction'
#schema['only_use_these_fields']=['transaction_description','section']
schema['only_use_these_fields']=['transaction_description','section','transaction_type'] #<-- added transaction_type ie/ withdrawal, deposit (helps with direction!)

schema['node_labels']=['Entity']
schema['alg_name']='create_ERS'  #<-- assigned to Transaction.algList once run (so don't fetch for processing if exists)

schema['fields_to_update']=['got_sr']  #Track node creation with field in transaction!


#NON JSON RETURNED: schema['header']="""For each bank statement deposit transaction provided in the JSON data, add the sender_entity_name and sender_entity_type. The sender_entity_name & souce_entity_type should be inferred from the description & section. Return the response in valid JSON format."""

#pre Entity# schema['header']="""For each bank statement deposit transaction provided in the JSON data, add the sender_entity_name and sender_entity_type. The sender_entity_name & souce_entity_type should be inferred from the description & section. Return the response in valid JSON format (don't explain it)."""

schema['header']="""For each bank statement transaction in the provided JSON, infer details about the sender and receiver entities: sender_entity_type, sender_entity_name, sender_entity_id (and receiver_*). Do not make things up. Always return your response as a valid json (no single quotes).

    - Entity roles are either: SENDER, RECEIVER, MAIN_ACCOUNT or OTHER
    - Typical Entity types are: individual, bank, check, cash, merchant, vendor, account, organization, other.
    - Typical Entity ids are: Check id, account number
    - Typical Entity names are: bank name, business name, individual name, organization name, other"""

schema['bullets']=[]

#NOROLES# schema['bullets']=['- Entity roles are either: SENDER, RECEIVER, MAIN_ACCOUNT or OTHER']
schema['bullets']=['- Typical Entity types are: main_account, individual, bank, check, cash, merchant, vendor, account, online, organization, other.']
schema['bullets']=['- Typical Entity ids are: Check id, account number']
schema['bullets']=['- Typical Entity names are: bank name, business name, individual name, organization name, other']

#Nov 1::
schema['bullets']=["- An 'Online Credit card payment' is receiver_entity_type: 'credit_card'"]

schema['examples']=[]

schema['examples']+=[
            {
                "transaction_description": "Remote Online Deposit",
                "section": "Deposits and Additions",
                "sender_entity_type": "online",
                "sender_entity_id": "",
                "sender_entity_name": "",
                "receiver_entity_type": "main_account",
                "receiver_entity_id": "main_account",
                "receiver_entity_name": "main_account",
                "id": 2
            }
            ]
schema['examples']+=[
            {
                "transaction_description": "ACCOUNT TRANSFER TRSF FROM 000245202689 2106527124",
                "section": "Deposits and Additions",
                "sender_entity_type": "account",
                "sender_entity_id": "000245202689",
                "sender_entity_name": "",
                "receiver_entity_type": "main_account",
                "receiver_entity_id": "main_account",
                "receiver_entity_name": "main_account",
                "id": 3
            } ]
#CCD: This could stand for "Cash Concentration or Disbursement," which is a type of ACH (Automated Clearing House) format. In the context of payroll, CCD might be used for direct deposit to an employee's bank account.
schema['examples']+=[
              {
                "transaction_description": "PAYCHEX - RCX    DES:PAYROLL    ID:95475300004896X  INDN:SKYVIEW\nCAPITAL GROUP   CO ID:1161124166 CCD",
                "section": "Transactions",
                "sender_entity_type": "organization",
                "sender_entity_id": "1161124166",
                "sender_entity_name": "SKYVIEW CAPITAL GROUP",
                "receiver_entity_type": "main_account",
                "receiver_entity_id": "main_account",
                "receiver_entity_name": "main_account",
                "id": 3
        } ]
schema['examples']+=[
              {
                "transaction_description": "GREAT-WEST TRUST DES:PAYMENTS   ID:703282404750  INDN:Skyview\nCapital         CO ID:5800220000 CTX  ADDITIONAL INFORMATION IS\nAVAILABLE FOR THIS PMT.  CONTACT A TREASURY SALES OFFICER FOR\nASSISTANCE.",
                "section": "Withdrawals and other debits",
                "sender_entity_type": "organization",
                "sender_entity_id": "703282404750",
                "sender_entity_name": "GREAT-WEST TRUST",
                "receiver_entity_type": "organization",
                "receiver_entity_id": "5800220000",
                "receiver_entity_name": "Skyview Capital",
                "id": 3
        }
        ]

schema['examples']+=[
            {
              "transaction_description": "SKYVIEW CAPI0099  DES:PAYMENTS    FL# 21355002617\nINDN:SETT-BATCH 1364873252  CO ID:1364873252 CCD  BATCH\nDESC:DISC DATA\nWIRE TYPE:WIRE OUT DATE:211221 TIME:1001 ET\nTRN:2021122100316255 SERVICE REF:374321 BNF:NEWNET\nCOMMUNICATION TECHN ID:216699928 BNF BK:JPMORGAN CHASE\nBANK, N. ID:0002 PMT DET:21C L8292793E2I20",
              "section": "Cash transactions",
                "sender_entity_type": "organization",
                "sender_entity_id": "1364873252",
                "sender_entity_name": "Skyview Capital",
                "receiver_entity_type": "organization",
                "receiver_entity_id": "216699928",
                "receiver_entity_name": "NEWNET COMMUNICATION TECHN",
                "id": 3
            }
            ]

### DYNAMICS ARE INCLUDED FIRST IN EXAMPLES LIST
schema['dynamics']=[]


### Card purchase classified as cash?? be sure as credit or debit card?
# atm_locations 

## Chase 4 p56
schema['dynamics']+=[('given_data',r'Electronic Withdrawals',
            {
                "transaction_description": "Employment Devel Edd Eftpmt 59347072 CCD ID: 2282533055",
                "section": "Electronic Withdrawals",
                "transaction_type":"payment",


                "sender_entity_type": "main_account",
                "sender_entity_id": "main_account",
                "sender_entity_name": "main_account",

                "receiver_entity_type": "government",
                "receiver_entity_id": "2282533055",
                "receiver_entity_name": "Employment Devel Edd",
                "id": 1
            }
            )]
# For chase 4 p 6 thought irs payment came from irs??
schema['dynamics']+=[('given_data',r'Irs ',
            {
                "transaction_description": "Irs Usataxpymt 220475655216495 CCD ID: 3387702000",
                "section": "Electronic Withdrawals",
                "transaction_type":"payment",

                "sender_entity_type": "main_account",
                "sender_entity_id": "main_account",
                "sender_entity_name": "main_account",

                "receiver_entity_type": "government",
                "receiver_entity_id": "IRS",
                "receiver_entity_name": "IRS",
                "id": 1
            }
            )]
schema['dynamics']+=[('given_data',r'Online Payment',
            {
                "transaction_description": "Citi Card Online Payment 23234555 Web ID: Citictp",
                "section": "Transaction detail",
                "transaction_type":"payment",

                "sender_entity_type": "main_account",
                "sender_entity_id": "main_account",
                "sender_entity_name": "main_account",

                "receiver_entity_type": "credit_card",
                "receiver_entity_id": "Citi Card",
                "receiver_entity_name": "Citi Card",
                "id": 1
            }
            )]
schema['dynamics']+=[('given_data',r'Card Purchase',
            {
                "transaction_description": "Card Purchase | 08/01 Fitness Mania Riverside CA Card 7397",
                "section": "ATM & DEBIT CARD WITHDRAWALS",
                "transaction_type":"purchase",

                "sender_entity_type": "debit_card",
                "sender_entity_id": "7397",
                "sender_entity_name": "main_account",

                "receiver_entity_type": "organization",
                "receiver_entity_id": "Fitness Mania",
                "receiver_entity_name": "Fitness Mania",
                "id": 1
            }
            )]

####    FARGO
## Possibly ok but include either way
#Money Transfer authorized on 01/22 From Zel*Marius Z Braun 165.00
#GA S00389023230063399 Card 9916
schema['dynamics']+=[('given_data',r'Money Transfer',
            {
                "transaction_description": "Money Transfer authorized on 01/22 From Zel*Marius Z Braun 165.00 GA S00389023230063399 Card 9916",
                "section": "Deposits/ Additions",
                "transaction_type":"transfer",

                "sender_entity_type": "individual",
                "sender_entity_id": "Marius Z Braun",
                "sender_entity_name": "Marius Z Braun",

                "receiver_entity_type": "main_account",
                "receiver_entity_id": "main_account",
                "receiver_entity_name": "main_account",
                "id": 1
            }
            )]

##  Check deposit with address
schema['dynamics']+=[('given_data',r'ATM.*Deposit',
            {
                "transaction_description": "ATM Check Deposit on 02/04 12172 Highway 92 Woodstock GA 38.00 0006156 ATM ID 6935B Card 9916",
                "section": "Deposits/ Additions",
                "transaction_type":"deposit",

                "sender_entity_type": "check",
                "sender_entity_id": "check",
                "sender_entity_name": "check",

                "receiver_entity_type": "main_account",
                "receiver_entity_id": "main_account",
                "receiver_entity_name": "main_account",
                "id": 1
            }
            )]

## Had as source was t-mobile??

#  Bill Pay Pnc Bank Credit Card on-Line Xxxxxxxxxxx73442 on 02-07
#- no receiver and think its' paying a bank not a credit card.

schema['dynamics']+=[('given_data',r'Bank Credit Card',
            {
                "transaction_description": "Bill Pay Pnc Bank Credit Card on-Line Xxxxxxxxxxx73442 on 02-07",
                "section": "Withdrawals/ Subtractions",
                "transaction_type":"payment",

                "sender_entity_type": "main_account",
                "sender_entity_id": "main_account",
                "sender_entity_name": "main_account",

                "receiver_entity_type": "credit",
                "receiver_entity_id": "Pnc Bank Credit Card",
                "receiver_entity_name": "Pnc Bank Credit Card",
                "id": 1
            }
            )]
schema['dynamics']+=[('given_data',r'Bill Pay ',
            {
                "transaction_description": "Bill Pay T-Mobile -Not for Prepaid Plans on-Line xxxx66628 on 01-17",
                "section": "Withdrawals/ Subtractions",
                "transaction_type":"payment",

                "sender_entity_type": "main_account",
                "sender_entity_id": "main_account",
                "sender_entity_name": "main_account",

                "receiver_entity_type": "organization",
                "receiver_entity_id": "T-Mobile",
                "receiver_entity_name": "T-Mobile",
                "id": 1
            }
            )]
####^^^ FARGO

schema['dynamics']+=[('given_data',r'Zelle Payment',
            {
                "transaction_description": "Zelle Payment To Anthony Bro Jpm679646739",
                "section": "ELECTRONIC WITHDRAWLS",
#                "sender_entity_role": "SENDER",

                "sender_entity_type": "main_account",
                "sender_entity_id": "main_account",
                "sender_entity_name": "main_account",

                "receiver_entity_type": "individual",
                "receiver_entity_id": "Anthony Bro",
                "receiver_entity_name": "Anthony Bro",
                "id": 1
            }
            )]
schema['dynamics']+=[('given_data',r'ATM',
            {
                "transaction_description": "ATM Withdrawal | August 24, 2021 | 6400 Laurel Canyon B North Hollywo CA | Card 7413 | $700.0",
                "section": "ATM & Debit Card Withdrawals",
#                "sender_entity_role": "SENDER",

                "sender_entity_type": "main_account_card",
                "sender_entity_id": "card 7413",
                "sender_entity_name": "Card 7413",

                "receiver_entity_type": "cash",
                "receiver_entity_id": "cash",
                "receiver_entity_name": "cash",
                "id": 1
            }
            )]

schema['dynamics']+=[('given_data',r'Check Deposit',
            {
                "transaction_description": "ATM Check Deposit 08/02 6400 Laurel Canyon Blv North Hollywo CA Card 7413",
                "section": "Deposits and Additions",
#                "sender_entity_role": "SENDER",

                "sender_entity_type": "check",
                "sender_entity_id": "check",
                "sender_entity_name": "check",

                "receiver_entity_type": "card",
                "receiver_entity_id": "Card 7413",
                "receiver_entity_name": "card",
                "id": 1
            }
            )]

# electronic withdrawl
schema['dynamics']+=[('given_data',r'Trn\:',
            {
                "transaction_description": "Orig CO Name:Allstate Nbindco Orig ID:1362999368 Desc Date:Aug 21 CO Entry\n #Descr:Ins Prem Sec:PPD Trace#:021000026074791 Eed:210826 Ind ID:\n #Ind Name:Flores Trn: 2386074791Tc",
                "section": "Electronic Withdrawl",
#                "sender_entity_role": "SENDER",
                "sender_entity_type": "main_account",
                "sender_entity_id": "main_account",
                "sender_entity_name": "main_account",

                "receiver_entity_type": "organization",
                "receiver_entity_id": "Allstate Nbindco",
                "receiver_entity_name": "Allstate Nbindco",
                "id": 1
            }
            )]



# general reversal (case insensitive!)
schema['dynamics']+=[('given_data',r'Reversal',
            {
                "transaction_description": "Reversal: Orig CO id:American Express",
                "section": "Deposits and Additions",
#                "sender_entity_role": "SENDER",
                "sender_entity_type": "bank",
                "sender_entity_id": "American Express",
                "sender_entity_name": "American Express",
#                "receiver_entity_role": "MAIN_ACCOUNT",
                "receiver_entity_type": "main_account",
                "receiver_entity_id": "main_account",
                "receiver_entity_name": "main_account",
                "id": 1
            }
            )]


schema['dynamics']+=[('given_data',r'DES\:',
              {
                "transaction_description": "SKYVIEW CAPI0099  DES:PAYMENTS    FL# 21364002340\nINDN:SETT-BATCH 1364873252  CO ID:1364873252 CCD  BATCH\nDESC:DISC DATA\nWIRE TYPE:WIRE OUT DATE:211230 TIME:1655 ET\nTRN:2021123000542437 SERVICE REF:020889 BNF:UNITED HEALTH\nCARE SERVICE ID:9056254 BNF BK:T HE BANK OF NEW YORK ME\nID:043000261 PMT DET:21CUA2 143QJH1J55REF IT 0903869 RMR IV\n157815069963 15,93",
                "section": "Cash transactions",
                "sender_entity_type": "organization",
                "sender_entity_id": "1364873252",
                "sender_entity_name": "Skyview Capital",
                "receiver_entity_type": "organization",
                "receiver_entity_id": "043000261",
                "receiver_entity_name": "United Heath Care Service",
                "id": 3
              }
              )]

schema['dynamics']+=[('given_data',r'TYPE\:WIRE',
              {
                "transaction_description": "TYPE:WIRE IN DATE: 211216 TIME:1348 ET\nTRN:2021121600427147\nSEQ:5242600350JO/009620 ORIG:UNITED CALL\nCENTER SOLUTI ID:373171237 SND\nBK:JPMORGAN CHASE BANK, NA ID:021000021\nPMT DET:ATS OF 21/12/16 INVSGM154",
                "section": "Deposits and other credits",
                "sender_entity_type": "organization",
                "sender_entity_id": "373171237",
                "sender_entity_name": "UNITED CALL CENTER SOLUTIONS",
                "receiver_entity_type": "main_account",
                "receiver_entity_id": "main_account",
                "receiver_entity_name": "main_account",
                "id": 3
              }
              )]

### **beware doc text can be very long
#schema['dynamics']+=[('doc_text',r'Reversal',
#            {
#                "transaction_description": "Reversal: Orig CO id:American Express",
#                "section": "Deposits and Additions",
#                "transaction_type":"reversal",
#                "transactin_method": "other",
#                "id": 2
#            }
#            )]


def dev1():
    return


if __name__=='__main__':
    branches=['dev1']
    for b in branches:
        globals()[b]()

"""
FAILS:
    {
        "transaction_description": "GREAT-WEST TRUST DES:PAYMENTS   ID:704914533408  INDN:Skyview\nCapital         CO ID:5800220000 CTX  ADDITIONAL INFORMATION IS\nAVAILABLE FOR THIS PMT.  CONTACT A TREASURY SALES OFFICER FOR\nASSISTANCE.",
        "section": "Cash transactions",
        "sender_entity_type": "organization",
        "sender_entity_id": "5800220000",
        "sender_entity_name": "Skyview Capital",
        "receiver_entity_type": "organization",
        "receiver_entity_id": "",
        "receiver_entity_name": "",
        "id": "6"
    },

"""

"""
   "transaction_description": "GREAT-WEST TRUST DES:PAYMENTS   ID:703282404750  INDN:Skyview\nCapital         CO ID:5800220000 CTX  ADDITIONAL INFORMATION IS\nAVAILABLE FOR THIS PMT.  CONTACT A TREASURY SALES OFFICER FOR\nASSISTANCE.",
    "section": "Withdrawals and other debits",
"""

"""
WIRE TRANSFER SAMPLE:

TYPE:WIRE IN DATE: 211216 TIME:1348 ET\nTRN:2021121600427147\nSEQ:5242600350JO/009620 ORIG:UNITED CALL\nCENTER SOLUTI ID:373171237 SND\nBK:JPMORGAN CHASE BANK, NA ID:021000021\nPMT DET:ATS OF 21/12/16 INVSGM154",
ChatGPT
This bank statement description seems to provide details about a wire transfer transaction. Let's break it down:

WIRE TYPE:WIRE IN: Indicates the nature of the wire as being incoming (i.e., funds are being received).

DATE: 211216 TIME:1348 ET: Specifies the date and time of the wire transfer. The date is December 16, 2021, and the time is 1:48 PM Eastern Time.

TRN:2021121600427147: "TRN" likely stands for "Transaction Number," and this is the unique identifier for this particular wire transaction.

SEQ:5242600350JO/009620: This appears to be a sequence or reference number, possibly an internal tracking number for the wire.

ORIG:UNITED CALL CENTER SOLUTI: "ORIG" likely stands for "Originator." The sender (or originator) of the wire appears to be a company/entity named "UNITED CALL CENTER SOLUTIONS" (or a truncated version of their name).

ID:373171237: This is likely an identification number associated with the originator (in this case, UNITED CALL CENTER SOLUTIONS).

SND BK:JPMORGAN CHASE BANK, NA ID:021000021: "SND BK" stands for "Sending Bank." The financial institution that sent the wire is JPMORGAN CHASE BANK, NA. The ID following it could be an ABA routing number, which in this case is associated with JPMORGAN CHASE BANK.

PMT DET:ATS OF 21/12/16 INVSGM154: "PMT DET" stands for "Payment Details." This section provides additional details about the wire's purpose or reference information. "ATS OF 21/12/16" might be a reference to the transaction date or some other detail, and "INVSGM154" could be an invoice or reference number.

Based on the provided description:

Sender Entity: The sender or originator of the wire is "UNITED CALL CENTER SOLUTIONS" and their bank is "JPMORGAN CHASE BANK, NA."

Receiver Entity: The specific receiver entity isn't mentioned in the provided details. If this is appearing on your bank statement, then the receiver would be your own entity or account.
"""
