import time
import os
import sys
import codecs
import json
import re

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"..")
from get_logger import setup_logging
logging=setup_logging()

from w_pdf.pdf_extractor import PDF_Extractor

from w_storage.ystorage.ystorage_handler import Storage_Helper

Storage=Storage_Helper(storage_dir=LOCAL_PATH+"../w_datasets/pipeline")
Storage.init_db('pdfs')
Storage.init_db('pdf_pages')


#0v1# JC  Sep 18, 2023  Setup


"""
LOCAL pdf2txt
- ideally use standard libraries for document normalization
"""

def local_pdf2base64_pages(full_filename):
    PDFE=PDF_Extractor()
    return PDFE.get_pdf_pages_as_base64(full_filename)

def local_pdfcontent2text_pages(pdf_content):
    # returns results['method']=['text_pages']
    PDFE=PDF_Extractor()
    return PDFE.pdf_content2text(pdf_content=pdf_content)

def dev1():
    case_id='case_dev'
    method_used='pdf2txt_generic'
    full_filename=''
    filename=re.sub(r'.*[\\\/]','',full_filename)

    return


if __name__=='__main__':
    branches=['dev1']
    for b in branches:
        globals()[b]()




"""

"""
