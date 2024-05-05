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

# Load logging earlier for pdf overhead
logging=setup_logging()
logging.info("[info] loading pdf libs...")

from pdf_extractor import AUDIT_does_pdf_require_ocr

from pdf_extractor import PDF_Extractor
from pdf_process import interface_is_image_pdf  # (Uses PDF extractor)
from pdf_extractor import alg_extract_pages_from_pdf
from pdf_dpi import calculate_image_dpi
from pdf_dpi import has_pdf_been_ocrd_already

from ocr_model import interface_pdfocr



logging.info("[debug] done loading pdf")


#0v2# JC  Mar  1, 2024  Add basic audit because pdf2txt sometimes requires ocr forced
#0v1# JC  Sep 19, 2023  PDF images


"""
    PDF WIH IMAGES OCR PROCESSING
    - output overlays text layer on top of image layer
    - ocrmypdf supports auto skew + greyscale mods
    - more image processing possible (deskew, opencv, etc)
    - more ocr possible sine tesseract based 
"""

Config = ConfigParser.ConfigParser()
Config.read(LOCAL_PATH+"../w_settings.ini")
BASE_STORAGE_DIR=Config.get('files','base_storage_rel_dir')
BASE_STORAGE_DIR=LOCAL_PATH+"../"+BASE_STORAGE_DIR

## SETUP DIRS
BASE_REL_PROCESSING_STORAGE_DIR="/processing"
BASE_ORG_PROCESSING_STORAGE_DIR="/org"
BASE_OCR_PROCESSING_STORAGE_DIR="/ocr_copies"

def process_pdfimage(storage_dir,pdf_filename,case_id=''):
    global BASE_STORAGE_DIR
    ###
    # PROCESS IMAGE BASED PDF (OCR)
    #- may take 3 minutes for 140 pages
    #- default is to overwrite original pdf file with the OCR version (layer of text over pdf)
    #- Use directories for processing:
    #   - /processing  ;   (move given file to processing state)
    #   - /org  ;          (keep a copy of the given file)
    #   - /ocr_copies ;    (keep a copy of the ocr file)

    OVERWRITE_INPUT_FILE=True # if False append -ocr to filename

    ## Check input storage directory
    if not storage_dir:
        if not case_id:
            raise Exception("[error] case_id required if storage_dir not provided")
        storage_dir=BASE_STORAGE_DIR+"/"+case_id

    ## Check input file
    input_pdf_full_filename=storage_dir+"/"+pdf_filename
    if not os.path.exists(input_pdf_full_filename):
        logging.error("[error] input file not found: "+input_pdf_full_filename)
        return {}

    input_filename=os.path.basename(input_pdf_full_filename)

    logging.info ("[OCR STATE PROCESSING]")

    ### SETUP DIRs
    if not os.path.exists(storage_dir):
        raise Exception("[error] storage_dir not found: "+storage_dir)

    ##/processing
    base_case_processing_storage=storage_dir+BASE_REL_PROCESSING_STORAGE_DIR
    if not os.path.exists(base_case_processing_storage):
        os.makedirs(base_case_processing_storage)

    ##/org
    base_case_org_storage=storage_dir+BASE_ORG_PROCESSING_STORAGE_DIR
    if not os.path.exists(base_case_org_storage):
        os.makedirs(base_case_org_storage)

    ##/ocr_copies
    base_case_ocr_storage=storage_dir+BASE_OCR_PROCESSING_STORAGE_DIR
    if not os.path.exists(base_case_ocr_storage):
        os.makedirs(base_case_ocr_storage)

    ### File based

    processing_pdf_filepath=base_case_processing_storage+"/"+input_filename
    done_org_pdf_filepath=base_case_org_storage+"/"+input_filename
    copy_ocr_pdf_filepath=base_case_ocr_storage+"/"+input_filename

    if OVERWRITE_INPUT_FILE:
        output_pdf_filepath=input_pdf_full_filename
    else:
        output_pdf_filepath=re.sub(r'\.pdf','-ocr.pdf',input_pdf_full_filename,flags=re.I) #add -ocr to input_filename

    ### START PROCESSING
    logging.info("[info] running pdf conversion...")

    logging.info("[1/5] move file: "+input_pdf_full_filename+" to: "+processing_pdf_filepath)
    shutil.move(input_pdf_full_filename,processing_pdf_filepath)

    logging.info("[2/5] start ocr processing input: "+processing_pdf_filepath+" output: "+output_pdf_filepath)

    if True:
        meta=interface_pdfocr(processing_pdf_filepath,output_pdf_filepath)
        logging.info("[info] copy OCR from: "+output_pdf_filepath+" to: "+copy_ocr_pdf_filepath)
        if not os.path.exists(output_pdf_filepath):
            logging.error("[error] output file not found: "+output_pdf_filepath)
            raise Exception("[error] output file not found: "+output_pdf_filepath)

        shutil.copy(output_pdf_filepath,copy_ocr_pdf_filepath)

    else:
        # SIMULATE
        shutil.copy(processing_pdf_filepath,output_pdf_filepath)

    logging.info("[3/5] done ocr processing:: "+str(meta))
    logging.info("[4/5] move temp processing to: "+done_org_pdf_filepath)
    shutil.move(processing_pdf_filepath,done_org_pdf_filepath)
    logging.info("[5/5] done.  See: "+output_pdf_filepath)

    return meta

## Don't REPROCESS!
def has_already_processed(storage_dir,pdf_filename):
    ## If file is in main directory AND ocr_copies then don't process
    pdf_filename=os.path.basename(pdf_filename)

    ## Check input storage directory
    if not storage_dir:
        if not case_id:
            raise Exception("[error] case_id required if storage_dir not provided")
        storage_dir=BASE_STORAGE_DIR+"/"+case_id
    
    ## Check input file
    input_pdf_full_filename=storage_dir+"/"+pdf_filename
    
    ## Check ocr filename
    base_case_ocr_storage=storage_dir+BASE_OCR_PROCESSING_STORAGE_DIR
    ocr_full_filename=base_case_ocr_storage+"/"+pdf_filename
    
    if os.path.exists(input_pdf_full_filename) and os.path.exists(ocr_full_filename):
        return True

    return False

def logic_run_ocr_on_image_pdf(meta,force,full_filename):
    run_ocr=True
    
    ## NOTES
    
    if False:
        # LOGIC 1: [tbd]  consider not running if 72 dpi and not image?
        if meta['dpi'] and meta['dpi']<100 and not meta['is_image_pdf']:
            logging.info('[warning] may not want to run ocr on low dpi file: '+full_filename)
        
        # LOGIC 2:  May have been ocr'd already by omnipage which causes problems with titles?
        #- but omnipage actually drops title so running again may be fine
        if meta['has_been_ocrd'] and not meta['is_image_pdf']:
            run_ocr=False
            logging.info("[info] Yes. PDF has already been ocrd (by omnipage likely): "+full_filename)
            
    if force:
        logging.info("[info] do ocr.  force ocr processing: "+full_filename)
        run_ocr=True

    elif meta['is_image_pdf']:
        run_ocr=True
        logging.info("[info] do ocr.  Yes. PDF is image based: "+full_filename)
        
    else:
        run_ocr=False
        logging.info("[info] do not ocr given meta: "+str(meta))
        

    ### POSITIVE OVERRIDES
    #- pdf2txt seeing issue with removing space in TD or similar statements
    if not run_ocr:

        ## If doesn't think need ocr check once more at special pdf2txt audit case
        require_ocr_because_poor_pdf2txt,reasons=AUDIT_does_pdf_require_ocr(full_filename)
        if require_ocr_because_poor_pdf2txt:
            run_ocr=True
            logging.info("[info] Yes. PDF requires ocr because poor: "+str(reasons))
    
    print ("[debug] ready to run ocr on pdf: "+str(run_ocr)+" meta: "+str(meta))
    return run_ocr


def interface_ocr_image_pdf_if_required(storage_dir,pdf_filename,force=False):
    ## NOTE: many returns if already OCRd!
    print ("[debug] given want to do ocr force state: "+str(force))

    meta={}
    meta['processed']=False
    meta['force_ocr']=force
    meta['is_image_pdf']=False

    full_filename=storage_dir+"/"+pdf_filename

    ## Check given file exists
    if not os.path.exists(full_filename):
        logging.error("[error] input file not found: "+full_filename)
        return meta['processed'],meta['is_image_pdf'],meta
    
    ## Check not already processed
    if has_already_processed(storage_dir,pdf_filename):
        logging.info("[info] file already OCR processed: "+full_filename)
        meta['processed']=True
        return meta['processed'],meta['is_image_pdf'],meta

    ## Check nothing currently processing
    base_case_processing_storage=storage_dir+BASE_REL_PROCESSING_STORAGE_DIR
    if not os.path.exists(base_case_processing_storage):
        os.makedirs(base_case_processing_storage)

    for f in os.listdir(base_case_processing_storage):
        meta['is_already_processing']=True
        logging.warning("[warning] file already processing: "+f)
        return meta['processed'],meta['is_image_pdf'],meta
    
    ##/  Calculate dpi because shouldn't force if not image and <100 dpi

    ##/  Is it an image pdf?
    meta['is_image_pdf']=interface_is_image_pdf(full_filename)
    meta['dpi']=calculate_image_dpi(full_filename) #Fails on no file??
    meta['has_been_ocrd']=has_pdf_been_ocrd_already(full_filename)
    
    logging.info("[info] is_image_pdf: "+str(meta['is_image_pdf']))
    logging.info("[info] pdf image dpi: "+str(meta['dpi']))
    
    ## Logical branch
    run_ocr=logic_run_ocr_on_image_pdf(meta,force,full_filename)
        
    if run_ocr:
        if force:
            logging.info("[info] force ocr processing: "+full_filename)

        meta_process=process_pdfimage(storage_dir,pdf_filename)
        meta.update(meta_process)
        meta['processed']=True

    else:
        pass
        

    print ("[debug ocr]: "+str(meta))
        
    logging.info("[info] done ocr conversion check")

    return meta['processed'],meta['is_image_pdf'],meta



def call_process_as_pdfimage():
    raw_pdf_with_images_filepath=LOCAL_PATH+'pdf_samples/IMAGE_BASED_Chase statements 1.pdf'
    raw_pdf_with_images_filepath=LOCAL_PATH+'pdf_samples/CORRUPT_rambouillett_20210129-statements-2695.pdf'

    raw_pdf_with_images_filepath=LOCAL_PATH+"../w_ui/file_manager/storage/case_temp/CORRUPT_rambouillett_20210129-statements-2695.pdf"

    storage_dir=LOCAL_PATH+"..________________er/storage/case_temp"
    pdf_filename="CORRUPT_rambouillett_20210129-statements-2695.pdf"

    case_id='case_temp'
    
    interface_ocr_image_pdf_if_required(storage_dir,pdf_filename,force=False)


#@    if os.path.exists(raw_pdf_with_images_filepath):
#@        logging.info("[info] found raw pdf with images: "+raw_pdf_with_images_filepath)
#@        meta=process_pdfimage(case_id,raw_pdf_with_images_filepath)

    print ("[done call_process_as_pdfimage")

    print("[ ] optionally, retry any failed (still exists in processing dir")

    return


if __name__=='__main__':
    branches=['dev3']
    branches=['dev_do_process_queue']
    branches=['call_process_as_pdfimage']

    for b in branches:
        globals()[b]()


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
