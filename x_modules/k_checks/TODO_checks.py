import os,sys
import re
import json
import time
import copy
import codecs

import requests

from pathlib import Path
import shutil

import numpy as np

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../../")

from z_apiengine.database import SessionLocal
from z_apiengine.database_models import Check
from sqlalchemy.orm import load_only



from get_logger import setup_logging
logging=setup_logging()



#0v1# JC  Feb 16, 2024  CHECKS SETUP TODO



"""

    [ ] see mikes' online worksheet

    
    JON NOTES:

    [ ] a) normalize date 07/23/2019 to 2019-07-23   (*should have a generic function!)
    [ ] b) single clean function for check  (see orginal matcher etc) ie $1873.20
    [ ] c) dealing with deposit slips
    [ ] d) credit or debit classifier?
    [ ] e) streamline check processing (wt_hub, pre-matcher, with transaction, etc)
    
    OTHER INFO:
    - if matches against transaction can confirm fields
    - stack of the same check source will have same base fields so possibly lietchentstein distance it auto correct
    
    - LLM auto clean fields

    - Generative restoration of scan?
    https://github.com/kayoyin/DirtyDocuments
    https://www.studocu.com/uk/document/sumy-state-pedagogical-university/machine-learning/cleaning-up-dirty-scanned-documents-with-deep-learning-by-kayo-yin-illuin-medium/22513401    
    https://www.kaggle.com/c/denoising-dirty-documents/discussion <-- mentioned in git repo


    EXCEPTIONS:
    - multiple row names on check (husband/wife)
    http://127.0.0.1:8008/api/v1/case/65caaffb9b6ff316a779f525/media/check_images/M%26T%20Victim%20Records__Operating%202017__CR__2017%2002__020717-%24732.00.pdf_2802_2_0_0
    
"""



def alg_clean_check_data(all_checks):
    #** beyond single check because need to validate various (ie/ type, date formats, etc)

    return


def spec_target_check_fields():
    
    ## From M&T Victim Records sample
    fields=[]
    fields+=['Posting Date']
    fields+=['Bank #']
    fields+=['Research Seq #']
    fields+=['Account #']
    fields+=['Dollar Amount']
    fields+=['Check/Serial Store #']
    fields+=['Tran Code']
    fields+=['RTABA']
    fields+=['DB/CR']

    return

if __name__ == "__main__":
    dev1()




"""

"""
