import os,sys
import time
import re
import json
import copy
import pandas as pd
import matplotlib.pyplot as plt

import configparser as ConfigParser

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../../")

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, text

from z_apiengine.database import SessionLocal


#all the tables are on your side
#https://github.com/WatchtowerGroup/wt_cognitive/blob/main/backend/application.py
#Oh good.  Was the get_faqs_from_db in the bank_azure_api?
#https://github.com/WatchtowerGroup/wt_cognitive/blob/main/backend/db_connections.py


"""
I USE:

DATABASE_URL = "mysql+mysqldb://"+config['username']+":"+config['password']+"@"+config['ip']+":3306/"+dbname
DATABASE_URL = "mysql+mysqldb://"+config['username']+":"+config['password']+"@"+config['ip']+"/"+dbname

print ("CONNECT: "+str(DATABASE_URL))

engine = create_engine(DATABASE_URL)
#- import SessionLocal and create instance when needed
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


"""

def SHANKAR_get_wt_short_cut_buttons_from_db():  
    faqs_list = ""
    try:   
        engine = wt_connect_mysql() 
        with engine.begin() as conn:
            cur_result = conn.execute(text("select shortcut_id, name, question from wtengine.short_cut_button_management order by shortcut_id")) 
            for row in cur_result: 
                 index = str(row[0])
                 name = str(row[1])
                 question = str(row[2])
                 faqs_list += index+":"+name+":"+question + "|" 
        #faqs_list = faqs_list.replace("||","")
    except Exception as e:   
         print(e) #if log_print else None  
         return str(e)
    return faqs_list



def get_wt_short_cut_buttons_from_db():
    try:
        # Create a new session
        with SessionLocal() as session:
            # Execute raw SQL query
            cur_result = session.execute(text("SELECT shortcut_id, name, question FROM wtengine.short_cut_button_management ORDER BY shortcut_id"))

            # Build a list of dictionaries
            buttons_list = [{"shortcut_id": row[0], "name": row[1], "question": row[2]} for row in cur_result]

        return buttons_list

    except Exception as e:
        print(e)
        return str(e)


def dev1():
    print ("KNOWN BUTTONS:")

    buttons=get_wt_short_cut_buttons_from_db()
    for button in buttons:
        print(button)
        
    """
    KNOWN BUTTONS:
    {'shortcut_id': 0, 'name': 'Test 1', 'question': 'Question 1'}
    """

    return


if __name__=='__main__':
    branches=['dev1']
    for b in branches:
        globals()[b]()