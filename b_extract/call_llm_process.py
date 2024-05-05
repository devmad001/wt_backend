import os
import sys
import codecs
import time
import json
import re
import ast
import random

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")


from schema_statement_kinds import dev_get_bank_schema
from w_pdf.pdf_process import interface_file2doc
from w_llm.llm_interfaces import OpenAILLM
#from algs_extract import alg_jsn2dict
from llm_page2transactions import llm_page2transactions
#MV# from llm_transactions_add_accounts import llm_transactions_add_accounts

from w_storage.gstorage.gneo4j import Neo
from alg_resolve_transaction_id import alg_resolve_transaction_id
from alg_resolve_transaction_id import alg_generate_transaction_id

from do_cypher import do_transactions2cypher
from do_cypher import do_cypher_link_transactions_to_BankStatement
from a_query.cypher_helper import try_clean_cypher

## Custom transaction extractors
from dev_fargo_page2t.fargo_page2t import fargo_pdf_page_to_transactions

from test_cache import store_page2transactions
from test_cache import page_samples

from get_logger import setup_logging
logging=setup_logging()


#0v3# JC  Dec 20, 2023  Branch to wells fargo custom transaction extractor
#0v2# JC  Sep 20, 2023  New epage (multi- page text extraction methods)
#0v1# JC  Sep  9, 2023  Init


## SOMEDAY OPTIONS:
# [ ] - remind not to use ' in response for transactions!

DISABLE_ADD_ACCOUNTS=True

#Global reload (or singleton option later)
BANK_SCHEMA=dev_get_bank_schema()

def call_transaction_processing_pipeline(epage={},filename_path='',input_filename='',input_page_number='',case_id='case_2',statement_id='debug_statement_id_1', doc_dict={}, suggestions=['default'],ptr={},allow_cache=True, db_commit=True):
    meta={}
    
    ## EXTRA SETTINGS:
    # options['db_commit'] -> db_commit=True by default;  unless debug mode

    ##
    #epage:  update page extractions with various methods

    ## GIVEN: page of text
    #  1)  Get raw transactions with section headings
    #  2)  Infer Account source + targets (precursor to double-bookkeeping)

    ## suggestions:  steer the LLM proompt with a list of suggestions
    # case_id
    # statement_id (extra meta attach to transaction)
    # doc_dict:  extra doc level (possibly page level tags/king)

    start_time=time.time()
    #########################################
    ## SETTINGS AND OPTIONS
    #- mostly verbose/save to db
    branch=[]
    branch=['insert_to_graph']

    verbose=True
    echos=[]
    echos=[]
    echos+=['transaction_dicts']
    echos+=['accounts']

    if 'transaction_dicts' in echos: verbose_transaction_dicts=True
    else: verbose_transaction_dicts=False
    if 'accounts' in echos: verbose_accounts=True
    else: verbose_accounts=False

    #########################################
    ### CHOOSE PAGE TEXT
    #[ ] upgradable or centralize!
    page_text=''
    methods=['pypdf2_tables','pdfminer']
    for method in methods:
        page_text=epage.get(method,'')
        if page_text:break

    #########################################
    ### CORE PROCESSING
    #########################################
    
    ## BRANCH CHOOSE CORE PROCESSING
    print ("[[manual at:  ptr: "+str(ptr)+" doc_dict: "+str(doc_dict))
        
    transactions={}
    
    ## Quick check if possible  wells_fargo
    if False and os.path.exists(filename_path):
    
        ## Custom wells fargo transaction extraction
        #[ ] ideally would know if page is wells fargo or bank name or previous (this keyword depends on content)
        if re.search(r'Transaction history',page_text):  #Try Wells Fargo (if randomly matches won't find expected format ok)
            logging.info("[info] trying wells_fargo extract at: "+str(filename_path))

            print ("[page number]: "+str(input_page_number))
            print ("[filename_path: "+str(filename_path))

            core_branch='wells_fargo'
            page_text=page_text  #For year extractor
            transactions=fargo_pdf_page_to_transactions(input_page_number,filename=filename_path,page_text=page_text,year='',verbose=False)
            #^ {'all_transactions':[]}
            
            if not transactions:
                transactions={}
            else:
                logging.info("[transactions found via custom extract]: "+str(len(transactions['all_transactions'])))

    else:
        logging.warning("[input filename full path not exists]: "+str(filename_path))
    

    ##:: METHOD IS LLM EXTRACTION
    if not transactions:
        DO_LLM=True

        ## SPECIAL CASE SKIP LOOKING FOR TRANSACTIONS (at bank schema level (schema_statement_kinds.py))
        for match_list in BANK_SCHEMA.get('skip_entire_transaction_page_regex',[]):
            matched_count=0
            for match in match_list:
                if re.search(match,page_text):
                    matched_count+=1
                else:
                    break #must be all
            if matched_count==len(match_list):
                logging.info("[skipping llm_page2transactions cause skip_entire_transaction_page_regex found]: "+str(match_list))

                DO_LLM=False
                break
    
        if DO_LLM:
            ###############################################################
            # CORE LLM ENTRY
            #- assuming not skip because no transaction page, and not wells fargo found above faster
            logging.info('[calling llm_page2transactions]')
            transactions,meta_page2t=llm_page2transactions(page_text='',epage=epage,verbose=verbose_transaction_dicts, doc_dict=doc_dict,bank_name=ptr.get('bank_name',''),try_cache=allow_cache,ptr=ptr)


    else:
        logging.info("[skipping llm_page2transactions cause already found]")
        
        


    ##:: METHOD IS LOGICAL AUGMENT
    #- include to account holder via ptr (should have been created in smart section)
    transactions=logical_markup_transactions(transactions,ptr)
    
    if not DISABLE_ADD_ACCOUNTS:
        transactions,meta=llm_transactions_add_accounts(transactions, suggestions=['default'],page_text=page_text,verbose=verbose_accounts)

    if 'store gold functional test' in []: #True: #Store gold functional test
        record=meta_page2t  #model_version, prompt header used
        store_page2transactions(input_filename,input_page_number,page_text,transactions,record=record)
        
    transactions=alg_resolve_transaction_id(transactions,file_page_number=ptr['page_num'],statement_id=ptr['statement_id'])
    
    transactions=alg_validate_transactions_before_storage(transactions,file_page_number=ptr['page_num'],statement_id=ptr['statement_id'])

    #########################################
    ## Create cypher
    # extra meta needed for transactions

    cypher,cyphers_as_list,meta_cypher=do_transactions2cypher(transactions,case_id=case_id,statement_id=statement_id,filename=input_filename,filename_page_num=input_page_number,verbose=False)
    
    ## Execute cypher
    #- nested exception handling for now
    #- fallback to clean text
    #- fallback to execute individual transactions
    #     ^ where a single transaction may be missed (optionall track this back to top job status too)
    if 'insert_to_graph' in branch and cypher and db_commit:
        ##; db_commit:  new True/False option for debug model of not changing Graph

        ## Inter nodes
        try:
            for dd in Neo.iter_stmt(cypher,verbose=True):   #response to dict
                print ("cypher insert response> "+str(dd))
        except Exception as e:
            logging.warning("[cypher insert failed -- will retry: ]: "+str(e))

            ## Full redo-- not great always!
            cypher=try_clean_cypher(cypher)

            try:
                for dd in Neo.iter_stmt(cypher,verbose=True):   #response to dict
                    print ("cypher insert response> "+str(dd))
            except Exception as e:
                logging.warning("[cypher insert failed (tried cleaning) -- will retry INDIVIDUALLY!: ]: "+str(e))
                for single_cypher in cyphers_as_list:
                    try:
                        for dd in Neo.iter_stmt(single_cypher,verbose=True):   #response to dict
                            pass
                    except Exception as e:
                        ## FINAL PATCH RETRY ** better to have simple ascii in description then no transaction!
                        simple_cypher=alg_final_attempt_clean_description(single_cypher)
                        try:
                            for dd in Neo.iter_stmt(simple_cypher,verbose=True):   #response to dict
                                pass
                        except Exception as e:
                            logging.warning("[error] could not insert transaction: "+str(single_cypher))
                            logging.dev("[error] could not insert transaction: "+str(single_cypher))
                            meta['transactions_not_saved']=meta.get('transactions_not_saved',[])+[single_cypher]

        #####################
        ## Link transactions with BankStatement- HAS_TRANSACTION -> transaction
        do_cypher_link_transactions_to_BankStatement(transactions,ptr['statement_id'])

    elif not cypher:
        logging.warning("[no cypher to insert]")
    elif not db_commit:
        logging.info("[ DEBUG MODE ]  Skipping cypher insert to Graph *** DEBUG MODE!!")

    else:
        raise Exception("unknown branch: "+str(branch))

    print ("[debug] done full cypher creation")

    meta['extract_run_time']=time.time()-start_time
    logging.info("[extraction run time]: "+str(int(meta['extract_run_time']))+" seconds")
    return transactions,cypher,meta



def alg_final_attempt_clean_description(cypher_query):
    #[ ] removes all non normal characters -- patch on retries but transaction still gets posted
    #[ ] Feb 13, 2024  (See  statement_id: '65caaffb9b6ff316a779f525-2018-06-14-350993518504-M&T Victim Records__Operating 2018__CR__2018 06__061418-$4,392.00.pdf')
    # Regex to match the transaction_description assuming it ends with ',
    pattern = re.compile(r"(transaction_description: ')(.*?)(',)", re.DOTALL)
    
    # Function to clean the transaction_description
    def clean_description(match):
        transaction_description = match.group(2)  # Extract the actual description text
        transaction_description = transaction_description.replace("''", "'")  # Handle escaped quotes
        cleaned_description = re.sub(r"[^a-zA-Z0-9 .,;:!?-\|\\\/]", ' ', transaction_description)  # Clean the description
        return match.group(1) + cleaned_description + match.group(3)  # Reconstruct the match with cleaned description
    
    # Replace the transaction_description in the cypher_query with the cleaned version
    modified_cypher = re.sub(pattern, clean_description, cypher_query)
    
    return modified_cypher

def alg_validate_transactions_before_storage(transactions,file_page_number=0,statement_id=''):
    ## Various checks for data quality -- just keep full coverage and can combine after
    #[A] Transaction ids must be unique and set
    saw_ids={}
    trans={}
    trans['all_transactions']=[]
    natural_offset=0
    for entry in transactions.get('all_transactions',[]):
        natural_offset+=1

        if not entry.get('id',''):
            raise Exception("transaction id missing: "+str(entry))

        if entry['id'] in saw_ids:
            logging.warning("[transaction id not unique on page]: "+str(entry))
            logging.warning("^^possibly a fee associated with the same transaction Trn: #")
                
            ## Auto transpose second
            # (see alg_resolve_transaction_id same but natural_offset is here)
            entry['id']=alg_generate_transaction_id(statement_id,file_page_number,natural_offset)
            
        trans['all_transactions']+=[entry]
            

        saw_ids[entry['id']]=True
    return trans

def logical_markup_transactions(transactions,ptr):
    ## Ideally add as links but attributes fine for now
    ## CONSIDER:
    #e>  account_number, statement_id, etc.
    gave_warning=False
    for transaction in transactions.get('all_transactions',[]):

        #[1]  map vars from global ptr
        transaction['account_number']=ptr.get('account_number','')
        transaction['account_id']=ptr['case_id']+"-"+ptr.get('account_number','') #Hard code for now
        
        if not transaction.get('account_number','') and not gave_warning:
            logging.warning("[warning] no account number found... possibly bad pdf")
            logging.dev("[warning] no account number found... possibly bad pdf")


        #[2]  Transaction amount to float or zero (no negative)
        amount=0
        try:
            amount=float(transaction['transaction_amount'])
        except Exception as e:
            pass
        if amount<0:
            amount=amount*-1
        transaction['transaction_amount']=amount
        
    return transactions


def profile_document(pages,doc_dict):
    ## Bank type
    ## pdf format type (image/text)?

    # ideally, page level since multiple kinds possible in document!
    doc_dict['tags']=doc_dict.get('tags',[])
    doc_dict['page_tags']=doc_dict.get('page_tags',[])

    ## BANK TYPE DOC WIDE
    #[ ] count?  specific? filename?
    if re.search(r'\WBOA', doc_dict.get('filename_path','')):
        doc_dict['tags']+=['BOA']

    c=0
    for page in pages:
        c+=1
        page_tags=[]

        if c<=2:

            ## DOC LEVEL
            if 'Bank of America' in page:
                doc_dict['tags']+=['BOA']
        if 'Bank of America' in page:
            page_tags+=['BOA']

        doc_dict['page_tags']=page_tags

        #Unique
        doc_dict['page_tags']=list(set(doc_dict['page_tags']))

    ## BANK TYPE PAGE WIDE
    doc_dict['tags']=list(set(doc_dict['tags']))

    return doc_dict


def get_next_page():
    meta={}
    doc_dict={}
    pages=[]
    ddir=LOCAL_PATH+"../w_datasets/Bank Statements - for Beta Testing/"


    filename="07A210E6-B60D-46B6-9D40-9B3239237F05-list.pdf"  #initial good 1 page stored gold test
    page_number=2

    #Comments:  ok but  alot of wire transfer odd destinations
    page_number=3 #ok BOA
    page_number=4 #Ok but destination may:  multiple accounts, names, refs, etc.
    page_number=5
    filename="SGM BOA statement december 2021.pdf"

    page_number=4 #*starts on page 3
    filename="Dec 31 2021 NST BOA Bank Statement.pdf"


    doc_dict['filename_path']=ddir+filename
    doc_dict['page_number']=page_number

    filename_path=ddir+filename

    doc_dict=profile_document(pages,doc_dict)

    source=['hardcoded']
    source=['realtime']
    if 'hardcoded' in source:
        watch=gold_test_save
        page=page_samples[0]
    else:
        print ("[realtime load]: "+str(filename_path))

        if 'BOA' in doc_dict.get('tags',[]):
            Doc=interface_file2doc(filename_path,branch=['pages_tables'])
        else:
            Doc=interface_file2doc(filename_path,branch=['pages'])

        pages=Doc.get_pages()
        #page=random.choice(pages)
        page_text=pages[page_number-1] #offset because page 1 is index 0

    doc_dict=profile_document(pages,doc_dict)

    return page_text,filename,page_number,doc_dict,meta

def local_call_processing_pipeline():
    ## Standard external

    #########################################
    ### BEGIN GRAB PAGE
    page_text,input_filename,input_page_number,doc_dict,meta=get_next_page()
    if True:
        print ("[PAGE]")
        print (str(page_text))
    #########################################

    transactions,cypher,meta=call_transaction_processing_pipeline(page_text=page_text,input_filename=input_filename,input_page_number=input_page_number,case_id='case_2',statement_id='debug_statement_id_1',doc_dict=doc_dict,suggestions=['default'])

    return


if __name__=='__main__':
    branches=['call_llm_processing_pipeline']
    branches=['call_processing_pipeline']
    branches=['local_call_processing_pipeline']
    for b in branches:
        globals()[b]()


"""
"""
