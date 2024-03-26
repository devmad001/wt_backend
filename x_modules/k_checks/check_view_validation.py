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
from sqlalchemy.orm import load_only

from check_matcher_support import query_get_case_transactions
from check_matcher_support import clean_to_check_id
from check_matcher_support import logic_if_transaction_looks_like_a_check

from get_logger import setup_logging
logging=setup_logging()



#0v2# JC  Feb 16, 2024  Slow if image bytes over network so don't include with check
#0v1# JC  Feb  3, 2024  Init


"""
    /media/check_images/check_identifier @media_router.py -> check_service.py -> here

    VALIDATE THAT CHECK IMAGE + META CAN BE SERVED
    - light-functional test
    [ ] also extend to test
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



def interface_load_all_checks(case_id):
    checks = []
    with SessionLocal() as db:
        check_orms = db.query(Check).options(Check.query_without_image_bytes()).filter(Check.case_id == case_id).all()
        for check in check_orms:
            checks.append(check.__dict__)
    return checks


def interface_load_case_checks(case_id, only_matches=True, no_image_bytes=True):
    ## Index by transaction_id for faster lookup
    start_time=time.time()
    assume_return_dict = True

    if not only_matches:
        raise Exception("only_matches=True is only supported for now")

    # Index checks by check.transaction_id
    checks = {}
    
    with SessionLocal() as db:
        # Define the base query
        base_query = db.query(Check).filter(Check.case_id == case_id, Check.transaction_id != '')

        if no_image_bytes:
            # Exclude 'image_bytes' from the query if requested
            columns_to_exclude = ['image_bytes']
            columns_to_load = [getattr(Check, column.name) for column in Check.__table__.columns if column.name not in columns_to_exclude]
            checks_orm = base_query.options(load_only(*columns_to_load)).all()
            #  checks = db.query(Check).options(Check.query_without_image_bytes()).filter(Check.case_id == case_id).all()
        else:
            # Include all columns in the query
            checks_orm = base_query.all()

        # Convert ORM objects to dictionaries if needed
        if assume_return_dict:
            for check_orm in checks_orm:
                check_dict = check_orm.__dict__
                check_dict.pop('_sa_instance_state', None)
                if no_image_bytes:
                    check_dict.pop('image_bytes', None)  # Ensure 'image_bytes' is excluded
                checks[check_orm.transaction_id] = check_dict
        else:
            for check_orm in checks_orm:
                checks[check_orm.transaction_id] = check_orm

    logging.info("[debug] loaded checks for case_id: "+str(case_id)+" in "+str(time.time()-start_time)+" seconds")
    return checks


def interface_serve_check_image(check_identifier):
    # pointer depends on whats' served to front-end as id of check

    #. use check_identifier (index there?)
    check_orm=None
    check_image_bytes=None
    check_image_filename=None
    meta={}
    with SessionLocal() as db:
        check_orm=db.query(Check).filter(Check.check_identifier==check_identifier).first()
        
    if check_orm:
        check_image_bytes=check_orm.image_bytes
        check_image_filename=check_orm.check_image_filename
        # Meta is dict of object without image_bytes
        meta=check_orm.__dict__
        meta.pop('image_bytes',None)
        meta.pop('_sa_instance_state',None) #?

    return check_image_bytes,check_image_filename,meta

def dev2(case_id):
    checks=interface_load_case_checks(case_id)
    print ("[debug] checks ouf of db: "+str(len(checks)))
    for check in checks:
        print ("[debug] check: "+str(check))
        check_image_bytes,check_image_filename,meta=interface_serve_check_image(check.check_identifier)

    return


def dev1():
    
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

    cases=['case_December 2021 Skyview Capital Bank Statement']  #1 check
    
    for case_id in cases:
        logging.info ("RESOLVING CHECKS FOR: "+case_id)
        dev2(case_id)

        break

    return


if __name__ == "__main__":
    dev1()




"""

"""
