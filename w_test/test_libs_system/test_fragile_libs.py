import os,sys

import fitz
import unittest

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")


class TestFitzLib(unittest.TestCase):
    def setUp(self):
        pass

    def test_fitz_library_drops_open_support(self):
        ## File exists
        filename=LOCAL_PATH+'fargo_1_page.pdf'
        test_file_exists=os.path.exists(filename)
        self.assertTrue(test_file_exists)
        
        ## Fitz has open command
        doc = fitz.open(filename)
        self.assertTrue(doc)

"""
camelot<>sqlachemy conflict?   Because old sqlalchemy is TOO old to use.

sqlachemy was upgraded as part of xxx lib (camelot or similar??)
   ???????????????????????????????????????? 3.0/3.0 MB 17.9 MB/s eta 0:00:00
Installing collected packages: sqlalchemy
  Attempting uninstall: sqlalchemy
    Found existing installation: SQLAlchemy 0.7.10
    Uninstalling SQLAlchemy-0.7.10:
      Successfully uninstalled SQLAlchemy-0.7.10
ERROR: pip's dependency resolver does not currently take into account all the packages that are installed. This behaviour is the source of the following dependency conflicts.
camelot 12.6.29 requires SQLAlchemy<0.8.0,>=0.7.7, but you have sqlalchemy 2.0.23 which is incompatible.
Successfully installed sqlalchemy-2.0.23

"""



def dev1():
    return


if __name__ == "__main__":
    unittest.main()


