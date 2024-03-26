import os
import sys
import codecs
import json
import re
import ast
from collections import OrderedDict

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")

from w_llm.llm_interfaces import LazyLoadLLM

from algs_extract import alg_resolve_to_date
from b_extract.alg_easy_extracts import alg_get_page_year

from get_logger import setup_logging
logging=setup_logging()



#0v4# JC  Jan 29, 2024  Call from support_gold.py (as part of functional test of balance extract)
#0v3# JC  Oct 13, 2023  json validate
#0v2# JC  Sep 20, 2023  Update
#0v1# JC  Sep  8, 2023  Init


"""
GOAL OF FULFILLING A DATA FIELD

- leverage llm to pull rdf/neo4j nodes + relationships from source
- ideally, txt2cypher but want to validate extraction first

"""

def remove_equals_field(record, kk, fields):
    if kk in record and record[kk] == fields[kk]:
        record.pop(kk)
    return record

def alg_field_extractor(blob,fields, prompt):
    #0v3# Upgrade to json_validate
    LLM=LazyLoadLLM.get_instance()

    record=LLM.prompt(prompt,json_validate=True)

    if not isinstance(record,dict):
        try:
            record=json.loads(record) #catch
        except Exception as e:
            logging.error("[error] could not load LLM json: "+str(record))
            logging.dev("[error] could not load LLM json: "+str(record))
            record={}

    ## Hard logic

    ## Remove keys where andy values like Unknown or unknown
    pop_these=[]
    for k,v in record.items():
        # UNKNOWN
        try:
            if v.lower()=='unknown': pop_these+=[k]  #ignore int
        except:pass
        if v=='N/A': pop_these+=[k]
        if v=='': pop_these+=[k]
        if not k in fields: pop_these+=[k] #remove any wierd fields
    for k in pop_these:
        record.pop(k,None)  #ignore if not there

    return record

def get_first_page_style_fields():
    ## FIELDS
    sample_address='123 Main St, Anytown, US 90212'
    fields=OrderedDict()
    fields['account_number']='00000055322233'
    fields['account_holder_name']='Big Joes Inc.'
    fields['account_holder_address']=sample_address
    fields['page_number']=0
    fields['statement_period']='2018-09-21 to 2018-10-20'
    fields['bank_name']='General National Bank'
    fields['bank_address']=''
    
    ## Oct 3 add statement style requests
    fields['opening_balance']='1000.00'
    fields['closing_balance']='1200.00'

    return fields

def local_extract_first_page_style_data(page_text):
    fields=get_first_page_style_fields()

    ## PROMPT
    #0v2# Oct 13 was pulling in barcode as account_number
    #still here but good in 3.5 chat    - The barcode is not the account_number (ie NOT 20 digits: 10753950202000022011 )
    # works but hard limits??    - The account_number is not 20 digits long (ie not: 10753950202000022011 )
    prompt="""
        You are an information extraction tool who returns responses in json format.
        The following is a page from a bank statement.  Extract as many information fields
        as possible.  If you cannot find a field then don't return it.
        - The account_number is not 20 digits long (ie not: 10753950202000022011 )
        Consider the following fields: """+",".join(fields.keys())+"""
        ie:
        """+str(json.dumps(fields,indent=0))+""" 

        Bank Statement Page:
        =====================
    """
    prompt+=page_text
    
#D1#    print ("RAW: "+str(prompt))

    record=alg_field_extractor(page_text,fields,prompt)

    #### ADJUST EXTRACTED FIELDS

    ## [A]  Remove hallucinated fields
    # All or some?
    #   record=remove_field(record,'account_holder_address',fields)
    for field in fields:
        record=remove_equals_field(record,field,fields)
        
    ## [B]  Normalize numbers
    if 'opening_balance' in record:
        record['opening_balance']=normalize_number(record['opening_balance'])
    if 'closing_balance' in record:
        record['closing_balance']=normalize_number(record['closing_balance'])
        
    ## [C]  Hard code logic (no known bad formats)
    if record.get('account_number','') is None:
        record['account_number']=''
    if len(record.get('account_number',''))==20:
        record['account_number']=''

    return record,fields

def get_field_from_record_or_past_ptr(field,record,ptr):
    ## For example: account_holder_name is only mentioned on first page but may want at any time
    vv=record.get(field,None)
    last_ptrs=ptr.get('last_ptrs',[]) #newest is last
    if not vv and last_ptrs:
        ## Look at history iterate in reverse list
        for p in last_ptrs[::-1]:
            vv=p.get(field,None)
            if vv:break
    return vv

def normalize_number(vv):
    if isinstance(vv,str):
        vv=re.sub(r'[\, \$]',"",vv)
        try: vv=float(vv)
        except Exception as e:
            if str(vv)=='NotFound':
                logging.info("[info] could not normalize number: "+str(e)+": "+str(vv))
                vv=0
            else:
                logging.error("[error] could not normalize number: "+str(e)+": "+str(vv))
                vv=0
    return vv

def map_to_ptr(record,ptr,fields):
    ## Assume first page style data
    #- ptr to assume new value or USE PREVIOUS!

    ## CREATE IDS
    # statement_id

    ## RECALL DOCUMENT-LEVEL SCHEMA TARGETS  (which general extractor does)
    #a)  Main Account number  (name + address)
    #b)  statement (id + statement page number + statement_period)
    #c)  bank name and address
    
    ### Allowed to update logic
    #- if field is set then do not update unless new page is NEW statement
    #- similar to bank name only updating once
    
    ## Target fields: bank_name, (possibly other normals)
    #                 opening_balance, closing_balance (dont' confuse with daily summary)
    
    ## INIT
    if not 'block_update' in ptr:
        ptr['block_update']=[]

    ## CLEAR BLOCK UPDATE
    if ptr.get('statement_page_number',0)==1:
        ptr['block_update']=[]

    dd={}
    for field in fields:
        vv=get_field_from_record_or_past_ptr(field,record,ptr)
        
        ## Block if flagged as blocked and does not exist
        if field in ptr['block_update'] and ptr.get(field,''):
            logging.info("[block_update field: "+str(field)+" value: "+str(vv))
            vv=None
        
        elif vv:
            ## Keep it
            dd[field]=vv
        else:
            pass

    print ("PUSHING FULL UPDATE: "+str(dd))
    ## Warning if name conflict?
    ptr.update(dd)
    

    ### Start blocking update once get value and not found again on first page
    ## UPDATE block_update
    if ptr.get('opening_balance',''): ptr['block_update']+=['opening_balance']
    if ptr.get('closing_balance',''): ptr['block_update']+=['closing_balance']
    ptr['block_update']=list(set(ptr['block_update'])) #unique

    return ptr

def create_statement_id(ptr):
    ## May not be included on page
    
    #[x] oct 3 remove file page_num
    statement_id=ptr['case_id']+"-"+ptr.get('statement_date','')+"-"+ptr.get('account_number','')+"-"+str(ptr['filename'])

    return statement_id

def add_smart_tags():
    #ie/ normalize bank name? ie: BOA
    #- to ptr sure.
    return

def logic_extract_bank_name():
    #Should come via field extract but not always?
    #- or, maybe just processing single page?
    
    return

#def smart_extract_statement_id(mega,page_text='',case_id='',filename='',page_number=0,run={}):
def smart_extract_fields(chunk,ptr):
    """
        STATEMENT LEVEL FIELDS
    """
    # ptr:  snapshot of where we are

    ## INPUTS
    ## Grab page (longer but more robust)
    page_text=''
    methods=['pypdf2_tables','pdfminer']
    for method in methods:
        page_text=chunk['epage'].get(method,'')
        if page_text:break

    ## Get first page of statement style of fields
    record,fields=local_extract_first_page_style_data(page_text)

    ### ADJUST FIELDS

    ##[A] Rename abiguous field
    if 'page_number' in record:
        record['statement_page_number']=record.pop('page_number')

    ##[B] Resolve true date format
    print ("[ ] pass year? or alg_get_page_year")
    statement_date=alg_resolve_to_date(record.get('statement_period',''))
    if statement_date:
        record['statement_date']=statement_date
    else:
        print ("[warning] could not resolve statement_date from period: "+str(record.get('statement_period','')))

    ##[C] Only allow bank_name updates when XXX
    ## {patch whereby non-main page has differnt bank name}
    ## {FIX:  only allow bank_name update when bank_address is present}
    #LOGIC:
    #- if bank_address then allow update
    #- if not bank_name then allow update
    #- if statement page number is 1 (maybe 2) then allow update
    #- else -- do not update
    #- if have some bank_name and bank_address the
    update_bank=False
    if record.get('bank_address','') or not record.get('bank_name',''):
        update_bank=True
    if record.get('statement_page_number',0) in [1,2]:
        update_bank=True
    if not update_bank:
        bank_name=record.pop('bank_name','')
        logging.dev("[bank_name] not allowed to update: "+str(bank_name)+" existing: "+str(ptr.get('bank_name','')))
        
    ## Store to rolling context
    fields_list=list(fields.keys())+['statement_date','statement_page_number']
    if 'page_number' in fields_list:
        fields_list.remove('page_number')

    ptr=map_to_ptr(record,ptr,fields_list)

    print ("[debug smart_extract]: "+str(record))
    print ("PTR: "+str(ptr))

    ##[C]  Statement concept
    # [ ] optionally pointer details on inner statement (see schema though ie/ page number of statement)
    ptr['statement_id']=create_statement_id(ptr)

    return record,ptr


if __name__=='__main__':
    branches=['do_extract']
    for b in branches:
        globals()[b]()


"""
"""
