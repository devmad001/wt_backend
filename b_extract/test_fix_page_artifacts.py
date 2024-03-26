import os
import sys
import copy
import codecs
import json
from datetime import datetime
import re
import random
import unittest

import configparser as ConfigParser

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")

from get_logger import setup_logging
logging=setup_logging()


from fix_page_artifacts import auto_clean_page_text


#0v1# JC  Jan 26, 2024  SETUP


"""

"""


class Test_fix_page_artifacts(unittest.TestCase):

    def setUp(self):
        pass

    def test_fixes_1(self):
        sample="""December 1, 2021 to December 31, 2021Your checking account"""
        out=auto_clean_page_text(sample)
        print ("FROM-->TO: "+str(sample)+"-->"+str(out))
        self.assertEqual(out,'December 1, 2021 to December 31, 2021 Your checking account')
    
        #[100]
        sample="""R8A6V7T8T9R3              Ind Name:Marner Holdings Inc Trn: 1650059214Tc36,964.36"""
        out=auto_clean_page_text(sample)
        print ("FROM-->TO: "+str(sample)+"-->"+str(out))
        self.assertNotIn('c36',out)
    
        #[100]
        sample="""R8A6V7T8T9R3              Ind Name:Marner Holdings Inc Trn: 1650059214Tc136,964.36"""
        out=auto_clean_page_text(sample)
        print ("FROM-->TO: "+str(sample)+"-->"+str(out))
        self.assertNotIn('c136',out)
    
        return



if __name__=='__main__':

    unittest.main()

