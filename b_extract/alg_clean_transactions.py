import os
import sys
import codecs
import json
import re
import ast
import random

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")

from get_logger import setup_logging
logging=setup_logging()


#0v2# JC  Oct 31, 2023  Amount as absolute value
#0v1# JC  Sep 23, 2023  Init


def clean_transaction_description(record):
    # \w\n\w to \w|\w
    #Usaa P&C Ext Autopay 195400021 Tel ID: Usaa-PC\nEllison Capers Grayson\n302 Paradise Dr. TIBURON, GA 84920'
    # BEFORE:  {'transaction_description': 'Usaa P&C Ext \nAutopay 195400021 Tel ID: Usaa-PC\nEllison Capers Grayson\n302 Paradise Dr. TIBURON, GA 84920'}
    # AFTER:  {'transaction_description': 'Usaa P&C Ext | Autopay 195400021 Tel ID: Usaa-PC | Ellison Capers Grayson | 302 Paradise Dr. TIBURON, GA 84920'}
    if record and record.get('transaction_description',None):
        record['transaction_description']=re.sub(r'([\s]{0,3}\n[\s]{0,3})',' | ',record['transaction_description'])
    return record


def adjust_transactions_top_level(transactions={},transaction={}):
    ## transaction_amount remove $ and commas immediately!
    #- process as str, expect float output
    #- full list of records or single record

    given_type='normal'

    ## FLEXIBLE INPUT
    if isinstance(transactions,dict) and 'all_transactions' in transactions:
        pass
    elif isinstance(transactions,list):
        given_type='list'
        temp={}
        temp['all_transactions']=transactions
        transactions=temp
    elif not transactions and transaction:
        given_type='one_record'
        transactions={}
        transactions['all_transactions']=[transaction]
        
    elif isinstance(transactions,str):
        logging.warning("No transactions (a string): "+str(transactions))
        transactions={}
    else:
        given_type='unknown'
        logging.warning("[strange transaction data model]: "+str(transactions))

    transactions_are_signed=False
    for entry in transactions.get('all_transactions',[]):
        if isinstance(entry,str):
            logging.error('[entry is str]: '+str(entry))
            entry={}
            continue # Will fail at dict get otherwise
        if re.search('-',str(entry.get('transaction_amount',''))):
            transactions_are_signed=True
            break

    for entry in transactions.get('all_transactions',[]):
        if isinstance(entry,str):
            logging.error('[entry is str]: '+str(entry))
            entry={}
            continue # Will fail at dict get otherwise

        #### SECTION
        if 'section' in entry:
            entry['section']=re.sub(r' - continued','',str(entry['section']))

        #### AMOUNT
        if entry.get('transaction_amount',''):
            ## Remove
            entry['transaction_amount']=re.sub(r'[\,\$]',r'',str(entry['transaction_amount']))

            ## Expect float
            #- a float to string with two decimals is still:  123.0 not 123.00 soue 2f...
            #y = format(x, '.2f')
            try:
                #'123.0'# # entry['transaction_amount'] = round(float(entry['transaction_amount']), 2)
                #'123.00'#  entry['transaction_amount'] = f"{round(float(entry['transaction_amount']), 2):.2f}"
                entry['transaction_amount'] = float(entry['transaction_amount'])
            except:
                logging.warning("[error] invalid amount (expected float): "+str(entry['transaction_amount']))
                

        #### -> AMOUNT SIGN new field
        #** good context but ultimately handled depending on how summed at db level
        #- recall, page-level sorting is by amount, so sign is important
        if transactions_are_signed:
            if '-' in str(entry['transaction_amount']):
                entry['amount_sign']='-'
            else:
                entry['amount_sign']='+'
        
        try: entry['transaction_amount']=abs(entry['transaction_amount'])
        except: pass


        #### DESCRIPTION
        if 'transaction_description' in entry:
            ## \n to | separator
            entry=clean_transaction_description(entry)

        #### NULLS
        ## Set any N/A to blank (or remove) ie: section, payer_id, receiver_id
        #"section": "N/A",
        for kk in entry:
            if entry[kk]=='N/A':
                entry[kk]=""

            elif entry[kk]==None:
                entry[kk]=""

    # UNWRAP FLEXIBLE INPUT
    if given_type=='list':
        response=transactions['all_transactions']
    elif given_type=='one_record':
        response=transactions['all_transactions'][0]
    else:
        response=transactions

    ## entry for single case
    return response



def dev1():
    return

if __name__=='__main__':
    branches=['dev1']
    for b in branches:
        globals()[b]()
