import os, sys
import time
import requests

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi import Query

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")


from a_agent.sim_wt import get_job_state
from a_agent.sim_wt import wt_main_pipeline

from z_apiengine.database import SessionLocal
from z_apiengine.services.case_service import list_all_cases

from a_query.admin_query import admin_remove_case_from_kb


from z_apiengine.services.FE_cases_page_states import admin_view_all_user_cases_page_status

from c_jobs_manager.ADMIN_mega_job import ADMIN_remove_job_from_queue
from c_jobs_manager.ADMIN_mega_job import LOCAL_add_case_request_to_job_queue
from c_jobs_manager.mega_job import interface_run_one_job_cycle
from c_jobs_manager.mega_job import Mega_Jobber


#0v1# JC Dec 29, 2023


"""
    SUPPORT FOR ADMIN  (keep functions separate -- somewhat clean)
"""



def jon_force_run_direct(case_id=''):
    pass
    #** easy_process_pdf_case()
#    from c_release.PROCESS_auto import local_process_pdf_case
#    print ("RUNNING LOCAL: "+str(case_id))
#    local_process_pdf_case(case_id=case_id)
    return
    
def dev_check_case_state(case_id=''):
#    case_id='6578e48c20668da6f77cd052' #" done" per ask 
    MJ=Mega_Jobber()
    state= MJ.get_verbose_state_of_case(case_id=case_id)
    print ("VERBOSE STATE: "+str(state))
    print ("Is anything running?: "+str(MJ.MInterface.is_background_case_processor_running()))
    return



def dev_run_page2transaction_on_local_pdf_file():
    #auto_create_test_sets
    #> pdf2subpages
    #> pdf2epages
    #run_page2transactions_test
    #test...
    
    ## STEP 1:  extract page
    steps=[]
    steps=['one page']

    steps+=['run on one file page']

    steps=['one page']
    steps=['run on one file page']
    
    output_filename='C:/scripts-23/watchtower/CASE_FILES_STORAGE/storage/6579bfd30c64027a3b9f2d3c/page89_62eac7ab-388c-4ff0-802e-65e96fedbd29.pdf'

    if 'one page' in steps:
        from b_extract.p2t_test_sets.auto_create_test_sets import pdf2subpages
        
        input_filename='C:/scripts-23/watchtower/CASE_FILES_STORAGE/storage/6579bfd30c64027a3b9f2d3c/62eac7ab-388c-4ff0-802e-65e96fedbd29.pdf'
        
        #pdf2subpages(input_filename=input_filename, output_filename=output_filename, keep_pages=[99])
        
        # p117 in wells fargo jwm raw
        input_filename='C:/scripts-23/watchtower/CASE_FILES_STORAGE/storage/colin_wells_1_odd_page/Wells Fargo JWM Raw.pdf'
        output_filename='C:/scripts-23/watchtower/CASE_FILES_STORAGE/storage/colin_wells_1_odd_page/Wells Fargo JWM Raw.pdf'

        pdf2subpages(input_filename, output_filename, keep_pages=[117])
        print ("Should have created: "+str(output_filename))
        
        #> then move to own case for running or use test thing.
        

    if 'run on one file page' in steps:
        
        output_filename='C:/scripts-23/watchtower/CASE_FILES_STORAGE/storage/colin_wells_1_odd_page/WFp117_0c5d42b4-77de-4e1a-a692-4eda74d2b894.pdf'

        print ("Run on: "+str(output_filename))

        ## Assumes 1 page
        if True:
            from b_extract.p2t_test_sets.auto_create_test_sets import run_page2transactions_test
            run_page2transactions_test(output_filename)


        ## Deals with 1 page from full doc (but a bit hacky)
        if False:
            from b_extract.p2t_test_sets.auto_create_test_sets import run_pdf2pdfpage2transactions_test
        
            filename='C:/scripts-23/watchtower/CASE_FILES_STORAGE/storage/6579bfd30c64027a3b9f2d3c/62eac7ab-388c-4ff0-802e-65e96fedbd29.pdf'

            run_pdf2pdfpage2transactions_test(filename,88)

        

    return



"""

1//
INFORMAL REFERENCES TO FUNCTIONS
~auto_sync_case_files.py
?run page2transactions given pdf")

2//
interface_run_one_job_cycle(commit=COMMIT)

3//
admin_view_all_user_cases_page_status()

4//
    if 'manual_remove_case_from_finaware_job_queue' in b:
        chadkk=eee
        case_id='6578e48c20668da6f77cd052'
        case_id='6579c53c0c64027a3b9f2f34'
        case_id='657a51719a57063d991dcd51' #<-- jon case!
        print ("Jon force remove case: "+str(case_id))
        ADMIN_remove_job_from_queue(case_id=case_id)

5//
  from mega_job import practical_fetch_next_case_from_FE_if_never_ran_before

  
"""




def dev1():
    return




if __name__ == "__main__":
    dev1()


"""
"""