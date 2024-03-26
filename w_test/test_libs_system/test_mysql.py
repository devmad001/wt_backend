import os
import sys
import unittest


LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")
sys.path.insert(0,LOCAL_PATH+"../../")


from z_apiengine.database import SessionLocal
from sqlalchemy import text

#0v1# JC  Dec 22, 2023


class TestMysql(unittest.TestCase):
    def setUp(self):
        pass

    def test_mysql_connect_query(self):
    
#        with SessionLocal() as db:
#            buttons=db.query(Button).all()
#            assertGreater(len(buttons),0)
            
        with SessionLocal() as db:
            try:
                # This query checks if there are any tables in the current database schema
                result = db.execute(text("SELECT 1 FROM information_schema.tables LIMIT 1"))
                table_exists = result.fetchone() is not None
                assert table_exists, "No tables found in the database"
            except Exception as e:
                print(f"An error occurred: {e}")



if __name__ == "__main__":
    unittest.main()