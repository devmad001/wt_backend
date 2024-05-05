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


#0v2# JC  Jan 15, 2024  Update for running from project dir
#0v1# JC  Sep  6, 2023  


#REF:  https://stackoverflow.com/questions/1896918/running-unittest-with-typical-test-directory-structure

PROJECT_ROOT_DIR=os.path.abspath(LOCAL_PATH+"..")


HARD_CODE_TEST_DIRS = []
HARD_CODE_TEST_DIRS += ['w_test']  # This root relative

HARD_CODE_TEST_DIRS += ['w_test/test_libs_system']

HARD_CODE_TEST_DIRS += ['w_test/test_fastapi']  
HARD_CODE_TEST_DIRS += ['w_test/test_fastapi/api/v1']

HARD_CODE_TEST_DIRS += ['c_case_manager']  # test_case_queue
HARD_CODE_TEST_DIRS += ['c_jobs_manager']  # job focused
HARD_CODE_TEST_DIRS += ['w_llm']           # Should do test_llm

HARD_CODE_TEST_DIRS += ['a_algs/geo_algs'] # google place lookup
HARD_CODE_TEST_DIRS += ['c_macros/fixed_queries'] # transaction tracker etc.
HARD_CODE_TEST_DIRS += ['w_mindstate']  # map urls

HARD_CODE_TEST_DIRS += ['z_apiengine.tests'] #Various
HARD_CODE_TEST_DIRS += ['b_extract']  # regex artifact cleaning etc




def create_test_suite(relative_dirs=None):
    ## Quick test loading across codebase

    if relative_dirs is None:
        relative_dirs = []

    relative_dirs += HARD_CODE_TEST_DIRS

    test_file_strings = []
    
    for relative_dir in relative_dirs:
        the_dir=os.path.join(PROJECT_ROOT_DIR, relative_dir)
        
        # Include files in the specified directory
        test_file_strings += glob.glob(os.path.join(the_dir, 'test_*.py'))

        # Include files in subdirectories that start with 'test_'
        # [ ] doesn't quite go to subs
        for root, dirs, files in os.walk(the_dir):
            if 'test_' in os.path.basename(root):
                test_file_strings += glob.glob(os.path.join(root, 'test_*.py'))

    #As absolute paths
    test_file_strings = [os.path.abspath(path) for path in test_file_strings]

    suites = []
    for file_string in test_file_strings:
        print("[debug]  STRING: " + str(file_string))

        # Remove the project root from the path and convert to module name
        if file_string.startswith(PROJECT_ROOT_DIR):
            module_name = file_string[len(PROJECT_ROOT_DIR) + 1:-3].replace(os.sep, '.')
        else:
            # Handle unexpected case
            print(f"Warning: File {file_string} is not under the project root: "+str(PROJECT_ROOT_DIR))
            continue

        # Remove leading dots from the module name
        module_name = re.sub(r'^\.+', '', module_name)

        print("[test_info] using test at: " + module_name + ".py")
        suite = unittest.defaultTestLoader.loadTestsFromName(module_name)
        suites.append(suite)

    return unittest.TestSuite(suites)


def dev_run_tests_locally():
    testSuite = create_test_suite(relative_dirs=[])
    text_runner = unittest.TextTestRunner().run(testSuite)
    return


if __name__=='__main__':
    branches=['dev_run_tests_locally']
    for b in branches:
        globals()[b]()






        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
