import re
import sys,os
import json
import uuid
import datetime
import copy


import configparser as ConfigParser


LOCAL_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '.'))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+'../')

from filerepo import File_Storage
from w_pdf.do_highlight.highlight_new import process_highlighting

from get_logger import setup_logging
logging = setup_logging()



#0v2# JC  Dec 30, 2023  Add highlighting
#0v1# JC  Oct 13, 2023  


"""
    MANAGE PDFS (viewer)
"""

Config = ConfigParser.ConfigParser()
Config.read(LOCAL_PATH+"../w_settings.ini")
BASE_STORAGE_DIR=Config.get('files','base_storage_rel_dir')
BASE_DIRECTORY=LOCAL_PATH+"../"+BASE_STORAGE_DIR  ## BASE_STORAGE_DIR may be:  ../x/y



def iter_case_pdfs(case_id):
    global BASE_DIRECTORY
    
    pdf_directory=BASE_DIRECTORY+'/'+case_id
    
    ## Iter full filenames in directory
    for root, dirs, files in os.walk(pdf_directory):
        # yield full filename path and base filename
        for f in files:
            if re.search(r'\.pdf$',f,re.IGNORECASE):
                full_path=os.path.join(root, f)
                if not os.path.exists(full_path):
                    raise Exception("File does not exist: "+full_path)
                yield f,full_path
    return

def dev1():
    print ("Store pdf")
    print ("Store pdf pages ?exists in sqlite?")
    print ("routing lookup")
    print ("api endpoint")
    print ("list at case level")
    
    case_id='case_atm_location'
    b=['touch_pdf']
    
    if 'iter_case_pdfs' in b:
        iter_case_pdfs(case_id)
        
    if 'touch_pdf' in b:
        for filename,fpath in iter_case_pdfs(case_id):
            print ("> "+str(filename)+" "+fpath)

    return

def dev_test_pdf_content():
    case_id='case_atm_location'
    filename='07A210E6-B60D-46B6-9D40-9B3239237F05-list.pdf'
    page_num=0
    
    serve_pdf_content(case_id,filename,page_num=page_num)

    return


def fully_process_unseen_filename(case_id,full_filename='',filename=''):
    ## check if seen?
    reasons=[]
    
    if not full_filename:
        ## Assume or iter?
        full_filename=BASE_DIRECTORY+'/'+case_id+'/'+filename

    if not os.path.exists(full_filename):
        print("File does not exist: "+full_filename)
        reasons.append("File does not exist: "+full_filename)

    else:

        FS=File_Storage()
        
        b=['store pdf normal']
        b=['store pdf and pages']

        if 'store pdf normal' in b:
            ### >> Normal pdf storage
            kkey,file_size=FS.store_pdf(full_filename,case_id=case_id)
            print ("[debug] stored file size: "+str(file_size)+" "+str(kkey))
            
        elif 'store pdf and pages' in b:
            status,meta=FS.full_process_pdf(full_filename,case_id)
            #[debug] status: done [debug] meta: {'count_pages': 4}
            
        else:
            raise Exception("Unknown branch")

    return reasons

def interface_get_pdf_content(case_id,filename='',full_filename='',page_num=0,search_strs=[]):
    full_content=''
    page_content=''
    
    full_key=''
    page_key=''
    

    FS=File_Storage()
    
    ## Full document
    #i)  Try cache
    fp,meta=FS.load_pdf_fp(case_id=case_id,full_filename=filename)
    
    if fp is None:
        ## Real-time process
        
        full_filename=BASE_DIRECTORY+'/'+case_id+'/'+os.path.basename(filename)
        if not os.path.exists(full_filename):
            logging.info("[warning] no pdf found (for viewer generator): "+str(full_filename))

        FS.full_process_pdf(full_filename,case_id)
        fp,meta=FS.load_pdf_fp(case_id=case_id,full_filename=full_filename)
    
    if not fp is None:
        full_key=meta.get('security_key',None)
    
        #ii) Process as new
        full_content=fp.getvalue() #binary bytes
    
        ## Single page
        full_filename=BASE_DIRECTORY+'/'+case_id+'/'+os.path.basename(filename)
        if page_num:
            fp,meta=FS.load_pdf_page(case_id=case_id,full_filename=full_filename,page_num=page_num)

            if fp is not None:
                print ("[auto calling process for storage]")
                status,meta=FS.full_process_pdf(filename,case_id)
                logging.info("[full process pdf page count]: "+str(meta.get('count_pages',None)))

                fp,meta=FS.load_pdf_page(case_id=case_id,full_filename=full_filename,page_num=page_num)
                page_content=fp.getvalue() #binary bytes
                page_key=meta.get('security_key',None)
            else:
                logging.info("[warning] could not load fp for: "+filename)
                stopp=no_fpp
                
    if len(page_content)==0:
        logging.info("[warning no page content size found]")
        
    ## Apply highlighting
    if search_strs and len(page_content)>0:
        page_content=process_highlighting(page_content,search_strs)

    return full_content,full_key,page_content,page_key


def dev3():
    print ("Utilize filerepo storage system to cache files + pages")

    case_id='case_atm_location'
    filename='07A210E6-B60D-46B6-9D40-9B3239237F05-list.pdf'
    
    enter_at=['know case_id and filename']
    enter_at=['know case_id want all files']

    enter_at=['know case_id,filename,page_num']
    enter_at=['get all pdf content and page 1']
    
    if 'know case_id,filename,page_num' in enter_at:
        ## i)   Get file content from actual file?
        ## ii)  Get file content from cached Storage
        ## iii) Get file content from cached Storage PAGE
        ## iv)  Fully process unseen/cached file
        
        #[iv]
        fully_process_unseen_filename(case_id,filename=filename)
    
    elif 'get all pdf content and page 1' in enter_at:
        full_content,page_content=interface_get_pdf_content(case_id,filename,page_num=1)
        print ("GOT full content length: "+str(len(full_content)))
        print ("GOT single page content: "+str(len(page_content)))
        
    else:
        raise Exception("Unknown entry point")

    return

def local_content2highlighted(page_content):
    from w_pdf.do_highlight.highlight_new import process_data
    output_file='jonhigh.pdf'
    search_str=['ATM']
    search_str=['2,084.00']
    search_str=['2084.00']
    page_content=process_data(page_content,output_file,search_str)
    return page_content

def dev4():
    ## Including highlighting

    case_id='case_atm_location'
    filename='07A210E6-B60D-46B6-9D40-9B3239237F05-list.pdf'
    full_content,full_key,page_content,page_key=interface_get_pdf_content(case_id,filename,page_num=1)
    
    page_content=local_content2highlighted(page_content)
    
    return

if __name__=='__main__':
    branches=['dev1']
    branches=['dev2']
    branches=['dev3']
    branches=['dev4']
    for b in branches:
        globals()[b]()
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
