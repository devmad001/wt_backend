import os
import sys
import codecs
import json
import re

from google.oauth2 import service_account
from google.cloud import storage #pip install google-cloud-storage


from fastapi import FastAPI

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")

sys.path.insert(0,LOCAL_PATH+"../..")


        
#0v1# JC Dec  6, 2023  Setup

##
# GLOBAL SETTINGS FOR staging vs production is tbd. If not found in staging, try production


IS_PRODUCTION=True

############################3
## Production config
production_config_filename='google.prod_COMMITED_TO_GIT.json'
staging_config_filename='google.staging_COMMITED_TO_GIT.json'
config_path=''

STORAGE_BASE_DIR=LOCAL_PATH+"../../../../CASE_FILES_GOOGLE_SYNC"

## VALIDATE FILES
if not os.path.exists(STORAGE_BASE_DIR):
    raise Exception(f"Storage base dir does not exist: {STORAGE_BASE_DIR}")

backup_config_dict=None
if IS_PRODUCTION:
    config_path=LOCAL_PATH+production_config_filename
    backup_config_path=LOCAL_PATH+staging_config_filename
else:
    config_path=LOCAL_PATH+staging_config_filename
    backup_config_path=LOCAL_PATH+production_config_filename

if not os.path.exists(config_path):
    raise Exception(f"Config file does not exist: {config_path}")

service_account_info=json.load(open(config_path,'r'))
backup_service_account_info=json.load(open(backup_config_path,'r'))
############################3



"""
    GOOGLE STORAGE INTERFACE
"""


def dev2():
    service_account_info=load_service_account_info()
    list_gcs_buckets(service_account_info)
    return


def download_google_storage_file(bucket_name,remote_path,local_path,storage_client=None):
    global service_account_info,backup_service_account_info
    ## Messy but allow for backup credentials (robustness)

    AUTO_TRY_BACKUP=True   #[ ] part of formalizing prod/staging
    is_downloaded=False


    if not storage_client:
        credentials = service_account.Credentials.from_service_account_info(
            service_account_info
        )
        storage_client = storage.Client(credentials=credentials)

    try:
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(remote_path)
        blob.download_to_filename(local_path)
        is_downloaded=True
    except Exception as e:
        print(f"[Default production/staging not used or error (re-trying other): {e}")

        if AUTO_TRY_BACKUP or 'it may not exist' in str(e):
            print(f"Trying backup credentials")
            credentials = service_account.Credentials.from_service_account_info(
                backup_service_account_info
            )
            storage_client = storage.Client(credentials=credentials)
            bucket = storage_client.bucket(bucket_name)
            blob = bucket.blob(remote_path)
            blob.download_to_filename(local_path)
            is_downloaded=True
        else:
            raise Exception(f"Error downloading file from google storage: {e}")

    return is_downloaded, storage_client


def sync_google_storage_files_local(case_id,google_filenames):
    #,"file_urls":["https://storage.cloud.google.com/watertower_bucket/input/20854c60-ecd4-4e7f-a611-e4b768429248.pdf"]
    storage_client=None
    syncd_files=[]
    
    for filename in google_filenames:
        if len(filename.split('/'))>3:
            bucket_name=filename.split('/')[3]
            remote_path="/".join(filename.split('/')[4:])
            remote_filename=remote_path.split('/')[-1]
            
            local_directory=f"{STORAGE_BASE_DIR}/{case_id}"
            if not os.path.exists(local_directory):
                os.makedirs(local_directory)
            local_path=f"{local_directory}/{remote_filename}"
            print(f"Downloading {filename} to {local_path}")
            
            local_file_size=os.path.getsize(local_path) if os.path.exists(local_path) else 0
            
            if local_file_size>0:
                ## Exists
                pass
            else:
                is_downloaded,storage_client=download_google_storage_file(bucket_name,remote_path,local_path,storage_client=storage_client)
            
            if not os.path.exists(local_path):
                raise Exception(f"File not downloaded: {local_path}")
    
            syncd_files.append(local_path)
        else:
            print(f"Skipping sync of google storage files: {google_filenames}")

    print(f"Syncd files: {syncd_files}")
    return syncd_files


def test_call_sync_files():
    #,"file_urls":["https://storage.cloud.google.com/watertower_bucket/input/20854c60-ecd4-4e7f-a611-e4b768429248.pdf"]
    case_id='jon_test_case_id_1'
    google_filenames=["https://storage.cloud.google.com/watertower_bucket/input/20854c60-ecd4-4e7f-a611-e4b768429248.pdf"]
    syncd_file_list=sync_google_storage_files_local(case_id,google_filenames)
    
    return

def list_gcs_buckets(service_account_info):
    credentials = service_account.Credentials.from_service_account_info(
        service_account_info
    )

    storage_client = storage.Client(credentials=credentials)

    # List all buckets
    buckets = storage_client.list_buckets()
    for bucket in buckets:
        print(bucket.name)

        # List all files in the bucket
        blobs = storage_client.list_blobs(bucket.name)
        for blob in blobs:
            if '.pdf' in blob.name:
                print(f"  File: {blob.name}")
                yield bucket.name,blob.name
    return


def debug_list_all_bucket_files():
    global service_account_info,backup_service_account_info

    print ("LIST ALL BUCKET FILES")

    for bucket_name,blob_name in list_gcs_buckets(service_account_info):
        print ("service> "+str(bucket_name)+" - "+str(blob_name))
        
    for bucket_name,blob_name in list_gcs_buckets(backup_service_account_info):
        print ("backup> "+str(bucket_name)+" - "+str(blob_name))

    return




if __name__=='__main__':

    branches=['dev1']
    branches=['dev2']
    branches=['dev_sync_files_local']
    branches=['test_call_sync_files']
    branches=['debug_list_all_bucket_files']
    
    for b in branches:
        globals()[b]()













"""


"""




