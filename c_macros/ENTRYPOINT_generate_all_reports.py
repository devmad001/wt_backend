import os
import sys
import time
import codecs
import json
import re

from datetime import datetime


LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"

sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")


## Import various reports
from w_file_repo.manage_pdfs import interface_get_pdf_content
from w_ui.sim_user import interface_dump_excel
from m_reports.report_case_summary import ALG_generate_report_v1
from m_reports.report_case_summary import alg_get_filenames 
        
from get_logger import setup_logging
logging=setup_logging()


#0v1# Dec 24, 2023

"""
    REPORT PERSPECTIVE
    - assume after data all exists
    - generate all reports (assume db cached)
    - do at end of pipeline or for refresh

"""


def get_case_info(case_id):
    # case to filenames
    
    return

def CALL_generate_all_reports(case_id):
    report_list=[]
    report_list.append('case_summary_report_v1')
    report_list.append('excel_report')
    report_list.append('pdf_content')

    rp={}
    rp['case_id']=case_id
    rp['reports_startime']=time.time()
    
    if 'case_summary_report_v1' in report_list:
        ALG_generate_report_v1(case_id)
        
    ## Excel including cache?
    #> general_router -> generate_excel -> generate_excel
    #? generation date (redo or flag on if changed)
    if 'excel_report' in report_list:
        rp['excel_startime']=time.time()
        logging.info("[generating excel]")
        #no await# from z_apiengine.services.general_services import generate_excel
        #await generate_excel(case_id)
        interface_dump_excel(case_id)
        rp['excel_runtime']=time.time()-rp['excel_startime']

    ## PDF including cache?
    #> serve_pdf_content(case_id,filename,page_num) <- case -> filenames -> page 1
    #from services.general_services import serve_pdf_content
    if 'pdf_content' in report_list:
        logging.info("[generating pdf]")
        # filename=??
        filenames=alg_get_filenames(case_id)
        for filename in alg_get_filenames(case_id):
            logging.info("[generating pdf] filename: %s"%(filename))
            full_content,full_key,page_content,page_key=interface_get_pdf_content(case_id=case_id,filename=filename,page_num=1)
            if not page_content:
                logging.info("[generating pdf] no content for filename: %s"%(filename))
                
    rp['reports_runtime']=time.time()-rp['reports_startime']

    ## REPORT META
    print ("[debug] report meta: "+str(rp))
    
    ## informal time log
    # MarnerHoldingsB (4 pages):   excel 2.2s
    # colin_dec_2statements:   total 1.9s

    return


def dev1():
#    CALL_generate_all_reports('MarnerHoldingsB')
    CALL_generate_all_reports('colin_dec_2statements')

    return


if __name__=='__main__':
    branches=['dev1']
    for b in branches:
        globals()[b]()
    

