import os
import sys
import json
import re
import time


LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)


#0v1# JC  Feb 28, 2023  Setup



"""
    AUDIT PLUGINS

"""

def alg_count_joined_words(blob):
    ## Metric for bad pdf2txt (likely raw pdf strange -- like TD)

    ## Joined words as artifact of bad pdf2txt  (see TD bank or similar)
    # ** related to pdf2txt tool NOT OCR
    
    # ElectronicWithdrawls   <-- Two capitalized words joined
    # PAYPALACCOUNT   <-- harder
    
    ## AUTO FIX COMMON??
    #> ends with Payout or Card or Com or Pay or...
    
    ## STATS:
    #- I suppose ok rate is < 0.00496 (which is silent pipe but td is higher)
    #- TD but only 1300 words has 7 joined so 0.0053 rate

    """
        samples (TD)
        [bad pdf2txt samples] ['LenderWe', 'BeginningBalance', 'EndingBalance', 'AverageCollected', 'EarnedThis', 'PaidYear', 'AnnualPercentage', 'YieldEarned', 'ElectronicDeposits', 'DepositOperations', 'ElectronicPayments']
        **ran again and only listed 7 samples!!
        
    """
    
    ## Normal word count  (baseline)
    words=re.findall(r'\b\w+\b',blob)
    
    ## Incident samples
    samples=[]
    samples+=re.findall(r'\b[A-Z][a-z]+[A-Z][a-z]+\b',blob)
    
    ## Manual filter
    #i)  if start with ^Mc common name
    samples=[s for s in samples if not s.startswith('Mc')]
    
    count_incidents=len(samples)

    ## Rate metric?
    if not words: words=['nowords']
    incident_rate=count_incidents/len(words)
    
    ## Verbose
    print ("[debug] joined words rate: "+str(incident_rate))

    """
            if joined_rate>0.005:
            raise Exception("Test failed too many conjoined words: "+str(tt))
       
    """
    return count_incidents,len(words),incident_rate,samples


def alg_count_comma_period_amounts(blob):
    ## Metric for OCR problem indicator of bad on commas vs periods
    
    # Intended to catch numbers with misplaced commas or periods, including smaller numbers
    # Bad examples: 23.234.00, 23,233,00, 1.234,567.89, 0,23
    # Good examples: 23,234.00, 23.233,00, 1,234,567.89, 0.23
    
    ## NOTES:
    #- less efficient but break out patterns for readability
    
    ## STATS:
    #- bad rate is: 2.6% or 141 over 5261  (silent pipe)
    
    
    ## Do incrementally
    start_time=time.time()
    
    # pattern = r'\b\d{1,3}([.,]\d{3})*([.,]\d{2})?\b'
    all_samples=re.findall(r'\b[\d\,\.]+[\,\.]\d\d\b',blob)
    if not all_samples: all_samples=['no_samples']  #divide by 0
    
    bad_samples = []

    # Pattern 1: Bad comma at dollar
    pattern1 = r'\b[\d\,\.]*\d,\d{2}\b'
    
    # Pattern 2: bad period at thousands
    pattern2 = r'\b[\d\,\.]+[\.]\d{3}[\,\.]\d{2}\b'

    # Pattern 3: bad period at millions
    pattern3 = r'\b[\d\,\.]+[\.]\d{3}[\.\,]\d{3}[\,\.]\d{2}\b'
    
    combined_pattern = f'({pattern1})|({pattern2})|({pattern3})'

    # Find matches and avoid duplicates by using a set
    bad_samples = set(re.findall(combined_pattern, blob))

    # flatten the result from a set of tuples to a set of strings
    bad_samples = {match for tup in bad_samples for match in tup if match}

    # Count incidents of bad number formats
    count_incidents = len(bad_samples)
    incident_rate=count_incidents/len(all_samples)

    bad_samples=list(set(bad_samples))
    print ("[debug] Samples of badly OCR'd amounts: ",bad_samples)
    
    run_time=time.time()-start_time
    print ("[debug] Bad amount text incident rate: "+str(incident_rate)+' over '+str(len(all_samples))+' in '+str(run_time)+' seconds')
    
    return count_incidents,incident_rate
    

def dev_alg_count_alpha_in_amounts(blob):
    ## Find alpha letters in amounts
    #- stats: only 3 within 5261 words on poor ocr
    #** don't include because seems fairly rare (but possible to swap)
    #b)  Letters within amounts   # Bad examples: 0O, 1l, 8B, 5S, 5S

    raise Exception("Not implemented because rare 3 in 5000")

    amounts_with_letters=re.findall(r'\b[A-Za-z\d]{0,3}[\,\.][A-Za-z\d]{1,3}\.[A-Za-z\d]{2}\b',blob) #Assume rarety would be max 1 char per word
    #Filter must contain at least 1 letter
    amounts_with_letters=[l for l in amounts_with_letters if any(c.isalpha() for c in l)]
    print ("check for letters in amounts (bad ocr): ",letters_in_amounts)
    return 


def alg_ocr_quality(blob,kind='bank_statement_transactions'):
    ## Metric for OCR quality
    # Intended to catch OCR quality issues
    meta={}
    
    ## OCR quality rating
    #- assume rate based on logic below
    ocr_reliability=1.0
    recommend_ocr_higher_quality=False
    
    count_bad_separators,rate_bad_separators=alg_count_comma_period_amounts(blob)
    meta['rate_bad_separators']=rate_bad_separators
    meta['count_bad_separators']=count_bad_separators

    #- bad rate is: 2.6% or 141 over 5261  (silent pipe)
    
    if rate_bad_separators>0.050:
        ocr_reliability=0.5
    elif rate_bad_separators>0.026:   #Known fairly poor
        ocr_reliability=0.7
    elif rate_bad_separators>0.018:
        ocr_reliability=0.8
    
    if ocr_reliability<0.75:
        recommend_ocr_higher_quality=True
    recommend_ocr_higher_quality=False

    return ocr_reliability,recommend_ocr_higher_quality,meta
    

if __name__=='__main__':
    branches=[]
    for b in branches:
        globals()[b]()


"""
FULL TD SAMPLE pdf file:
[debug] count_joined: 351, joined_rate: 0.007861670436983447 count_words : 44647
"""








