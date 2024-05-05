import os
import sys
import codecs
import json
import copy
import re
import time
import datetime


LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")


#0v1# JC  Mar  7, 2023  Auto schema audit


"""
    DOCUMENT EXISTING AND UPCOMMING POINTS TO AUDIT
    - any non-deterministic data
    - new controls or adjustments taken
    
    STEPs:
    - informal list   *this
    - basic audit
    - rollup status
    - conditional reroute

"""




def doc_audit_list():
    ## Informal list for now  (may not continue but a good start)
    

    ## TO VALIDATE LIST:

    dlist=[]

    #March 1, 2024
    dlist+=['OCR confidence via comma<>period rate'] #> flag now, possible conditionally reroute

    #March 7, 2024
    dlist+=['date within statement date'] #> base schema + looks bad on timeline
    dlist+=['transaction_id in llm cypher response data'] #> shivam request for s_event tool
    dlist+=['schema fix for amount normalization']   #> base schema ie/ should normalize to float (fix comma<>periods, etc)


    return




if __name__=='__main__':
    branches=['doc_audit_list']
    for b in branches:
        globals()[b]()





