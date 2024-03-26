import os
import sys
import time
import unittest



LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"

sys.path.insert(0,LOCAL_PATH)
#sys.path.insert(0,LOCAL_PATH+"../")
#sys.path.insert(0,LOCAL_PATH+"../../")


from fixed_query_transaction_tracker import FIXED_query_transaction_tracker
from fixed_query_transactions import FIXED_get_all_cases_transactions


#0v1# Jan 22, 2024


"""
    Transaction Tracker:  on main dashboard view
    - this test also covers basics of transactions query
    - ideally not real db data but fine for now

"""

def load_sample_transactions():
    # Ideally fixed but...
    tts,meta=FIXED_get_all_cases_transactions(limit=100)
    return tts


class TestTransitionTracker(unittest.TestCase):
    
    def setUp(self):
        self.tts=load_sample_transactions()

    
    def test_1(self):
        self.assertTrue(len(self.tts)>0,"No transactions in the neo4j database")
        results,meta=FIXED_query_transaction_tracker(tts=self.tts)
        self.assertEqual(results['count_transactions_total'],len(self.tts))



if __name__=='__main__':
    unittest.main()










