import os
import sys
import codecs
import json
import re

from sqlalchemy.orm import Session


LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")
sys.path.insert(0,LOCAL_PATH+"../..")

from database_models import Faq
from database import SessionLocal


from get_logger import setup_logging
logging=setup_logging()


        
#0v1# JC Nov  8, 2023  Setup


"""
    FAQ MANAGEMENT SERVICE
"""


def list_user_faqs(username: str):
    with SessionLocal() as db:
        user = db.query(User).filter_by(username=username).first()
        if user:
            user_faqs = db.query(Faw).filter_by(user_id=user.id).all()
            return user_faqs
        return []  # Return an empty list if the user is not found


if __name__=='__main__':
    branches=['dev1']
    for b in branches:
        globals()[b]()

