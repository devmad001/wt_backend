import time
import os
import sys
import codecs
import json
import re
import io
import base64


LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"..")

from get_logger import setup_logging
logging=setup_logging()

logging.debug("[loading pdf_extractor.py] -- 0.3s...")

from pdfminer.high_level import extract_text #pip install pdfminer.six
from pdfminer.high_level import extract_pages as pdfminer_extract_pages
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfpage import PDFPage
from pdfminer.layout import LTTextContainer

from pdfminer.layout import LAParams
from pdfminer.converter import TextConverter
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter

import PyPDF2
from PyPDF2 import PdfReader   #BOA tables



#0v3# JC  Sep 18, 2023  pdf to base64 pages
#0v2# JC  Sep 11, 2023  pypdf2 works better for BOA tables
#0v1# JC  Sep  2, 2023  Init



"""
https://pdfminersix.readthedocs.io/en/latest/
"""

### NOTES:
#- pdfminer does columns separately (ie/ totals at bottom of page!)
#- pypdf2 does tables well!
#- camelot heavy install

class PDF_Extractor():
    """
        Various pdf to text extraction methods
    """
    def __init__(self):
        return

    def pdfminer_extract_text_pages(self,pdf_content=''):
        """
        Extracts text from each page of the given PDF content using pdfminer.
        
        :param pdf_content: Byte content of the source PDF.
        :return: List of extracted text for each page.
        """
        rsrcmgr = PDFResourceManager()
        retstr = io.BytesIO()
        codec = 'utf-8'
        laparams = LAParams()
        device = TextConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)
        
        # Use an in-memory binary stream to read the PDF content
        pdf_file_like = io.BytesIO(pdf_content)
        
        interpreter = PDFPageInterpreter(rsrcmgr, device)
        pages_text = []

        for page in PDFPage.get_pages(pdf_file_like):
            interpreter.process_page(page)
            pages_text.append(retstr.getvalue().decode(codec,'replace')) #0v2# replace!
            retstr.truncate(0)  # Clear the BytesIO object for the next page

        device.close()
        retstr.close()

        return pages_text

    def pypdf2_extract_text_pages(self, pdf_content=''):
        """
        Extracts text from each page of the given PDF content using PyPDF2.
        
        :param pdf_content: Byte content of the source PDF.
        :return: List of extracted text for each page.
        """
        # Use an in-memory binary stream to read the PDF content
        pdf_stream = io.BytesIO(pdf_content)
        reader = PyPDF2.PdfFileReader(pdf_stream)
    
        pages_text = []
        for page_num in range(reader.numPages):
            page = reader.getPage(page_num)
            page_text = page.extractText().encode('utf-8', 'replace').decode('utf-8', 'replace')
            pages_text.append(page_text)
    
        return pages_text

    def basic_extract_text(self,filename):
        text = extract_text(filename) #pdfminer high text
        return text

    def extract_text(self,filename):
        stopp=chekkk
        pages_text_iter = extract_text(filename)
        for i, text in enumerate(pages_text_iter):
            text = text.encode('utf-8', 'replace').decode('utf-8', 'replace') #0v2#
            yield text
        return

    def extract_pages_text(self,pdf_path):
        pages_text = []
        for page_layout in pdfminer_extract_pages(pdf_path):
            text = ''
            for element in page_layout:
                if isinstance(element, LTTextContainer):
                    text += element.get_text()
            pages_text.append(text)
        return pages_text

    def extract_pages_text_tables_priority(self,pdf_path,break_at=0):
        ## pypdf2 works default for tables
        # pdfminer, pdfplumber miss BOA
        #- break_at for pdf image check
        read_pdf=False
        try:
            reader = PdfReader(pdf_path)
            read_pdf=True
        except Exception as e:
            logging.error("[error] Could not read pdf: "+str(pdf_path))
            logging.dev("[error] Could not read pdf: "+str(pdf_path))

        pages_text=[]
        
        if read_pdf:
            #number_of_pages = len(reader.pages)
            for page in reader.pages:
                text = page.extract_text()
                text = text.encode('utf-8', 'replace').decode('utf-8', 'replace') #0v2#
                pages_text.append(text)
                if break_at and len(pages_text)>=break_at:
                    break
        return pages_text

    def get_pdf_pages_as_base64(self,input_pdf):
        return alg_get_pdf_pages_as_base64(input_pdf)

    def pdf_content2text(self,pdf_content=''):
        ## Could be a page or a whole pdf
        results={}

        methods=[]
        methods+=['pdfminer_extract_text']
        methods+=['pypdf2_tables_priority']

        if 'pypdf2_tables_priority' in methods:
            results['pypdf2_tables_priority']=self.pypdf2_extract_text_pages(pdf_content=pdf_content)
        
        if 'pdfminer_extract_text' in methods:
            results['pdfminer_extract_text']=self.pdfminer_extract_text_pages(pdf_content=pdf_content)

        return results
    
    def get_dpi(self,pdf_filename):
        #** must use:  Pillow or pdf2image or PuMu...libs
        dpi=0
        if os.path.exists(pdf_filename):
            pdf = PyPDF2.PdfFileReader(open(pdf_filename, 'rb'))
            page = pdf.getPage(0)
            page_size = page.mediaBox
            width_pt = page_size.getWidth()
            height_pt = page_size.getHeight()
            
            dpi_x = width_pt / 72  #<-- ps to inches
            dpi_y = height_pt / 72
            dpi=dpi_x
        return dpi


def alg_get_pdf_pages_as_base64(input_pdf):
    """
    Reads the content of each page from a PDF and returns it as a list of Base64 encoded strings.
    
    :param input_pdf: Path to the source PDF file.
    :return: List of Base64 encoded page contents.
    """
    base64_pages = []

    with open(input_pdf, 'rb') as file:
        reader = PyPDF2.PdfFileReader(file)

        for page_num in range(reader.numPages):
            writer = PyPDF2.PdfFileWriter()
            writer.addPage(reader.getPage(page_num))

            # Use an in-memory binary stream to store the PDF page content
            page_content = io.BytesIO()
            writer.write(page_content)

            # Seek back to the start of the stream to read its content
            page_content.seek(0)
            
            # Encode the binary content as Base64 and append to the list
            base64_encoded_content = base64.b64encode(page_content.read()).decode('utf-8')
            base64_pages.append(base64_encoded_content)

    return base64_pages

def alg_extract_pages_from_pdf(pdf_filename, new_pdf_filename,keep_pages=[]):
    """
    Extracts specific pages from a given PDF and saves them as a new PDF.
    
    Parameters:
    - pdf_filename (str): The path to the input PDF.
    - keep_pages (list of int): The list of pages (1-indexed) to be extracted.

    Returns:
    - str: The path to the new PDF.
    """
    if keep_pages==[]: raise Exception("keep_pages is empty")

    # Check if the provided file exists
    if not os.path.exists(pdf_filename):
        logging.error(f"The file {pdf_filename} does not exist.")
        return None
    
    # Create a new PDF writer object
    pdf_writer = PyPDF2.PdfFileWriter()

    # Open the source PDF file
    with open(pdf_filename, 'rb') as file:
        pdf_reader = PyPDF2.PdfFileReader(file)

        # Check if the specified pages are within the valid range
        for page_num in keep_pages:
            if page_num > pdf_reader.numPages or page_num < 1:
                logging.warning(f"Page number {page_num} is out of range.")
                continue

            # Extract the page
            pdf_page = pdf_reader.getPage(page_num - 1)  # 0-indexed
            pdf_writer.addPage(pdf_page)

        # Create a new PDF filename based on current time to avoid collisions
        #new_pdf_filename = os.path.join(LOCAL_PATH, f"extracted_{int(time.time())}.pdf")

        # Save the new PDF
        with open(new_pdf_filename, 'wb') as out_file:
            pdf_writer.write(out_file)

        logging.info(f"Extracted pages saved to {new_pdf_filename}.")
        return new_pdf_filename



def dev1():

    ddir=LOCAL_PATH+"../w_datasets/Bank Statements - for Beta Testing/"

    filename=ddir+"07A210E6-B60D-46B6-9D40-9B3239237F05-list.pdf"

    if 'basic' in []:

        text=PDF_Extractor().basic_extract_text(filename)
    
        # Text to utf-8
        text = text.encode('utf-8', 'replace').decode('utf-8', 'replace')
    
        print ("TEXT: "+str(text))

    print ("FILENAME: "+str(filename))

    return

ddir=LOCAL_PATH+"../w_datasets/Bank Statements - for Beta Testing/"
sample_filename=ddir+"SGM BOA statement december 2021.pdf"

def dev_camelot():
    print ("pdfminer does columns separately")

    import camelot
    ddir=LOCAL_PATH+"../w_datasets/Bank Statements - for Beta Testing/"
    filename=ddir+"SGM BOA statement december 2021.pdf"

    tables = camelot.read_pdf(filename)

    for table in tables:
        print ("> "+str(table.parsing_report))

    return

def dev_pypdf2():
    global sample_filename
    from PyPDF2 import PdfReader
    print ("pypdf2 works well for tables")

    reader = PdfReader(sample_filename)
    number_of_pages = len(reader.pages)
    print ("FOUN P: "+str(number_of_pages))
    page = reader.pages[2]
    text = page.extract_text()
    text = text.encode('utf-8', 'replace').decode('utf-8', 'replace')
    print ("PAGE: "+str(text))
    return

def dev_pdfplumber():
    global sample_filename
    # pdfminer higher level for tables
    import pdfplumber
    #https://github.com/jsvine/pdfplumber

    print ("pdfplumber has many options for table but pypdf2 works best for now https://github.com/jsvine/pdfplumber")

    with pdfplumber.open(sample_filename) as pdf:
        page = pdf.pages[1]
        print ("PAGE: "+str(page))

        table_settings={'horizontal_strategy': 'lines'}
        table = page.extract_table(table_settings=table_settings)
        print ("TABLE: "+str(table))
        for row in table:
            print(row)

    return

def dev_pdfpages():

    from PyPDF2 import PdfReader
    print ("pypdf2 works well for tables")

    reader = PdfReader(sample_filename)

    number_of_pages = len(reader.pages)
    print ("FOUN Page count: "+str(number_of_pages))

    ## FOR CONTENT (rather then filename)

    # Read the PDF content from a file (as an example)
    pdf_content=''
    with open(sample_filename, "rb") as f:
        pdf_content = f.read()


#    page = reader.pages[2]
#    text = page.extract_text()
#    print ("PAGE: "+str(text))

    return

if  __name__=='__main__':
    branches=['dev1']
    branches=['dev_camelot']
    branches=['dev_pypdf2']
    branches=['dev_pdfplumber']

    branches=['dev_pdfpages']

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
