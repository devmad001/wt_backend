import os
import sys
import codecs
import json
import re

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")


from get_logger import setup_logging
logging=setup_logging()


#0v1# JC  Sep 25, 2023  Init



def dev1():
    
    """
    https://observablehq.com/@asg017/introducing-dataflow
    https://github.com/asg017/dataflow

    https://github.com/observablehq/runtime
    """
    return

if __name__=='__main__':
    branches=['dev1']
    for b in branches:
        globals()[b]()


"""

"""
