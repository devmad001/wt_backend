import os, sys
import time
import requests


LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")



from z_apiengine.database import SessionLocal
from database_models import Button

#from w_utils import get_base_endpoint
#from w_utils import get_ws_endpoint
#WS_ENDPOINT=get_ws_endpoint()



#0v1# JC Dec 28, 2023  Setup for button routing



"""
    BUTTON ROUTING
    - recall, have previous chat phrase (keyword) to action
    [1]  User clicks to /button_handler
    [2]  Enters at button_hub.py
    
    GOAL: 
    - dynamically saved button query gets submitted for processing

"""


def local_list_buttons():
    buttons=[]
    with SessionLocal() as db:
        buttons_list = db.query(Button).all()
        print ("[debug] button count: "+str(len(buttons)))
        for button in buttons_list:
            print(button.id, button.query)
            buttons+=[button]
    return buttons

def local_get_button(button_id):
    button=None
    with SessionLocal() as db:
        button = db.query(Button).filter(Button.id == button_id).first()
        break
    return button

def dev_dynamic_button_query():
    print ("** moved to button_hub.py")
    
    case_id='65858e0c198ceb69d5058fc3' #Two statement test
    
    buttons=local_list_buttons()
    
    for button in buttons:
        print(button.id, button.query)
        
    a=kkk

    ##1/  Given button id
    button_id='' #Clicked x
    
    ##2/  Get button query (if applicable)
    query='show me transactions < $1000'

    ##3/  Run button query (should auto push answer)
    
    ## Recall original router at (you have that documented)
    
    # bot_service.py --> handle_question
    #   --> wt_brains.py --> Bot_Interface.handle_bot_query()
    # 
    from z_apiengine.services.bot_service import handle_question
    output,meta=handle_question(query,case_id,params={}) #

    return




if __name__ == "__main__":
    dev_dynamic_button_query()




"""
"""



