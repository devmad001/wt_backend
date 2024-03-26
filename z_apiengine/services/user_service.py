import os
import sys
import codecs
import json
import re


LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")
sys.path.insert(0,LOCAL_PATH+"../..")

from sqlalchemy.orm import Session
from database_models import User
from database import SessionLocal

from get_logger import setup_logging
logging=setup_logging()


        
#0v1# JC Nov  8, 2023  Setup


"""
    USER MANAGEMENT SERVICE
"""

def get_user(username: str):
    with SessionLocal() as db:
        user = db.query(User).filter_by(username=username).first()
    return user  # This could be a user object or None

def list_users():
    with SessionLocal() as db:
        users = db.query(User).all()  # Get all users from the database
    return users  # This could be a list of user objects

def delete_user(username: str):
    with SessionLocal() as db:
        user = db.query(User).filter_by(username=username).first()
        if user:
            db.delete(user)
            db.commit()
            return True  # User deleted successfully
        else:
            return False  # User not found

def create_set_user(username: str):
    # Check if user already exists
    with SessionLocal() as db:
        existing_user = db.query(User).filter_by(username=username).first()
        if existing_user is None:
            new_user = User(username=username)
            db.add(new_user)
            db.commit()
            return new_user  # Return the newly created user object
        else:
            return None  # User already exists


if __name__=='__main__':
    branches=['dev1']
    for b in branches:
        globals()[b]()

