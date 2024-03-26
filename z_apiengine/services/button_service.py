import os
import sys
import codecs
import json
import re
from typing import Union


LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")
sys.path.insert(0,LOCAL_PATH+"../..")

from database import SessionLocal
from database_models import Button
#from database_models import Case
#from database_models import User

from get_logger import setup_logging
logging=setup_logging()


        
#0v4# JC Jan 13, 2023  mysql timeout (possibly related to root login on workbench)
#0v3# JC Dec 22, 2023  Include Global buttons always
#0v2# JC Dec  9, 2023  New button service
#0v1# JC Nov  8, 2023  Setup


"""
    BUTTON MANAGEMENT SERVICE
"""


def button_as_dict(button):
    return {key: value for key, value in button.__dict__.items() if not key.startswith('_')}
    
def list_buttons_as_dict(case_id='',username=''):
    with SessionLocal() as db:
        buttons=[]
        
        ## USER BASED BUTTON QUERY
        if username:
            buttons = db.query(Button).filter(Button.username == username).all()
            
        ## CASE BASE BUTTON QUERY
        elif case_id:
            try:
                buttons = db.query(Button).filter(Button.case_id == case_id).all() #timeout?
            except:
                buttons = db.query(Button).filter(Button.case_id == case_id).all() #timeout?
            

        ## GLOBAL BUTTONS
            buttons+= db.query(Button).filter(Button.scope == 'global').all()
            
        if not buttons:
            ## Return all even though ...
            buttons = db.query(Button).all()

        list_of_buttons=[]
        list_of_buttons=[button_as_dict(button) for button in buttons]
        ## Filter fields to front-end? -- do in view
        return list_of_buttons

def create_button(scope='user',case_id='',label='', query='', username='', action='', visible=True, category='', bmeta={}):

    new_button = Button(case_id=case_id,query=query,username=username, label=label, action=action, visible=visible, category=category, bmeta=bmeta,scope=scope)
    with SessionLocal() as db:
        db.add(new_button)
        db.commit() #<-- mysql has gone away? Dec 22
        return new_button.id


def update_button(button_id=None,scope='user',case_id='',label='', query='', username='', action='', visible=True, category='', bmeta={}):

    with SessionLocal() as db:

        button = db.query(Button).filter(Button.id == button_id).first()
        if button:
            button.scope=scope

            button.case_id=case_id
            button.username=user_id
            button.query=query
            button.username=username
            button.label=label
            button.action=action
            button.visible=visible
            button.category=category
            button.bmeta=bmeta

            db.commit()
            db.refresh(button)
            return button_id
        else:
            return None

# Read Function
def get_button(button_id):
    with SessionLocal() as db:
        return db.query(Button).filter(Button.id == button_id).first()

# Read Function
def get_button_as_dict(button_id):
    with SessionLocal() as db:
        button_instance=db.query(Button).filter(Button.id == button_id).first()
        button_dict=button_as_dict(button_instance)
        return button_dict


# Delete Function
def delete_button(button_id):
    with SessionLocal() as db:
        button = db.query(Button).filter(Button.id == button_id).first()
        if button:
            db.delete(button)
            db.commit()
            return True
        else:
            return False


def dev1():
    user_id='6571b86a88061612aa2fc8b7'
    case_id='65858e0c198ceb69d5058fc3'
    buttons=list_buttons_as_dict(case_id=case_id)
    for button in buttons:
        print ("> "+str(button))

    return

if __name__=='__main__':
    branches=['dev1']
    for b in branches:
        globals()[b]()




