import time
import os
import sys
import codecs
import copy
import json
import re
import datetime
import hashlib
import random
import threading
import pandas as pd

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../../")


from w_llm.llm_interfaces import OpenAILLM

from get_logger import setup_logging

logging=setup_logging()


#0v1# JC  Mar 16, 2024  Stand-alone


"""
    CONCLUSION:
    - gpt-4 would be required to catch all edge cases
    - HOWEVER, some like:  02/08 26,363,086 Business to Business ACH Debit - TX Comptroller Tax Pymt 05059764/20207
         ^suggest that an alternate OCR technology is used

    LLM Repair Text
    - from poor ocr
    -

    ADJUSTMENT NOTES:
    - larger input better if want consistent column results.
    - gpt-4 required ok but when throws in random zero what to do?
        02/08 26,363,086 Business to Business ACH Debit - TX Comptroller Tax Pymt 05059764/20207
    
"""


def load_sample_text():
    filename=LOCAL_PATH+"sample_poor_ocr.txt"
    content=None
    with codecs.open(filename, 'r', 'utf-8',errors='ignore') as f:
        content=f.read()
    return content

repair_prompt_1="""
    You are a data entry clerk and you have been given a document to enter into a computer system.
    The document is a bank statement and it has been scanned and the OCR is not perfect.
    You need to enter the text into the computer system making corrections to OCR errors as you go.
    Errors may include:

    Dollar format amounts with commas as decimals:
       - 26,363,06 --> 26,363.06    ; bad comma
       - 2.233.00 --> 2,233.00      ; bad period
       - 23423232 --> 234,232.32    ; missing all delimiters
       
    Beware:
    - Some amounts in the vertical column of number types may be missing , and .  Infer from context if they're currencies.
    - Don't drop trailing cents (amounts will always be 2 decimal places - never zero cents)
    - Numbers are not usually dropped so don't infer .00  (ie/ 2000 -> 20.00 is correct. 2000 -> 2,000.00 is wrong)
    
    Watch for commonly swapped OCR characters:
    - 0 and O
    - 1 and I
    - 5 and S
    - 8 and B
    - 2 and Z
    - 6 and G
    - 9 and q
    - 7 and T
    - 3 and E
    - 4 and A
    - 0 and D
    - 1 and L
    - f and t

    
    Do NOT return json. Return the text in the same form.

    The text is as follows:

    """

# no still 4000 -> 4000.00
repair_prompt_2_just_numbers="""
    You are a data entry clerk and have been given a bank statement document that has been scanned and the OCR is not perfect.
    You need to enter the text into the computer system making corrections to OCR errors as you go.

    Errors in the dollar format amounts may include:
       - 26,363,06 --> 26,363.06    ; bad comma
       - 2.233.00 --> 2,233.00      ; bad period
       - 23423232 --> 234,232.32    ; missing all delimiters
       
    Beware:
    - Some dollar amounts in the vertical column of number types may be missing , and . syntax
    - Don't drop trailing cents (amounts will always be 2 decimal places - never zero cents)
    - Numbers are not usually dropped so don't infer .00  (ie/ 2000 -> 20.00 is correct. 2000 -> 2,000.00 is wrong)
    
    Do NOT return json. Return the text in the same form.

    The text is as follows:

    """

repair_prompt_3_quote="""
    You are a data entry clerk you are given a document.
    Put double quotes around all dollar amounts.
    26,363,06 --> "26,363.06"
    Do NOT return json. Return the text in the same form.
    The text is as follows:

    """


"""
JC:  STILL ISSUES WITH amounts event gpt4.
- Even from prompt 1,2, experimental...still misses.  So just use 3 to FIND currencies for rule logic
- instead, consider JUST looking at numbers
"""

print ("[ ] jc, add self audit that all numbers ")

def alg_pretty_quoted_currencies(content):
    # "26,363,06" --> 26,363.06
    # "2.233.00" --> 2,233.00
    # "23423232" --> 234,232.32
    
    ## Apply rules regex
    #
    # 1) Two decimal places always ending with .\d\d
    content=re.sub(r'\"[\d\,\.]*(\d\d)\"',r'\1.\2',content) #space?

    return
        
def alg_do_content_repair(content,kind='statement'):
    liners=re.split(r'[\n\r]+',content)

    print ("LINE COUNT: "+str(len(liners)))
    
    method='quote_numbers_apply_logic'
    method='first_long'
    method='just_numbers'

    model_name='gpt-3-fast'  #** got possible with 3!
    model_name='gpt-4-fast'  # ok but still misses general edge cases
    model_name='gpt-4-slow'  # works with just numbers
    
    
    if method=='first_long':
        print ("Ok, but adds .00")
        chunk_size=len(liners)
    else:
        chunk_size=len(liners)
        #chunk_size=20

    LLM=OpenAILLM(model_name=model_name)
   
    ## Split into chunks of 20 lines
    content_repaired=""
    chunks=[liners[i:i + chunk_size] for i in range(0, len(liners), chunk_size)]

    for i,chunk in enumerate(chunks):
#D1        print ("CHUNK: "+str(i))
#D1        print (chunk)
        chunk="\n".join(chunk)
        
        #text_prompt=repair_prompt_2_just_numbers+chunk
        if method=='quote_numbers_apply_logic':
            text_prompt=repair_prompt_3_quote+chunk
            
        elif method=='just_numbers':
            text_prompt=repair_prompt_2_just_numbers+chunk

        elif method=='first_long':
            text_prompt=repair_prompt_1+chunk

        else:
            raise ValueError("Unknown method: "+method)
        
        ## Repair
        repaired=LLM.prompt(text_prompt)

#D1        print ("="*30)
#D1        print (repaired)

        ## Apply logic
        if method=='quote_numbers_apply_logic':
            repaired=alg_pretty_quoted_currencies(repaired)
        
        content_repaired+=repaired
        

#D1    print ("="*50)
#D1    print (content_repaired)
    return content_repaired


def interface_repair_doc(content,kind='statement'):
    content_repaired=alg_do_content_repair(content,kind)
    return content_repaired


def test_call_repair():
    content=load_sample_text()

    print ("GIVEN:"+"="*50)
    print(content)
    
    ### Sample errors seen:
    #i)  No commas or decimals so just a long string of numbers !!

    # 02/08 26,363,086 Business to Business ACH Debit - TX Comptroller Tax Pymt 05059764/20207
    # 02/09 2,059,09 Business to Business ACH Debit - Wl Dept Revenue Taxpaymnt 220208
    # 02/10 20,00 Bill Pay Xueer Zhu on-Line No Account Number on 02-10
    # 02/08 41216777 Business to Business ACH Debit -Brex Inc. Payments 220206 Brexi7WrofdwOF
    # NTE*ZZZ*BrexCard Paymenf\
            
    content=interface_repair_doc(content)

    print ("REPAIRED:"+"="*50)
    print (content)
    return

if __name__=='__main__':
    branches=['dev1']
    branches=['test_call_repair']

    for b in branches:
        globals()[b]()






