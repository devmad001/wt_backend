import time
import os
import sys
import codecs
import json
import re
import shutil


LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"


#0v1# JC  Jan  9, 2023  Outline basic install notes




"""

STANDALONE OCR

- ocrmypdf with tesseract 5 library
- control over library allows for better testing + tuning if needed + can fix performance
- high cpu usage

Task:  Migrate to standalone OCR on cloud server  (AWS lambda or similar)

Install:
- can be tricky
- we currently use ubuntu 20.04

1)     pip install ocrmypdf
2)     tesseract (wrapped by ocrmypdf) requires LATEST trained data file (eng.traineddata)
https://github.com/tesseract-ocr/tessdata/blob/main/eng.traineddata  (22MB version -- not 4MB like Jan 2023)
ubuntu keeps it here:tessdata='/usr/local/share/tessdata'

Usage:
ocrmypdf.ocr(input_pdf, output_pdf, language='eng',rotate_pages=True, deskew=True, force_ocr=True)
- see sample pdfs

"""



"""
Google cloud vision
https://cloud.google.com/vision/docs/drag-and-drop
^^ not pdf.

"""


"""
RAW NOTES:

maybe on lambda: **5 years old.
https://github.com/chronograph-pe/lambda-OCRmyPDF


    TEST:  ./ocr_development/test_ocr.py

    OCR using ocrmypdf via tesseract 5
    - see dev_ocr.py notes
    - highly dependend on latest training data file (eng.traineddata) + various configs
    - freeze performance and add tests for future debug
    
    REF:
    https://tesseract-docs.readthedocs.io/_/downloads/en/latest/pdf/
    


  ocrmypdf.ocr(input_pdf, output_pdf, language=language,rotate_pages=True, deskew=True, force_ocr=True, jobs=jobs)

downsample option with gs

decrypt with Pdf

from pikepdf import Pdf



## ubuntu tesseract data files
if not 'nt' in os.name:
    tessdata='/usr/local/share/tessdata'
    os.environ["TESSDATA_PREFIX"] = tessdata  #osr & eng.testeddata
    if not os.path.exists(tessdata+'/eng.traineddata') or not os.path.exists(tessdata+'/osd.traineddata'):
        raise Exception("MISSING tesseract data files: "+str(tessdata))


import ocrmypdf  #pip install ocrmydf   **also above



ocrmypdf
#    sudo apt-get update
#    sudo apt-get -y install ocrmypdf python3-pip
#    pip install --user --upgrade ocrmypdf
#
#    ## WINDOWS:
#    powershell.exe   *may have already
#    choco to test
#    https://chocolatey.org/install
#
#    from powershell admin:
#    choco install python3
#    choco install --pre tesseract
#    choco install ghostscript
#    choco install pngquant (optional)


RAW OCR COMMENTS:
- tesseract 5 drops many config parameter options
- options not well documented but see dev_tess for samples
- what worked in end:
UPGRADE to latest trained data:
eng.traineddata
(22.9MB (Oct 2023) from 4.0MB (Jan 2023?))
https://github.com/tesseract-ocr/tessdata/blob/main/eng.traineddata

- validate same performance on ubuntu machine
https://tesseract-docs.readthedocs.io/_/downloads/en/latest/pdf/


 Required upgrade to tesseract. retry
#                         - see integrated test via: /w_pdf/ocr_development/test_ocr.py
 test_cor...


"""



def dev1():
    return


if __name__=='__main__':
    branches=['dev1']
    for b in branches:
        globals()[b]()


"""
"""




