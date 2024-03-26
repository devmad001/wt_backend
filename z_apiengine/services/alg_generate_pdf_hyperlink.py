import os
import sys
import codecs
import json
import re

from fastapi import FastAPI

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")

sys.path.insert(0,LOCAL_PATH+"../..")

from w_utils import am_i_on_server
from w_utils import get_base_endpoint

from w_file_repo.filerepo import interface_get_security_key
from w_file_repo.filerepo import top_highlight_terms

from get_logger import setup_logging
logging=setup_logging()


        
#0v2# JC Nov 10, 2023  Update for fastapi
#0v1# JC Oct 30, 2023  Setup


"""
    fast_main.py -> general_router -> view_pdf
    http://127.0.0.1:8008/api/v1/case/chase_3_66_5ktransfer/pdf/Chase%20Statements%203%2012.pdf?page=1&key=0da450fb3141c2097d1b60398886459aff428fe302cc3157f85d3599495fe956
    
"""


def alg_generate_transaction_hyperlink(transaction):

    ## MAP
    case_id=transaction['case_id']
    filename=transaction.get('filename','')
    page_num=transaction.get('filename_page_num','')

    if not filename:
        filename=transaction.get('Transaction_filename','')  #Try common
    if not page_num:
        page_num=transaction.get('Transaction_filename_page_num','')  #Try common
    
    if not filename:
        logging.info("[warning] no filename so no hyperlink at headers: "+str(transaction.keys()))
        return ''
    
    security_key=interface_get_security_key(case_id,filename)
    
    ## Recall, transaction headers are field based so not absolute
    amount=''
    description=''
    for k in transaction.keys():
        if 'amount' in k.lower():
            amount=transaction[k]
        if 'description' in k.lower():
            description=transaction[k]
    search_strs=top_highlight_terms(amount,description)
    
    base_url=get_base_endpoint() #core.epventures.co (or :8008)
        
#D    logging.info("[generate_pdf_hyperlink] base_url: "+str(base_url))

    if page_num:
        app_url=base_url+"/api/v1/case/"+case_id+"/pdf/"+filename+"?page="+str(page_num)+"&key="+str(security_key)+"&highlight="+str(search_strs)
    else:
        app_url=base_url+"/api/v1/case/"+case_id+"/pdf/"+filename+"?key="+str(security_key)+"&highlight="+str(search_strs)
        
    # Escape for url
    app_url=app_url.replace(" ","%20")
    return app_url


def dev1():
    return


if __name__=='__main__':
    branches=['dev1']
    for b in branches:
        globals()[b]()



"""
"""
