import os
import sys
import codecs
import json
import re

import configparser as ConfigParser


LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")

from get_logger import setup_logging
logging=setup_logging()


from w_file_repo.filerepo import File_Storage
from w_storage.gstorage.gneo4j import Neo

Config = ConfigParser.ConfigParser()
Config.read(LOCAL_PATH+"../w_settings.ini")
BASE_STORAGE_DIR=Config.get('files','base_storage_rel_dir')
BASE_STORAGE_DIR=LOCAL_PATH+"../"+BASE_STORAGE_DIR


#0v1# JC  Sep 17, 2023  Init


"""
    DOC META
    - single field update algs may require high-level meta
    - on-demand doc meta
    - leverage stored files with transaction pointer
"""

def query_transaction(transaction_id):
    ## Data (may not have Label)
    ## Transaction meta
    stmt="""
        MATCH (n:Transaction {id: '"""+str(transaction_id)+"""'})
        RETURN n
        """
    record={}
    # single?!
    if 'alt normal' in ['alt normal']:
        for record in Neo.iter_stmt(stmt,verbose=False):   #response to dict
            record=record[0] #list is standard
            break
    if 'run get list ok' in []:
        results,tx=Neo.run_stmt(stmt,tx='',parameters={})
        record=results.data() #[0]
    return record

def get_full_filename(transaction_id=''):
    transaction=query_transaction(transaction_id=transaction_id)

    if transaction.get('filename',''):
        case_id=transaction['case_id']
        full_filename=BASE_STORAGE_DIR+'/'+case_id+'/'+transaction['filename']
    
    if not os.path.exists(full_filename):
        raise Exception("Missing file: "+str(full_filename))
    return full_filename

def alg_source_doc_meta(transaction_id='',full_filename='',case_id='',all_pages=True):
    ###
    #- start with raw text  (possibly real-time generated)
    # doc_meta['page_meta']={} -> extracted['method']=['text of pages']
    ## Assume pointer via transaction
    #   ^ future possible in graph but recall (transaction to doc location so it'll be there)

    FS=File_Storage()

    full_doc_text=''

    field_support=['page_level_text_with_alg_type']
    doc_meta={}

    ## Get file from transaction if needed
    if not full_filename:
        full_filename=get_full_filename(transaction_id=transaction_id)
        
    if not os.path.exists(full_filename):
        logging.info("[warning] Missing file (may not have locally): "+str(full_filename))

    ## Full process or get
    if not FS.is_fully_processed(full_filename,case_id):
        status,meta=FS.full_process_pdf(full_filename,case_id)
        print ("STATUS: "+str(status))
    else:
        print ("[info] yes fully processed!")

    ## Get meta
    ## full_filename may be loaded from Storage

    page_metas={}
    if not all_pages:
        page_num=int(transaction.get('filename_page_num',0))
        raise Exception("Not implemented single page doc_meta")
    else:
        page_num=0

        page_meta=True
        while page_meta:
            page_num+=1
            auto_process=False #Already requested process
            page_meta=FS.get_page_meta_realtime(full_filename,case_id=case_id,page_num=page_num, auto_process=auto_process,verbose=True)

            ## Full doc text
            page_texts=''
            for method in page_meta.get('extracted',[]):
                for page_text in page_meta['extracted'][method]:
                    page_texts+=page_text
                    full_doc_text+=page_text

            if page_meta:
                page_metas[str(page_num)]=page_meta
            else:
                break

    doc_meta['page_metas']=page_metas
    doc_meta['full_doc_text']=full_doc_text

    return doc_meta


def dev1():

    transaction_id='2ed1b349b19f67503eaf41411c5dfb25f145d77135948a4e2a77e43198c71e15'

    trans=query_transaction(transaction_id=transaction_id)
#    print ("Gtrans: "+str(trans))

    alg_source_doc_meta(transaction_id=transaction_id)

    return

if __name__=='__main__':
    branches=['dev1']
    for b in branches:
        globals()[b]()



"""
"""
