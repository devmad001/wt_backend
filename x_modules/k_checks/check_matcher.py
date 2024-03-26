import os,sys
import re
import json
import time
import copy
import codecs

import requests

from pathlib import Path
import shutil

import numpy as np

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../../")

from z_apiengine.database import SessionLocal
from z_apiengine.database_models import Check

from check_matcher_support import query_get_case_transactions
from check_matcher_support import clean_to_check_id
from check_matcher_support import logic_if_transaction_looks_like_a_check

from get_logger import setup_logging
logging=setup_logging()



#0v1# JC  Feb  1, 2024  Init


"""
    CHECK MATCHER
    - review checks in db
    - dump for match to transaction
    - ?serve image for front-end
    - org was check_management on wt_hub

    DEMO CHECK MATCHER
    - docs tbd
    - data files built with k_checks @wt_hub

    HOW CHECKS GET HERE?
    - /wt_hub/k_checks
    - run_check_pipline.py -> load_checks_into_db.py (via API post)
"""

"""
    OVERVIEW
    --------

    ENTRYPOINT:  check_matcher_pipeline(case_id)
    - fetches check image and check meta (previously extracted) from Checks table
    - fetches transactions for case_id
    - matches check image to transaction
    - updates Check.transaction_id field in db

"""


def dev_iter_checks_in_db():
    #^recall, see above for path
    
    all_ids={}
    with SessionLocal() as db:
        checks=db.query(Check).all()
        for check in checks:
            all_ids[check.check_id]=True
#            print ("[debug] check: "+str(check))

    loggin.info("[raw] all check ids: "+str(all_ids))
    return


def dev_admin_remove_check_records():
    add=admin_only
    logging.info ("ORG 65a* has bad id")
    # where Check.case_id=' case_id='65a8168eb3ac164610ea5bc2' 
    count=0
    with SessionLocal() as db:
        checks=db.query(Check).filter(Check.case_id=='65a8168eb3ac164610ea5bc2').all()
        for check in checks:
            count+=1
            logging.info ("[debug] check: "+str(check))
            db.delete(check)
        db.commit()
    logging.info ("[debug] count: "+str(count))

    return

def local_clean_check_amount(amount):
    # Assume str
    amount=str(amount)
    if amount[-2:]==".0":
        amount+="0"
    # Remove $ and ,
    amount=re.sub(r'[$,]','',amount)
    return amount

def check_matcher_pipeline(case_id,verbose=False,commit=True):
    
    logging.info ("[debug] check matcher for case: "+case_id)

    
    ## Get known check image meta

    ## Create easy index
    checks={}
    checks_meta={}
    logging.info("[debug] query for checks (large load with image bytes in table) case: "+str(case_id))
    with SessionLocal() as db:
        check_orms=db.query(Check).filter(Check.case_id==case_id)
        for check_orm in check_orms:
            ## Upfront clean? [ ] 
            ## Create easy index
            checks[check_orm.check_id]=check_orm  #ie/ don't modify unless planning to save
            checks_meta[check_orm.check_id]=json.loads(check_orm.meta)

    logging.info ("[debug] loaded check image meta count: "+str(len(checks)))

    if verbose:
        logging.info ("[image check ids]: "+str(checks.keys()))


    ## Get transactions
    trs=query_get_case_transactions(case_id=case_id)
    logging.info ("[debug] loaded Transactions count: "+str(len(trs)))
    
    ## Clean
    
    matched_transaction_id={}
    transaction_clean_ids=[]
    count_matching_amounts={}  #Match on amount if the only amount that matches
    check_image_amounts=[]
    
    ## Stats
    counts={}
    counts['via_id_match']=0
    counts['via_amounts_match']=0
    counts['via_description_match']=0
    for tr in trs:
        is_match=False
        
        ## Prepare what transaction check_id might look like
        tr_check_id=clean_to_check_id(description=tr['transaction_description'])
        if tr_check_id:
            transaction_clean_ids+=[tr_check_id]
        
        ## Count as easy way to look for matches
        tr_amount_str=local_clean_check_amount(tr['transaction_amount'])
        
        #If ends in .0$ add a zero
        if tr_amount_str[-2:]==".0": tr_amount_str+="0"
        try: count_matching_amounts[tr_amount_str]+=1
        except: count_matching_amounts[tr_amount_str]=1
        

        ############################################
        #  MATCH LOGIC  check_image <> transaction
        ############################################
        #
        #MISC:
        #i) check match for leichtenstein distance?

        ## FILTER 1
        if logic_if_transaction_looks_like_a_check(tr):

            ## MATCH LOGIC A
            ## Match if check_ids match  (check_image check id == transaction clean tr_check_id)
            if tr_check_id in checks:
                logging.info ("[debug] match: "+str(tr['transaction_description']))
                is_match=True
                matched_transaction_id[tr_check_id]=tr['id']
                counts['via_id_match']+=1
        ## Match A(ii)
        #** check_id is a possible key in transaction
        if tr.get('check_id','') in checks:
            logging.info ("[debug] match: "+str(tr['transaction_description']))
            is_match=True
            matched_transaction_id[tr['check_id']]=tr['id']
            counts['via_id_match']+=1

    logging.info ("[debug] matching amounts via check id: "+str(count_matching_amounts))
                
    ## MATCH LOGIC B:  single instance amounts match
    for check_id in checks:
        if check_id in matched_transaction_id: continue

        check_amount=local_clean_check_amount(checks_meta[check_id].get('check-amount',''))
        if check_amount:
            check_image_amounts+=[check_amount]
        if check_amount in count_matching_amounts:
            if count_matching_amounts[check_amount]==1:
                logging.info ("[debug] match to check_image <> transaction based on single amount: "+str(check_amount))
                matched_transaction_id[check_id]=tr['id']
                counts['via_amounts_match']+=1
                
    ## MATCH LOGIC C:
    #- if full check image id appears in description ie/  \bcheck_id\b
    for check_id in checks:
        if check_id in matched_transaction_id: continue
        ## More fuzzy but not real-time
        for tr in trs:
            try:
                temp=re.search(r'\b'+check_id+r'\b',tr['transaction_description']) #Nothing to repeat?
            except: continue  #[ ] debug
            if re.search(r'\b'+check_id+r'\b',tr['transaction_description']): #Possible non
                logging.info ("[debug] match to check_image <> transaction based on check_id in description: "+str(check_id))
                matched_transaction_id[check_id]=tr['id']
                counts['via_description_match']+=1
                break

    logging.info ("[debug] check image amounts: "+str(check_image_amounts))
    logging.info ("[debug] check image clean ids: "+str(checks.keys()))
#    logging.info ("[debug] transaction clean ids: "+str(transaction_clean_ids))

    logging.info ("[summary]  Potential chech image counts: "+str(len(checks)))
    logging.info ("[summary]  Got match count: "+str(len(matched_transaction_id)))
    logging.info ("[stats]  counts: "+str(counts))


    #############################
    ## Update db
    #* watch because orm class is carried through
    
    for check_image_id in checks:
        check_orm=checks[check_image_id]
        ## Update db field set transaction_id field to new value. Others the same
        if check_image_id in matched_transaction_id:
            check_orm.transaction_id=matched_transaction_id[check_image_id]
            if commit:
                with SessionLocal() as db:
                    db.add(check_orm)
                    db.commit()
                    logging.info ("[debug] updated check with transaction id match: "+str(check_orm.check_id))


    #### Assumptions
    logging.info ("Assume only look at potential transaction checks if section like 'check' (igonre description for now)")
    logging.info ("Assume match if check_ids found AND match (ignore amount, filename of case, etc. etc.)")
    
    meta={}
    meta['total_match_count']=len(matched_transaction_id)
    return meta


def dev_call_check_matcher_pipeline():
    cases=[]

    case_id='65a8168eb3ac164610ea5bc2'
    
    cases+=[case_id]
    case_id='case_December 2021 Skyview Capital Bank Statement'  #~1 (other is too hard to see?)
    cases+=[case_id]
    case_id='65a8168eb3ac164610ea5bc2' #[x] ~23
    cases+=[case_id]

    cases=['case_December 2021 Skyview Capital Bank Statement']

    cases=[]
    case_id='case_schoolkids'
    cases+=[case_id]

    cases=[]
    case_id='65caaffb9b6ff316a779f525'
    cases+=[case_id]

    
    for case_id in cases:
        logging.info ("RESOLVING CHECKS FOR: "+case_id)
        check_matcher_pipeline(case_id,verbose=True,commit=True)

    return


def dev_report_on_checks():
    case_id='65caaffb9b6ff316a779f525'

    print ("DEV CHECKS REPORT")
    
    print ("[info] querying for checks...")
    with SessionLocal() as db:
        start_time=time.time()
        checks = db.query(Check).options(Check.query_without_image_bytes()).filter(Check.case_id == case_id).all()

        print ("[info] query time: "+str(time.time()-start_time))
        for check in checks:
            pass
#            print ("[debug] check: "+str(check))

    print ("Done checks")
    
    return



if __name__ == "__main__":
#    dev_iter_checks_in_db()
#    dev_admin_remove_check_records()
#    dev_call_check_matcher_pipeline()
    dev_report_on_checks()




"""

"""
