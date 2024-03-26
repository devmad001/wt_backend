import os
import sys
import codecs
import json
import re
import requests
from configparser import ConfigParser

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")
sys.path.insert(0,LOCAL_PATH+"../../")

from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, JSON
from datetime import datetime

from w_utils import am_i_on_server

from database_models import Button
from database import SessionLocal
from database import Base,engine


#0v1# JC Dec  9, 2023  Setup

"""
    BUTTONS  (mostly dev not test)
    -  update fields, migrate mysql strictly to sqlalchemy model
    -  service_buttons?
"""

def button_as_dict(button):
    return {key: value for key, value in button.__dict__.items() if not key.startswith('_')}

def list_buttons_as_dict():
    with SessionLocal() as db:
        buttons = db.query(Button).all()
        return [button_as_dict(button) for button in buttons]


#*************** moved to button_service.py

# Create Function

def create_button(scope='user',user_id=None, label='', action='', visible=True, category=None, bmeta=None, query=''):
    new_button = Button(scope=scope,user_id=user_id, label=label, action=action, visible=visible, category=category, bmeta=bmeta, query=query)
    with SessionLocal() as db:
        db.add(new_button)
        db.commit()
        return new_button.id

# Read Function
def get_button(button_id):
    with SessionLocal() as db:
        return db.query(Button).filter(Button.id == button_id).first()

# Update Function
def update_button(button_id, **kwargs):
    with SessionLocal() as db:
        print ("AT SESSION...")
        button = db.query(Button).filter(Button.id == button_id).first()
        if button:
            for key, value in kwargs.items():
                setattr(button, key, value)
            db.commit()
            return button_id
        else:
            return None

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


def dev_buttons():
    a=okk
     
    ########## ADMIN recreate table new fields (no data so ok)
    if True:
        watchh=dropp
        # Drop the table
        Button.__table__.drop(engine)
    
        # Recreate the table
        Base.metadata.create_all(engine)

    
    # Sample Usage
    #Base.metadata.create_all(engine)  # Create tables
    
    # Create a button
    button_id = create_button(user_id=1, label="Test Button", action="http://example.com")
    
    # Update the button
    updated_button_id = update_button(button_id, label="Updated Test Button")

    # Read the button
    read_button = get_button(updated_button_id)
    
    # Delete the button
    delete_button(updated_button_id)
    
    read_button = get_button(updated_button_id)
    print ("Deleted button is: "+str(read_button))


    return


def dev_list_delete_all_buttons():
    for button in list_buttons_as_dict():
        print ("BUT: "+str(button))
#        hhard=checkdelbutt
        delete_button(button['id'])

    return

def dev_list_all_buttons():
    for button in list_buttons_as_dict():
        print ("BUT: "+str(button))
    return


def ADMIN_drop_entire_button_table():
    harddd=schekk
    # Drop the table
    Button.__table__.drop(engine)

    # Recreate the table
    Base.metadata.create_all(engine)
    return

def dev_create_sample_buttons():
    b=[]
    b+=['first_some']
    a=kkk
    
    if 'first_some' in b:
#        bb['scope']='global'
#        bb['label']='Global Button 1'
#        bb['action']='expect_ws_response_loading_spinner_required'
#        bb['query']='Show me all transactions >$1000'
#        create_button(**bb)
    
        bb={}
        bb['scope']='global'
        bb['label']='Download Excel'
        bb['action']='expect_ws_response_loading_spinner_required'
        create_button(**bb)

        bb={}
        bb['scope']='global'
        bb['label']='Accounts Chart'
        bb['action']='expect_ws_response_loading_spinner_required'
        create_button(**bb)

        bb={}
        bb['scope']='global'
        bb['label']='Balance Chart'
        bb['action']='expect_ws_response_loading_spinner_required'
        create_button(**bb)

        bb['scope']='global'
        bb['label']='Transactions > $10k'
        bb['action']='expect_ws_response_loading_spinner_required'
        bb['query']='Show me all transactions >$10000'
        create_button(**bb)
    
        print ("created 2? sample global buttons")

    return


def dev2():
    for button in list_buttons_as_dict():
        print ("BUT: "+str(button))
#        hhard=checkdelbutt
#        delete_button(button['id'])

    a=kkk
    return


def dev_create_realish_global_buttons():
    dev_list_all_buttons()

    if False:
        bb={}
        bb['scope']='global'
        bb['label']='Accounts Chart'
        bb['action']='expect_ws_response_loading_spinner_required'
        create_button(**bb)

        bb={}
        bb['scope']='global'
        bb['label']='Balance Chart'
        bb['action']='expect_ws_response_loading_spinner_required'
        create_button(**bb)

    return



def ADMIN_remove_a_global_button():
    

    for button in list_buttons_as_dict():
        print ("BUT: "+str(button))
        if button['scope']=='global':
            if button['label']=='Transactions > $10k':
                print ("DELETE BUTTON: "+str(button))
                delete_button(button['id'])

#        hhard=checkdelbutt
#        delete_button(button['id'])

    return



if __name__=='__main__':
    branches=['dev_buttons']
    branches=['dev_list_delete_all_buttons']
    branches+=['dev2']

    branches=['ADMIN_drop_entire_button_table']
    branches+=['dev_create_sample_buttons']

    branches=['ADMIN_drop_entire_button_table']
    branches=['dev_list_all_buttons']
    branches=['dev_create_sample_buttons']
    branches=['dev_create_realish_global_buttons']

    branches=['dev_create_sample_buttons']
    branches=['dev_list_all_buttons']
    branches=['ADMIN_remove_a_global_button']


    for b in branches:
        globals()[b]()


"""

"""
