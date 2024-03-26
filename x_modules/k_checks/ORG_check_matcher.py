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


CHECK_MEDIA_STORAGE_DIR=LOCAL_PATH+"CHECK_MEDIA_STORAGE"

#0v1# JC  Jan 27, 2024  Init


"""
    DEMO CHECK MATCHER
    - docs tbd
    - data files built with k_checks @wt_hub

"""

def load_checks_meta(case_id):
    force_checks_meta_filename=LOCAL_PATH+"manual_match_checks_newage.json"
    fp=codecs.open(force_checks_meta_filename,"r","utf-8")
    checks_meta=json.loads(fp.read())
    fp.close()
    return checks_meta



def load_validated_checks(case_id):
    if not case_id=='65a8168eb3ac164610ea5bc2': return {}

    checks_meta=load_checks_meta(case_id)
    validated={}
    
    c=0
    for transaction_id in checks_meta:
#        print ("[debug] transaction_id: "+str(transaction_id))
#        print ("[debug] check_meta: "+str(checks_meta[transaction_id])) 
        pdf_filename=CHECK_MEDIA_STORAGE_DIR+"/"+checks_meta[transaction_id]['check_image_filename']
        if not os.path.isfile(pdf_filename):
            print ("[error] missing file: "+str(pdf_filename))
            continue
        checks_meta[transaction_id]['check_image_filename']=pdf_filename #** RELATIVE 
        
        ## MAP TO SLIM VERSION
        # real image filename
        # check raw extracted meta
        
#D#        print ("AT: "+str(checks_meta[transaction_id]))
        dd={}
        dd['check_image_filename']=checks_meta[transaction_id]['check_image_filename']
        dd['check_meta']=checks_meta[transaction_id]['check_meta']
        validated[transaction_id]=dd


#    print ("FO: "+str(checks_meta))
    print ("[debug] loaded validated checks match count: "+str(len(validated)))

    return validated


def dev1():

    case_id='65a8168eb3ac164610ea5bc2'# force_checks_meta_filename=LOCAL_PATH+"manual_match_checks_newage.json"
    validate=load_validated_checks(case_id)
    return



def dev_integrate_check_meta_into_system():
    
    #[1] just include check picture
    #  [ ] do to get format of data response

    #[2] include pay-to-order info into raw graph transaction nodes
    #  [ ] start as manual, then integrate into pipeline later


    return



if __name__ == "__main__":

    dev1()



"""

            records[transaction_id]={}
            records[transaction_id]['check_meta']=checks[hardcoded_match_index]
            records[transaction_id]['transaction_record']=cts[transaction_id]

            ## Redundant obvious fields
            relfname=checks[hardcoded_match_index]['check_image_filename']
            relfname=re.sub(r'.*'+case_id,case_id,relfname)
            records[transaction_id]['check_image_filename']=relfname
            print ("[debug] check_image_filename: "+str(records[transaction_id]['check_image_filename']))

"""
