import time
import os
import sys
import codecs
import json
import re
import shutil
import configparser as ConfigParser

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"..")
sys.path.insert(0,LOCAL_PATH+"../..")

from get_logger import setup_logging
from w_storage.ystorage.ystorage_handler import Storage_Helper


#from pdf_extractor import PDF_Extractor
#from pdf_process import interface_is_image_pdf  # (Uses PDF extractor)
#from pdf_images import interface_pdfocr

from pdf_extractor import alg_extract_pages_from_pdf
from w_pdf.pdf_process import interface_file2doc  #epages
from ocr_model import interface_pdfocr

import unittest

class MyOCRCase(unittest.TestCase):
    def test_run_this_function(self):
        # Your test logic here
        is_good=call_test_run_with_test_files()
        self.assertTrue(is_good)


logging=setup_logging()


#0v1# JC  Oct 22, 2023  Standard test


"""
    (recall) solution in end is to upgrade to latest tesseract data -- so have test for that
    (see dev_ocr.py for various low-level tesseract config options
    )
"""

#Config = ConfigParser.ConfigParser()
#Config.read(LOCAL_PATH+"../../w_settings.ini")
#BASE_STORAGE_DIR=Config.get('files','base_storage_rel_dir')
#BASE_STORAGE_DIR=LOCAL_PATH+"../"+BASE_STORAGE_DIR


def local_pdf2epages(path_filename):
    file_pages={}
    file_pages[path_filename]={}

    Doc=interface_file2doc(path_filename)
    file_pages[path_filename]['epages']=Doc.get_epages()

    return file_pages


#def test_latest_eng_trainingdata():
#    ## Assume tesseract 5
#    return
#def test_tesseract_version_about_5():
#    return


def local_run_ocr(input_filename,output_filename):
    meta=interface_pdfocr(input_filename,output_filename)
    return meta

def prepare_test_files():
    ## Entire statement
    test_files=[]
    test_case_entire_statement=LOCAL_PATH+"../pdf_samples/TEST_CASE_1_ORG_IMAGE_Management-Properties-v-Brusko-Copy-of-First-Citizens-Bank-Checks-2020.pdf"

    ## One (first) page of statement
    test_case_1_fpath=LOCAL_PATH+"../pdf_samples/TEST_CASE_1_PAGE_ORG_IMAGE_Management-Properties-v-Brusko-Copy-of-First-Citizens-Bank-Checks-2020.pdf"

    if not os.path.exists(test_case_1_fpath):
        new_pdf_filename=alg_extract_pages_from_pdf(test_case_entire_statement,test_case_1_fpath,keep_pages=[1])
    if not os.path.exists(test_case_1_fpath):
        raise Exception("ERROR: "+str(test_case_1_fpath)+" not found")

    test_files+=[test_case_1_fpath]

    return test_files


def call_test_run_with_test_files(verbose=False):
    is_passed=False

    test_files=prepare_test_files()
    
    for test_file in test_files:
        is_passed=True  

        output_filename=re.sub(r'\.pdf$','_OCR.pdf',test_file,flags=re.IGNORECASE)
        if os.path.exists(output_filename):
            os.remove(output_filename)
        
        ### DO OCR
        meta=local_run_ocr(test_file,output_filename)
        run_time=meta['run_time']
        
        ### USE OCR OUTPUT  (leverages pdf2text but keep here because functional performance is important)

        avg_line_lengths={}
        file_pages=local_pdf2epages(output_filename)
        checked_content=False
        page_text=''
        for fname in file_pages:
            epages=file_pages[fname]['epages']
            for page_num in epages:
                if not page_num==0:
                    print ("PAGE NUM?: "+str(page_num))
                    raise Exception ("Just check 1 page for now -- otherwise update avg line length calc")

                for method in epages[page_num]:
                    if not method=='pypdf2_tables': continue
                    print ("METHOD: "+str(method))
                    page_text=epages[page_num][method]
                    
                    if verbose:
                        print ("="*40+" PAGE: "+str(page_num)+" METHOD: "+str(method)+"="*40)
                        print (str(page_text))
                    avg_line_lengths[method]=sum([len(l) for l in page_text.split("\n")])/len(page_text.split("\n"))
                    
                    print ("="*30)
                    print ("PAGE TEXT: "+str(page_text))
        
        #######   TEST SPECIFICS::

        ### CHECK FOR BAD OCR (1 thinks is 4)
        ### Top check for known values
        if not 'TEST_CASE_1' in test_file:
            is_passed=False
            raise Exception("ERROR: "+str(test_file)+" not found")
        else:
            ## Check that bad OCR is not present
            #- assumes filename
            if '40117' in str(page_text):
                is_passed=False
                raise Exception("OCR FAILED: interpreted 1 as 4!!!!!")
        

        ### CHECK OUTPUT FORMATS
        # 37 is good 10 is bad
        # pypdf2_tables 37, pdfminer: 10
        max_line_length=0
        max_line_method=''
        for method in avg_line_lengths:
            if avg_line_lengths[method]>max_line_length:
                max_line_length=avg_line_lengths[method]
                max_line_method=method
        if max_line_length<25:
            is_passed=False
            print ("[WARNING] OCR output is not in good format line length: "+str(max_line_length))
            print (str(epages[0][max_line_method]))  #Assume page 0
            raise Exception("ERROR: OCR output is not in table format")
        
        ### CHECK PROCESSING TIMES
        #?? throughput targets?
        print ("[info] ocr runtime: "+str(run_time))
        if run_time>130:
            print ("[warning] runtime on PENT is 127s here: "+str(run_time))

    print ("[raw test result]: "+str(is_passed))
    return is_passed



if __name__=='__main__':
    branches=['call_test_run_with_test_files']
    for b in branches:
        globals()[b]()


"""
"""
