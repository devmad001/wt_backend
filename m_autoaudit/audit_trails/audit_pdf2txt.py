import os
import sys
import codecs
import json
import re
import time
import requests

import configparser as ConfigParser


LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")

from get_logger import setup_logging
logging=setup_logging()



#0v1# JC  Feb 28, 2023  Auto audit



"""
    AUDIT OCR
    - 


"""

def incident_pdf2txt_TD_etc():
    """
    pypdf2

        pdf2txt requires review per TD challenge or similar
        case_id: 65cd06669b6ff316a77a1d21 (file: 65cd06669b6ff316a77a1d21_d0765e38-0724-475e-97fa-e27ffc31f484.pdf)
    """
    """
    [Sample pdf2txt raw output on given pdf]
    - standard "pdf2txt lib pytables etc?"
    [Incident]:  spaces dropped  (ElectronicDeposits section difficult to understand)
    [audit logic]:  regex for Joined words as count/percent would flag this as an issue
    [resolution]:  Force OCR or swap to another pdf2txt library (though this is most stable)
    
    EndingBalance 1,323.14AverageCollectedBalance  1,438.85
    Interest EarnedThis Period 0.00
    Interest PaidYear-to-Date 0.00
    AnnualPercentageYieldEarned 0.00%
    Days in Period 31DAILY ACCOUNT ACTIVITY
    Deposits
    POSTING DATE DESCRIPTION AMOUNT
    03/12 MOBILEDEPOSIT 136.00
    03/17 MOBILEDEPOSIT 5.00
    Subtotal: 141.00
    ElectronicDeposits
    POSTING DATE DESCRIPTION AMOUNT
    03/12 DEBIT CARD CREDIT, *****30080880669,AUT 031221VISADDA REF
    AMAZONCOM AMZN COMBILL * WA138.60
    03/15 ACH DEPOSIT, PAYPALTRANSFER ****690842848 20.00
    

    [Sample ocr2pdf2txt raw output on given pdf]
    - NOTE: OCR is not perfect, but it is better than pdf2txt

    Ending Balance  1,323.14
    DAILY ACCOUNT ACTIVITY
    Deposits
    POSTING DATE DESCRIPTION AMOUNT
    03/12 MOBILE DEPOSIT 136.00
    03/17 MOBILE DEPOSIT 5.00
    Subtotal: 141.00
    Electronic Deposits
    POSTING DATE DESCRIPTION AMOUNT
    03/12 DEBIT CARD CREDIT, *****30080880669, AUT 031221 VISA DDA REF 138.60
    AMAZON COM AMZN COM BILL * WA
    03/15 ACH DEPOSIT, PAYPAL TRANSFER ****690842848 20.00

    """
    
    return

def notes_on_auto_audit_pdf2txt():
    """
    [Notes]
    CHALLENGE:
    - pdf2txt may randomly fail to parse fonts in a pdf (See TD case)
    - one way to spot this is to count the number of words LikeThis. 
    - however, pdf2txt MUST be run before this can be evaluated.
    - This can be resolved by forcing OCR prior to pdf2txt
    - This iterative audit loop can make thing very complicated -- hence this!
    
    - Future proof is to use a more stable pdf2txt library
    
    CODE FLOW CURRENTLY:
        
    RUN_sim_wt -> wt_main_pipeline
    
    sim_wt.py ->
    
       ^^some where above a few entrypoints
        modules_hub.py
            -> TASK_convert_raw_image_pdfs_to_text() ->
                --> interface_ocr_image_pdf_if_required(dir,filename,force?)
                    -> pdf_images.py
                        -> process_pdfimage()
                            -> interface_pdfocr()  (raw)

    
    **DEBUG SETUP:  a_agent/modules_hub.py -> run directly TASK_convert_raw_image_pdfs_to_text()
    #- can integrate auditor there

    """
    print (">> document this file flow back to main visio")
    

    return

if __name__=='__main__':
    branches=['incident_pdf2txt_TD_etc']
    for b in branches:
        globals()[b]()





