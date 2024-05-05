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


#0v1# JC  Mar  1, 2024  move comments here from pdf_images.py

"""
LOG THROUGHPUT:
- on pent, 142 pages of Chase statements 1.pdf
- 288s (4.8 minutes)  (3.2 pages per second)

"""

def dev1():
    """
        JON SUGGESTION:
        - good to have searchable pdf (for previews & general debug of quality)
        - OCRmyPDF (outputs pdf supprt tesseract)  (10k stars)

    """

    """

    PYTESSERACT
    DESKEW using pytesseract lower level or custom function
    https://medium.com/social-impact-analytics/extract-text-from-unsearchable-pdfs-for-data-analysis-using-python-a6a2ca0866dd
    op pytess.. 2:
    https://github.com/annacprice/pdf-scraper/blob/master/pdfscraper.py
    pytesseract.image_to_string()
    ** deskew, gray scale,
    Pytesseract reads the input file as an image, so opencv-python and pdf2image are included to help transfer PDF files into images. The steps will look like this:


    OPT LIBRARIES:
    - pyocr (supports tesseract)
          ^^ text layer to pdf
    - OCRmyPDF (outputs pdf supprt tesseract)  (10k starts)
          ^^ output is searchable still!
    - NO (poppler isntall required):  pdf2image
    """

    return

def INSTALL_NOTES_ocrmypdf():
    # https://ocrmypdf.readthedocs.io/en/latest/installation.html
    ## Sample flow for ocrmypdf

    ## INSTALL UBUNTU:
    # apt install ocrmypdf

    ## INSTALL UBUNTU 22 (latest)
    """
    sudo apt-get update
    sudo apt-get -y install ocrmypdf python3-pip
    pip install --user --upgrade ocrmypdf
    """

    ## WINDOWS:
    """
    powershell.exe   *may have already
    choco to test
    https://chocolatey.org/install

    from powershell admin:
    choco install python3
    choco install --pre tesseract
    choco install ghostscript
    choco install pngquant (optional)


    ********* OPTIONAL INSTALL?
    The optional dependency 'jbig2' was not found, so some image optimizations could not be attempted.
    sudo snap install jbig2enc --edge
    ; makes output smaller and less lossy

    """


    """
    import ocrmypdf

input_pdf = "path_to_input.pdf"
output_pdf = "path_to_output.pdf"

try:
    ocrmypdf.ocr(input_pdf, output_pdf, rotate_pages=True, deskew=True)
    print("OCR complete!")
except ocrmypdf.exceptions.PriorOcrFoundError:
    print("OCR layer already found in the input PDF.")
except Exception as e:
    print(f"Error: {e}")
    """

    return

def dev3():
    #ocrmypdf ref:  https://ocrmypdf.readthedocs.io/en/v10.0.1/api.html

    print ("[info] running pdf conversion...")
    pdf_with_images_filename=LOCAL_PATH+'pdf_samples/IMAGE_BASED_Chase statements 1.pdf'
    input_pdf=pdf_with_images_filename
    output_pdf=LOCAL_PATH+'pdf_samples/OUTPUT_IMAGE_BASED_Chase statements 1_OCR.pdf'

    ## Force option if some text in
    ocrmypdf.ocr(input_pdf, output_pdf, rotate_pages=True, deskew=True, force_ocr=True)
    return



if __name__=='__main__':
    branches=['call_test_run_with_test_files']
    for b in branches:
        globals()[b]()


"""
"""
