import os
import sys
import codecs
import json
import re

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")


from get_logger import setup_logging

logging=setup_logging()

#0v1# JC  Sep 22, 2023  Init


"""
    CONVERGE + DEV AREA FOR TXT PROCESSING

"""

## Specifically adjust the transaction_description area in the text and escape double quotes so valid json
def clean_field_values(text,field='transaction_description'):
    # Expect transaction_descriptin=".....",    note comma could have " within 
    pattern = r''+str(field)+r'": "(.*?)(?=",)' #expect comma after! otherwise " inside it!
    matches = re.findall(pattern, text)

    for match in matches:
        ##[A] Escape inner double quotes
        escaped_match = match.replace('"', '\\"')

        ##[B] Escape inner slashes (single only)
        escaped_match=re.sub(r'(?<!\\)\\(?!\\)', r'\\\\', escaped_match)

        text = text.replace(field+f'": "{match}"', field+ f'": "{escaped_match}"')
    if not matches:
        print ("[dev] warning no field found: "+str(field))

    return text

def auto_clean_bad_json(blob,verbose=True):
    ## CLEAN LLM OUTPUT FOR json loading
    #* expect json is quoted

    if isinstance(blob,dict):
        return blob

    blob=blob.strip()

    #1//
    # Remove beginning until bracket (ie ignore text at start)
    try: blob=re.sub(r'^.*?([\[\{\`])',r'\1',str(blob),flags=re.DOTALL).strip()
    except: #Could fail for encoding etc, but works in most case
        pass

    #2// if line ends with " expect a comma (even if last line would be ok
    lines=[]
    for liner in re.split(r'\n',blob):
        liner=re.sub(r'\"[\s]{0,5}$','",',liner)
        lines+=[liner]
    blob='\n'.join(lines)

    #3// remove right double quotes:  ”
    blob = blob.replace('“', '\"').replace('”', '\"')

    #5/
    blob=re.sub(r'[\‘\’]',' ',blob)  #

    #6/
    blob=clean_field_values(blob)

    #7  \\" to \"
    blob=re.sub(r'\\\\\"','\\\"',blob)

    blob=blob.strip()

    return blob

def load_tests():
    tests=[]
    tests+=["""
     {"all_transactions": [
    {"transaction_description": "CHECK NavCHEQUES AL? CHASEO WITHDRAWAL/RETIRO savinggiaHoRRos [C_", "transaction_amount": 120.00, "transaction_date": "2020-06-25", "section": "Cash transactions"},
    {"transaction_description": "uros) WOSSRSOGJH4a\\" ESOGDObOLTE", "transaction_amount": 84.98, "transaction_date": "2020-06-22", "section": "Cash transactions"},
    {"transaction_description": "Purchasing a Cashier's endive ayes AS dedes comprar om cirque deca, excriba el acre HH Dertaciane Aur\err Seems dl alerts", "transaction_amount": 9000.00, "transaction_date": "2020-06-29", "section": "Cash transactions"}
]}
    """]

    return tests

def dev1():
    tests=load_tests()

    c=0
    for test in tests:
        c+=1
        after_pass=False
        before_pass=False
        try:
            temp=json.loads(test)
            before_pass=True
        except: pass

        test=auto_clean_bad_json(test)
    
        try:
            temp=json.loads(test)
            after_pass=True
        except Exception as e:
            pass

        if not after_pass:
            print ("="*40)
            print ("BEFORE> "+str(test))
            print ("="*40)
            print ("AFTER> "+str(test))
            #print ("MSG: "+str(e))
            liner=str(c)+"#  Before: "+str(before_pass)+" After: "+str(after_pass)
            raise Exception("Failed to clean json: https://jsonformatter.org/json-viewer")

        liner=str(c)+"#  Before: "+str(before_pass)+" After: "+str(after_pass)
        print (liner)

    return


if __name__=='__main__':
    branches=['dev1']

    for b in branches:
        globals()[b]()


"""
"""