import unittest


"""
(Nov 1)
LLM2LLM check:  
    This 280 number page requires gpt-4 otherwise, gpt 3.5 skips the duplicate named transaction.  Not good.  (should be caught by exceptions estimate number expected but a bunch of check summaries confuse)			
    - ie:   
     IDEALLY this LLM <> LLM'  needs to be captured in a test but diffcicult to do maybe start with file			
		C:\scripts-23\watchtower\wcodebase\w_ui\file_manager\storage\chase_3_66_b4	
        
07/15 Domestic Incoming Wire Fee - 15.00 705.90
07/15 Domestic Incoming Wire Fee - 15.00 690.90

"""

class TestAPIBasic(unittest.TestCase):
    def setUp(self):
        print ("Sample test_local")

    def test_something(self):
        self.assertEqual(2+2, 4)
#        self.assertEqual(2+1, 4)

if __name__ == "__main__":
    unittest.main()


