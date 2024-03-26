import time
import os
import sys
import codecs
import json
import re
import shutil
from collections import Counter

import configparser as ConfigParser

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"..")

import fitz # PyMuPDF

from get_logger import setup_logging
logging=setup_logging()


#0v1# JC  Nov  3, 2023  PDF images


"""
"""

Config = ConfigParser.ConfigParser()
Config.read(LOCAL_PATH+"../w_settings.ini")
BASE_STORAGE_DIR=Config.get('files','base_storage_rel_dir')
BASE_STORAGE_DIR=LOCAL_PATH+"../"+BASE_STORAGE_DIR

def has_pdf_been_ocrd_already(pdf_path):
    # {'format': 'PDF 1.6', 'title': '', 'author': '', 'subject': '', 'keywords': '', 'creator': 'OmniPage CSDK 18', 'producer': 'OmniPage 18', 'creationDate': "D:20230828120728-08'00'", 'modDate': '', 'trapped': '', 'encryption': None}
    has_it=False
    doc = fitz.open(pdf_path)
    # Access the metadata
    metadata = doc.metadata
    print ("[debug] PDF META: "+str(metadata))
    if 'OCR' in str(metadata): has_it=True
    if 'OmniPage' in str(metadata): has_it=True
    return has_it
    

def calculate_image_dpi(pdf_path):
    # Open the PDF
#    pdf_path='C:/scripts-23/watchtower/DEMO_SET/colin_for_dec_21/Wells Fargo JWM Raw.pdf'
    doc = fitz.open(pdf_path)
    
    # Access the metadata
    #metadata = doc.metadata
    #print ("META: "+str(metadata))
    ## {'format': 'PDF 1.6', 'title': '', 'author': '', 'subject': '', 'keywords': '', 'creator': '', 'producer': 'PyPDF2', 'creationDate': '', 'modDate': '', 'trapped': '', 'encryption': None}

    dpi_values = []

    samples=[]
    for i in range(len(doc)):
        # Iterate through each page
        page = doc[i]
        # Get list of images in the page
        image_list = page.get_images(full=True)
        
        for img_index, img in enumerate(image_list, start=1):
            xref = img[0]
            base_image = doc.extract_image(xref)
            image = base_image["image"]

            # Image width and height in pixels
            width_px = base_image["width"]
            height_px = base_image["height"]

            # Image width and height in points (1 point = 1/72 inches)
            width_pt = img[2]
            height_pt = img[3]

            # Convert points to inches
            width_in = width_pt / 72
            height_in = height_pt / 72

            # Calculate DPI
            dpi_width = width_px / width_in
            dpi_height = height_px / height_in

            dpi_values.append((dpi_width, dpi_height))
            
            samples+=[dpi_width]
            
        if len(samples)>10:
            break
            
    doc.close()
    
    ## Get most common samples value
    org_samples=samples
    samples=Counter(samples)
    samples=samples.most_common(1)
    
    try:
        samples=int(samples[0][0])
    except:
        print ("[error] Could not get DPI: "+str(org_samples))
        samples=0
    
    return samples


def dev1():
    full_path='_______________________________________________nager/storage/chase_4_a/org'
    full_path+='/Chase Statements 4.pdf'
    dpi = calculate_image_dpi(full_path)
    print ("DPI: "+str(dpi))

    return



if __name__=='__main__':
    branches=['dev1']

    for b in branches:
        globals()[b]()


"""
"""
