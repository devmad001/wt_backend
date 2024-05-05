import os
import sys
sys.stdout.reconfigure(encoding='utf-8') #Global character output for stdout


import codecs
import json
import re
import uuid
import time
import copy

from collections import OrderedDict

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")


import configparser as ConfigParser
from a_agent.iagent import Smart_Agent
from w_storage.ystorage.ystorage_handler import Storage_Helper

from get_logger import setup_logging

Storage=Storage_Helper(storage_dir=LOCAL_PATH+"../w_datasets/pipeline")
Storage.init_db('megas')

from std_normalize import do_normalize
from a_custom.smart_extract import smart_extract_fields
from a_custom.smart_store_fields import smart_store_fields

from b_extract.call_llm_process import call_transaction_processing_pipeline
from x_modules.log_hub.log_hubby import log2hub


from source_schema import PTR_SCHEMA
from multi import Multi_Wrap



RootConfig = ConfigParser.ConfigParser()
RootConfig.read(LOCAL_PATH+"../w_settings.ini")
THREADS_FOR_LLM_EXTRACTION=int(RootConfig.get('performance','threads_for_llm_extraction')) #0 off, 10 high
    

#0v6# JC  Feb  9, 2024  Add logging hub (db based) [ ] TODO complete
#0v5# JC  Dec 27, 2023  Include report generation
#0v4# JC  Dec 19, 2023  Upgrade to multi thread statement-level batching multi_chunks
#0v3# JC  Sep 20, 2023  Upgrade ptr (multi-statement files etc)
#0v2# JC  Sep 10, 2023  Swap in b_extract cleaner transaction extractor
#0v1# JC  Sep  6, 2023  Init


"""
    EXECUTION ENTRYPOINTS:  run_pipeline, /a_agent/run_iagent.py, cron?
    - Uses "Job" abstraction to track state
        - A Jobs' main var is case_id

"""


### THREAD OPTIONS
#THREAD_COUNT=5  # 400
#THREAD_COUNT=0  # 763
#THREAD_COUNT=10 # colin_dec_21_direct_multi10
#THREAD_COUNT=12 # gpt-4 10k per minute warnings.  Try running full at  colin_dec_21_direct_multi12
#THREAD_COUNT=8  #                                 Try running full at  colin_dec_21_direct_multi8

THREAD_COUNT=THREADS_FOR_LLM_EXTRACTION

# Allow DEV machine no threads
if os.name=='nt':
    THREAD_COUNT=0
else:
    THREAD_COUNT=THREADS_FOR_LLM_EXTRACTION

if THREAD_COUNT:
    Multi=Multi_Wrap(multi='thread',max_workers=THREAD_COUNT)
    logging=setup_logging(suppress_stdout=True) #Should still go to log file
    
else:
    logging=setup_logging()
    logging.warning("[warning] running extractor in single thread mode!")
    
THREAD_MAX_RUNTIME=8*60*60  # 4 hours timeline on hogan 65caaffb9b6ff316a779f525


def init_mega(case_id=''):
    mega={}
    mega['id']=case_id
    mega['chunks']=OrderedDict()         #ie/ one long file with many pages -> chunks @ page
    mega['statements']={}           # statement 'abstract level' info (ie/ account_number)
    mega['case_id']=case_id
    mega['fields']={}               # target fields but mega is case level so multiple docs + statements possible
    return mega

### DOCUMENT / CASE SCHEMA


def alg_is_start_of_statement(page_text):
    ## Find start of statement based on page number 1 of x
    #- why?  Allows splitting pdf into individual statements for parallelized run

    ## Define known:
    #i)  Wells Fargo:  Page 1 of 22    But if neither Wells Fargo or page x of x then unknown
    is_page_known=False
    
    page_number=0
    
    m=re.search(r'Page\s+(\d+)\s+of\s+(\d+)',page_text,flags=re.I)
    if m:
        is_page_known=True
        page_number=m.group(1)
        page_count=m.group(2)
#D1        logging.info("[debug] page known: "+str(page_number)+" of "+str(page_count))
        
    if not m:
        if not re.search(r'Wells Fargo',page_text,flags=re.I):
            logging.info("[warning] split pdf into individual statements but unknown page content")
            
    if int(page_number)==1:
        return True 
    else:
        return False

def prep_chunks(mega):
    #0v2# Upgrade to use multiple page extraction methods
    ## Split given document(s) into chunks (page scope likely)
    #
    scope='page'  #force page for now

    ## Assume mega has been do_normalize
    file_pages=mega.get('file_pages',[])
    if not file_pages: return 0

    ## Profile document
    mega['doc_dict']={} #moved or want running style?#  profile_document(file_pages,mega.get('doc_dict',{}))

    case_id=mega['case_id']
    
#D1    print ("MEGA: "+str(mega))

    ## DEFINE A CHUNK
    # - mega is case level, tracks files at fname ids
    # - scope='page' from active file
    
    count_multi_chunks=0
    mega['multi_chunks']=OrderedDict()  #Or above see

    for filename_path in file_pages: #see std_normalize.py
        print ("FP: "+str(filename_path))
        
        ## Get FULL path (for downstream processing option -- ie/ wells fargo transactions)
        full_path=''
        for temp,f_path in mega.get('path_filenames',[]):
            if f_path==filename_path:
                full_path=temp

        filename=os.path.basename(filename_path)
        start_of_new_file=True

        for page_number_index in file_pages[filename_path]['epages']:
            page_number=page_number_index+1

            chunk_type='page'

            ## epage: per pdf_process is [0][extraction_method]=page_text
            page_extractions=file_pages[filename_path]['epages'][page_number_index]

            ## CREATE CHUNK
            #- chunk will act like mega but sub-processing

            chunk_id=case_id+"-"+scope+"-"+filename+"-"+str(page_number)
#D1            print ("[info] prep chunk_id: "+str(chunk_id))

            # Not id or not epage
            if not chunk_id in mega['chunks'] or not mega['chunks'].get(chunk_id,{}).get('epage',''):
                #**watch over write
                chunk={}
                chunk['id']=chunk_id
                chunk['chunk_type']=chunk_type
                chunk['case_id']=case_id

                chunk['epage']=page_extractions

                chunk['filename']=filename
                chunk['filename_path']=full_path  #Full absolute filename path (for downstream processing)
                chunk['page_num']=page_number

                chunk['fields']={}  #Target output fields
#D2                print ("PREP: "+str(chunk))
                
                ###############################################################################
                ## Include multiple pages of collective statement option
                # build multi_chunks built of many pages of text
                # Include chunks into groups of chunks
                is_chunk_in_new_group=False
                page_text=''
                for extract_method in chunk['epage']:
                    #if method==pypdf2_tables is default and first 'ideal'
                    page_text=chunk['epage'][extract_method]
                    if page_text: break
                is_start_of_statement=alg_is_start_of_statement(page_text)

                if is_start_of_statement or start_of_new_file:
                    # New group
                    count_multi_chunks+=1
                    multi_chunk_id=case_id+"-"+scope+"-"+filename+"-"+str(count_multi_chunks)
                    mega['multi_chunks'][multi_chunk_id]=[]
                    logging.info("[debug] new multi_chunk_id: "+str(multi_chunk_id))
                    
                    # Append new chunk (page) to start of new statement
                    mega['multi_chunks'][multi_chunk_id]+=[chunk]
                else:
                    # Append chunk (page) to active statement
                    multi_chunk_id=case_id+"-"+scope+"-"+filename+"-"+str(count_multi_chunks)
                    if not multi_chunk_id in mega['multi_chunks']:
                        raise Exception("[error] multi_chunk_id not in mega: "+str(multi_chunk_id))
#D1                    logging.info("[debug] existing multi_chunk_id: "+str(multi_chunk_id))
                    
                    # Append chunk
                    mega['multi_chunks'][multi_chunk_id]+=[chunk]

                ###############################################################################


                ## Save standard chunk into mega  (org)
                mega['chunks'][chunk_id]=chunk

            else:
                ### CHECK SOME LAST STATUS
                # chunk['processed_on']=int(time.time(
                try: hours_since_last_processed=(int(time.time())-mega['chunks'][chunk_id]['processed_on'])/3600
                except: hours_since_last_processed=0
                print ("[chunk] "+str(chunk_id)+" hours since last processed: "+str(hours_since_last_processed))

            start_of_new_file=False

    count_chunks=len(mega.get('chunks',[]))
    logging.info("[Parallizeable chunk groups]  speedup x"+str(count_multi_chunks+1)+" compared to serial processing of: "+str(count_chunks)+" items")

    """
        MULTI NOTES

    """
    return count_chunks


def check_ptr(ptr):
    ## Against PTR_SCHEMA
    ## Unmentioned?
    for field in ptr:
        if not field in PTR_SCHEMA:
            pass
            #logging.error("[error] ptr field not in schema: "+str(field))
    ## Not mentioned?
    for field in PTR_SCHEMA:
        if not field in ptr:
            pass
            #logging.warning("[warignr] ptr field missing: "+str(field))
    return

def process_statement_chunk_pages(multi_chunk,ptr,meta,options):

    ## PROCESS EACH STATEMENT
    ## Start a thread for each multi_chunk set
    doc_dict={}
    for chunk in multi_chunk:
        chunk_id=chunk['id']
        print ("[info] chunk_id: "+str(chunk_id))
        
        ## SAME PREP AS BELOW
        
        ptr['chunk_id']=chunk_id
        ptr['page_num']=chunk['page_num']
        ptr['filename']=chunk['filename']
        ptr['filename_path']=chunk.get('filename_path','')
        
        ######################################################
        ## CALL STAND-ALONE CHUNK PROCESSING
        chunk,ptr,doc_dict,meta,transaction_count=process_chunk_page(chunk,ptr,doc_dict,meta,options)
        ######################################################
        print ("="*50)
        print ("DOC DIC: "+str(doc_dict))
        print ("PTR    : "+str(ptr))
              
    return

def process_chunk_page(chunk,ptr,doc_dict,meta,options):
    ## KEEP CHUNK PROCESSING AS SEPARATE FUNCTION  (possibly multithreaded)
    
    transactions_count=0
    
    branches=[]
    branches=['transaction_processing_pipeline']
    
    ## year maybe since used on statement date, wells fargo and generals?
    # alg_get_page_year()

    #######################################
    ## SMART EXTRACT STATEMENT/DOC LEVEL FIELDS
    #- account_number, bank_name, etc.
    #- updates ptr!
    #- bank_name, etc.
    page_level_record,ptr=smart_extract_fields(chunk,ptr)
    check_ptr(ptr)  #Dev
    smart_store_fields(page_level_record,chunk,ptr)
    
    #######################################
    ## MAIN PIPELINE ACTIVATE VARIABLES
    #- chunk_id=case_id+"-"+scope+"-"+filename+"-"+str(page_number)
    #- assume chunk scope is page
    #- recall, call_processing_pipeline does full transaction: extract, normalize, store

    print ("PTR: "+str(json.dumps(ptr,indent=4)))

    #############################################
    ### transaction processing vars:
    vars={}
    vars['case_id']=chunk['case_id']
    vars['statement_id']=ptr['statement_id']     #via smart_extract_
    vars['epage']=chunk['epage']                           #via chunking
    vars['input_filename']=chunk['filename']
    vars['filename_path']=chunk.get('filename_path','')
    vars['input_page_number']=chunk['page_num']
    vars['ptr']=ptr
    vars['allow_cache']=options.get('allow_cache',True)
    vars['db_commit']=options.get('db_commit',True) #Always commit unless debug
    
    # doc_dict blank because ptr should track active x
    vars['doc_dict']=doc_dict   #More detailed doc info (ie to track type)


    if 'transaction_processing_pipeline' in branches:
        #* also applies: logical_markup_transactions() for custom validation


#THREAD_QUIET        try: logging.info("[start transaction extract and store]: "+str(vars))
#THREAD_QUIET        except: pass #Patch output
#LIKE:  print(("="*20+" MULTIPLE TRIES ON PAGE2T NOTE ACTIVE PROMPT: "+str(model)+" "+str(full_prompt)).encode('utf-8', errors='replace').decode())


        transactions,cypher,trans_meta=call_transaction_processing_pipeline(**vars)
        meta.update(trans_meta)

        ## SPECIAL HANDLING [ ] 
        if trans_meta.get('transactions_not_saved',[]):
            #[ ] handle special exceptions
            #- this is cypher
            ## Log to agent or up
            #[x] this happened in corrupt pdf with multiple single chars!
            logging.error("[error] transaction not saved!! Invalid at: "+str(trans_meta))
            logging.dev("[error] transaction not saved!! Invalid at: "+str(trans_meta))

        logging.info("[done transaction extract and store]")

        transactions_count+=len(transactions.get('all_transactions',[]))

    #############################################

    return chunk,ptr,doc_dict,meta,transactions_count


    
def run_pipeline(job={}, Agent=None, options={}):
    global Storage
    if not Agent:
        Agent=Smart_Agent()

    if not job:
        raise Exception("[error] no job provided -- check flow [ ]")
    case_id=job['case_id']
    logging.info("[debug] running job / case id: "+str(case_id))

    meta={}
    meta['count_transactions']=0

    """
        mega:   # entire data set. Specifically targeting fields
        run:    # run/cycle speicifc (ie/ all ins & outs -- replay run option?)
        pipe:   # the meta data on pipeline running (errors etc)
        iagent: # the abstract agent helper (aka API)
        - assumed process to apply to each mega input
        - reload/resume state tracking possible
        - use API interface rather then direct library imports
        - a_* for module level. acts on mega. could be class but upper level here.
    """

    run={}
    run['id']=str(uuid.uuid4())
    
    ptr={}

    ## Job scheduling note started
    
    ## New db log
    log_job_time_started=int(time.time())
    log2hub(case_id=case_id,current_state='starting',job_time_started=log_job_time_started,meta={})

    job=Agent.note_job_status(job,'running_KBAI_processing_pipeline')
    
    FORCE_INIT_MEGA=True

    ## mega load
    if FORCE_INIT_MEGA:
        logging.info("[debug] force init mega cause want multi_chunks")
        mega=init_mega(case_id=case_id)
    else:
        mega=Storage.db_get(case_id,'record',name='megas')
        if not mega:
            mega=init_mega(case_id=case_id)
    

    ## MAIN PHASE:  normalize
    #- [ ] optionally use cache
    out_fields=['file_pages']

    #########################################
    ## Load pdfs into document object(s)
    #########################################
    #print ("[ ] force do normalize!  Recall, file pages is across all documents")
    if not all(field in mega['fields'] for field in out_fields):
        out_normalize=do_normalize(mega,run=run,job=job)  #<-- prepare epages etc.
        #^ filename.pages=[page_text]
        
    ## Map path filenames to mega
    #> migrate pdf for downstream processing (ie/ wells fargo transactions)
    if job.get('path_filenames',''):
        mega['path_filenames']=job.get('path_filenames',[])  #[(fullpath,basepath)]

    ## CHUNK PROCESSING
    #- Sub-processing smaller units (pages)
    count_chunks=prep_chunks(mega)
    
    job=Agent.set_job_field(job,'pages_count',count_chunks)

    print ("[info] total chunks to process: "+str(count_chunks))

    ## See source_schema.py PTR_SCHEMA
    ptr_temp=ptr
    ptr={}
    if ptr_temp: ptr['last_ptrs']+=[ptr_temp]
    ptr['case_id']=case_id
    
    ### EVERTHING BELOW IS FORWARD MOTION/MEMORY
    
    BRANCH='SINGLE_THREAD'
    BRANCH='MULTI_THREAD'
    
    print ("MEGA KEYS: "+str(mega.keys()))
    # dict_keys(['id', 'chunks', 'statements', 'case_id', 'fields', 'file_pages', 'doc_dict', 'multi_chunks', 'count_transactions'])
    
    log2hub(case_id=case_id,current_state='start_threading',job_time_started=log_job_time_started,meta={})
    if 'MULTI_THREAD' in BRANCH:
        multi_chunk_count=len(mega['multi_chunks'].keys())
        print ("Multi chunk count: "+str(multi_chunk_count))

        if not multi_chunk_count:
            print ("NO CHUNKS (maybe you're using a cached mega): "+str(mega['multi_chunks']))
            raise Exception("[error] no multi_chunks found")
        
        start_time=time.time()
        
        ## multi_chunks are sets of chunks (pages in 1 statement)
        threaded_results=[]
        for multi_chunk_id in mega['multi_chunks']:
            multi_chunk=mega['multi_chunks'][multi_chunk_id]
            print ("[info] multi_chunk_id: "+str(multi_chunk_id))
            
            ## CREATE INSTANCE OF ALL VARS

            if THREAD_COUNT:
                ## Get thread and execute if able otherwise wait
                ptr=copy.deepcopy(ptr)
                meta=copy.deepcopy(meta)
                options=copy.deepcopy(options)
                logging.info("[call at thread count]: "+str(THREAD_COUNT))
                Multi.execute(process_statement_chunk_pages,multi_chunk=multi_chunk,ptr=ptr,meta=meta,options=options)
                
                ### CHECK FOR COMPLETION RESPONSES
                #- hard fail on error? #- see: wait_for_completed, get_completed, etc.
                completed=Multi.get_completed(fail_on_error=True,verbose=True )#Dec 16 verbose)
                threaded_results+=completed
                if completed: print ("[debug] raw THREAD RESPONSE (expect none): "+str(completed))
                
                expected_count=len(mega['multi_chunks'].keys())
                completed_count=len(threaded_results)
                logging.info("[debug] threaded completed count: "+str(completed_count)+" of "+str(expected_count))

            else:
                ## Non-threaded but have batches of chunks done sequentially
                process_statement_chunk_pages(multi_chunk,ptr,meta,options)
                
        ## Wait for all threads to complete
        #- include 1 hour max timeout on waiting for final results
        if THREAD_COUNT:
            print ("[debug] waiting for all threads to complete")
            max_wait_time=4*60*60    # 4 and 2 hour timeout on 4k nodes
            all_results=Multi.wait_for_all_results(max_wait_time=4*60*60,delay=0.5, fail_on_error=True, update_interval=30)
            print ("[debug] all threads complete")
            
            
        run_time=time.time()-start_time
        print ("RAW RUN TIME: "+str(run_time))
        logging.info("[info] raw run time: "+str(run_time))
        

    elif 'SINGLE_THREAD' in BRANCH:
    
        doc_dict={}
        for chunk_id in mega['chunks']:
            chunk=mega['chunks'][chunk_id]
    
            ptr['chunk_id']=chunk_id
            ptr['page_num']=chunk['page_num'] #DOC LEVEL
            ptr['filename_path']=chunk.get('filename_path','')
    
            ######################################################
            ## CALL STAND-ALONE CHUNK PROCESSING
            chunk,ptr,doc_dict,meta,transaction_count=process_chunk_page(chunk,ptr,doc_dict,meta,options)
            ######################################################
            print ("="*50)
            print ("DOC DIC: "+str(doc_dict))
            print ("PTR    : "+str(ptr))
            
    else:
        raise Exception("[error] unknown branch: "+str(BRANCH))
    
    
    
    
    
    
    #        ## EXTRA META NOT REQUIRED
    #        run['transactions_processed']=run.get('transactions_processed',0)+transaction_count
    ##        mega['count_transactions']=mega.get('count_transactions',0)+transaction_count
    #        mega['doc_dict']=doc_dict
    #
    #        ### UPDATE MEGA + tracking
    #        #[1]  set timestamp on chunk done
    #        chunk['processed_on']=int(time.time())
    #        ## Mega update (optional partial save)
    #        mega['chunks'][chunk_id]=chunk
    #        Storage.db_put(case_id,'record',mega,name='megas')
    #
    ##        job_meta={}
    #        job_meta['progress']=chunk['page_num']/count_chunks
    #        job=Agent.note_job_status(job,'running_KBAI_processing_pipeline',meta=job_meta)
    ##


    # Mega store
    Storage.db_put(case_id,'record',mega,name='megas')
    
    ### RUN ALL REPORTS FOR CASE
    try:
        from c_macros.ENTRYPOINT_generate_all_reports import CALL_generate_all_reports  #JC DEBUG circular import
        CALL_generate_all_reports(case_id)
    except Exception as e:
        logging.error("[error] failed to generate reports: "+str(e)+" for case: "+case_id)

    ## END MAIN PIPELINE
    job=Agent.note_job_status(job,'end_KBAI_processing_pipeline') #<-- may be called on return later but ok

    log2hub(case_id=case_id,current_state='finished',job_time_started=log_job_time_started,meta={})

    job={}

    print ("[info] run processed transaction count: "+str(run.get("transactions_processed",0)))
    meta['ptr']=ptr
    return meta


def ORG_SINGLE_run_pipeline(job={}, Agent=None, options={}):
    stop=wellsfargomaybefilename
    global Storage
    if not Agent:
        Agent=Smart_Agent()
    meta={}
    meta['count_transactions']=0

    """
        options:# dev control over run ie: only_page=3

        mega:   # entire data set. Specifically targeting fields
        run:    # run/cycle speicifc (ie/ all ins & outs -- replay run option?)
        pipe:   # the meta data on pipeline running (errors etc)
        iagent: # the abstract agent helper (aka API)
        - assumed process to apply to each mega input
        - reload/resume state tracking possible
        - use API interface rather then direct library imports
        - a_* for module level. acts on mega. could be class but upper level here.
    """

    pipe={}  # pipeline info
    run={}
    run['id']=str(uuid.uuid4())
    
    ## Clean givens
    if 'only_pages' in options:
        options['only_pages']=[int(x) for x in options['only_pages']]

    ptr={}
    running=True
    while running:
        running=False  #Run once on this setup

        if not job:
            raise Exception("[error] no job provided -- check flow [ ]")
            job=Agent.get_next_job()

        case_id=job['case_id']


        ## Job scheduling note started
        job=Agent.note_job_status(job,'running_KBAI_processing_pipeline')

        ## mega load
        mega=Storage.db_get(case_id,'record',name='megas')
        if not mega:
            mega=init_mega(case_id=case_id)
        
        print ("[debug] running job / case id: "+str(case_id))

        ## MAIN PHASE:  normalize
        #- [ ] optionally use cache
        out_fields=['file_pages']

        #print ("[ ] force do normalize!  Recall, file pages is across all documents")
        if not all(field in mega['fields'] for field in out_fields):
            out_normalize=do_normalize(mega,run=run,job=job)
            #^ filename.pages=[page_text]

        ## CHUNK PROCESSING
        #- Sub-processing smaller units (pages)
        count_chunks=prep_chunks(mega)
        
        job=Agent.set_job_field(job,'pages_count',count_chunks)

        print ("[info] total chunks to process: "+str(count_chunks))

        ## Per-chunk processing
        #- other options but this scoped to page ~ llm limit
        #- heavy sequential processing
        #- chunks makes sense here but not necesary for full mega

        branches=[]
        branches=['transaction_processing_pipeline']

        ## See source_schema.py PTR_SCHEMA
        ptr_temp=ptr
        ptr={}
        if ptr_temp: ptr['last_ptrs']+=[ptr_temp]
        ptr['case_id']=case_id
        
        chunk_counter=0
        for chunk_id in mega['chunks']:
            chunk_counter+=1

            Agent.set_job_field(job,'page_active',chunk_counter)

            chunk=mega['chunks'][chunk_id]

            logging.info("="*50)
            logging.info("[at chunk] page: "+str(chunk['page_num'])+" of "+str(count_chunks))

            #######################################
            ## POINTER update (ie/ page level via chunk)
            #- ptr is used to track code back to doc source + concepts
            ptr['chunk_id']=chunk_id
            ptr['page_num']=chunk['page_num'] #DOC LEVEL
            ptr['filename']=chunk['filename']
            ptr['filename_path']=chunk.get('filename_path','')
            check_ptr(ptr)  #Dev


            #######################################
            ## SMART EXTRACT STATEMENT/DOC LEVEL FIELDS
            #- account_number, bank_name, etc.
            #- updates ptr!
            #- bank_name, etc.
            page_level_record,ptr=smart_extract_fields(chunk,ptr)
            check_ptr(ptr)  #Dev
            smart_store_fields(page_level_record,chunk,ptr)
            
            
            ## Global options (dev)
            #- move page skip AFTER page processing (want bank_name etc)
            if options.get('only_pages',[]):
                if not chunk['page_num'] in options['only_pages']:
                    logging.info("[dev_options skip page] "+str(chunk['page_num']))
                    continue
                
            #######################################
            ## MAIN PIPELINE ACTIVATE VARIABLES
            #- chunk_id=case_id+"-"+scope+"-"+filename+"-"+str(page_number)
            #- assume chunk scope is page
            #- recall, call_processing_pipeline does full transaction: extract, normalize, store

            print ("PTR: "+str(json.dumps(ptr,indent=4)))

            #############################################
            ### transaction processing vars:
            vars={}
            vars['case_id']=case_id
            vars['statement_id']=ptr['statement_id']     #via smart_extract_
            vars['epage']=chunk['epage']                           #via chunking
            vars['input_filename']=chunk['filename']
            vars['filename_path']=chunk.get('filename_path','')
            vars['input_page_number']=chunk['page_num']
            vars['ptr']=ptr
            vars['allow_cache']=options.get('allow_cache',True)
            vars['db_commit']=options.get('db_commit',True) #Always commit unless debug
            
            # doc_dict blank because ptr should track active x
            vars['doc_dict']=mega['doc_dict']   #More detailed doc info (ie to track type)

            if 'transaction_processing_pipeline' in branches:
                #* also applies: logical_markup_transactions() for custom validation

                logging.info("[start transaction extract and store]: "+str(vars))
                transactions,cypher,trans_meta=call_transaction_processing_pipeline(**vars)
                meta.update(trans_meta)

                ## SPECIAL HANDLING [ ] 
                if trans_meta.get('transactions_not_saved',[]):
                    #[ ] handle special exceptions
                    #- this is cypher
                    ## Log to agent or up
                    #[x] this happened in corrupt pdf with multiple single chars!
                    logging.error("[error] transaction not saved!! Invalid at: "+str(trans_meta))
                    logging.dev("[error] transaction not saved!! Invalid at: "+str(trans_meta))

                logging.info("[done transaction extract and store]")
                run['transactions_processed']=run.get('transactions_processed',0)+len(transactions.get('all_transactions',[]))
                meta['count_transactions']=meta.get('count_transactions',0)+len(transactions.get('all_transactions',[]))
            #############################################


            ### UPDATE MEGA + tracking
            #[1]  set timestamp on chunk done
            chunk['processed_on']=int(time.time())

            ## Mega update (optional partial save)
            mega['chunks'][chunk_id]=chunk
            Storage.db_put(case_id,'record',mega,name='megas')

            # Running or basic progress
            progress=chunk['page_num']/count_chunks
            job_meta={}
            job_meta['progress']=chunk['page_num']/count_chunks
            job=Agent.note_job_status(job,'running_KBAI_processing_pipeline',meta=job_meta)

#            print ("[debug] break at first chunk!")
#            break

        # Mega store
        Storage.db_put(case_id,'record',mega,name='megas')

        ## END MAIN PIPELINE
        job=Agent.note_job_status(job,'end_KBAI_processing_pipeline') #<-- may be called on return later but ok

        job={}
        running=False #End -- assume run once

        ## DEBUG
#D4        print ("Run page texts first 60 chars: "+str(run['page_text']))

    ## Final stats output
    print ("[info] run processed transaction count: "+str(run.get("transactions_processed",0)))
    
    meta['ptr']=ptr

    return meta


def interface_run_pipeline(job={},Agent=None,options={}):
    ## a_agent/run_agent.py
    ## job:  dict from Agent managed job scheduler
    ## Agent:  smart agent (if None will spawn itself)

    #[ ] check job not already running
    meta=run_pipeline(job=job,Agent=Agent,options=options)

    return meta



if __name__=='__main__':
    branches=['run_pipeline']
    for b in branches:
        globals()[b]()


"""
"""
