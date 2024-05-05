import os
import sys
import copy
import codecs
import json
from datetime import datetime
import re
import ast
import random

import configparser as ConfigParser

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")

from w_llm.llm_interfaces import LazyLoadLLM
from alg_clean_transactions import adjust_transactions_top_level
from alg_easy_extracts import alg_get_page_year

from schema_statement_kinds import dev_get_bank_schema

#from algs_extract import alg_json2dict
from llm_p2t_support import local_epage2page_text
from llm_p2t_support import is_normal_valid_date
from llm_p2t_support import estimate_number_of_transactions_on_page
from llm_p2t_support import alg_force_skip_page
from llm_p2t_support import split_complicated_pages
from llm_p2t_support import alg_insert_bullet_point
from llm_p2t_support import force_manual_page_fixes
from fix_page_artifacts import auto_clean_page_text  

from m_autoaudit.auto_auditor import AutoAuditor
from m_autoaudit.auto_auditor import An_Incident
from m_autoaudit.auto_auditor import register_plugin

from a_agent.global_routes import get_global_routes
from typing import Dict, Any

from get_logger import setup_logging
logging=setup_logging()


#1v5# JC  Mar 20, 2024  Allow for global configuration of base method
#1v4# JC  Mar 14, 2024  Add Auto Audit approach if page2T looks difficult  (summary section or complex)
#1v3# JC  Jan 25, 2024  Extend auto clean page text
#1v2# JC  Jan 15, 2024  Migrate functions to llm_p2t_support if stand-alone
#1v1# JC  Jan 13, 2024  Add hard coded filter for transactions (section=Account Summary for example)
#1v0# JC  Jan 11, 2024  Various.  But, extend is date normal to catch all errors!
#0v9# JC  Dec 20, 2023  Wells Fargo allow auto data extract (close debit/credit columns cause issues)
#0v8# JC  Nov 21, 2023  Extend LLM hotswap options
#0v7# JC  Nov  1, 2023  Allow for section skipping (CHASE Checking summary or similar via schema_statement_kinds)
#0v6# JC  Oct 31, 2023  Normalize amounts to positive!
#0v5# JC  Oct 27, 2023  Add re.sub as option for per-bank or pdf oddities: "- 18.81 vs -18.81"
#0v4# JC  Oct 25, 2023  Add skip page regex (ie/ just checks etc.)
#0v3# JC  Oct 13, 2023  Wells fargo has sections as headers.
#0v2# JC  Sep 29, 2023  Leverage GPT4 on failure/retry (from gpt 3.5 default)
#0v1# JC  Sep  6, 2023  Init


"""
    EXTRACT TRANSACTIONS FROM A TEXT PAGE OF STATEMENT
    - works via single text pages but carries forward global vars between pages:
        > relevant account number, 
    - ?carry fwd section?
    
    ADJUSTING:
      This file cal be applied generically
      - see schema_statement_kinds.py for handling customizations
        > generally follows at: "If [keyword] found on this page -> then add this bulletpoint to the prompt"
        
    
    TESTING:
    - see function_test_page2transactions.py

"""


## Global defs
GLOBAL_ROUTES=get_global_routes()


Config = ConfigParser.ConfigParser()
Config.read(LOCAL_PATH+"../w_settings.ini")
SMARTEST_MODEL_NAME=Config.get('performance','smartest_llm_name')
BASE_MODEL_NAME=GLOBAL_ROUTES['global_config']['llm_page2transactions_base_model_name'] #gpt-3.5-turbo org


BANKS_SCHEMA=dev_get_bank_schema()

def suggest_section_heads(page_text):
    global BANKS_SCHEMA
    ### SUGGEST HEADINGS
    #- originally was default, then pre-pend if match ie BOA. THEN schema based.
    MAX=4
    heads=[]
    
    ### APPLY SCHEMA BASED OPTIONS FIRST
    #> iter all kinds, all section match types and suggest if match
    #   ^^ ideally you KNOW what kind of statement this is
    for bank_kind in BANKS_SCHEMA['banks']:
        for section_heading in BANKS_SCHEMA['banks'][bank_kind].get('section_headings',[]):
            if re.search(section_heading,page_text,flags=re.I):
                heads+=[section_heading]

    ### ORIGINAL DEFAULT SECIONS <-- chase. ** these will now be included since CHASE schema should match
    #- but keep some for fun anyways if no matches.
    default_append=['ATM & DEBIT CARD WITHDRAWLS','CASH TRANSACTIONS','ELECTRONIC WITHDRAWALS']


    ##### Include odd headers
    ## MISC?
    if 'Checks ' in page_text:  #BOA  Checks - continued
        heads+=['Checks']
    if 'Check images' in page_text:  #BOA  Check images ** because actually don't want this section!
        heads+=['Check images']
        
    ## Chase
    if 'DEPOSITS AND ADDITIONS' in page_text:
        heads=['DEPOSITS AND ADDITIONS']+heads

    #BOA
    if re.search(r'TRANSACTION DETAIL',page_text,flags=re.I):
        heads+=['Transaction Detail']

    heads+=default_append
    
    # UNIQUE!
    uheads=[]
    for head in heads:
        if not head in uheads:
            uheads+=[head]

    heads=uheads[:MAX]

    #(ie/ ATM & DEBIT CARD WITHDRAWALS, CASH TRANSACTIONS, ELECTRONIC WITHDRAWALS, etc)
    sections="(ie/ "+", ".join(uheads)+", etc)"
    #print ("[debug] auto sections: "+str(sections))
    return sections

def suggest_record_samples(page_text):
    global BANKS_SCHEMA
    ## Fewer the better
    
    ## Base
    record={"all_transactions":[]}
    
    ## Apply ALL possibles via schema on direct regex matching
    for bank_kind in BANKS_SCHEMA['banks']:
        for sample in BANKS_SCHEMA['banks'][bank_kind].get('samples',[]):
            if re.search(sample[0],page_text,flags=re.I):
                record['all_transactions']+=sample[1]

    ## Default if none
    if len(record['all_transactions'])<2:
        record["all_transactions"]+=[{"transaction_description": "full description", "transaction_amount": 123.45, "transaction_date": "2021-01-01", "section":"Cash transactions"}]
        
    return record

def get_p2t_prompt(page_text):
    ## Various.
    #- track performance w/ Storage

    ## NOTES:
    ## THIS CONFUSES IT:
    #- Any single quotes in the data should be escaped with a backslash (ie/ \')

    all_prompts={}

    ###########################################
    #  ACTIVE PROMPT
    ###########################################
    ## SUGGEST SECTION HEADS
    record=suggest_record_samples(page_text)

    ## DYNAMIC transactions

    ## BOA (schoolkidz)
    if re.search(r'Bank reference',page_text,flags=re.I):
        record['all_transactions'][0]['transaction_reference']='9023444333555'

    #Nov1:  Missing Domestic Incoming Wire Fee twice- There shouldn't be duplicates, so return all transactions on every row!
    #- There shouldn't be duplicates, so return all transactions on every row!
    prompt={}
    prompt['index']=1
    prompt['name']='page2transactions1'
    prompt['experiment']='removed transaction_id' #Update exp
    prompt['prompt']="""
    Please retrieve details about the transactions from the following bank statement page.
    If you cannot find the information from this text then return "".  Do not make things up. Always return your response as a valid json (no single quotes).
    - Include any section heads """+suggest_section_heads(page_text)+"""
    - Format the transaction_date as yyyy-mm-dd
    - The transaction_description should include the address and be fully descriptive (it may be multi-line)
    All the transactions should be included in a valid JSON list (double quotes):

    """+str(json.dumps(record))+"""

    Bank Statement Page:
    =====================

    """
#D1    print ("PROMPT: "+str(prompt['prompt']))

    all_prompts[prompt['name']]=prompt

    ###########################################
    #  "DOT DOT DOT"  PROMPT TO REITERATE NOT TO END WITH ...
    ###########################################
    ## SUGGEST SECTION HEADS
    # Sept 29:  GPT-4 will include an Explanation.
    record=suggest_record_samples(page_text)

    ## DYNAMIC transactions

    ## BOA (schoolkidz)
    if re.search(r'Bank reference',page_text,flags=re.I):
        record['all_transactions'][0]['transaction_reference']='9023444333555'

    prompt={}
    prompt['index']=1
    prompt['name']='page2transactions1_NO_DOT_DOT_DOT'
    prompt['experiment']='removed transaction_id' #Update exp
    prompt['prompt']="""
    Please retrieve details about the transactions from the following bank statement page.
    If you cannot find the information from this text then return "".  Do not make things up. Always return your response as a valid json (no single quotes).
    - Include any section heads """+suggest_section_heads(page_text)+"""
    - Format the transaction_date as yyyy-mm-dd
    - The transaction_description should include the address and be fully descriptive (it may be multi-line)
    All the transactions should be included in a valid JSON list (Double quotes, Do NOT end with ..., do NOT include any Explanations):

    """+str(json.dumps(record))+"""

    Bank Statement Page:
    =====================

    """
    #D1#  print ("PROMPT: "+str(prompt['prompt']))

    """
        PROMPT ENGINEERING NOTES:
        - gpt-4 may include Explanation: in results => specifically tell it not to.
    """
    all_prompts[prompt['name']]=prompt


    ###########################################
    #  GPT-4 request all large (ie 72 trans)
    ###########################################
    ## SUGGEST SECTION HEADS
    # oct 1:  GPT-4 will include an Explanation.
    record=suggest_record_samples(page_text)

    ## DYNAMIC transactions

    ## BOA (schoolkidz)
    if re.search(r'Bank reference',page_text,flags=re.I):
        record['all_transactions'][0]['transaction_reference']='9023444333555'

    prompt={}
    prompt['index']=1
    prompt['name']='page2transactions_GPT4_lotsa_records'
    prompt['experiment']='upto 75 records'
    prompt['prompt']="""
    Please retrieve details about the transactions from the following bank statement page.
    If you cannot find the information from this text then return "".  Do not make things up. Always return your response as a valid json (no single quotes).
    - Include any section heads """+suggest_section_heads(page_text)+"""
    - Format the transaction_date as yyyy-mm-dd
    - The transaction_description should include the address and be fully descriptive (it may be multi-line)
    All the transactions should be included in a valid JSON list.   Include EVERY record.  Do not truncate the response.  Be verbose but don't include explanations. There are a lot more then 10 transactions on this page:


    """+str(json.dumps(record))+"""

    Bank Statement Page:
    =====================

    """
    #D1#  print ("PROMPT: "+str(prompt['prompt']))

    """
        PROMPT ENGINEERING NOTES:
        - gpt-4 on cases with 75 or >30 transactions
    """
    all_prompts[prompt['name']]=prompt
    return all_prompts



def validate_transactions(transactions,doc_dict={}):
    ## BOA has tables that pdfminer puts into stacked columns
    ## swap to PyPDF2!
    warnings=[]

    stats={}
    stats['count_transactions']=0
    stats['count_amounts']=0
    is_valid=True

    try: stats['count_transactions']=len(transactions['all_transactions'])
    except: pass

    if stats['count_transactions']:
        for entry in transactions['all_transactions']:
            if isinstance(entry,dict):
                try:
                    if entry['transaction_amount']:
                        stats['count_amounts']+=1
                except:
                    entry['transaction_amount']=""

    ##[1] #  ## WARNINGS
    if stats['count_transactions']>3 and 0.75>stats['count_amounts']/stats['count_transactions']:
        msg="[error] missing transaction amounts: "+str(json.dumps(doc_dict))
        warnings.append("missing_transaction_amounts")
        logging.error(msg)
        logging.dev(msg)
        
    ##[2] # Raw text search ie/ is it recurgitating what I asked?
    if '123 ABC STREET' in str(transactions):
        logging.warning("[warning] LLM is recurgitating what I asked: "+str(transactions))
        is_valid=False
        
    ##[3] # Empty?
    if not stats['count_transactions']:
        logging.warning("[warning] no transactions: "+str(transactions))
        is_valid=False
        
    ##[3.5]  is string?
    for entry in transactions.get('all_transactions',[]):
        if isinstance(entry,str):
            if not entry.strip():
                logging.warning("[entry is empty str]: "+str(entry))
                is_valid=False
            else:
                logging.warning("[entry is str]: "+str(entry))
                is_valid=False
        
    ##[4]
    if is_valid:
        ##[4] # Check dates cause seeing:  2020-03-41
        for entry in transactions.get('all_transactions',[]):
            the_date=entry.get('transaction_date','')
            if the_date: #Should be valid cause neo4j insert will fail!
                is_normal_date=is_normal_valid_date(the_date)
                if not is_normal_date:
                    logging.warning("Not normal date found: "+str(the_date))
                    is_valid=False

    print ("[debug validate transactions] transaction stats: "+str(stats))
    return stats,is_valid

def alg_remove_filter_transactions(transactions):
    global BANKS_SCHEMA
    ## Ideally not but speed up oddities

    if not isinstance(transactions,dict):
        logging.warning("[transactions is not dict]: "+str(transactions))
        return transactions

    all_amounts=[]
    new_entries=[]
    for entry in transactions.get('all_transactions',[]):
        keep_it=True
        if isinstance(entry,str):
            keep_it=False
            entry={} #String so empty

        if keep_it:

            #[A]  section: "Check images" is just images of checks so can discard
            #** should be done at page level already! (though sometimes cache has it)
            if entry.get('section','')=='Check images':
                keep_it=False
#D2#                logging.info("[filtering] removing check images: "+str(entry).encode('utf-8', errors='replace').decode('utf-8'))
                
        #[B]  If amount but no description then likely bad extraction so don't keep
        #[ ] do a QA check on existing records or remove entirely?
        if keep_it and entry.get('transaction_amount','') and not entry.get('transaction_description',''):
            keep_it=False
            logging.warning("[filtering] removing entry with amount but no description: "+str(entry))
            logging.dev("[filtering] removing entry with amount but no description: "+str(entry))

        #[C]  BANKS_SCHEMA (schema_statement_kinds)
        # i) remove summary sections as transactions ie/ Checking Summary or Checks paid is actually a duplicate!
        # - ok, apply all banks options here
        if keep_it:
            for bank_kind in BANKS_SCHEMA['banks']:
                for skip_section_regex in BANKS_SCHEMA['banks'][bank_kind].get('skip_sections',[]):
                    if re.search(skip_section_regex,entry.get('section',''),flags=re.I):
                        logging.info("[skip section]: "+str(entry))
                        keep_it=False
                    if re.search(skip_section_regex,entry.get('transaction_description',''),flags=re.I):
                        logging.info("[skip section description]: "+str(entry))
                        keep_it=False
                    
        #[D]  Don't keep bad ones
        if not entry.get('transaction_amount',''):
            logging.info("[skip entry without amount]: "+str(entry))
            keep_it=False
        elif not entry.get('transaction_date',''):
            logging.warning("[skip entry without date]: "+str(entry))
            logging.dev("[skip entry without date]: "+str(entry))
            keep_it=False
            
        ##[E+] EXTEND transaction keep it list
        if keep_it:
            keep_it=hardcode_transaction_removal_assumptions(entry,keep_it)
                
        #[F]  Fix transaction_amount.  OCR may drop period?!!   Colin:     output_filename='C:/scripts-23/watchtower/DEMO_SET/colin_for_dec_21/Wells Fargo JWM Raw 69.pdf'
        # But gpt already appends .0 to value so need to move upstream
        #all_amounts+=[entry.get('transaction_amount','')]
        
        ### MODIFICATION [ ] move
        #[G]  "transaction_description": "Wells Fargo Fee Refund 722102005436026 Nte*Obi*Addl Credit. Questions:1-800-424-0948\\",
        #- LLM responds with double quoted end of line will cause problems downstream (special case)
        #- remove escapes at raw data level (cypher will put back in if needed)
        if 'transaction_description' in entry:
            entry['transaction_description']=entry['transaction_description'].replace('\\','')

        if keep_it:
            new_entries+=[entry]
    if transactions.get('all_transactions',[]):
        transactions['all_transactions']=new_entries
        

    #print ("ALL AMOUNTS: "+str(all_amounts))
    return transactions

def hardcode_transaction_removal_assumptions(transaction,keep_it):
    #0v1# Jan 13, 2024  Migrate manual fix or obvious bad transactions here as stand-alone
    #- log all into logging.dev because shouldn't be here in the first place
    #!! Ideally this wouldn't be here but final filter is here until can be adjusted for
    
    if not keep_it: return keep_it
    reasons=[]

    #ie/ FIRM_REMOVE_DESCRIPTIONS=['Beginning Balance','Ending Balance'] #chrome-extension://efaidnbmnnnibpcajpcglclefindmkaj/https://core.epventures.co/api/v1/case/6570af77949fdfbf2c5810e8/pdf/20854c60-ecd4-4e7f-a611-e4b768429248.pdf?page=8&key=08cab371d4a85e05826756dd370b9e292cce198db97491503e54f2c24547d31d


    section=transaction.get('section','').lower()
    desc=transaction.get('transaction_description','').lower()
    
    ## SECTION BASED
    if 'beginning balance' in section:
        reasons+=['beginning balance in section']
        keep_it=False
    if 'daily ledger balances' in section:
        reasons+=['daily ledger balances in section']
        keep_it=False
    if 'account summary' in section:
        reasons+=['account summary in section']
        keep_it=False
    if 'summary'==section:
        reasons+=['summary in section']
        keep_it=False
    
    # Fargo specific
    if 'summary of checks written' in section:
        reasons+=['summary of checks written in section']
        keep_it=False
    if 'activity summary' in section:
        reasons+=['activity summary in section']
        keep_it=False
    if 'fee summary' in section:
        reasons+=['fee summary in section']
        keep_it=False

    ## DESCRIPTION BASED
    if re.search(r'^beginning balance',desc):
        reasons+=['Beginning balance at start of description']
        keep_it=False
    if re.search(r'^ending balance',desc):
        reasons+=['Beginning balance at start of description']
        keep_it=False
    if re.search(r'^total checks',desc):
        reasons+=['Total checks at start of description']
        keep_it=False
        
    #Patch
    if re.search(r'closing balance$',desc,re.I):
        reasons+=['closing balance at end of description']
        keep_it=False
    if re.search(r'opening balance$',desc,re.I):
        reasons+=['opening balance at end of description']
        keep_it=False
        

    ## SECTION AND DESCRIPTION BASED
    if keep_it:
        #[ ] case-by-case?
        both_equal=['deposits and other credits','service fees','checks','Withdrawals and other debits']
        for be in both_equal:
            if be==section==desc:
                reasons+=['both in section and description: '+str(be)]
                keep_it=False

    #################
    # WARNINGS
    #################
    # if section == description then consider warning
    # Maybe:  section='summary'
    if keep_it:
        #1) if equal
        if section and section==desc:
#            reasons+=['section equals description: '+str(section)]
            logging.info("[warning] section equals description: "+str(section))
            logging.dev("[warning] section equals description: "+str(section))
#            #keep_it=False
        #2) if 'summary' in section name
        if 'summary' in section:
#            reasons+=['summary in section: '+str(section)]
            logging.info("[warning] summary in section: "+str(section))
            logging.dev("[warning] summary in section: "+str(section))
            
        #3) if see amount = 123.45 then that's a sample record
            
    ## LOG
    if reasons:
        logging.dev("[hardcode_transaction_removal_assumptions] "+str(reasons)+" "+str(transaction))
        logging.info("[hardcode_transaction_removal_assumptions] "+str(reasons)+" "+str(transaction))

    return keep_it


def heuristic_page_stats(page_text):
    ### ESTIMATE TRANSATIONS ON PAGE
    ## Chase:
    #a)  Count max of YOUR REF: or Trn: (not transaction can have both)
    page_stats={}
    
    #### ESTIMATE TRANSACTIONS ON PAGE
    page_stats['estimated_transactions']=estimate_number_of_transactions_on_page(page_text)
    
    ### IS PAGE COMPLEX?
    ## Check page text for anomolies
    # Count number words
    
    #** keep sign since semantic value!
    count_numbers=len(re.findall(r'\b[\$]{0,2}[\d\,]+\b',page_text)) #**keep sign!
    page_stats['is_complex_page']=False

    #295 skips some dupicate rows# if count_numbers>300:  #*260 is fairly complex but 420 is 76 transactions, 335 is lots
    if count_numbers>280:  #*260 is fairly complex but 420 is 76 transactions, 335 is lots
        page_stats['is_complex_page']=True
        
    if page_stats['estimated_transactions']>30:
        page_stats['is_complex_page']=True
        
    page_stats['count_numbers']=count_numbers

    logging.info("[page_stats] "+str(page_stats))

    return page_stats


def formal_prompt_prep(all_prompts={},focus='normal',page_text='',page_lines=[],ptr={}):
    global BANKS_SCHEMA
    
    ## PARAMS:
    #ptr: general page to page pointer.  Ideally not used but gives better date period

    meta={}
    
    if focus=='normal':
        ## Normal (mostly chase but good)
        prompt_dict=all_prompts['page2transactions1']
        prompt=prompt_dict['prompt']
    elif focus=='gpt-4':
        prompt_dict=all_prompts['page2transactions_GPT4_lotsa_records']
        prompt=prompt_dict['prompt']
    elif focus=='dotdotdot':
        prompt_dict=all_prompts['page2transactions1_NO_DOT_DOT_DOT']
        prompt=prompt_dict['prompt']
    else:
        raise Exception("[error] invalid focus: "+str(focus))
                        
        
    #### Statement kind based additions
    ## If looks like Wells Fargo then no sections so infer from column headings
    if 'Transaction history' in page_text:
        if focus=='normal': pass

        stmt='- Note: "section":"Transaction history" is not a section. Infer the section from the likely headings: Deposits and Additions or Withdrawals and Subtractions'
        prompt=alg_insert_bullet_point(prompt,stmt)
        
    ## If FirstCitizensBank then possible 3 columns of descriptive checks
    #a)  if 'First Citizens Bank' in page_text: pass
    add_suggest_three_columns=False
    for liner in page_lines:
        if liner.count("Check No.") == 3:
            meta['is_complex_page']=True

    #b)  Use schema for extra notes
    for bank_kind in BANKS_SCHEMA['banks']:
        for bullet_regex,bullets in BANKS_SCHEMA['banks'][bank_kind].get('bullets',[]):  #ltiple bullets
            if re.search(bullet_regex,page_text,flags=re.I):
                for bullet in bullets:
                    prompt=alg_insert_bullet_point(prompt,bullet)
                    
    #c) Include period range of statement
    if ptr.get('statement_period',''):
        bullet='- The statement period is: '+ptr['statement_period']
        prompt=alg_insert_bullet_point(prompt,bullet)

    #d) Chase started having difficulties with year
    #[?] suggest with chase or all so dates are resolved correctly?  Do all for now
    year=alg_get_page_year(page_text,statement_date=ptr.get('statement_date',''))
    if year:
        # Suggest year format
        bullet='- Note:  The year is likely: '+str(year)+' So, 04/20  -->  '+str(year)+'-04-20'
        prompt=alg_insert_bullet_point(prompt,bullet)
        

    return prompt,meta

### * Auto Audit 'demo' of local plugin to apply  (see: apply_auto_audit.py)
@register_plugin(['odd_content_not_3.5'])
def challenging_content(scope, schema, state):
    #** hard to enforce schema stuff while remaining flexible so have loosely bound but modular

    suggestive_actions=[]
    suggest_good_results=[]

    incidents=[]
    report={}
    
    ## Check state assuming
    if 'content' in state:
        
        # A)  recall if >250 numbers then yes challenging  (move this from codebase to here)
        if len(re.findall(r'[\d\.\,]+', state['content']))>250:
            Incident=An_Incident('content has over 250 numbers',scope='odd_content_not_3.5')
            Incident.suggest_action("use_gpt_4")
            incidents.append(Incident)
            
        # B)  if summary in text then do blanket gpt-4 suggestive action
        if re.search(r'summary',state['content'],re.IGNORECASE):
            ## Assume state 'models' would have '4' in it
            if '4' in str(state.get('models',[])):
                print ("[debug] ignore if it thinks gpt-4 already used")
            else:
                Incident=An_Incident('content has SUMMARY => no 3.5',scope='odd_content_not_3.5')
                Incident.suggest_action("use_gpt_4")
                incidents.append(Incident)
    
    return incidents,report

@register_plugin(['hallucination_gpt3_5'])
def audit_hallucinations(scope, schema, state):
    incidents=[]
    report={}
    probh=0
    assumed_model_used='gpt-3.5'  #Not used but for reference since suggested_actions is to gpt-4

    ### General prompt terms repeated back
    #    ^yes, this is rather specific to application
    bad_terms=['123 Main St','Anytown,']
    
    def search_in_dict_dump(data: Dict[str, Any], search: str) -> bool:
        match=False
        json_content = json.dumps(data)
        pattern = re.compile(search)
        match=pattern.search(json_content)

    for term in bad_terms:
        if search_in_dict_dump(state, term):
            probh=70
            incidents.append(An_Incident('Hallucinated address: '+term))
            print ("[audit_hallucinations] Hallucinated address: "+term)
            break

    return incidents,report
    
## Called from:  call_transaction_processing_pipeline @ call_llm_process.py
def llm_page2transactions(epage=None,bank_name='',doc_dict={},page_text='',try_cache=True, verbose=True, ptr={}):
    global BANKS_SCHEMA, SMARTEST_MODEL_NAME, BASE_MODEL_NAME
    
    ## PARAMS
    # To grab global state (statement-wise, use ptr directly)
    # ptr: standard pointer of info
    # doc_dict:  not used?
    
    ## BASE_MODEL_NAME suggestions:
    #- recall, will fall back to smarter model if complex page!


    THREAD_QUIET=False

    ## doc_dict:  full path of input file (filename_path, page_number)
    meta={}
    transactions={'all_transactions':[]}
    
    ## [ ] optionally upgrade to KBAI
    if page_text or doc_dict:
        logging.warning("[warn] allow page_text during debug only")
    
    ## Initialize base LLM model
    #- original gpt-3.5-turbo
    validated_types=['gpt-3.5-turbo','gpt-4','gpt-4-turbo']
    if not BASE_MODEL_NAME in validated_types:
        raise Exception("[error] invalid BASE_MODEL_NAME: "+str(BASE_MODEL_NAME))
    LLM=LazyLoadLLM.get_instance(model_name=BASE_MODEL_NAME)
    
    ### TRACK odd pdf conversions:
    #- pdfminer:  schoolkidz page 10 puts some amounts to very end of text list. Basically unuseable.
    #                  ^ should be able to detect with missing amounts (if found at all though)
    if page_text:
        ## See above warning debug only
        pass
    else:
        page_text=local_epage2page_text(epage,bank_name=bank_name)

    if page_text is None:
        print ("[warning] page_text is None")
        raise Exception("[error] page_text is None at: "+str(epage))
    
    ###############################################
    ### CLEAN PAGE TEXT
    page_text=auto_clean_page_text(page_text)
    
    ## Include global statement period or year
    
    ## Pseudo suggest date range since entries may not have year
    #statement_date='2016-04-15'  #Default start of period
    #statement_period: '2016-04-15 to 2016-05-12''
    year=alg_get_page_year(page_text,statement_date=ptr.get('statement_date',''))

    page_text=force_manual_page_fixes(page_text,year=year,statement_date=ptr.get('statement_date',''),statement_period=ptr.get('statement_period',''))
    ###############################################
    

    page_texts=split_complicated_pages(page_text)
#    page_texts=[page_text]

    sub_transactions=[]
    
    for page_text in page_texts:
        page_lines=page_text.splitlines()
    
        ## Check page text for anomolies
        page_stats=heuristic_page_stats(page_text)
        
        ####  FORCE skip page on regex
        skip_it,skip_reason=alg_force_skip_page(page_text, skip_regexes=BANKS_SCHEMA.get('skip_entire_page_regex',[]))
        if skip_it:
            logging.info("[SKIP PAGE BECAUSE]: "+str(skip_reason))
            continue

    
        all_prompts=get_p2t_prompt(page_text)

        prompt,formal_meta=formal_prompt_prep(all_prompts=all_prompts,focus='normal',page_text=page_text,page_lines=page_lines,ptr=ptr)
    
        if verbose:
            print ("[page2transactions prompt]: "+str(prompt))
            print ("(text char length: "+str(len(page_text))+")")
    
        meta['prompt']=prompt       #Store for test review
        full_prompt=prompt+page_text

        # print(("="*20+" MULTIPLE TRIES ON PAGE2T NOTE ACTIVE PROMPT: "+str(model)+" "+str(full_prompt)).encode('utf-8', errors='replace').decode())
        if THREAD_QUIET:
            logging.info("[ skip logging full_prompt -- threaded encoding??]")
        else:

            try:
                ## May still throw error because logging throwing to file?
                temp=page_text.encode('utf-8', errors='replace').decode('utf-8')
                logging.info("[d3]  full_prompt: "+temp)
            except Exception as e:
                print(f"Logging failed with exception: {e}")
    

        #######################################
        # CONDITIONAL BRANCHE OPTIONS
        #  *part of auto audit design
        #  (dynamic configuration based on page stats and other factors)
        #######################################
        #[A]  -> direct to gpt-4 if complex page
        if page_stats['is_complex_page'] or formal_meta.get('is_complex_page',False):
            model='gpt-4'
            logging.info("[choose gpt-4 because complex page]")
        else:
            model='default'
            
        #[B]  -> If summary section use gpt-4 since issues with 3.5 thinking its' a transaction
        #> direct logic fine but for demo I want auto audit
        if model=='default':
            scopes=['odd_content_not_3.5']
            state={'content':page_text}
            Auditor=AutoAuditor()
            incidents,report=Auditor.run_audit_pipeline(scopes=scopes,schema={},state=state)
            for incident in incidents:
                if incident.scope=='odd_content_not_3.5':
                    model='gpt-4'
                    logging.info("[choose gpt-4 because odd_content_not_3.5]")
            if incidents:
                Auditor.log_audit_results(scopes=scopes,state=state,results='pre-config set gpt-4 as model')

        #######################################
            
        try_cache=True
        got_all_transactions=False
        count_tries=0
    
        found_log=[]
        while not got_all_transactions:
    
            count_tries+=1
            if count_tries>3:
                logging.info("[warning] too many tries on page2transactions (could not find transactions): "+str(count_tries)+" active model: "+str(model))
                #raise Exception("warning] too many tries on page2transactions: "+str(count_tries)+" active model: "+str(model))
                break
            
    
            ### EXECUTE LLM PROMPT FOR TRANSACTION EXTRACTION
            
            logging.info("[page2t] trying model: "+str(model)+" at attempt #"+str(count_tries)+" (try_cache: "+str(try_cache)+")")
    
            if model=='default':
                transactions=LLM.prompt(full_prompt,json_validate=True,try_cache=try_cache)
#                try: print ("[RAW TRANS response]: "+str(transactions))  #Debug
#                except: pass
    
            else:
                if not model=='gpt-4': raise Exception("[error] invalid model: "+str(model))
    
                ## Larger model if issues or ie/ >30 transactions
                prompt,formal_meta=formal_prompt_prep(all_prompts=all_prompts,focus='gpt-4',page_text=page_text,page_lines=page_lines,ptr=ptr)

                full_prompt=prompt+page_text
                LLMSMARTEST=LazyLoadLLM.get_instance(model_name=SMARTEST_MODEL_NAME) #OPTIONALLY BOOST TO GPT4 IF PROBLEMS
    
                transactions=LLMSMARTEST.prompt(full_prompt,json_validate=True,try_cache=try_cache)
    
            if count_tries>1:
                if THREAD_QUIET:
                    logging.info(("="*20+" MULTIPLE TRIES ON PAGE2T NOTE ACTIVE PROMPT: "+str(model)))
                else:
                    #** throws encoding
                    try: logging.info(("="*20+" MULTIPLE TRIES ON PAGE2T NOTE ACTIVE PROMPT: "+str(model)+" "+str(full_prompt)).encode('utf-8', errors='replace').decode())
                    except:pass
                

            ## AUTO ADJUST RESPONSE:
            #** ideally elsewhere
            #[logic 1] if [ ] list of dicts then assume forgot all_transactions
            if isinstance(transactions,list):
                if len(transactions)>1:
                    transactions={'all_transactions':transactions}
    
            ### VALIDATE
            ## IF NOT DICTIONARY
            if not isinstance(transactions,dict):
                
                if count_tries==1:  ## First time
                    ## Case ends ... (not closed)
                    #i)  Specifically ask for no ... and proper json reiterate
                    if re.search(r'\.\.\.',str(transactions)) or re.search(r'\d$',str(transactions)):
                        prompt,meta=formal_prompt_prep(all_prompts=all_prompts,focus='dotdotdot',page_text=page_text,page_lines=page_lines,ptr=ptr)

                        full_prompt=prompt+page_text
                    else:
                        model='gpt-4' #<--- swaps prompt above
                        logging.info("[page2t] retrying (because no dict response) (next with gpt-4 model) at attempt #"+str(count_tries))
    
                elif count_tries==2 and model=='default':  ## Second time if still on std model
                    model='gpt-4' #<--- swaps prompt above
                    try_cache=False
                    logging.info("[page2t] retrying (because no dict response) with gpt-4 model at attempt #"+str(count_tries))
    
                else:
                    logging.warning("[error] invalid transactions (multiple tries ("+str(count_tries)+"),  still no dict): "+str(transactions))
    
            ## OK DICTIONARY !
            else:
                found_log+=[len(transactions.get('all_transactions',[]))]
                
                ### THESE EXCEPTIONS cover output realized during dev
    
                ## [A]  LOGIC:  >30 transactions requires gpt-4 model or equivalent
                #** default llm assume 3.5 which is limited >30 so auto swap to gpt-4 and retry
                if len(transactions.get('all_transactions',[]))>30 and model=='default':
                    model='gpt-4' #<--- swaps prompt above
                    logging.info("[page2t] (more then 30 transactions) retrying with gpt-4 model at attemp #"+str(count_tries))
                    looks_valid=False
    
                ## [B]  LOGIC:  subsequent 3.5 retries transactions drop from >30 or bad to 5
                #- ie/ if it can't find <10 trans on first try then why on second so ask for retry
                elif page_stats['is_complex_page'] and count_tries>1 and model=='default' and len(transactions.get('all_transactions',[]))<10:
                    model='gpt-4'
                    model='gpt-4' #<--- swaps prompt above
                    logging.info("[page2t] (complex page and haven't tried gpt-4) retrying with gpt-4 model at attemp #"+str(count_tries)+" because few transactions found")
                    looks_valid=False
    
                else:
        
                    stats,looks_valid=validate_transactions(transactions,doc_dict=doc_dict)
                    
                    if looks_valid:
                       got_all_transactions=True
                    else:
                        logging.info("[warning] final transaction check says it looks bad...")
                        
            ## CATCH ALL LOGIC
            if isinstance(transactions,dict):
                logging.info("[intermediary found count]: "+str(len(transactions.get('all_transactions',[]))))
            
            #################################
            ## EXTENDED LOGIC FOR CONTINUING
            ##[A] If complex and not got all or tried gpt-4 then do that
            if page_stats['is_complex_page'] and count_tries>2 and not got_all_transactions and model=='default':
                model='gpt-4' #<--- swaps prompt above
                try_cache=False
                logging.info("[page2t] retrying catchall (because no dict response) with gpt-4 model at attempt #"+str(count_tries))
                
            ##[B] If estimated page transactions>found then try gpt-4
            #- ie/ chase single transaction missed (ie/ single transaction in own section)
            if isinstance(transactions,dict) and page_stats['estimated_transactions']>len(transactions.get('all_transactions',[])) and model=='default':
                logging.info("[WARNING] transactions found: "+str(len(transactions.get('all_transactions',[])))+" but estimated: "+str(page_stats['estimated_transactions'])+" so retrying with gpt-4 model at attempt #"+str(count_tries))
                got_all_transactions=False
                model='gpt-4' #<--- swaps prompt above
                try_cache=False
                
            ##[C] If tries =2 and not got transactions swap to gpt4 model
            if count_tries==2 and not got_all_transactions and model=='default':
                model='gpt-4'
                logging.info("[BOOST TO GPT-4] onto try #3 and not all transactions")

            #### AUDIT conditional branch
            #[D]  -> Check for hallucination ie/ 123 Main St
            if model=='default':
                scopes=['hallucination_gpt3_5']
                state=transactions
                Auditor=AutoAuditor()
                incidents,report=Auditor.run_audit_pipeline(scopes=scopes,schema={},state=state)
                if incidents:
                    got_all_transactions=False
                    model='gpt-4'
                    logging.info("[choose gpt-4 because possible hallucination with default model")
                    Auditor.log_audit_results(scopes=scopes,state=state,results='use gpt-4 possible hallucination')
    
    
    
#        logging.info ("[page2t] EXTRACTED: "+str(json.dumps(transactions,indent=4)))
        if isinstance(transactions,str):
            logging.info("[warning] no transactions just a string: "+str(transactions))
    
        ## Remove commas and $ from amount
        transactions=adjust_transactions_top_level(transactions=transactions)
    
        #####################################
        ##  FILTER TRANSACTIONS
        #- ignore 'Check images', etc.
        transactions=alg_remove_filter_transactions(transactions)
        
        sub_transactions+=[transactions]
        
    ## Merge sub_transactions
    global_transactions={'all_transactions':[]}
    for transactions in sub_transactions:
        #List?
        if isinstance(transactions,list):
            for entry in transactions:
                global_transactions['all_transactions']+=[entry]
        else: #Assume dict
            for entry in transactions.get('all_transactions',[]):
                global_transactions['all_transactions']+=[entry]

    if verbose:
        print ("[llm_page2t] TRANSACTIONS FOUND ON PAGE FINAL:")
        print (str(json.dumps(transactions,indent=4)))
#
#    ## Possible invalid json
    try: print ("[found "+str(len(global_transactions['all_transactions']))+" transactions]")
    except: pass

    ## Return model version info
    meta['model_version']=LLM.get_model_version()
    meta['transaction_count']=len(global_transactions.get('all_transactions',[]))
    return global_transactions,meta

def dev_test_split():
    blob="""
    12/10    Bill Pay Cobb Emc on-Line xxxx87002 on 12-10    46.00
    12/10    Bill Pay TDS Telecom on-Line xxxxx83692 on 12-10        89.59
    12/10    Bill Pay Card Services on-Line Xxxxxxxxxxx51678 on 12-10        100.00
    """
    enum=estimate_number_of_transactions_on_page(blob)
    print ("EST: "+str(enum))

    return

if __name__=='__main__':
    branches=['dev1']
    branches=['dev_test_split']
    for b in branches:
        globals()[b]()

