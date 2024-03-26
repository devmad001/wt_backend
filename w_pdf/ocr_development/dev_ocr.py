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

from get_logger import setup_logging
from w_storage.ystorage.ystorage_handler import Storage_Helper

from pdf_extractor import PDF_Extractor
from pdf_process import interface_is_image_pdf  # (Uses PDF extractor)
from pdf_extractor import alg_extract_pages_from_pdf

import ocrmypdf  #pip install ocrmydf   **also above
from pdf_images import interface_pdfocr
from w_pdf.pdf_process import interface_file2doc

logging=setup_logging()


#0v1# JC  Oct 21, 2023  PDF images

"""
    THIS IS A DEVELOPMENT FILE -- migrate functionality to stand alone ___ + add common test to validate oddidites
"""

"""
RAW OCR COMMENTS:
- tesseract 5 drops many config parameter options
- options not well documented but see dev_tess for samples
- what worked in end:
UPGRADE to latest trained data:
eng.traineddata
(22.9MB (Oct 2023) from 4.0MB (Jan 2023?))
- validate same performance on ubuntu machine
https://tesseract-docs.readthedocs.io/_/downloads/en/latest/pdf/

"""


"""
OCR evaluations
- aws Textract nope (unless doing y value)
- google vision nope
- google document ai nope
- some 3rd parties not too bad:
$0.50 per page??
https://www.newocr.com/
https://nanonets.com/online-ocr

APPROACH:
a)  Upgrad ocrmypdf to higher resolution or newer version?
b)  train new font set for First Citizens bank
"""

"""
FINE TUNING DOCS:
    https://www.statworx.com/en/content-hub/blog/fine-tuning-tesseract-ocr-for-german-invoices/
    https://gist.github.com/flaviut/d901be509425098645e4ae527a9e9f3a
    https://www.youtube.com/watch?v=TpD76k2HYms&ab_channel=GabrielGarcia

"""

Config = ConfigParser.ConfigParser()
Config.read(LOCAL_PATH+"../w_settings.ini")
BASE_STORAGE_DIR=Config.get('files','base_storage_rel_dir')
BASE_STORAGE_DIR=LOCAL_PATH+"../"+BASE_STORAGE_DIR


from w_pdf.pdf_extractor import PDF_Extractor


def local_pdf2text(filename):
    ##? method?

    PP=PDF_Extractor()
    pages=PP.extract_pages_text(filename)
    return pages

def local_pdf2epages(path_filename):
    file_pages={}
    file_pages[path_filename]={}

    Doc=interface_file2doc(path_filename)
    file_pages[path_filename]['epages']=Doc.get_epages()

    return file_pages

#from pdf_extractor import alg_extract_pages_from_pdf

def test_ocr():
    ## TEST CASE:
    #- 1 page pdf with image but messes up 1s with 4s!
    start_time=time.time()
    
    force_new_ocr=True
    
    input_filename=LOCAL_PATH+"pdf_samples/"+"ORG_IMAGE_Management-Properties-v-Brusko-Copy-of-First-Citizens-Bank-Checks-2020.pdf"
    output_filename=LOCAL_PATH+"pdf_samples/"+"ORG_IMAGE_FIRST_PAGE_Management-Properties-v-Brusko-Copy-of-First-Citizens-Bank-Checks-2020.pdf"
    
    if not os.path.exists(output_filename):
        new_pdf_filename=alg_extract_pages_from_pdf(input_filename,output_filename,keep_pages=[1])
        print ("NEW PDF: "+str(new_pdf_filename))

    processed_filename=LOCAL_PATH+"pdf_samples/"+"ORG_IMAGE_PROCESSED_OCR_FIRST_PAGE_Management-Properties-v-Brusko-Copy-of-First-Citizens-Bank-Checks-2020.pdf"


    if not os.path.exists(processed_filename) or force_new_ocr:

        ### OPTIMIZE DOES NOTE WORK
        optimize=3 #Highest
        optimize=2
        """ optimize 3 recommends:
        The program 'jbig2' could not be executed or was not found on your
        system PATH.  This program is recommended when using the --optimize {2,3} | --jbig2-lossy arguments,
        but not required, so we will proceed.  For best results, install the program.
        Optimization is improved when a JBIG2 encoder is available and when pngquant is installed. If either of these components are missing, then some types of images cannot be optimized.
        
        Image optimization did not improve the file - optimizations will not be used
        
        ??Manually train?
        https://vietocr.sourceforge.net/training.html
        
        """
        meta={}
        if 'via_import' in []:
            meta=interface_pdfocr(output_filename,processed_filename, optimize=optimize)
            
        else:
            ## EXPERIMENTS:

            notes=[]

            notes+=['standard fails']
            # 1200 I think is my pdf took 138s 1 page
            #ocrmypdf.ocr(input_filename, output_filename, rotate_pages=True, deskew=True, force_ocr=True)

            output_filename=LOCAL_PATH+"pdf_samples/"+"T1_ORG_IMAGE_FIRST_PAGE_Management-Properties-v-Brusko-Copy-of-First-Citizens-Bank-Checks-2020.pdf"
            #: image_dpi will not work cause its' a pdf!
#FF            ocrmypdf.ocr(processed_filename, output_filename, oversample =600, rotate_pages=True, deskew=True, force_ocr=True)

            output_filename=LOCAL_PATH+"pdf_samples/"+"T2_ORG_IMAGE_FIRST_PAGE_Management-Properties-v-Brusko-Copy-of-First-Citizens-Bank-Checks-2020.pdf"
            #: image_dpi will not work cause its' a pdf!
#FF          ocrmypdf.ocr(processed_filename, output_filename, language=['eng'], rotate_pages=True, deskew=True, force_ocr=True)
            
            """
            THRESHOLDING?
            The available thresholding methods in Tesseract are:

                0 - Original Tesseract algorithm. Good general purpose thresholding. This is the default.
                1 - Sauvola's algorithms. Good at dealing with low contrast images.
                2 - Phansalkar's algorithm. Also good with low contrast.
                3 - Adaptive algorithm based on the local area. Can work well for bleedthrough.
                So in general, you would use:
                
                tesseract_thresholding=0 - Default and good for general use.
                tesseract_thresholding=1 or tesseract_thresholding=2 - For cases when the image has low contrast or the font is faint.
                tesseract_thresholding=3 - If you have issues with bleedthrough or other local contrast variations.
                The higher the value, the more aggressive the thresholding. Higher values can help for problematic cases but may introduce other issues. Some experimentation is suggested.
                 auto, otsu, adaptive-otsu, sauvola
            """

            #### JONs NOTES:
            # (this is pre-tesseract data lib update)
            #- 
            output_filename=LOCAL_PATH+"pdf_samples/"+"TOTSU_ORG_IMAGE_FIRST_PAGE_Management-Properties-v-Brusko-Copy-of-First-Citizens-Bank-Checks-2020.pdf"
            
#FF           ocrmypdf.ocr(processed_filename, output_filename, tesseract_thresholding='otsu', language=['eng'], rotate_pages=True, deskew=True, force_ocr=True)


## THESE PASS::

## NOTE USEABLE::
#            output_filename=LOCAL_PATH+"pdf_samples/"+"ATOTSU_ORG_IMAGE_FIRST_PAGE_Management-Properties-v-Brusko-Copy-of-First-Citizens-Bank-Checks-2020.pdf"
#            ocrmypdf.ocr(processed_filename, output_filename, tesseract_thresholding='adaptive-otsu', language=['eng'], rotate_pages=True, deskew=True, force_ocr=True)
            
#nope            output_filename=LOCAL_PATH+"pdf_samples/"+"SAU_ORG_IMAGE_FIRST_PAGE_Management-Properties-v-Brusko-Copy-of-First-Citizens-Bank-Checks-2020.pdf"
#nope            ocrmypdf.ocr(processed_filename, output_filename, tesseract_thresholding='sauvola', language=['eng'], rotate_pages=True, deskew=True, force_ocr=True)
            
#            output_filename=LOCAL_PATH+"pdf_samples/"+"SAU_ORG_IMAGE_FIRST_PAGE_Management-Properties-v-Brusko-Copy-of-First-Citizens-Bank-Checks-2020.pdf"
#nah?            ocrmypdf.ocr(processed_filename, output_filename, tesseract_thresholding='sauvola', language=['eng'], rotate_pages=True, deskew=True, force_ocr=True)


#            output_filename=LOCAL_PATH+"pdf_samples/"+"SAU_ORG_IMAGE_FIRST_PAGE_Management-Properties-v-Brusko-Copy-of-First-Citizens-Bank-Checks-2020.pdf"
#            ocrmypdf.ocr(processed_filename, output_filename, tesseract_thresholding='sauvola', language=['eng'], rotate_pages=True, deskew=True, force_ocr=True)

#            ocrmypdf.ocr(processed_filename, output_filename, tesseract_thresholding='sauvola', language=['eng'], rotate_pages=True, deskew=True, force_ocr=True)







            ##C1
            # Create a local tesseract config file
#            with open('local_config.cfg', 'w') as f:
#                f.write("""preserve_interword_spaces=0
#user-words:1
#user-patterns:1""")
#            
#            output_filename=LOCAL_PATH+"pdf_samples/"+"CONFIG1_ORG_IMAGE_FIRST_PAGE_Management-Properties-v-Brusko-Copy-of-First-Citizens-Bank-Checks-2020.pdf"
#            
#

#3            ##C3
#3            # Create a local tesseract config file
#3            with open('local_config.cfg', 'w') as f:
#3##                f.write("""user-defined-dpi 300""")
#3                
#3                f.write("""
#3psm 6
#3oem 1
#3user-defined-dpi 300
#3""")
#3
#            
#            output_filename=LOCAL_PATH+"pdf_samples/"+"CONFIG4_ORG_IMAGE_FIRST_PAGE_Management-Properties-v-Brusko-Copy-of-First-Citizens-Bank-Checks-2020.pdf"
#            
#            #but it find it...full_filename='local_config.cfg'
#            full_filename=LOCAL_PATH+'local_config.cfg'
#            
#            ocrmypdf.ocr(processed_filename, output_filename, tesseract_config=['local_config.cfg'], language=['eng'], rotate_pages=True, deskew=True, force_ocr=True)
        
            output_filename=LOCAL_PATH+"pdf_samples/"+"CONFID1_ORG_IMAGE_FIRST_PAGE_Management-Properties-v-Brusko-Copy-of-First-Citizens-Bank-Checks-2020.pdf"
#FF           ocrmypdf.ocr(processed_filename, output_filename, user_words="1",rotate_pages=True, deskew=True, force_ocr=True)

            output_filename=LOCAL_PATH+"pdf_samples/"+"CONFID2_ORG_IMAGE_FIRST_PAGE_Management-Properties-v-Brusko-Copy-of-First-Citizens-Bank-Checks-2020.pdf"
#?            ocrmypdf.ocr(processed_filename, output_filename, user_patterns="1", user_words="1",rotate_pages=True, deskew=True, force_ocr=True)


            #???ocrmypdf.ocr(processed_filename, output_filename, redo_ocr=True, deskew=False, clean_final=False, remove_background=False, force_ocr=True)
#F            ocrmypdf.ocr(processed_filename, output_filename, tesseract_oem=1,rotate_pages=True, deskew=True, force_ocr=True)

            ## WORKS!  EIther legacy or remove vectors!

            #*** legacy at oem=0 but may need to install someting...
            #*** legacy at oem=0 but may need to install someting...
            #*** legacy at oem=0 but may need to install someting...

#works!! D3            ocrmypdf.ocr(processed_filename, output_filename, tesseract_oem=0,remove_vectors=True,rotate_pages=True, deskew=True, force_ocr=True)

### WORKS D4
#            output_filename=LOCAL_PATH+"pdf_samples/"+"CONFID4_ORG_IMAGE_FIRST_PAGE_Management-Properties-v-Brusko-Copy-of-First-Citizens-Bank-Checks-2020.pdf"
#            ocrmypdf.ocr(processed_filename, output_filename, remove_vectors=True,rotate_pages=True, deskew=True, force_ocr=True)

            output_filename=LOCAL_PATH+"pdf_samples/"+"CONFID5_ORG_IMAGE_FIRST_PAGE_Management-Properties-v-Brusko-Copy-of-First-Citizens-Bank-Checks-2020.pdf"
#            ocrmypdf.ocr(processed_filename, output_filename, rotate_pages=True, deskew=True, force_ocr=True)


            ### NEW PROBLEM WITH LAYOUT
            
            ## OPEN ISSUES:
            #- new training library fixed the 1 to 4 but now it's one large column
            #- how do adjust for layout?  try with config file (which want' accepted last time)
            #- psm 6 will treat as single uniform block

            
            ###JC:  updateing the training data fixed char issue but now one large column??
            ocrmypdf.ocr(processed_filename, output_filename, rotate_pages=True, deskew=True, force_ocr=True,tesseract_config=['local_config.cfg'])
            

            ### NEXT TO TRY:
            #- if config is working with new setup... try things like dpi to 600

            ##**** REMOVE VECTORS WORKED>... 


            """
    remove_vectors: bool | None = None,   <-- recall lines or things
    force_ocr: bool | None = None,
    redo_ocr: bool | None = None,
    optimize: int | None = None,
    jpg_quality: int | None = None,
    png_quality: int | None = None,
    jbig2_lossy: bool | None = None,
    jbig2_page_group_size: int | None = None,

    tesseract_config: Iterable[str] | None = None,
    tesseract_pagesegmode: int | None = None,
    tesseract_oem: int | None = None,

    pdf_renderer: str | None = None,

    pdfa_image_compression: str | None = None,

    user_words: os.PathLike | None = None,
    user_patterns: os.PathLike | None = None,

        """

            """
        Adjust the --tesseract-config settings that affect Tesseract's thresholds for detecting fonts and text. You may need to experiment with these.
        """

        """
EXTRA CONTROLS:
Here's an explanation of some common Tesseract configuration options like psm, oem, and user-defined-dpi:

psm stands for "page segmentation mode". This controls how Tesseract splits the image into regions for OCR. The default is 3 for auto page segmentation, but other values like 0 for no segmentation or 6 for single uniform block are useful for certain document layouts.
oem controls the "OCR engine mode". This affects the algorithm Tesseract uses for text recognition. The default is 3 for neural nets LSTM OCR, but 2 or 0 may work better for some font and image types.
user-defined-dpi overrides the image resolution that Tesseract detects and uses the provided DPI value instead. This can improve OCR if Tesseract is incorrectly determining the DPI.
Some examples:

psm 0 - Treat the image as a single text block, rather than trying to detect columns, paragraphs, etc. Good for posters.

psm 6 - Assume a single uniform text block. Can help for OCRing plain text.
oem 0 - Use the legacy Tesseract OCR engine. Sometimes works better for formatted text.
oem 1 is LSTM neural nets (which i don't think works with config on teseract 5??)

user-defined-dpi 300 - Manually specifies the image DPI is 300. May help if auto-detection is wrong.
So in summary:

psm controls the page segmentation mode and layout analysis
oem selects the OCR recognition algorithm
user-defined-dpi overrides the detected image resolution

If Tesseract is unable to detect the DPI, it will assume a default DPI value of:

70 DPI for images smaller than 1280x768 pixels
300 DPI for images larger than 1280x768 pixels

        """        

        print ("OCR PDF AT: "+str(output_filename))
        print ("meta: "+str(meta))
        

### ALT FINE TUNING:  https://vietocr.sourceforge.net/training.html

    
    ## Do local pdf2text to check for ocr validation?
    #text=local_pdf2text(processed_filename)
    text=local_pdf2text(output_filename)
    print ("TEXT: "+str(text))
    
    run_time=time.time()-start_time
    print ("OCR RUN TIME: "+str(run_time))

    print ("DONE AT FILENAME: "+str(output_filename))
    if '40117' in str(text):
        raise Exception("OCR FAILED: interpreted 1 as 4!!!!!")
    
    lines=[]
    if isinstance(text,list):
        for liner in text:
            lines+=[liner]
            print ("> "+str(liner))
    else:
        for liner in text.split("\n"):
            lines+=[liner]
            print ("> "+str(liner))
    avg_line_char_length=0
    avg_line_char_length=sum([len(l) for l in lines])/len(lines)
    print ("AVG LINE LENGTH: "+str(avg_line_char_length))


    print ("DOING EPAGES...")

    file_pages=local_pdf2epages(output_filename)
    for fname in file_pages:
        epages=file_pages[fname]['epages']
        for page_num in epages:
            for method in epages[page_num]:
                page_text=epages[page_num][method]
                print ("="*40+" PAGE: "+str(page_num)+" METHOD: "+str(method)+"="*40)
                print (str(page_text))
    
    return


def dev_thoughts():
    tt=[]
    tt+=['increase resolution']
    tt+=['turn off check for text because already do so assume images']
            
    return

def dev_test_functional_ocr():
    ## Integrated tests
    #- check for text in good format (not column high)
    """
    prints resolution during ocrmy..
    
OCR                   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━   0% 0/1 -:--:--    1 resolution (1199.9976, 1199.9976)
resolution (1199.9976, 1199.9976)
OCR                   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━   0% 0/1 -:--:--    1 convert


should look like:  tesseract C:\path\to\your\image.png outputfile -l eng --oem 1 --psm 3



Note that these parameter are used only by the legacy engine.
In general, unlike the legacy engine, the neural network based engine has very little configurable parameters.

this config is ok:
tessedit_create_pdf 1
**HOWEVER tesseract 5 new neural you cant specify much...


data file
https://github.com/tesseract-ocr/tessdoc/blob/main/Data-Files.md


    """

    return


if __name__=='__main__':
    branches=['test_ocr']

    for b in branches:
        globals()[b]()
        
    print ("[ ] formally integrate this into functional test if ocr is changed!")


"""
THROUGHPUT NOTES:
> ORG IMAGE_BASED_Chase statements 1 - Copy.pdf
     - 142 image pages
     - run on pent
"""

"""
EXTRA NOTES:
- deskew function:  https://medium.com/social-impact-analytics/extract-text-from-unsearchable-pdfs-for-data-analysis-using-python-a6a2ca0866dd
^^or: https://pyimagesearch.com/2017/02/20/text-skew-correction-opencv-python/

"""
