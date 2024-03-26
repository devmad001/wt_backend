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

from w_mindstate.mindstate import Mindstate


from w_ui.sim_user import interface_dump_excel
from w_file_repo.manage_pdfs import interface_get_pdf_content

from get_logger import setup_logging
logging=setup_logging()


        
#0v1# JC Nov  5, 2023  Setup


"""
    GENERAL SERVICES
"""


#def local_load_multimodal(case_id):
#    ## Can access via api or module
#    Mind=Mindstate()
#    sesh,session_id,is_created=Mind.start_or_load_session(case_id=case_id)
#    answer_dict=Mind.get_field(session_id,'last_answer_meta')
#    return Mind,session_id,answer_dict
    

async def generate_excel(case_id):
    ## ORG:  x_components/serve_ui_flask.py 
    rr={}

    if True:
        try:
            rr['full_filename'], rr['case_filename'] = interface_dump_excel(case_id=case_id)
        except Exception as e:
            logging.error("[ERROR CREATING EXCEL] "+str(e))
            rr['error'] = str(e)
    return rr


async def serve_pdf_content(case_id,filename,page_num,search_strs=[]):
    #; search_strs for highlighting
    return interface_get_pdf_content(case_id=case_id,filename=filename,page_num=page_num, search_strs=search_strs)


if __name__=='__main__':
    branches=['dev1']
    for b in branches:
        globals()[b]()


"""
"""