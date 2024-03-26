import os
import sys
import codecs
import json
import re
import datetime
import uuid

from urllib.parse import quote
from fastapi import FastAPI

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")

sys.path.insert(0,LOCAL_PATH+"../../")


from get_logger import setup_logging
logging=setup_logging()

from w_utils import get_base_endpoint
from x_modules.k_checks.check_view_validation import interface_serve_check_image
from x_modules.k_checks.check_view_validation import interface_load_case_checks
        

#0v1# JC Feb  3, 2023  Setup


"""
    CHECK SERVICE INTERFACE
"""

BASE_SERVER_ENDPOINT=get_base_endpoint()


def get_check_image_meta_image(check_identifier):
    check_image_bytes,check_image_filename,meta=interface_serve_check_image(check_identifier)
    return check_image_bytes,check_image_filename,meta
    

def dev_check_checks():

    """ SAMPLE:  'check_identifier': 'December 2021 Skyview Capital Bank Statement.pdf_5092_11_0_0', 'case_id': 'case_December 2021 Skyview Capital Bank Statement', 'check_id': '5092'
    """
    

    case_id='case_December 2021 Skyview Capital Bank Statement'
    print ("Sample checks review for case_id:",case_id)
    checks=interface_load_case_checks(case_id)  #Indexed by transaction_id
    
    stopp=new_idex
    for check in checks:
        check_identifier=check.check_identifier
        check_image_bytes,check_image_filename,meta=get_check_image_meta_image(check_identifier)
        print('check_identifier:',check_identifier)
        print('check_image_filename:',check_image_filename)
        print('meta:',meta)
        break
    
    return

def generate_check_image_url(case_id,check_identifier_safe):
    global BASE_SERVER_ENDPOINT
    #[ ] moved into database_models for now
    #[ ] ideally registered with router but hard code for now
    url=BASE_SERVER_ENDPOINT+'/api/v1/case/'+case_id+'/media/check_images/'+check_identifier_safe
    return url


def DEMO_merge_check_data(case_id,validated,records,verbose=False):
    # validated=interface_load_case_checks(case_id) #; indexed by transaction_id

    status_check_identifiers={}  #Track status of check_identifiers True==matched
    
    if verbose:
        print ("[debug] VALIDATED match count: "+str(len(validated)))
#        print ("RECORDS: "+str(records))

    merge_count=0
    new_records=[]
    for record in records:

        transaction_id=record.get('id',record.get('transaction_id',''))
        if transaction_id in validated:  #Pre-matched good

            ## Below is for check matches
        
            merge_count+=1

            record['check_info']=validated[transaction_id]

            ## FINAL MAPPING
            #[ ] hard code assume #[ ] relative to base domain

            check_identifier=validated[transaction_id]['check_identifier'] #dict not orm
            status_check_identifiers[check_identifier]=True

            # urlencode
            check_identifier_safe=quote(check_identifier)

            record['check_url']=generate_check_image_url(case_id,check_identifier_safe)

            ## Echo first match
            if merge_count==1:
                print ("[sample]  MATCHED CHECK: "+str(validated[transaction_id]))
                print ("[sample url] "+str(record['check_url']))

            
            new_records.append(record)

        else:
            new_records.append(record)
            
    return new_records,status_check_identifiers



if __name__=='__main__':
    branches=['dev_check_checks']
    for b in branches:
        globals()[b]()


"""
"""










