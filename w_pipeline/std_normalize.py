import os
import sys
import codecs
import json
import re

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")

from w_pdf.pdf_process import interface_file2doc
from w_pdf.pdf_process import interface_is_image_pdf
from get_logger import setup_logging
logging=setup_logging()


#0v3# JC  Sep 20, 2023  Upgrade to multiple page extraction methods
#0v2# JC  Sep 12, 2023  Use job scheduler
#0v1# JC  Sep  6, 2023  Init

"""
    CONVERT PDF FILE INTO DOCUMENT OBJECT
    - Helps Pipeline Normalize PDF Pages
"""


def do_normalize(mega,run={},job={}):
    ## mega:  overall case manager memory
    ## run:   current run specific memory
    ## job:   scheduled job to be run status (external to mega)

    ## Hard code
    #ddir=LOCAL_PATH+"../w_datasets/Bank Statements - for Beta Testing/"
    #filename=ddir+"07A210E6-B60D-46B6-9D40-9B3239237F05-list.pdf"

    local_state_good=True  #Reminder to high level check state

    ## Map from job
    #- Job created/managed in a_agent/iagent.py

    if len(job['path_filenames'])>1:
        logging.info("[do_normalize] DOING multiple files: "+str(job['path_filenames']))

    total_pages=0
    file_pages={}

    for path_filename,fname in job['path_filenames']:

        file_pages[fname]={}

        if not os.path.exists(path_filename):
            raise Exception("[do_normalize] file not found: "+str(path_filename))

        ## Check if image pdf
        is_image_pdf=interface_is_image_pdf(path_filename)

        if is_image_pdf:
            logging.warning("[do_normalize] THINKS is_image_pdf: "+str(path_filename))
            #JC branch old# raise Exception("[do_normalize] BAD OCR?? THINKS is_image_pdf: "+str(path_filename))

        #################################
        ## PDF FILE TO DOCUMENT OBJECT
        #################################
        Doc=interface_file2doc(path_filename)
        file_pages[fname]['epages']=Doc.get_epages()
        
        print ("[debug] file pages: "+str(Doc.count_pages()))
        total_pages+=Doc.count_pages()

    if file_pages:
        mega['file_pages']=file_pages  #Nested but complete

    logging.info("[do_normalize] loaded files count: "+str(len(file_pages.keys()))+" total pages count: "+str(total_pages))
    
    if not len(file_pages.keys()):
        raise Exception("[do_normalize] no files loaded at job: "+str(job))
    
#    a=okk

    return file_pages


if __name__=='__main__':
    branches=['do_normalize']
    for b in branches:
        globals()[b]()


"""
"""
