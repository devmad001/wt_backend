import os
import sys
import codecs
import json
import re

from fastapi import FastAPI

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")

sys.path.insert(0,LOCAL_PATH+"../..")


from w_chatbot.wt_brains import Bot_Interface
from database import SessionLocal

from get_logger import setup_logging
logging=setup_logging()


        
#0v1# JC Nov  5, 2023  Setup


"""
    CASE FILES
    - store into local file system, sqlite or db?
    - for now, do via file system

"""

def create_set_file(user_id: int, case_id: str, filename: str, file_meta: dict, file_url: str = None, is_stored: bool = False, db: Session = None):
    #: file_meta is updated (not overwritten)
    # Check if file already exists
    with SessionLocal() as db:
        existing_file = db.query(File).filter_by(user_id=user_id, case_id=case_id, filename=filename).first()

        if existing_file:
            # Update the existing file's meta data
            existing_file.file_meta.update(file_meta)
            if file_url is not None:  # Update the file URL if provided
                existing_file.file_url = file_url
            existing_file.is_stored = is_stored  # Update the stored status
            db.commit()
            db.refresh(existing_file)
            return existing_file  # Return the updated file object
        else:
            # Create a new file if it doesn't exist
            new_file = File(user_id=user_id, case_id=case_id, filename=filename, file_meta=file_meta, file_url=file_url, is_stored=is_stored)
            db.add(new_file)
            db.commit()
            db.refresh(new_file)
            return new_file  # Return the newly created file object


#def fetch_file(file_id: int, db: Session = None):
#    file=db.query(File).filter_by(id=file_id).first()
#    if file:
#        ## Fetch how?
#        pass
#    return

    
if __name__=='__main__':
    branches=['dev1']
    for b in branches:
        globals()[b]()


"""
"""