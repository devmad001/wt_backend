import os
import sys
import codecs
import json
import re

from fastapi import FastAPI

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")

from get_logger import setup_logging
logging=setup_logging()


#0v1# JC  Oct  2, 2023  Init

"""
[given]
section:  Desposits and Credits
description:
Book Transfer Credit B/O: Integrated Call Center Solutions, Florham Park NJ 07932- US Trn: 1428300342Jo
YOUR REF:  ATS OF 21/12/08
[notes]
> Credit so deposited into account.  From Business: Integrated Call Center SOlutions.  To: me.


"""


def dev1():
    return

if __name__=='__main__':
    branches=['dev1']
    for b in branches:
        globals()[b]()

"""
"""
