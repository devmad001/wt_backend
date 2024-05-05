import time
import os
import sys
import codecs
import json
import re
import shutil
import subprocess
import configparser as ConfigParser

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"..")


## Validate fully installed:  ubuntu tesseract data files
if not 'nt' in os.name:
    tessdata='/usr/local/share/tessdata'
    os.environ["TESSDATA_PREFIX"] = tessdata  #osr & eng.testeddata
    if not os.path.exists(tessdata+'/eng.traineddata') or not os.path.exists(tessdata+'/osd.traineddata'):
        raise Exception("MISSING tesseract data files: "+str(tessdata))

from get_logger import setup_logging
from w_storage.ystorage.ystorage_handler import Storage_Helper


from pdf2image import convert_from_path  #Rasterize pdf lib  pip install pdf2image
from PIL import Image

from pikepdf import Pdf
import ocrmypdf  #pip install ocrmydf   **also above

from pdf_dpi import calculate_image_dpi


#sudo apt install ghostscript

logging=setup_logging()


#0v6# JC  Mar 25, 2024  Global enforce upsample to 300 dpi for std OCR (esp since full cpu required is still tbd)
#0v5# JC  Mar 21, 2024  Recommend to upscale to 400 dpi for ideal rasterized OCR (tesseract) as option
#0v4# JC  Jan 13, 2024  *beware jobs=0 can freeze machine (ie/ if happens twice) [ ] check
#0v3# JC  Nov 23, 2023  decryption option
#0v2# JC  Oct 25, 2023  Down sampling option
#0v1# JC  Oct 22, 2023  OCR MODEL


"""
    TEST:  ./ocr_development/test_ocr.py

    OCR using ocrmypdf via tesseract 5
    - see dev_ocr.py notes
    - highly dependend on latest training data file (eng.traineddata) + various configs
    - freeze performance and add tests for future debug
    
    REF:
    https://tesseract-docs.readthedocs.io/_/downloads/en/latest/pdf/
"""

GLOBAL_CONFIG_DOWNSAMPLE=False
GLOBAL_CONFIG_FORCE_DOWNSAMPLE_IF_OVER=1000  #ie/ 1000dpi
GLOBAL_CONFIG_FORCE_UPSAMPLE=300


def interface_pdfocr(input_pdf,output_pdf,downsample=300,upsample=0,jobs=2):
    global GLOBAL_CONFIG_DOWNSAMPLE
    global GLOBAL_CONFIG_FORCE_UPSAMPLE
    
    #[ ] debug mar 25 until approach is refined.
    logging.info("======= [ DEV ] GLOBAL FORCE OCR upsample to: "+str(GLOBAL_CONFIG_FORCE_UPSAMPLE)+" dpi =======")
    upsample=GLOBAL_CONFIG_FORCE_UPSAMPLE

    #0v4#
    #- enter from pdf_images.py once check on whether been ocr'd and dpi

    notes=[]
    meta={}
    
    ### CHECK INPUTS

    dpi=calculate_image_dpi(input_pdf)
    logging.info("##### PDF DPI: "+str(dpi)+" ##### at: "+str(input_pdf))
    if dpi<100:
        logging.warning("[OCR DPI <100 may cause issues] *consider upsampling")
    elif dpi<300:
        logging.warning("[OCR DPI <300 may cause issues] *consider upsampling")
    elif dpi>1000:
        logging.info("[OCR DPI >1000 may be slow to process (consider downsampling to 300)")
    meta['dpi']=dpi
    
    if jobs==0 or jobs>2:
        logging.warning("[OCR jobs at 0 or >2 may cause issues]")
    
    ### DEFAULT OPTIONS
    #; jobs:  0 is max threads
    language='eng'  #Assume fixed. Will help narrow tesseract models
    
    ### PERFORMANCE THOUGHTS
    #- reduce dpi, max threads per processor, watch memory (ubuntu crashes? or pre-split pdf?)
    
    ### PRE-PROCESS:  is "encrypted"  (encryption maybe can open but not index, also, can't OCR)
    is_encrypted,did_decryption,unused_name_of_output_file=alg_decrypt_pdf(input_pdf,output_filename=input_pdf)

    if did_decryption:
        logging.info("[decrypted pdf]: "+str(input_pdf))
        
    
    start_time = time.time()
    
    #############################
    # THREE ENTRYPOINTS (upsample, downsample, normal)
    #############################
    ## Remove upsample request if already greater
    if dpi and dpi>upsample: upsample=0
    
    if upsample:
        temp_upsampled=re.sub(r'\.pdf$','_upsampled.pdf',input_pdf)
        print ("[debug] UPSAMPLING TO: "+str(upsample)+" to: "+str(temp_upsampled)+" from: "+str(dpi))
        
        rasterize_pdf(input_pdf, temp_upsampled, dpi=upsample)
        #        upsample_pdf(input_pdf, temp_upsampled, upsample) #gs ghost script won't rasterize & upscale
        meta['upsampled_to']=upsample

        input_pdf=temp_upsampled
        ocrmypdf.ocr(input_pdf, output_pdf, optimize=3, image_dpi=upsample,language=language,rotate_pages=True, deskew=True, force_ocr=True, jobs=jobs)
        
        ## Remove temp if everything looks good
        if os.path.exists(output_pdf) and os.path.exists(temp_upsampled):
            try: os.remove(temp_upsampled)
            except:pass #If opened in pdf viewer
    
    elif (downsample and GLOBAL_CONFIG_DOWNSAMPLE) or (dpi>GLOBAL_CONFIG_FORCE_DOWNSAMPLE_IF_OVER):
    
        ###################################3
        # DOWNSAMPLE
        # ie 1200 ->> 300
        # optimize==3
        temp_downsampled=re.sub(r'\.pdf$','_downsampled.pdf',input_pdf)

        downsample_pdf(input_pdf=input_pdf,output_pdf=temp_downsampled,dpi=downsample)

        if not os.path.exists(temp_downsampled):
            raise Exception("Failed to downsample pdf: "+str(input_pdf))

        input_pdf=temp_downsampled
        ocrmypdf.ocr(input_pdf, output_pdf, optimize=3, image_dpi=downsample,language=language,rotate_pages=True, deskew=True, force_ocr=True, jobs=jobs)
        
        
        ### NOTES:
        #image_dpi ony for images not .pdfs#  ocrmypdf.ocr(input_pdf, output_pdf, optimize=3, image_dpi=downsample,language=language,rotate_pages=True, deskew=True, force_ocr=True, jobs=jobs)

        meta['downsampled_to']=downsample
        
        ## Remove temp if everything looks good
        if os.path.exists(output_pdf) and os.path.exists(temp_downsampled):
            os.remove(temp_downsampled)
    else:
#        print ("** TRY psm 6 on tesseract_args to pull as single block of text...")

        #6 no diff??   ocrmypdf.ocr(input_pdf, output_pdf, language=language,rotate_pages=True, deskew=True, force_ocr=True, jobs=jobs,tesseract_config=['--psm 6'])
        #ocrmypdf.ocr(input_pdf, output_pdf, language=language,rotate_pages=True, deskew=True, force_ocr=True, jobs=jobs,tesseract_config=['--psm 4']) #4 is single column expected

        #no#        ocrmypdf.ocr(input_pdf, output_pdf, language=language,rotate_pages=True, deskew=True, force_ocr=True, jobs=jobs,tesseract_config=[LOCAL_PATH+'local_config.cfg'])
        #        ocrmypdf.ocr(input_pdf, output_pdf, language=language,rotate_pages=True, deskew=True, force_ocr=True, jobs=jobs,tesseract_config=['configfile '+LOCAL_PATH+'local_config.cfg'])

        #        print ("INPUT: "+str(input_pdf))
        #        print ("OUTPUT: "+str(output_pdf))
        #        print ("JOBS: "+str(jobs))
        """
        
        c:\Python310tk\Scripts\ocrmypdf.exe --language eng --rotate-pages --deskew --force-ocr --jobs 2 --tesseract-config C:/scripts-23/watchtower/wcodebase/w_pdf/ocr_development/local_config.cfg  "c:\scripts-23\watchtower\wcodebase\a_agent\..\..\CASE_FILES_STORAGE\storage\colin_wells_1_odd_page\processing\WFp117_0c5d42b4-77de-4e1a-a692-4eda74d2b894.pdf" "c:\scripts-23\watchtower\wcodebase\a_agent\..\..\CASE_FILES_STORAGE\storage\colin_wells_1_odd_page\WFp117_0c5d42b4-77de-4e1a-a692-4eda74d2b894.pdf"

        --tesseract-config C:/scripts-23/watchtower/wcodebase/w_pdf/ocr_development/local_config.cfg

        c:\Python310tk\Scripts\ocrmypdf.exe --language eng --rotate-pages --deskew --force-ocr --jobs 2 --tesseract-config "psm 6" "c:\scripts-23\watchtower\wcodebase\a_agent\..\..\CASE_FILES_STORAGE\storage\colin_wells_1_odd_page\processing\WFp117_0c5d42b4-77de-4e1a-a692-4eda74d2b894.pdf" "c:\scripts-23\watchtower\wcodebase\a_agent\..\..\CASE_FILES_STORAGE\storage\colin_wells_1_odd_page\WFp117_0c5d42b4-77de-4e1a-a692-4eda74d2b894.pdf"
        
        ocrmypdf --language eng --rotate-pages --deskew --force-ocr --jobs 2 --tesseract-config "psm 6" "c:\scripts-23\watchtower\wcodebase\a_agent\..\..\CASE_FILES_STORAGE\storage\colin_wells_1_odd_page\processing\WFp117_0c5d42b4-77de-4e1a-a692-4eda74d2b894.pdf" "c:\scripts-23\watchtower\wcodebase\a_agent\..\..\CASE_FILES_STORAGE\storage\colin_wells_1_odd_page\WFp117_0c5d42b4-77de-4e1a-a692-4eda74d2b894.pdf"

        """
        #        ocrmypdf.ocr(input_pdf, output_pdf, language=language,rotate_pages=True, deskew=True, force_ocr=True, jobs=jobs)
        

        try:
            ocrmypdf.ocr(input_pdf, output_pdf, language=language,rotate_pages=True, deskew=True, force_ocr=True, jobs=jobs)

        except Exception as e:
            str_e=str(e)

            logging.error("[error] at ocr: "+str_e)
            notes+=["[error] at ocr: "+str_e]
            
            if 'PDF is encrypted' in str_e:
                notes+=["[error] PDF is encrypted -- skipping OCR!"]
                shutil.copyfile(input_pdf,output_pdf)

            else:
                raise Exception("OCR failed: "+str_e) #[1] (count)  out of memory?


    meta['run_time']=time.time() - start_time
    meta['input_pdf']=input_pdf
    meta['output_pdf']=output_pdf
    meta['notes']=notes
    
    return meta



def downsample_pdf(input_pdf, output_pdf=None, dpi=300):
    #? check if already at 150?
    """
    Processes a PDF file by downsampling images, converting to grayscale, and saving the result.

    :param input_pdf: str, the path to the input PDF file
    :param output_pdf: str or None, the path to the output PDF file (can be the same as input_pdf for overwriting)
    :param dpi: int, the DPI to which images in the PDF should be downsampled
    :return: None
    """
    
    input_pdf = os.path.normpath(os.path.abspath(input_pdf))
    output_pdf = os.path.normpath(os.path.abspath(output_pdf))



    # Check if Ghostscript is installed
    if shutil.which("gs") is None:
        raise Exception("Ghostscript is not installed or not in PATH.")

    if not os.path.exists(input_pdf):
        raise FileNotFoundError(f"Input PDF file {input_pdf} does not exist.")
        
    if output_pdf is None:
        output_pdf = input_pdf

    ## OPTION 1:  writes incomplete file ...maybe color stuff??
    cmd = [
        'gs',
        '-o', output_pdf,
        '-sDEVICE=pdfwrite',
        '-dNOPAUSE',
        '-dQUIET',
        '-dSAFER',
        '-dDownsampleColorImages=true',
        f'-dColorImageResolution={dpi}',
        f'-dGrayImageResolution={dpi}',
        f'-dMonoImageResolution={dpi}',
        '-dColorImageDownsampleThreshold=1.0',
        '-dGrayImageDownsampleThreshold=1.0',
        '-dMonoImageDownsampleThreshold=1.0',
        '-sColorConversionStrategy=Gray',
        '-dProcessColorModel=/DeviceGray',
        input_pdf
    ]
    
    ## OPTION 2:  works (100 pager from 15MB to 5MB looks the same -- likely ocrs the same but faster)
    #[ ] note:  screen PDF setting likely sets to 400 even though asking 300

    cmd = [
    'gs',
    '-o', output_pdf,
    "-sDEVICE=pdfwrite",
    "-dNOPAUSE",
    "-dBATCH",
    "-sColorConversionStrategy=Gray",
    "-dProcessColorModel=/DeviceGray",
    f"-r{dpi}",
    input_pdf
    ]


    logging.info("[OCR.downsampling to: "+str(output_pdf)+"] at "+str(dpi)+" dpi")

    try:
        subprocess.run(cmd, check=True, shell=True)
    except FileNotFoundError:
        print("Error: Ghostscript is not installed or not in the system's PATH.")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while running Ghostscript: {e}")
    else:
        print("PDF processed successfully.")
        
#    ## CHECK OUTPUT
#    dpi=calculate_image_dpi(output_pdf)
#    print ("[debug] output dpi: "+str(dpi))
    
    # If size of pdf<5kb then throw error
    if os.path.exists(output_pdf):
        size=os.path.getsize(output_pdf)
        if size<5000:
            raise Exception("ERROR: Downsampled PDF is too small: "+str(size)+" bytes")

    return


def upsample_pdf(input_pdf, output_pdf=None, dpi=600):
    """
    **NOTE:  If text is already text then trying to upsample won't have the desired effect
    
    Processes a PDF file by upsampling images and saving the result.

    :param input_pdf: str, the path to the input PDF file
    :param output_pdf: str or None, the path to the output PDF file (can be the same as input_pdf for overwriting)
    :param dpi: int, the DPI to which images in the PDF should be upsampled
    :return: None
    """
    
    input_pdf = os.path.normpath(os.path.abspath(input_pdf))
    output_pdf = os.path.normpath(os.path.abspath(output_pdf if output_pdf is not None else input_pdf))

    # Check if Ghostscript is installed
    if shutil.which("gs") is None:
        raise Exception("Ghostscript is not installed or not in PATH.")

    if not os.path.exists(input_pdf):
        raise FileNotFoundError(f"Input PDF file {input_pdf} does not exist.")
        
    # Command to upsample images within the PDF
    cmd = [
        'gs',
        '-o', output_pdf,
        "-sDEVICE=pdfwrite",
        "-dNOPAUSE",
        "-dBATCH",
        f"-r{dpi}",
        input_pdf
    ]
    
    ## RASTERIZE no effect.
        #'-dDEBUG',
    cmd = [
        'gs',
        '-o', output_pdf,
        '-sDEVICE=pdfwrite',
        '-dNOPAUSE',
        '-dBATCH',
        '-dPDFSETTINGS=/prepress',  # High quality setting for prepress output
        f'-r{dpi}',  # Set your desired DPI resolution
        input_pdf
    ]

    
    ## when upscale also do greyscale
    if False: #Greyscale options work but no direct effect either
        cmd = [
        'gs',
        '-o', output_pdf,
        "-sDEVICE=pdfwrite",
        "-dNOPAUSE",
        "-dBATCH",
        "-sColorConversionStrategy=Gray",
        "-sProcessColorModel=DeviceGray",
        f"-r{dpi}",
        input_pdf
        ]


    logging.info(f"[OCR.upsampling to: {output_pdf}] at {dpi} dpi")
    print ("[debug] upsample cmd: "+str(" ".join(cmd)))

    try:
        subprocess.run(cmd, check=True)
    except FileNotFoundError:
        print("Error: Ghostscript is not installed or not in the system's PATH.")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while running Ghostscript: {e}")
    else:
        print("PDF processed successfully.")

    ## CHECK OUTPUT
    dpi_output=calculate_image_dpi(output_pdf)
    print ("[debug] output dpi: "+str(dpi_output))
    if dpi_output<dpi:
        #raise Exception("ERROR: Upsampled PDF is too small: "+str(dpi_output)+" dpi expected: "+str(dpi))
        print ("ERROR: Upsampled PDF is too small: "+str(dpi_output)+" dpi expected: "+str(dpi))
        
    # Check the output size
    if os.path.exists(output_pdf):
        size = os.path.getsize(output_pdf)
        if size < 5000:
            raise Exception(f"ERROR: Upsampled PDF is too small: {size} bytes")

    return


## DEV OPTION:
def rasterize_pdf(input_pdf_path, output_pdf_path, dpi=300):
    ## Use this rasterize for upsampling because ideally don't just want to upscale pdf text but as image!
    #- see silver_test_ocr for evaluations.  @400 better then 300. 8000 too big. 600 not bad.
    
    # Convert each page of the PDF to an image
    images = convert_from_path(input_pdf_path, dpi=dpi)

    # Save the images as a single PDF
    images[0].save(output_pdf_path, "PDF", resolution=dpi, save_all=True, append_images=images[1:])
    return


### NOTE ON ENCRYPTION:
#- ocrmypdf won't OCR an encrypted pdf.
#- encrypted pdfs can still be opened but if you go to Properties -> Security, you'll see that Content Copying is not allowed.
#- for example, won't search engine index etc
#- to remove use library pikepdf (which wraps lower level xxx)
#- see pdf/samples.

def alg_is_encrypted(filename):
    is_encrypted=False
    return

def alg_decrypt_pdf(input_filename,output_filename='',check_if_encrypted=True):
    ## Assume in-place conversion
    #input_pdf=LOCAL_PATH+"pdf_samples/ENCRYPTED_INPUT_2021-06June-statement-0823.pdf"
    #output_pdf=LOCAL_PATH+"pdf_samples/ENCRYPTED_OUTPUT_DECRYPTED_2021-06June-statement-0823.pdf"
    is_encrypted=False
    did_decryption=False
    
    if not output_filename:
        output_filename=input_filename
    
    if not os.path.exists(input_filename):
        raise Exception("File does not exist: "+str(input_filename))

    with Pdf.open(input_filename,allow_overwriting_input=True) as pdf:
        is_encrypted=pdf.is_encrypted
        if is_encrypted:
            logging.info("[file is encrypted]: "+str(input_filename))
            pdf.save(output_filename)
            did_decryption=True
        else:
            if not input_filename==output_filename:
                shutil.copyfile(input_filename,output_filename)

    return is_encrypted,did_decryption,output_filename


def dev1():
    dpi=300
    input_filename=LOCAL_PATH+"pdf_samples/ORG_IMAGE_FIRST_PAGE_Management-Properties-v-Brusko-Copy-of-First-Citizens-Bank-Checks-2020.pdf"
    output_filename=LOCAL_PATH+"pdf_samples/ORG_IMAGE_FIRST_PAGE_DOWNSAMPLED_Management-Properties-v-Brusko-Copy-of-First-Citizens-Bank-Checks-2020.pdf"

    print ("DOWNSAMPLING TO: "+str(dpi)+" to: "+str(output_filename))
    downsample_pdf(input_pdf=input_filename,output_pdf=output_filename,dpi=dpi)
    
    return


def upscale_pdf(input_pdf, output_pdf=None, from_dpi=72, to_dpi=150):
    """
    Processes a PDF file by upsampling images from a lower to a higher DPI, and saving the result.

    :param input_pdf: str, the path to the input PDF file
    :param output_pdf: str or None, the path to the output PDF file (can be the same as input_pdf for overwriting)
    :param from_dpi: int, the DPI from which images in the PDF should be upscaled
    :param to_dpi: int, the DPI to which images in the PDF should be upscaled
    :return: None
    """

    print ("WARNING py2pdf still sees as 72 after processing?? then ocr sees as 400?")


    input_pdf = os.path.normpath(os.path.abspath(input_pdf))
    output_pdf = os.path.normpath(os.path.abspath(output_pdf if output_pdf else input_pdf))

    # Check if Ghostscript is installed
    if shutil.which("gs") is None:
        raise Exception("Ghostscript is not installed or not in PATH.")

    if not os.path.exists(input_pdf):
        raise FileNotFoundError(f"Input PDF file {input_pdf} does not exist.")
        
    cmd = [
        'gs',
        '-o', output_pdf,
        '-sDEVICE=pdfwrite',
        '-dNOPAUSE',
        '-dQUIET',
        '-dSAFER',
        '-dPDFSETTINGS=/printer',  # Optimal setting for higher quality output
        f'-r{to_dpi}',  # Set the resolution to the desired DPI
        input_pdf
    ]

    logging.info("[OCR.upsampling to: "+str(output_pdf)+"] from "+str(from_dpi)+" dpi to "+str(to_dpi)+" dpi")

    try:
        subprocess.run(cmd, check=True, shell=True)
    except FileNotFoundError:
        print("Error: Ghostscript is not installed or not in the system's PATH.")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while running Ghostscript: {e}")
    else:
        print("PDF processed successfully.")
        
    # Check Output Size
    if os.path.exists(output_pdf):
        size = os.path.getsize(output_pdf)
        if size < 5000:  # You may adjust this threshold as needed
            raise Exception("ERROR: Upsampled PDF is too small: "+str(size)+" bytes")

    return


def dev_call_upsample():
    file_in=LOCAL_PATH+"pdf_samples/WFp117_0c5d42b4-77de-4e1a-a692-4eda74d2b894.pdf"

    file_out=LOCAL_PATH+"pdf_samples/UP150_WFp117_0c5d42b4-77de-4e1a-a692-4eda74d2b894.pdf"
    
    print ("FROM: "+str(file_in))
    print ("TO  : "+str(file_out))
    
    upscale_pdf(input_pdf=file_in,output_pdf=file_out,from_dpi=72,to_dpi=150)
    return


if __name__=='__main__':
    branches=['dev1']
    branches=['dev_call_upsample']
    for b in branches:
        globals()[b]()

"""
DPI NOTES:
    
    - [ ] check pdf beforehand??
    - oversample=1 will disable resampling (but ie/ 72 to 144 with =2 i think)
    - downsample_image=False  (to keep at native)
    - output_type='pdf', dpi=300


"""


"""
PERFORMANCE::
option 1
  optimize=3,  # Apply maximum optimization

  option 2
gs -o downsampled.pdf -sDEVICE=pdfwrite -dNOPAUSE -dQUIET -dSAFER \
  -dDownsampleColorImages=true \
  -dColorImageResolution=150 \
  -dGrayImageResolution=150 \
  -dMonoImageResolution=150 \
  -dColorImageDownsampleThreshold=1.0 \
  -dGrayImageDownsampleThreshold=1.0 \
  -dMonoImageDownsampleThreshold=1.0 \
  input.pdf


  2/
  pip install ocrmypdf-downsample

  3/  ocrmypdf.ocr(input_file, output_file, image_dpi=150)
  



"""
