import os
import sys
import codecs
import json
import re
import ast
import random
import hashlib

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")

from get_logger import setup_logging
logging=setup_logging()


#0v1# JC  Oct  2, 2023  Init


"""
NOTES:
- [x] move prior to cypher insert
- use description? statement specific info?

IDEALLY?
- case id +
- statement_id + specific transaction reference (not universal!)
- statement_id + date + amount (not unique)
- statement_id + page + date + amount (not unique)
- statement_id + transaction description  (not constant if swap betweeen pdf2text)
- statement_id + page # + natural offset from top of page??

- account number + trn?  (Chase)

"""


## Transaction ID Generation
#- may not be in the source
#- transaction list may be partial (ie/ 1 page of statement)
#- could keep global transaction pointer?
#- create via content then hash?
def generate_hash(text):
    # Create a SHA-256 hash object
    sha256 = hashlib.sha256()
    # Update the hash object with the bytes-like object (text in bytes format)
    sha256.update(text.encode())
    # Return the hexadecimal representation of the hash
    return sha256.hexdigest()
    
def ORG_alg_generate_transaction_id(entry):
    ## Special case at BOA
    #[ ] beware description varies per pdf2text
    if entry.get('bank_reference',''):
        return entry['bank_reference']
    else:
        blob=entry.get('transaction_description','')
        blob+=str(entry.get('transaction_amount',''))
        blob+=str(entry.get('transaction_date',''))
        return generate_hash(blob)

def alg_generate_transaction_id(statement_id,file_page_number,natural_offset):
    blob=''
    blob+=str(statement_id)
    blob+=str(file_page_number)
    blob+=str(natural_offset)
    return generate_hash(blob)

def alg_extract_chase_trn(entry):
    #** Trn: number missing from some Chase transactions at description cropping!
    # Trn: 1234567890123456
    #- may be \n between
    entry_str=str(entry)  #normalize
    trn=None
    m=re.search(r'Trn:[\s\n ]+([\w\d]+)\b',entry_str,flags=re.DOTALL)
    if m:
        trn=m.group(1)
    return trn

def alg_resolve_transaction_id(transactions,file_page_number=0,statement_id=''):
    raw_page_number=0
    natural_offset=0
    for entry in transactions.get('all_transactions',[]):
        natural_offset+=1
        
        ## Look for unique identifier
        #- see assuptions above

        #[A]  If chase use Trn number
        trn=alg_extract_chase_trn(entry)

        if 'id' not in entry:
            if trn:
                entry['id']=trn  #Append case?
            else:
                entry['id']=alg_generate_transaction_id(statement_id,file_page_number,natural_offset)

    return transactions


def dev1():
    return

if __name__=='__main__':
    branches=['dev1']
    for b in branches:
        globals()[b]()



