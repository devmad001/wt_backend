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

#from get_logger import setup_logging
#logging=setup_logging()


#0v1# JC  Dec 19, 2023  PaddleOCR or similar


"""
"""

#Config = ConfigParser.ConfigParser()
#Config.read(LOCAL_PATH+"../w_settings.ini")
#BASE_STORAGE_DIR=Config.get('files','base_storage_rel_dir')
#BASE_STORAGE_DIR=LOCAL_PATH+"../"+BASE_STORAGE_DIR


def dev1():
 
    ## Install notes:  try individually eventually went...
    #- pdf2image requires https://github.com/oschwartz10612/poppler-windows/releases/tag/v23.11.0-0 https://poppler.freedesktop.org/   (not pip installable)
    
    import numpy as np
    from pdf2image import convert_from_path  # pip install pdf2image paddlepaddle paddleocr
    from paddleocr import PaddleOCR, draw_ocr


    input_file=LOCAL_PATH+"../pdf_samples/WFp117_0c5d42b4-77de-4e1a-a692-4eda74d2b894.pdf"

    print ("pdf2 images...")
    images = convert_from_path(input_file)

    print ("Load model...")
    # Create an OCR model
    ocr_model = PaddleOCR(use_angle_cls=True, lang='en')
    
    print ("DO IT...")
    for i, image in enumerate(images):
        
        ## Save copy of image
        image.save(f'page_{i}.png')

        
        # Convert the PIL.Image object to a NumPy array
        np_image = np.array(image)


        # Perform OCR on the image
        result = ocr_model.ocr(np_image)
    
        # Saving or processing the result
        # Each element in the 'result' is a tuple (box, text, confidence)

        for res in result:
            # Each 'res' is a tuple, with the first element being the bounding box
            # and the second element being a tuple containing the recognized text and its confidence
            text, confidence = res[1]
            print(f"Detected text: {text}, Confidence: {confidence}")

    return


if __name__=='__main__':
    branches=['dev2']

    for b in branches:
        globals()[b]()


"""
"""




