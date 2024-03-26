import os
import time
import sys
import codecs
import time
import json
import re
import ast
import random

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")

from get_logger import setup_logging
logging=setup_logging()



#0v1# JC  Dec 20, 2023  Init



def alg_get_page_year(page_text,verbose=True):
    #** transaction entries are sometimes ie/ 10/26 without year soneed to cross reference!
    # OPTION 1:  from header
    # OPTION 2:  On page somewhere
    # OPTION 3:  From previous page (assuming rare that not included and not usually diff year on previous page)
    # OPTION 4:  Most common 4 digit number?

    year=None

    #m=re.search(r'\d, (\d\d\d\d) ',page_text)
    m=re.search(r'\d, (20\d\d)\b',page_text) #y21k
    if m:
        year=m.group(1)
        
    if not year: #**space not required
        # July 8,2021
        m=re.search(r'(\w+) ([\d]{1,2}),(\d\d\d\d)\b',page_text)
#D1        if verbose: print ("AT 1: "+str(m))
        if m:
            year=m.group(3)
        
    if not year:
        #Format:  dd/mm/yyyy
        m=re.search(r'(\d\d)[\/\-](\d\d)[\/\-](\d\d\d\d)\b',page_text)
#D1        if verbose: print ("AT 2: "+str(m))
        if m:
            year=m.group(3)
            
    if not year:
        #Format:  dd/mm/yy
        m=re.search(r'(\d\d)[\/\-](\d\d)[\/\-](\d\d)\b',page_text)
#D1        if verbose: print ("AT 3: "+str(m))
        if m:
            year="20"+str(m.group(3))
            
    ## Any 4 digits?
    if not year:
        m=re.search(r'\b(20\d\d)\b',page_text)
#D1        if verbose: print ("AT 4: "+str(m))
        if m:
            year=m.group(1)
            this_year=int(time.strftime("%Y"))
            if int(year)>this_year:
                year=None
                
    if not year:
        # 28-Dec-22
        m=re.search(r'\b(\d\d)[\/\-]([A-Z]\w\w)[\/\-](\d\d)\b',page_text)
        # Assume year last (ie/ Wells Fargo)
        if m:
            year="20"+str(m.group(3))

    if not year:
        year=""
        
#D2        print ("[warning]  NO YEAR FOUND DUMP: "+str(page_text))

    return year

def dev1():
    return


if __name__=='__main__':
    branches=['dev1']
    for b in branches:
        globals()[b]()
