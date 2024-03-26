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

from database_models import A_Session, User, Case
from database import SessionLocal


from get_logger import setup_logging
logging=setup_logging()


        
#0v1# JC Nov  8, 2023  Setup


"""
    SESSION MANAGEMENT SERVICE
"""

SESSION_AGE_EXPIRY=12*60*60 #12 hours

def delete_session(session_id: str):
    with SessionLocal() as db:
        try:
            session = db.query(Session).filter_by(session_id=session_id).first()
            if session:
                db.delete(session)
                db.commit()
                return True  # Session deleted successfully
            else:
                return False  # Session not found
        except Exception as e:
            # Log the exception and optionally handle it
            logging.error(f"Error in delete_session: {str(e)}")
            db.rollback()  # Rollback in case of exception
            return False

def create_set_session(session_id: str, username: int):
    # Check if session already exists
    
    with SessionLocal() as db:
        existing_session = db.query(A_Session).filter_by(session_id=session_id).first()
        if existing_session is None:
            # Assuming User model has an 'id' field that is a primary key
            user = db.query(User).filter_by(username=username).first()
            if user:
                new_session = A_Session(session_id=session_id, user_id=user.id)
                db.add(new_session)
                db.commit()
                return new_session  # Return the newly created session object
            else:
                return None  # User not found
        else:
            return None  # Session already exists

def list_all_sessions():
    with SessionLocal() as db:
        all_sessions = db.query(A_Session).all()  # Retrieve all sessions
    return all_sessions  # Returns a list of all session objects

def list_user_sessions(username: str):
    with SessionLocal() as db:
        user_sessions = db.query(A_Session).filter_by(username=username).all()  # Retrieve sessions for a specific user
    return user_sessions  # Returns a list of session objects for the given user

def get_session(session_id: str):
    with SessionLocal() as db:
        session = db.query(A_Session).filter_by(session_id=session_id).first()  # Retrieve session by session_id
    return session  # Returns a session object


######
## User based or case based?
#- can user access case details?
#- must be logged in AND have access to case

def alg_is_user_session_valid(username: str, session_id: str):
    global SESSION_AGE_EXPIRY

    is_valid=False
    
    ## LOCAL DB CHECK
    session=get_session(session_id=session_id)
    ## Check local
    #   ^if not expired [ ]
    if session:
        age=session.get_age()
        if age>SESSION_AGE_EXPIRY:
            logging.info("Session expired: "+str(session_id))
            delete_session(session_id=session_id)
            session=None
    
    if session:
        if session.user.username==username:
            is_valid=True

    ## REMOTE DB CHECK
    if not is_valid:
        ## Check remove
        is_valid=proxy_auto_validate_user_session(username=username, session_id=session_id)
        
        if is_valid:
            ## Update local sessoin state
            create_set_session(session_id=session_id, username=username)

    return is_valid


def alg_can_user_access_case(username: str, case_id: str, session_id: str):
    ## Check user session
    is_valid=alg_is_user_session_valid(username=username, session_id=session_id)
    
    if is_valid:
        with SessionLocal() as db:
            case = db.query(Case).filter_by(case_id=case_id).first()
            user=db.query(User).filter_by(username=username).first()
            if case and user:
                if case.user_id==user.id:
                    is_valid=True
    ## Check user case
    return is_valid

def alg_set_user_session(username: str, session_id: str):
    #1/  validate
    is_authenticated=proxy_auto_validate_user_session(username=username, session_id=session_id)

    #2/  set
    if is_authenticated:
        create_set_session(session_id=session_id, username=username)

    else:
        pass

    return is_authenticated

def proxy_auto_validate_user_session(username: str, session_id: str):
    ## Proxy from shivam backend session service
    is_authenticated=True
    
    return is_authenticated


## [ ] this is essentially dev mixed with future test to validate functionality
def dev1():
    username='jontest1'
    case_id='casetest1'
    session_id='1234'
    
    b=['auto create objects']
    b=['request to validate user session']
    b=['auto validate user session']

    
    ##
    b=['auto create objects']
    b=['auto validate user session']
    b=['can user access session case']

    b=['is user session valid']

    if 'auto create objects' in b:
        #DEV LOCAL IMPORTS
        from case_service import create_set_case
        from user_service import create_set_user
        from session_service import create_set_session
        
        print ("> create case: ", case_id)
        create_set_case(case_id=case_id)
        print ("> create user: "+str(username))
        create_set_user(username=username)

#        create_set_session(username=username, session_id=session_id)

    if 'auto validate user session' in b:
        ## Validate and set user session
        print ("Set user session: "+str(username)+" at: "+str(session_id))
        alg_set_user_session(username=username, session_id=session_id)

    if 'is user session valid' in b:
        is_valid=alg_is_user_session_valid(username=username, session_id=session_id)
        print ("IS VALID: "+str(is_valid)+" for user: "+str(username)+" at: "+str(session_id))

    if 'request to validate user session' in b: pass

    if 'can user access session case' in b:
        can_access=alg_can_user_access_case(username=username, case_id=case_id, session_id=session_id)
        print ("CAN ACCESS: "+str(can_access)+" for user: "+str(username)+" at: "+str(session_id))

    return




if __name__=='__main__':
    branches=['dev1']
    for b in branches:
        globals()[b]()













