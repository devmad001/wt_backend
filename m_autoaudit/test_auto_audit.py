import os
import sys

import unittest

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")

from auto_auditor import AutoAuditor



#0v1# JC  Mar 14, 2023  Setup basic test (esp if used throughout program)


"""

"""



class TestAutoAudit(unittest.TestCase):
    
    def setUp(self):
        #self.Auditor=AutoAuditor()
        pass

    def test_direct_incident(self):
        #> see modules_hub.py
        
        self.Auditor=AutoAuditor()
        self.Auditor.add_incident('test_direct_incident')
        self.assertEqual(len(self.Auditor.all_incidents),1)
        
        self.Auditor.stop_audit()
        
    
    def test_run_dummy_pipeline(self):
        
        scopes=['dummy_check']
        schema={}
        state={}

        Auditor=AutoAuditor()
        incidents,report=Auditor.run_audit_pipeline(scopes=scopes,schema=schema,state=state)
        
        self.assertEqual(len(incidents),0) #  [ ] need actual test

        return




if __name__ == "__main__":
    unittest.main()




