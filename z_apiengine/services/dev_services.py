import os
import sys
import codecs
import json
import re


LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")
sys.path.insert(0,LOCAL_PATH+"../..")

from database import SessionLocal
from database_models import User, Case, Button, Session

from get_logger import setup_logging
logging=setup_logging()


        
#0v1# JC Nov  8, 2023  Setup


"""
    DEV VARIOUS SERVICES
"""

def dev1():
    global session
    
    # now you can query 


    # user
    # case
    # session
    # button
    
    b=[]
    b+=['users_list']
    b+=['cases_list']
    b+=['sessions_list']
    b+=['buttons_list']

    if 'users_list' in b:
        users = session.query(User).all()
        print(str(users))
    if 'cases_list' in b:
        records= session.query(Case).all()
        print(str(records))
    if 'users_list' in b:
        records = session.query(Button).all()
        print(str(records))

    return


def create_update_case(case_id=''):
    #[ ] consider wrapping in ClassManager

    case=None
    if case_id:
        with SessionLocal() as session:
            case = session.query(Case).filter_by(case_id=case_id).first()
            if case:
                pass
          #    user.name = name 
          #    user.email = email
            else:
                case = Case(case_id=case_id)
                session.add(case)
                session.commit()
                session.refresh(case)
    return case

def create_update_user(username=''):
    #[ ] consider wrapping in ClassManager
    with SessionLocal() as session:
        user = session.query(User).filter_by(username=username).first()
        if user:
            pass
      #    user.name = name 
      #    user.email = email
        else:
            user = User(username=username)
            session.add(user)
            session.commit()
            session.refresh(user)

    return user


def dev_create_test_objects():

    b=[]
    b+=['user']
    b=[]
    b+=['case']
    b=[]
    b+=['button']

    if 'user' in b:
        username='test_user_1'
        user = create_update_user(username=username)

    if 'case' in b:
        case_id='chase_4_a'
        user = create_update_case(case_id=case_id)

    if 'button' in b:
        username='test_user_1'
        button_label='test_button_1'
        user = create_update_button(username, button_label)


    return



if __name__=='__main__':
    branches=['dev_create_test_objects']
    branches=['dev1']

    for b in branches:
        globals()[b]()

