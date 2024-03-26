import os
import sys
import codecs
import json
import re

from datetime import datetime
from urllib.parse import quote

from sqlalchemy import create_engine, Column, Integer, String, Sequence, DateTime, MetaData, ForeignKey, Boolean, Text, text, LargeBinary
from sqlalchemy import BigInteger
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import load_only

#old#from sqlalchemy.dialects.mysql import JSON
from sqlalchemy import JSON
from sqlalchemy import Index  #Composit



LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"

sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")

from database import Base
from database import engine

from w_utils import get_base_endpoint

        

#0v5# JC Feb 16, 2023  Beware of loading Check with image_bytes (use load_only)
#0v4# JC Feb  8, 2023  Log entry table + quick clean
#0v3# JC Jan 30, 2023  Add Check class (check image)
#0v3# JC Jan 12, 2023  Query by JSON is db dependent -- ideally upgrade to direct fields
#0v2# JC Dec  8, 2023  fin_session_id
#0v1# JC Nov  8, 2023  Setup


"""
    DATABASE MODELS
    - see ~/services/dev_services.py for sample usage
"""


BASE_SERVER_ENDPOINT=get_base_endpoint()


class File(Base):
    #** File meta (not the actual content)
    __tablename__ = 'files'
    __table_args__ = {'extend_existing': True}

    def __repr__(self):
        return f"File(filename='{self.filename}')"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    case_id = Column(String(100), nullable=False)
    filename = Column(String(255), nullable=False)
    file_url = Column(String(255))
    is_stored = Column(Boolean, default=False) #Stored locally?
    created = Column(DateTime, default=datetime.utcnow)
    file_meta = Column(JSON, default=lambda: {})  # Default empty dictionary

    location= Column(String(255), nullable=False) #Local,sqlite,db, etc.
    


class Faq(Base):
    __tablename__ = 'faqs'
    __table_args__ = {'extend_existing': True}   #Redefine ok
    
    
    def __repr__(self):
        return f"Faq(label='{self.label}')"
        

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    case_id=Column(String(100))
    created=Column(DateTime, default=datetime.utcnow)
    label = Column(String(100), nullable=False)
    visible = Column(Boolean, default=True)  # To control visibility of the button
    category = Column(String(100))  # For grouping buttons into categories
    faq_meta = Column(JSON, default=lambda: {})  # Default empty dictionary




class CaseReports(Base):
    __tablename__ = "reports"
    __table_args__ = {'extend_existing': True}   #Redefine ok

    def __repr__(self):
        return f"Reports(case_id='{self.case_id}')"
    id = Column(Integer, Sequence('case_id_seq'), primary_key=True)
    case_id=Column(String(100))
    user_id = Column(Integer,nullable=True)
    created=Column(DateTime, default=datetime.utcnow)
    reports = Column(JSON, default=lambda: {})  # Default empty dictionary
    meta = Column(JSON, default=lambda: {})  # tbd

    #reports['kind_name']={}



class Case(Base):
    __tablename__ = "cases"
    __table_args__ = {'extend_existing': True}   #Redefine ok

    def __repr__(self):
        return f"Case(case_id='{self.case_id}')"
    id = Column(Integer, Sequence('case_id_seq'), primary_key=True)
    case_id=Column(String(100))
    created=Column(DateTime, default=datetime.utcnow)
    case_meta = Column(JSON, default=lambda: {})  # Default empty dictionary

    user_id = Column(Integer)
    
    #**beware query by JSON is db specific
    state=Column(String(25))
    case_state = Column(JSON, default=lambda: {})  # Default empty dictionary

    #? owner
#    title = Column(String(100))
#    description = Column(String(255))



class A_Session(Base):  # (don't confuse with Session)
    __tablename__ = 'sessions'
    __table_args__ = {'extend_existing': True}   #Redefine ok
    
    id = Column(Integer, primary_key=True)
    session_id = Column(String(255), nullable=False, unique=True)
    
    user_id = Column(Integer, ForeignKey('users.id'))
#loosen    user = relationship("User", backref="sessions")

    created = Column(DateTime, default=datetime.utcnow)
    
    ## Last valid time
    ## is Valid (method)
    
    
    def get_age(self):
        """Return the age of the session in seconds."""
        now = datetime.utcnow()
        age = now - self.created
        return age.total_seconds()



class Button(Base):
    ## Allow non FK & repeat data
    __tablename__ = 'buttons'
    __table_args__ = {'extend_existing': True}   #Redefine ok
    
    def __repr__(self):
        return f"Button(label='{self.label}')"
        
    id = Column(Integer, primary_key=True)
    #user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    user_id = Column(Integer, nullable=True)
    username = Column(String(255), nullable=True)
    case_id=Column(String(255), nullable=True)
    scope=Column(String(255), nullable=True)
    created=Column(DateTime, default=datetime.utcnow)
    label = Column(String(100), nullable=True)
    action = Column(String(255),nullable=True)  # This can be a URL or some identifier for the action to take
    query = Column(String(255),nullable=True)  # This can be a URL or some identifier for the action to take
    visible = Column(Boolean, default=True)  # To control visibility of the button
    category = Column(String(100),nullable=True)  # For grouping buttons into categories
    bmeta = Column(JSON, default=lambda: {})  # Default empty dictionary

#    user = relationship('User', back_populates='buttons')



class User(Base):
    __tablename__ = 'users'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    username = Column(String(100), nullable=False, unique=True)
    created = Column(DateTime, default=datetime.utcnow)
    # other user fields like email, hashed_password etc.
    umeta = Column(JSON, default=lambda: {})  # Default empty dictionary

#    buttons = relationship('Button', back_populates='user')

    def __repr__(self):
        return f"User(username='{self.username}')"


### fin_session_id
class FinSession(Base):
    """
        TODO:  check link to case when 'created'
    """

    __tablename__ = 'fin_sessions'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    session_id = Column(String(255), nullable=False, unique=True)


    # ForeignKey linking to the User model
#    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    user_id = Column(Integer, nullable=True)
    
    # Relationship to the User model
#    user = relationship("User", backref="auth_sessions")
    
    token = Column(String(255), nullable=False)
    expiry = Column(Integer,nullable=True)  # Expiry time in seconds
    ip_address = Column(String(255))  # IP address of the client
    user_agent = Column(String(255))  # User agent of the client

    fmeta = Column(JSON, default=lambda: {})  # Default empty dictionary

    created_at = Column(DateTime, default=datetime.utcnow)

    def is_valid(self):
        """Determine if the session is still valid based on expiry."""
        if self.expiry is None:
            return True  # Always valid if no expiry is set
        age = (datetime.utcnow() - self.created_at).total_seconds()
        return age < self.expiry

#    def __repr__(self):
#        return f"<AuthSession(user_id='{self.user_id}', session_id='{self.session_id}', created_at='{self.created_at}')>"

## Prepopulate?
#User.buttons = relationship('Button', order_by=Button.id, back_populates='user')



class Check(Base):
    __tablename__ = 'checks'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    check_identifier = Column(String(255), unique=True, nullable=False,index=True) #file name + position counters =unique

    case_id = Column(String(255), index=True)  # 
    transaction_id = Column(String(255), index=True,nullable=True)  # 

    check_id = Column(String(255))  # 
    pdf_filename = Column(String(255),nullable=True)  #
    check_image_filename = Column(String(255),nullable=True)  

    payor_name = Column(String(255),nullable=True)  # Name of the payor, initially empty
    payee_name = Column(String(255),nullable=True)  # Name of the payee, initially empty
    account_num = Column(String(255),nullable=True)  # Possible query param

    image_bytes = Column(LargeBinary(length=2 * 1024 * 1024)) #(mysql no Medium)

    meta = Column(JSON)  # Storing additional metadata as JSON. Use JSON for non-PostgreSQL databases

    created = Column(DateTime, default=datetime.utcnow)
    state = Column(String(255),nullable=True)  # Status of the check record, initially 'created'



    # 17s with image (over network) or 0.1 without
    #        columns_to_exclude = ['image_bytes']
    #        columns_to_load = [getattr(Check, column.name) for column in Check.__table__.columns if column.name not in columns_to_exclude]
    #        checks_orm = base_query.options(load_only(*columns_to_load)).all()


    @classmethod
    def query_without_image_bytes(cls):
        return load_only(
            cls.id, cls.check_identifier, cls.case_id, cls.transaction_id, cls.check_id,
            cls.pdf_filename, cls.check_image_filename, cls.payor_name, cls.payee_name,
            cls.account_num, cls.meta, cls.created, cls.state
        )


    def generate_check_image_url(self):
        global BASE_SERVER_ENDPOINT
        safe_identifier=quote(self.check_identifier)
        url = f"{BASE_SERVER_ENDPOINT}/api/v1/case/{self.case_id}/media/check_images/{safe_identifier}"
        return url

    def __repr__(self):
        attributes = {key: value for key, value in self.__dict__.items() if key != '_sa_instance_state' and key != 'image_bytes'}
        attr_str = ', '.join(f"{key}={repr(value)}" for key, value in attributes.items())
        return f"<Check({attr_str})>"


class LogEntryModel(Base):
    """
    
    Track long-running processes and their state transitions.
    - support tracking background processes (and consequently time estimation)
    - /log_hub/log_hubby.py
    
    """
    #

    __tablename__ = 'log_entries'
    
    ## Composite index:
    #> by case_id & sort by time_updated


    __table_args__ = (
        Index('ix_case_id_time_updated', 'case_id', 'time_updated'),
        {'extend_existing': True},
    )


    id = Column(Integer, primary_key=True)
    case_id = Column(String(255))
    job_id = Column(String(255))
    case_status = Column(String(255))
    job_state = Column(String(255))
    job_time_started = Column(BigInteger)  # UNIX timestamp
    current_state = Column(String(255))
    current_state_start_time = Column(BigInteger) 
    state_transition_name = Column(String(255))
    transition_timestamp = Column(BigInteger)
    time_updated = Column(BigInteger, index=True)  # Index added here
    token_a = Column(Integer, default=0)
    token_b = Column(Integer, default=0)
    meta = Column(JSON)  # Flexible JSON field for additional data



def ADMIN_queries():
    
    
    b=['remove_partial_table_log']
    b=[]


    ## MANUAL MIGRATION
    if 'migrate add String(25) at Case.state for easy query' in b:
        raise Exception('Manual migration')
        print('migrate add String(25) at Case.state for easy query')
        with engine.connect() as con:
            con.execute(text("ALTER TABLE cases ADD COLUMN state VARCHAR(25) DEFAULT 'NEW' AFTER case_meta"))
            
    ## REMOVE PARTIAL TABLES
    if 'remove_partial_table_log' in b:
        raise Exception('Manual migration')
        print('remove_partial_table_log')
        with engine.connect() as con:
            con.execute(text("DROP TABLE log_entries")) 
            
    return



if __name__=='__main__':

    branches=['dev1']
    branches=['ADMIN_queries']

    for b in branches:
        globals()[b]()







