import os, sys
import time
import requests

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")
sys.path.insert(0,LOCAL_PATH+"../../")
sys.path.insert(0,LOCAL_PATH+"../../../")


from get_logger import setup_logging
logging=setup_logging()

#from services.square_service import get_service_square_data_records

## For CASE_Proxy memory:
from z_apiengine.services.case_service import admin_set_case_state
from z_apiengine.services.case_service import admin_set_case_state_dict
from z_apiengine.services.case_service import admin_get_case_state_dict
from z_apiengine.services.case_service import admin_get_case_state_info

from z_apiengine.services.case_service import delete_case
from z_apiengine.services.case_service import create_set_case
from z_apiengine.services.case_service import admin_create_user

from z_apiengine.services.case_service import list_all_cases
from z_apiengine.services.case_service import query_cases_by_state_name

from z_apiengine.services.case_service import update_case_state
from z_apiengine.services.case_service import get_case_orm


## Include Job status locally for real-time update


#0v1# JC Jan 11, 2023  Clean Case states


"""
    MANAGE STATE MACHINE FOR USER CASES PAGE

    - supports UI, persistent db state, and backend processing option
    - good standalone & easy check, cache and update
- org was FE_simulate_user_flow...

"""



class Cases_State_Manager:
    """
        Support status across many cases
    """

    def __init__(self):
        return 
    
    def query_cases(self,state_name=''):
        if state_name:
            mode='by_state_name'
        else:
            raise Exception("Not implemented")

        if mode=='by_state_name':
            cases = query_cases_by_state_name(state_name)
            for case in cases:
                yield case
        return
    
    def iter_cases(self,limit=1000):
        #* does not iter on backend
        for case in list_all_cases(limit=limit):
            yield case
        return
    
    def get_case_state_dict(self,case_id):
        case_state_dict=admin_get_case_state_dict(case_id)
        if not case_state_dict:
            case_state_dict={}
        return case_state_dict
    
    def delete_case(self,case_id):
        ## Delete entire object (recall, this is proxy)
        return delete_case(case_id)
    
    def create_set_case(self,case_id,username,case_meta={}):
        # Does .update
        new_case,did_create=create_set_case(case_id,username,case_meta=case_meta)
        return new_case,did_create
    
    def create_user(self,username):
        return admin_create_user(username)
    


class Case_Proxy:
    ## This is not a wrapper for Case obj but collection of methods
    #**ideally migrate to sqlalchemy function definitions

    def __init__(self,case_id):
        self.case_id=case_id
        return
    
    def is_state(self,state):
        isit=False
        case=get_case_orm(self.case_id)
        if case and case.state==state:
            isit=True
        return isit
    
    def update_state(self,state):
        return update_case_state(self.case_id,state)
    
    def set_case_state_info(self,state,case_state_dict):
        return admin_set_case_state_dict(self.case_id,case_state_dict,state=state)

    def get_state_dict(self):
        state_dict=admin_get_case_state_dict(self.case_id)
        if not state_dict: state_dict={}
        return state_dict

    def get_state_info(self):
        state,case_meta,state_dict=admin_get_case_state_info(self.case_id)
        if not state_dict: state_dict={}
        return state,case_meta,state_dict
    
#    def set_state_key(self,kkey,vvalue):
#        return admin_set_case_state(self.case_id,kkey,vvalue) #returns full dict
#    
#    def set_state_word(self,word):
#        print ("[debug] case_id: "+str(self.case_id)+" STATE: "+str(word))
#        return self.set_state_key('state_word',word)
#    
#
#    def set_state_dict(self,state_dict):
#        if state_dict:  #Basic check
#            admin_set_case_state_dict(self.case_id,state_dict)
#        return
   

def dev_queries():
    CM=Cases_State_Manager()
    
    if True or 'dev_query' in []:
        for case in CM.query_cases():
            print ("!!: "+str(case))
            
    if 'dev_list' in []:
        for case in CM.iter_cases():
            print ("!!: "+str(case.case_state))
            
    if 'hard code db migration':
        pass

    if 'dev_query' in []:
        pass

    return


if __name__ == "__main__":
    dev_queries()









