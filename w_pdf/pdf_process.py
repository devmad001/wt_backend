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
from w_storage.ystorage.ystorage_handler import Storage_Helper


from pdf_extractor import PDF_Extractor
from azure_ocr.azure_ocr import DocumentIntelligence

logging=setup_logging()


#0v4# JC  Mar 18, 2024  Add azure document intelligence for pdf2txt (via ocr)
#0v3# JC  Oct 13, 2023  Log error but don't fail if given pdf exists without conversion
#0v2# JC  Sep 19, 2023  Support for multiple pdf2txt methods!
#0v1# JC  Sep  2, 2023  Init


"""
HIGH-LEVEL LOGIC:
- do pagination
- sectional types:
?IS_SECTION_HAS_TRANSACTIONS

CHASE:
- No duplicates but summary totals

CHECKING SUMMARY, DEPOSITS AND ADDITIONS, ATM & DEBIT CARD WITHDRAWLS, ATM & DEBIG CARD SUMMARY, ELECTRONIC WITHDRAWLS, FEES, DAILY ENDING BALANCE< SERVICE CHARGE SUMMARY  **includes extra per card details
>> ATM & DEBIT CARD SUMMARY:  Includes cardholder_name, card number and totals

"""

Storage=Storage_Helper(storage_dir=LOCAL_PATH+"../w_datasets")
Storage.init_db('cache_docs')

def cache_document(record):
    global Storage
    if not 'id' in record:
        raise Exception("No id in record")
    Storage.db_put(record['id'],'record',record,name='cache_docs')
    return

def iter_query_documents():
    global Storage
    # External access (ie/ ai_extractor)
    found=False
    for kkey in Storage.iter_database('cache_docs'):
        record=Storage.db_get(kkey,'record',name='cache_docs')
        Doc=Doc_Model()
        Doc.load(record)
        yield Doc
        found=True
    if not found:
        logging.info("[info] No documents found in: cache_docs")
    return

class Doc_Model():
    """
        See visio design
        - DOC SCHEMA:
        - many statements
        - many pages
        - many sections
        - TARGET SCHEMA: (so not here)
        - many transaction
    """
    def __init__(self):
        self.id=''
        self.filename=''
        self.statements=[]
        self.pages=[]

        ## Allow multiple kinds of extraction
        self.epages={}
        return

    def set_filename(self,filename):
        self.filename=filename
        self.id=re.sub(r'.*\/','',filename)
        return

    def add_page(self,page_text):
        self.pages+=[page_text]
        return

    def dump(self):
        # Dump all variables to json
        #[ ] version?
        #dd=json.dumps(self.__dict__)
        dd=self.__dict__
        return dd

    def load(self,dd):
        self.__dict__ = dd #json.loads(dd)
        return

    def get_pages(self):
        raise Exception("Not implemented -- upgrade to epages")
        return self.pages
    def get_epages(self):
        ## E-page contains multiple extraction methods
        return self.epages

    def set_extracted_pages(self,pages,method):
        #  page_num.method
        c=-1
        for page_text in pages:
            c+=1
            if not c in self.epages:
                self.epages[c]={}
            self.epages[c][method]=page_text
        return

    def count_pages(self):
        #epages based
        pages_count=len(self.epages.keys())
        return pages_count

    def count_words(self,pages):
        words=0
        for page_text in pages:
            words+=len(page_text.split())
        return words
    
    def count_one_char_words(self, pages):
        one_char_words = 0
        for page_text in pages:
            for word in page_text.split():
                if len(word) == 1:
                    one_char_words += 1
        return one_char_words


    def is_image_pdf(self,pages):
        ## If average words per page <50 then is image pdf!
        is_image=False

        if pages:
            words=self.count_words(pages)
            avg_words=words/len(pages)
            if avg_words<50:
                is_image=True
                
            ## One char words:
            ocw=self.count_one_char_words(pages)
            ocw_rate=ocw/len(pages)
            
            if ocw_rate>500: #< 100 is normal.  I'm seeing 1400!! so limit at 500.
                is_image=True
                logging.info("[OCR NEEDED]  Too many characters on page with normal pdf2text: "+str(ocw_rate))
#D            print ("AV WORDS: "+str(avg_words)+" one char words: "+str(ocw)+" pages: "+str(len(pages))+" rate: "+str(ocw_rate))
        else:
            logging.warning("No pages for is_image_pdf??")

        return is_image



#####################################################
#  MAIN INTERFACE::  FILENAME TO CONVERTED DOCUMENT #
#####################################################
#
def interface_file2doc(filename,branch=['pages']):
    # Doc is type but can dump pages easily
    if not os.path.exists(filename):
        raise Exception("[error] file not found: "+str(filename))
    Doc=do_pdf2txt(filename,extract_methods=[])
    return Doc

def interface_is_image_pdf(filename):
    ## Do text extraction and check for density of words
    if not os.path.exists(filename):
        raise Exception("[error] file not found: "+str(filename))

    break_at=10
    PDFE=PDF_Extractor()
    Doc=Doc_Model()
    Doc.set_filename(filename)
    pages_of_text=PDFE.extract_pages_text_tables_priority(filename,break_at=break_at)
    is_image_pdf=Doc.is_image_pdf(pages_of_text)

    return is_image_pdf


def do_pdf2txt(filename='',extract_methods=[]):
    local_count_pages=0
    logging.info("[info] do_pdf2txt: "+str(filename))
    extract_methods=['pypdf2_tables','pdfminer','azure_ocr']
    extract_methods=['pypdf2_tables','pdfminer']

    if not filename:
        ddir=LOCAL_PATH+"../w_datasets/Bank Statements - for Beta Testing/"
        filename=ddir+"07A210E6-B60D-46B6-9D40-9B3239237F05-list.pdf"
        stopp=checkk_call

    ## TOP LEVEL OPTIONS:
    is_image_pdf=False
    enforce_pages_found=0

    PDFE=PDF_Extractor()

    Doc=Doc_Model()
    Doc.set_filename(filename)

    ## VARIOUS METHODS OF EXTRACTION:
    #- pdfminer, pypdf2, image2pdf, etc.

    ## pypdf2 good for tables
    if 'pypdf2_tables' in extract_methods:
        pages_of_text=PDFE.extract_pages_text_tables_priority(filename)

        ### CHECK IF IMAGE PDF!
        is_image_pdf=Doc.is_image_pdf(pages_of_text)
        if is_image_pdf:
            logging.error("[pdf is image and should be pre-processed]: "+str(filename))
            logging.dev("[pdf is image and should be pre-processed]: "+str(filename))
            
        else:

            Doc.set_extracted_pages(pages_of_text,'pypdf2_tables')
            enforce_pages_found=len(pages_of_text)
            local_count_pages=len(pages_of_text)

    if 'pdfminer' in extract_methods:
        pages_of_text=PDFE.extract_pages_text(filename)

        ### CHECK IF IMAGE PDF!
        is_image_pdf=Doc.is_image_pdf(pages_of_text)
        if is_image_pdf:
            logging.error("[pdf is image and should be pre-processed]: "+str(filename))
            logging.dev("[pdf is image and should be pre-processed]: "+str(filename))
            
        else:
            ### Must find same number of pages (since aligned later)
            if enforce_pages_found and enforce_pages_found!=len(pages_of_text):
                raise Exception("[error] enforce_pages_found: "+str(enforce_pages_found)+" != "+str(len(pages_of_text)))
    
            Doc.set_extracted_pages(pages_of_text,'pdfminer')

    if 'azure_ocr' in extract_methods:
        raise Exception("Not implemented")
        pages_of_text=local_pdf2azure_ocr2txt(filename)
        #** OVERWRITE!!
        Doc.set_extracted_pages(pages_of_text,'pypdf2_tables')
        #Doc.set_extracted_pages(pages_of_text,'azure_ocr')

#    local_review_pdf2text_quality(Doc)
    logging.info("[pdf_process.py]  DONE FILENAME: "+str(filename))
    logging.info("[pages found]^: "+str(local_count_pages))

    return Doc

def local_pdf2azure_ocr2txt(filename):
    #Mar 18, 2024
    
    ## Reconnect for each file
    DI=DocumentIntelligence()
    pages_meta=DI.doc2txt(filename)
    pages_of_text=[item[0] for item in pages_meta]
    return pages_of_text

def local_review_pdf2text_quality(Doc):
    ## 
    epages=Doc.get_epages()
    for item in epages:
        print ("PAGE: "+str(item))
        for method in epages[item]:
            print ("="*30)
            print ("METHOD: "+str(method))
            print (epages[item][method])
    print ("RECALL:   pypdf2_tables is preferred method")

    return


def dev_call_try_image_pdf():
    input_pdf=LOCAL_PATH+"pdf_samples/IMAGE_BASED_Chase statements 1.PDF"
    is_image_pdf=interface_is_image_pdf(input_pdf)
    print ("[info] is_image_pdf: "+str(is_image_pdf)+" for "+str(input_pdf))

    input_pdf=LOCAL_PATH+"pdf_samples/IMAGE_BASED_Chase statements 1-ocr.pdf"
    is_image_pdf=interface_is_image_pdf(input_pdf)
    print ("[info] is_image_pdf: "+str(is_image_pdf)+" for "+str(input_pdf))

    return

def dev_call_process_pdf():
    input_pdf=LOCAL_PATH+"pdf_samples/IMAGE_BASED_Chase statements 1-ocr.pdf"
    do_pdf2txt(filename=input_pdf)
    return

    return


if __name__=='__main__':
    branches=['dev1']
    branches=['do_pdf2txt']
    branches=['dev_call_try_image_pdf']
    branches=['dev_call_process_pdf']

    branches=['dev_remove_encryption']

    for b in branches:
        globals()[b]()




"""
DEV NOTES:
- recall want x,y page from pdf extraction


pdfminer
https://stackoverflow.com/questions/22898145/how-to-extract-text-and-text-coordinates-from-a-pdf-file

pdfquery
https://github.com/jcushman/pdfquery
- support xy

https://github.com/chezou/tabula-py



"""
