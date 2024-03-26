import os,sys
import re
import json
import time
import copy
import codecs
import datetime

import requests

from pathlib import Path
import shutil

from sqlalchemy.exc import IntegrityError

import numpy as np

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../../")

from get_logger import setup_logging
logging=setup_logging()

from z_apiengine.database import SessionLocal
from z_apiengine.database_models import Check


CHECK_MEDIA_STORAGE_DIR=LOCAL_PATH+"CHECK_MEDIA_STORAGE" # temp


#0v1# JC  Jan 30, 2024  Init


"""
    LOAD CHECKS INTO DB
    - via API post  services.service_check_images.py  <-- route_checks.py

"""


def demo_load_checks_meta(case_id):
    force_checks_meta_filename=LOCAL_PATH+"manual_match_checks_newage.json"
    fp=codecs.open(force_checks_meta_filename,"r","utf-8")
    checks_meta=json.loads(fp.read())
    fp.close()
    return checks_meta


def iter_checks_meta(case_id):
    checks_meta=demo_load_checks_meta(case_id)
    for tid in checks_meta:
        check_meta_dict=checks_meta[tid]['check_meta']
        transaction_record=checks_meta[tid]['transaction_record']
        yield tid,check_meta_dict,transaction_record
    return


def validate_check_record(record):
    ## Check image file bytes
    print ("[debug] image size: ",len(record['image_bytes']))
    if not record['image_bytes']:
        return False
    return True


def prepare_check_record(case_id,check_meta,check_image_bytes,t_record={}):
    
    ## Pop if don't want to store or will already be in core record
    POP_FIELDS_FINAL=['temp_image_filename','case_id']
    
#D1        print(check_meta)
        
    record={}

    ## Touch on key vars
    #DB will set        record['id']=''

    record['check_identifier']=check_meta.pop('id')  #check record id
    record['case_id']=case_id
    record['transaction_id']='' #t_record

    record['check_id']=check_meta.pop('check_id','')
    record['pdf_filename']=check_meta.pop('pdf_filename','')
    record['check_image_filename']=os.path.basename(check_meta.pop('check_image_filename',''))
    
    ## FK possible  (future extract NER or similar but may want in local db field)
    record['payor_name']=''
    record['payee_name']=''
    record['account_num']=''
    
    ## Image translate into record
    if not isinstance(check_image_bytes,bytes):
        raise ValueError("Image bytes not found")
    record['image_bytes']=check_image_bytes

        
    ## Filter unwanted fields
    for k in POP_FIELDS_FINAL:
        check_meta.pop(k,'')
    
    record['meta']=check_meta   #"JSON"
    
    ## record vars
    record['created']='' 
    record['state']='created'

    #print(record) #Don't print image_bytes
    
    is_valid=validate_check_record(record)

    return record,is_valid


def post_check_to_db(record):
    """
    Inserts a check record into the database within a managed session context.
    Parameters:
    - record: A dictionary containing the check record data.
    """
    is_posted=False
    is_duplicate=False

    logging.info("[info] posting check record to db...")

    # Create a new session using SessionLocal() as a context manager
    with SessionLocal() as db:
        # Create an instance of the Check model from the record dictionary

        check = Check(
            case_id=record.get('case_id', ''),
            check_identifier=record.get('check_identifier', ''),
            transaction_id=record.get('transaction_id', ''),
            check_id=record.get('check_id', ''),
            pdf_filename=record.get('pdf_filename', ''),
            check_image_filename=record.get('check_image_filename', ''),
            payor_name=record.get('payor_name', ''),
            payee_name=record.get('payee_name', ''),
            account_num=record.get('account_num', ''),
            image_bytes=record.get('image_bytes', b''),  # Assuming image bytes are properly set in the record
            meta=json.dumps(record.get('meta', {})),  # Convert the meta dictionary to a JSON string
            created=datetime.datetime.utcnow(),  # Set the creation time to now
            state=record.get('state', 'created')  # Set the initial state
        )

        # Add the new check instance to the session and commit the transaction
        db.add(check)
        try:
            db.commit()
            is_posted=True
            
        # Handle IntegrityError gently
        except IntegrityError:
            is_duplicate=True
            # An IntegrityError indicates a duplicate entry for a unique column
            db.rollback()  # Roll back the transaction
    
            # Option 1: Skip the duplicate
            print("Duplicate record found, skipping the add.")
    
            # Option 2: Update the existing record
            # existing_check = session.query(Check).filter_by(check_identifier=record['check_identifier']).one_or_none()
            # if existing_check:
            #     # Update fields of the existing_check with information from the record
            #     existing_check.case_id = record.get('case_id', '')
            #     # ... [update other fields as necessary]
            #     session.commit()

        except Exception as e:
            db.rollback()  # Roll back the transaction on error
            raise e  # Optionally, re-raise the exception or handle it as needed
        
    return is_posted,is_duplicate


def dev_post_checks_for_case():
    case_id='65a8168eb3ac164610ea5bc2'    # force_checks_meta_filename=LOCAL_PATH+"manual_match_checks_newage.json"
    prepare_check_records(case_id)
    return

def db_review_checks():
    with SessionLocal() as db:
        checks = db.query(Check).all()
        for check in checks:
            print(check)

    return

def get_next_check_meta(case_id):
    ## Simulate post
    check_meta={}
    check_image_bytes=b''

    for tid, check_meta,t_record in iter_checks_meta(case_id):
        record={}
         
        ####################
        ## pre-Validate image   (since will be coming from POST)
        fp=''
        check_image_path='' #Exists locally or passed
        record['image_bytes']=''
        image_filename=check_meta.get('temp_image_filename','')
        if os.path.exists(image_filename):
            fp=open(image_filename, "rb")
            record['image_bytes']=fp.read()
            fp.close()
        else:
            raise ValueError("Image file not found: "+image_filename)
        ####################
        
        break

    return check_meta,check_image_bytes


def interface_post_check_to_db(case_id,check_meta,check_image_bytes):
    is_posted=False
    is_valid=False
    is_duplicate=False

    record,is_valid=prepare_check_record(case_id,check_meta,check_image_bytes)

    if is_valid:
        is_posted,is_duplicate=post_check_to_db(record)
    return is_valid,is_posted, is_duplicate

def dev_test_prepare_post_workflow(case_id,commit=True):
    ## OK test entry at commit=False
    ## Get check_meta

    check_meta,check_image_bytes=get_next_check_meta(case_id)
    record,is_valid=prepare_check_record(case_id,check_meta,check_image_bytes)
    if is_valid and commit:
        post_check_to_db(record)
    return is_valid

def test_check_post_to_db():
    case_id='65a8168eb3ac164610ea5bc2'  
    dev_test_prepare_post_workflow(case_id,commit=False)
    return


if __name__ == "__main__":
#    db_review_checks()
#    dev_post_checks_for_case()
    dev_test_prepare_post_workflow()






"""

sample check meta:
{'check-name-address': 'NEW AGE VENDING LLC 380 CHAMBERS ST UNIT 412 WOODSTOCK GA 301 85-5021', 'pay-to-order': 'Jackson Bartz', 'check-amount': '251.34', 'bank-name': 'America', 'check-number': '1403', 'check-memo': '2/12/20-2/25/20', 'check-date': '2/28/2020', 'check-amount-words': 'Two Hundred Fifty one 100', 'case_id': '65a8168eb3ac164610ea5bc2', 'pdf_filename': 'NEW AGE VENDING LLC.pdf', 'temp_image_filename': 'c:\\scripts-23\\watchtower\\wt_hub\\k_checks/CHECK_MEDIA_STORAGE/65a8168eb3ac164610ea5bc2/extracted_objects_images\\NEW AGE VENDING LLC_check_53_0_0.jpg', 'check_image_filename': 'c:\\scripts-23\\watchtower\\wt_hub\\k_checks/CHECK_MEDIA_STORAGE/65a8168eb3ac164610ea5bc2/check_images_meta/NEW AGE VENDING LLC_check_53_0_0.jpg', 'check_id': '1403', 'id': 'NEW AGE VENDING LLC.pdf_1403_extracted_objects_images\\NEW AGE VENDING LLC'}


"""
