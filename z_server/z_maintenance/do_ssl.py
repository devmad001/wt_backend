import os
import sys
import time
import codecs
import json
import re
import subprocess

import configparser as ConfigParser

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")

from w_utils import am_i_on_server
from mod_execute.mod_execute import The_Execute_Command
from mod_execute.mod_execute import is_process_running_linux

from get_logger import setup_logging
logging=setup_logging()

#0v1# JC  Jan  2, 2024  Init


"""
    SSL / letsencrypt certificate
"""


def dev_letsencrypt():
    """
     sudo certbot certificates
     Feb 2024

    """

    return


if __name__=='__main__':
    branches=['dev_letsencrypt']
    for b in branches:
        globals()[b]()






"""
"""
