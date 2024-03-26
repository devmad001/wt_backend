import os
import sys
import codecs
import json
import re

from datetime import datetime

from sqlalchemy import create_engine, Column, Integer, String, Sequence, DateTime, MetaData
from sqlalchemy import ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.mysql import JSON

from sqlalchemy import text


LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"

sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")


from database import SessionLocal
from database import Base
from database import engine

from get_logger import setup_logging
logging=setup_logging()


        

#0v1# JC Nov  9, 2023  Setup


"""
    ADMIN SERVICES FOR DATABASE
    - ideally controlled via alembic (migration library)
    - practically, do sql directly
"""



def RUN_sql(cmd):
    is_run = False

    # Start a new session
    with SessionLocal() as db:
        try:
            print("[debug] executing...")
            # Execute the command
            result = db.execute(text(cmd))
            print("[debug] fetching...")

            # Fetch all results and print them
            for row in result.fetchall():
                print(row)

            # Commit the transaction
            db.commit()

            is_run = True
        except Exception as e:
            logging.error("[bad sql]: " + str(cmd) + ":: " + str(e))
            is_run = False
            # Rollback in case of exception
            db.rollback()

    return is_run

### Implement option #2 direct sql modifications
def ADMIN_alter_table_direct_sql():
    
    ## Tracking commands

    #[1]#  Nov  9, 2023:  Add umeta on User for user settings etc.
    #[x]   Nov  9, 2023#    sql_umeta="ALTER TABLE users ADD COLUMN umeta JSON"
    #[x]   Dec  6 2023#    sql_umeta="ALTER TABLE cases ADD COLUMN case_state JSON"
    # * DEFAULT value not allowed on JSON  
    sql_umeta="show tables;"
    sql_umeta="ALTER TABLE cases ADD COLUMN case_state JSON"
    sql_umeta="SHOW OPEN TABLES WHERE In_use > 0;" # This command shows tables that are currently being use"

    logging.info("[ADMIN sql]: "+str(sql_umeta))
    is_run=RUN_sql(sql_umeta)
    logging.info("[ADMIN sql]: "+str(sql_umeta)+" RAN: "+str(is_run))
    
    
    return
    

###############################################
#  OPTION 1:  DESTROY ALL TABLES FOR UPDATE
###############################################

def ADMIN_create_all_tables():
    print ("[ADMIN] creating all tables!")
    #  [ ] use alembic to manage?
    Base.metadata.create_all(bind=engine)
    # DELTE: Base.metadata.drop_all(bind=engine)
    return

def ADMIN_delete_all_tables():
#    checkk=manual_block
    print ("[ADMIN] DELETING all tables!")
    #  [ ] use alembic to manage?
    #Base.metadata.create_all(bind=engine)
    Base.metadata.drop_all(bind=engine)
    return

###############################################
#  OPTION 2:  SAMPLE MANUALLY ADD FIELD
###############################################
"""
ALTER TABLE users ADD COLUMN umeta JSON;


# Import text function for raw SQL
from sqlalchemy import text

# Get the session from your database manager
db_session = db #session

# Start a transaction
with db_session.begin():
    # Define the SQL command
    alter_table_command = text(
        "ALTER TABLE users ADD COLUMN umeta JSON"
    )
    # Execute the command
    db_session.execute(alter_table_command)

"""

###############################################
#  OPTION 3:  SAMPLE MANUALLY ADD FIELD
###############################################

"""
##>  pip install alembic
##>  alembic upgrade head


#Add umeta column to users
#
#Revision ID: <revision_id>
#Revises: <previous_revision>
#Create Date: <date_time>
#

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '<revision_id>'
down_revision = '<previous_revision>'
branch_labels = None
depends_on = None

def upgrade():
    op.add_column('users', sa.Column('umeta', sa.JSON, nullable=True))

def downgrade():
    op.drop_column('users', 'umeta')

"""

def dev1():
    return


def list_actual_table_fields():
    sql='DESCRIBE cases;'
    RUN_sql(sql)
    return

if __name__=='__main__':


    branches=['ADMIN_delete_all_tables']
    branches+=['ADMIN_create_all_tables']

    branches=['list_actual_table_fields']
    branches=['ADMIN_alter_table_direct_sql']


    for b in branches:
        globals()[b]()







