import os
import sys
import re

import glob
import unittest


LOCAL_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '.'))+"/"
sys.path.insert(0,LOCAL_PATH)

# Include system base path for regular imports
sys.path.insert(0,LOCAL_PATH+"../")


from test_local import TestAPIBasic #works w path insert


#0v1# JC  Dec  2, 2023  



def converge_fastapi_tests():
    #### FASTAPI

    ### ENTRYPOINT RUN ALL TESTS (1)
    ### ENTRYPOINT RUN SPECIFIC  (2)

    #cd> /w_test/test_fastapi
    #                      python -m pytest
    #                      /api/v1/test_chart_barchart.py

    #cmd='cd '+LOCAL_PATH+'test_fastapi; python -m pytest'
    #print ("[fastapi tests]: "+str(cmd))

    print ("==== CALLING pytest via os.system call...")

    cmd = f'cd {LOCAL_PATH}test_fastapi && python -m pytest'
    print(f"[fastapi tests]: {cmd}")
    os.system(cmd)

    return


def converge_standalone_tests():
    #/z_apengine/tests/*
    
    #*** SO MANY DETAILED CHECK -- but yes, standalone 'cause functional

    return

def converge_base_org_tests():
    ## this
    # /w_test/*
    
    print ("cd /")
    print ("python test_wt.py")

    return

def entrypoint_all_tests():
    print ("[ ] create test cases for standard offerings")

    print ("[fastapi specific]")
    print ("[llm specific]")
    
    converge_fastapi_tests()

    ## standalones
    converge_standalone_tests()
    
    return



if __name__=='__main__':
    branches=['entrypoint_all_tests']
    for b in branches:
        globals()[b]()






        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
