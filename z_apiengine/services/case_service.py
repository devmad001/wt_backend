import os
import sys
import codecs
import json
import re
from datetime import datetime,timedelta

from sqlalchemy.orm import Session
from sqlalchemy import cast, String
from sqlalchemy import func, desc

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")
sys.path.insert(0,LOCAL_PATH+"../..")

from database_models import Case,User
from database import SessionLocal
from fastapi import Depends


from get_logger import setup_logging
logging=setup_logging()


        
#0v4# JC Jan 17, 2023  Call to initialize case
#0v3# JC Jan 11, 2023  Formalize  (lead local 'admin' functions or see test_case_queue.py)
#0v2# JC Dec  6, 2023  Add state to Case for better sync tracking
#0v1# JC Nov  8, 2023  Setup


"""
    CASE MANAGEMENT SERVICE
    - tested (basic) in test_finaware_services (or test_case_queue etc)
    - Cases assume a processing state in case_state_service
"""

# Dependency for session management

        
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def admin_create_user(username):
    # Get user
    user=None
    with SessionLocal() as db:
        user = db.query(User).filter_by(username=username).first()
        if not user:
            # Create a new user if it doesn't exist
            user = User(username=username)
            db.add(user)
            db.commit()
            db.refresh(user)
        return user
    return user

def admin_set_case_state_dict(case_id: str, case_state: dict, state=''):
    case=None
    with SessionLocal() as db:
        case = db.query(Case).filter_by(case_id=case_id).first()
        if not case:
            #**case note exists so create
            case=Case(case_id=case_id, case_state=case_state)
            db.add(case)

        if case and case_state:
            # Update the entire case_state dictionary
            case.case_state = case_state
            case.state=state
    
            # Commit the changes to the database
            db.commit()
            db.refresh(case)  # Refresh to get the latest state
        
            return case.case_state
        else:
            logging.warning("[no case state dict cause no case at]: "+str(case_id))
            return {}  # Return an empty dict if the case does not exist

## ALT is pass it
#@app.get("/get_case_state/{case_id}")
#def get_case_state(case_id: str, db: Session = Depends(get_db)):
#    return admin_get_case_state_dict(case_id, db)

def admin_get_case_state_dict(case_id: str):
    #*migrate to get_case_state_info
    case=None
    case_state_dict={}
    with SessionLocal() as db:
        case = db.query(Case).filter_by(case_id=case_id).first()
    if case:
        case_state_dict=case.case_state
#D        print ("[debug @admin_get_case_state_dict] case_state: "+str(case_state)+" AT ID: "+str(case_id))
    else:
        logging.warning("[no case state dict cause no case at]: "+str(case_id))
    return case_state_dict

def admin_get_case_state_info(case_id: str):
    #case_meta like created etc?
    case=None
    case_state_dict={}
    case_meta={}
    state=''

    with SessionLocal() as db:
        case = db.query(Case).filter_by(case_id=case_id).first()
    if case:
        state=case.state
        case_state_dict=case.case_state
        case_meta=case.case_meta
        case_meta['created']=case.created
    else:
        logging.warning("[no case state dict cause no case at]: "+str(case_id))

    return state,case_meta,case_state_dict

def update_case_state(case_id='',state=''):
    #** no touching dict for now
    with SessionLocal() as db:
        case = db.query(Case).filter_by(case_id=case_id).first()
        if case and state:
            case.state=state
            db.commit()  #<-- 
            db.refresh(case)
    return

def admin_set_case_state(case_id: str, kkey: str, vvalue: str):
    case_state={}
    case=None
    with SessionLocal() as db:
        case = db.query(Case).filter_by(case_id=case_id).first()
        if case:
            # Update the existing case's case_state={}
            ## No default on JSON

            if not case.case_state: #<-- 
                case.case_state={}
            case.case_state[kkey]=vvalue
            
            ## New .state
            if kkey=='state': case.state=vvalue

            # Resave case instance
            db.commit()  #<-- 
            db.refresh(case)  # Refresh to get the latest state
    
            case_state=case.case_state
        else:
            logging.warning("[no case state dict cause no case at]: "+str(case_id))
        return case_state

def get_case_orm(case_id: str):
    case=None
    with SessionLocal() as db:
        try:
            case = db.query(Case).filter_by(case_id=case_id).first()  #Timeout?
        except Exception as e:
            logging.warning("mysql timeout or similar?: "+str(e))
            case = db.query(Case).filter_by(case_id=case_id).first()  #For auto retry
    return case

def get_case_meta(case_id: str):
    case=None
    case_meta={}
    with SessionLocal() as db:
        case = db.query(Case).filter_by(case_id=case_id).first()
    if case:
        case_meta=case.case_meta
    return case_meta

def delete_case(case_id: str):
    case=None
    is_deleted=False
    with SessionLocal() as db:
        # Select all cases with case_id ** enforce unique
        #case = db.query(Case).filter_by(case_id=case_id).first()
        cases=db.query(Case).filter_by(case_id=case_id).all()
        ## Delete all cases with case_id
        for case in cases:
            db.delete(case)
            is_deleted=True
        db.commit()
    return is_deleted

def does_case_exist(case_id: str):
    case=None
    with SessionLocal() as db:
        case = db.query(Case).filter_by(case_id=case_id).first()
    if case:
        return True
    else:
        return False

def list_all_cases(user_id='',limit=1000):
    # Recall mapping user_id (external) is username internally
    # (see CASE_State_Manager)
    #[ ] sort by latest?
    cases=[]
    if not user_id:
        with SessionLocal() as db:
            # Get all cases from the database
            if limit:
                cases = db.query(Case).limit(limit).all()
            else:
                cases = db.query(Case).limit.all()
    else:
        cases=list_user_cases(user_id)
    return cases  # This could be a list of case objects

def list_all_cases_sorted_by_newest(limit=1000):
    #sorted by date
    # Recall mapping user_id (external) is username internally
    # (see CASE_State_Manager)
    cases=[]
    with SessionLocal() as db:
        # Get all cases from the database
        if limit:
            cases = db.query(Case).order_by(Case.created.desc()).limit(limit).all()
        else:
            cases = db.query(Case).order_by(Case.created.desc()).all()
    return cases  # This could be a list of case objects

def list_user_cases(username: str):
    logging.info("[debug] list_user_cases for username: "+str(username))
    user=None
    with SessionLocal() as db:
        try:
            user = db.query(User).filter_by(username=username).first() # ? MySQL timeout?
        except Exception as e:
            logging.warning("mysql timeout or similar?: "+str(e))
        user = db.query(User).filter_by(username=username).first() # ? MySQL timeout?

    if user:
        # Once you have the user object, you can access their cases
        
        ## Case user_id is not hard coded user.id
        user_cases = db.query(Case).filter_by(user_id=user.id).all()
        #NO!# user_cases = db.query(Case).filter_by(user_id=username).all()
        #ALL FOR DEV#  user_cases = db.query(Case).all()
        # Now you have a list of cases associated with the user
        return user_cases  # Returns a list of Case instances
    else:
        logging.warning("[user not found]: "+str(username))

    return []  # Return an empty list if the user is not found

def local_initialize_case_FSM(case_id):
    ## On new Case record creation -- also initialize FSM to INIT
    #[ ] TODO circular import
    from c_case_manager.case_pipeline import interface_initialize_case
    interface_initialize_case(case_id)
    return

def create_set_case(case_id: str, username:str, case_meta: dict={}):
    #: case_meta is updated (not overwritten)
        
    ## Store username in meta but passed here because expect load user down stream
    case_meta['username']=username
    
    user=None
    with SessionLocal() as db:
        user = db.query(User).filter_by(username=username).first()
    
    if not user:
        raise Exception("User not found (require create in front_create_set_case): "+str(username))
    
    did_created=False
    # Check if case already exists
    existing_case = db.query(Case).filter_by(case_id=case_id).first()
    if existing_case:
        # Update the existing case's meta data
        existing_case.case_meta.update(case_meta)
        existing_case.user_id=user.id
        db.commit()
        return existing_case,did_created  # Return the updated case object
    else:
        did_created=True
        # Create a new case if it doesn't exist
        new_case = Case(case_id=case_id, user_id=user.id, case_meta=case_meta)
        
        db.add(new_case)
        db.commit()
        
        ## Initialize case FSM to INIT
        local_initialize_case_FSM(case_id)

        return new_case,did_created  # Return the newly created case object


################################################
# *below is post 2023
################################################


def query_cases_by_state_name(state_name):
    cases=[]
    with SessionLocal() as db:
        #cases = db.query(Case).filter(Case.case_state['state'].astext == state_name).all()
        cases= db.query(Case).filter(Case.state == state_name).all()
    return cases


def query_cases_by_various(username='', age_hours=0, state_name='', not_state_name=''):
    cases=[]
    with SessionLocal() as db:
        #cases = db.query(Case).filter(Case.case_state['state'].astext == state_name).all()
        #cases= db.query(Case).filter(Case.state == state_name).all()
        #[ ] get username
        if not_state_name:
            cases= db.query(Case).filter(Case.state != not_state_name).all()
        
    return cases

def query_list_cases_grouped_by_username_ordered_by_created():
    cases = []
    with SessionLocal() as db:
        # Aggregate function applied to other fields or include them in GROUP BY
        cases = db.query(
            Case.user_id, 
            func.count(Case.id),  # Example of using an aggregate function
            func.max(Case.created)  # Get the latest created date for each user
        ).group_by(Case.user_id).order_by(func.max(Case.created)).all()
    return cases


def list_recent_cases(hours: int = 100):
    recent_cases=[]
    with SessionLocal() as session:

        # Calculate the timestamp for 100 hours ago
        time_limit = datetime.utcnow() - timedelta(hours=hours)
    
        # Query the cases created within the last 100 hours
        recent_cases = session.query(
            Case.case_id, Case.user_id, Case.created, Case.case_state
        ).filter(
            Case.created >= time_limit
        ).order_by(desc(Case.created)).all()

    return recent_cases
    

def canned_queries(branch=''):
    results=[]
    if branch=='list_recent_cases':
        results=list_recent_cases()
    return results


def dev1():
    print ("Update db sessions")
    
    return


if __name__=='__main__':
    branches=['dev1']
    for b in branches:
        globals()[b]()

