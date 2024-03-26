import os,sys
import re

import unittest
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any


LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"

sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../../")

from z_apiengine.database import SessionLocal
from z_apiengine.database_models import LogEntryModel
from log_hubby import LogEntry


#0v1# JC  Feb  8, 2024  Init

"""
- generic statement for sqlalchemy
with SessionLocal() as db:
    pass

"""


class TestLogEntryLifecycle(unittest.TestCase):

    def setUp(self):
        # Create a session for the test
        self.db = SessionLocal()

    def tearDown(self):
        # Rollback and close the session after each test method
        self.db.rollback()
        self.db.close()

    def test_create_and_delete_log_entry(self):
        # Create a log entry instance using your Pydantic model
        log_entry_data = LogEntry(
            case_id=123,
            job_id=456,
            case_status="active",
            job_state="running",
            job_time_started=1617983106,
            current_state="processing",
            current_state_start_time=1617983106,
            state_transition_name="processing_to_completed",
            transition_timestamp=1617983200,
            time_updated=1617983200,
            token_a=161,
            token_b=11,
            meta={
                "cpu_usage": 80.0,
                "memory_usage": 2000.0,
                "notes": "Transition to completed state"
            }
        )

        # Convert Pydantic model to SQLAlchemy model and add it to the session
        db_log_entry = LogEntryModel(**log_entry_data.dict())
        self.db.add(db_log_entry)
        self.db.commit()
        self.db.refresh(db_log_entry)

        # Assert the log entry was created by checking if it has an ID
        self.assertIsNotNone(db_log_entry.id)

        # Delete the log entry from the database
        self.db.delete(db_log_entry)
        self.db.commit()

        # Verify that the log entry was successfully deleted by querying it
        deleted_log_entry = self.db.query(LogEntryModel).filter_by(id=db_log_entry.id).first()
        self.assertIsNone(deleted_log_entry)




if __name__ == '__main__':

    unittest.main()





"""

"""



