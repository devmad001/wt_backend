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


#[ ] upgrade to llm

#0v2# JC  Mar 16, 2024  Use most common year >1.  Otherwise, use statement period [ ] TODO
#0v1# JC  Dec 20, 2023  Init



def alg_get_page_year(page_text,statement_date='', verbose=True):
    #[ ] migrate to llm_functions based.

    #[ ] single year is discontinued really because should be in relation to statement period
    
    ## BEWARE (Following are notes)
    #i)  suggests year from bottom of page instead of common year mentioned or statement period
    #** transaction entries are sometimes ie/ 10/26 without year soneed to cross reference!
    # OPTION 1:  from header
    # OPTION 2:  On page somewhere
    # OPTION 3:  From previous page (assuming rare that not included and not usually diff year on previous page)
    # OPTION 4:  Most common 4 digit number?

    reasons=[]
    year=None
    
    this_year=int(time.strftime("%Y"))
    
    ## (-1) Special case patch. Affinity statements poor OCR looses year --so allow default.
    ## () 01/01/22 | 01/31/22
    if not year and 'Affinity' in page_text:
        m=re.search(r'\b(\d\d)\/(\d\d)\/(\d\d)\b',page_text)
        if m:
            year=int("20"+str(m.group(3)))
            if year<=this_year:
                reasons+=['affinity common format \d\d\/\d\d\/\d\d '+str(year)]
            else:
                year=None
    
    ##########################################################
    # Normal priority
    ##########################################################
    ## (0) 2015-01-02 assume ptr sourced
    if not year and statement_date:
        m=re.search(r'\b(\d\d\d\d)\D',statement_date)
        if m:
            year=int(m.group(1))
            if year<=this_year:
                reasons+=['statement date '+str(year)]
            else:
                year=None
    
    ## (A) 01/01/22 | 01/31/22
    if not year:
        m=re.search(r'\b(\d\d)\/(\d\d)\/(\d\d)\b',page_text)
        if m:
            year=int("20"+str(m.group(3)))
            if year<=this_year:
                reasons+=['common format \d\d\/\d\d\/\d\d '+str(year)]
            else:
                year=None
    
    ## (L) Get from statement range
    ## Statement range is best place to start.
    if not year:
        #m=re.search(r'\d, (\d\d\d\d) ',page_text)
        m=re.search(r'through.{1,20}\d, (20\d\d)\b',page_text) #y21k
        if m:
            year=int(m.group(1))
            if year<=this_year:
                reasons+=[ 'common format: through....\d, 20\d\d '+str(year)]
            else:
                year=None
    
    ## (N) Common format (but may be in footer and unrelated)
    if not year:
        #m=re.search(r'\d, (\d\d\d\d) ',page_text)
        m=re.search(r'\d, (20\d\d)\b',page_text) #y21k
        if m:
            year=int(m.group(1))
            if year<=this_year:
                reasons+=[ 'common format \d, 20\d\d '+str(year)]
            else:
                year=None

    ## (M) Get most common year.
    if not year:
        #candidates=re.findall(r'\b(20\d\d)\b',page_text)  #ignores # and . in $2032.12
        candidates = re.findall(r'(?<![$#\d])(20\d\d)\b', page_text)
        #^ looks like year. not start with $ or #, and not ^ at start of line all by self.
        freq={}
        for c in candidates:
            try:
                c=int(c)
            except:
                continue
            if c>this_year: continue

            if c in freq:
                freq[c]+=1
            else:
                freq[c]=1
        if freq:
            most_common_year=max(freq, key=freq.get)
            count_most_common_year=freq[most_common_year]
            if count_most_common_year>1:
                year=most_common_year
                reasons+=['most common year '+str(year)+" mentioned "+str(count_most_common_year)+" times"]

        
    if not year: #**space not required
        # July 8,2021
        m=re.search(r'(\w+) ([\d]{1,2}),(\d\d\d\d)\b',page_text)
#D1        if verbose: print ("AT 1: "+str(m))
        if m:
            year=int(m.group(3))
            if year<=this_year:
                reasons+=['common format \w+ [\d]{1,2},\d\d\d\d '+str(year)]
            else:
                year=None
        
    if not year:
        #Format:  dd/mm/yyyy
        m=re.search(r'(\d\d)[\/\-](\d\d)[\/\-](\d\d\d\d)\b',page_text)
#D1        if verbose: print ("AT 2: "+str(m))
        if m:
            year=int(m.group(3))
            if year<=this_year:
                reasons+=['common format \d\d\/\d\d\/\d\d\d\d '+str(year)]
            else:
                year=None
            
    if not year:
        #Format:  dd/mm/yy
        m=re.search(r'(\d\d)[\/\-](\d\d)[\/\-](\d\d)\b',page_text)
#D1        if verbose: print ("AT 3: "+str(m))
        if m:
            year=int("20"+str(m.group(3)))
            
            if year<=this_year:
                reasons+=['common format \d\d\/\d\d\/\d\d '+str(year)]
            else:
                year=None
            
    ## Any 4 digits?
    if not year:
        m=re.search(r'\b(20\d\d)\b',page_text)
#D1        if verbose: print ("AT 4: "+str(m))
        if m:
            year=int(m.group(1))
            if int(year)>this_year:
                year=None
            else:
                reasons+=['Any 4 digits '+str(year)]
                
    if not year:
        # 28-Dec-22
        m=re.search(r'\b(\d\d)[\/\-]([A-Z]\w\w)[\/\-](\d\d)\b',page_text)
        # Assume year last (ie/ Wells Fargo)
        if m:
            year=int("20"+str(m.group(3)))
            if year>this_year:
                year=None

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
