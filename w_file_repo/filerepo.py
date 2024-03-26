import time
import os
import sys
import codecs
import json
import hashlib
import re
import base64
from io import BytesIO
from urllib.parse import quote_plus

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"..")
from get_logger import setup_logging
logging=setup_logging()


from w_storage.ystorage.ystorage_handler import Storage_Helper

from local_pdf2txt import local_pdf2base64_pages
from local_pdf2txt import local_pdfcontent2text_pages


Storage=Storage_Helper(storage_dir=LOCAL_PATH+"../w_datasets/pipeline")
Storage.init_db('pdfs')
Storage.init_db('pdf_pages')
Storage.init_db('pdf_texts')
Storage.init_db('pdf_security_keys')


#0v4# JC  Jan 11, 2023  urlencode words destined for href
#0v3# JC  Jan  5, 2023  top highlight words (with href safe filter)
#0v2# JC  Oct 13, 2023  Link to manage_pdfs.py for general pdf viewer tool
#0v1# JC  Sep 18, 2023  Setup


"""
FILE REPO
- pdf storage
- pdf pages storage
- pdf text storage (various inputs)
- use sqlite for now (bin64 likely)

OPTIONS:
> on-demand conversions to txt!
> on-demand pdf to pdf pages
- try to kep file storage based but pdf<>txt is very relevant

HIGHLIGHT:
- see do_highlight/highlight_new.py

"""

#
def alg_get_page_meta_realtime(full_filename='',pdf_content='',page_num=0):
    #- ok to move but relevant to page fetching
    page_text={} #method.content
    return page_text

def generate_hash(text):
    salt='saltykey123!'
    # Create a SHA-256 hash object
    sha256 = hashlib.sha256()
    # Update the hash object with the bytes-like object (text in bytes format)
    sha256.update(text.encode('utf-8')+salt.encode('utf-8'))
    # Return the hexadecimal representation of the hash
    return sha256.hexdigest()

def interface_get_security_key(case_id,filename):
    FS=File_Storage()
    security_key=FS.generate_security_key(case_id,filename)
    return security_key

class File_Storage(object):
    def __init__(self):
        return

    def is_fully_processed(self,full_filename,case_id):
        ## For now, just if page text exists
        is_proccesed=False
        pdf_key=self.generate_key(case_id,full_filename)
        page_number=1
        kkey_page=self.generate_page_key(case_id,full_filename,page_number)
        extracted_texts=self.load_pdf_texts(kkey_page)
        if extracted_texts:
            is_processed=True
            print ("[debug] fully processed cause: "+str(kkey_page)+" has: "+str(extracted_texts))
        return is_processed
    
    def generate_security_key(self,case_id,full_filename):
        filename=os.path.basename(full_filename)
        text=case_id+"-"+filename
        return generate_hash(text)

    def full_process_pdf(self,full_filename,case_id,check_if_exists=False):
        ## Raw pdf to pdf page content to text
        #- ideally not within here but ok stand-alone since common tasks
        if check_if_exists:
            raise Exception("Not implemented yet")
        
        logging.info("[starting full_process_pdf]: "+str(full_filename))

        meta={}
        status='started'
        if not os.path.exists(full_filename):
            logging.warning("[full_process_pdf] file not found: "+str(full_filename))
            status='missing'
            return status,meta

        ## STORE FULL PDF
        pdf_key=self.generate_key(case_id,full_filename)
        security_key=self.generate_security_key(case_id,full_filename)

        ## Store pdf
        self.store_pdf(full_filename,kkey=pdf_key,security_key=security_key)

        ## STORE PDF PAGES
        logging.info("[debug file to pages]...")
        pdf_pages_base64=local_pdf2base64_pages(full_filename)

        ## PROCESS EACH PAGE
        logging.info("[debug pages to text...]")
        page_number=0
        for pdf_content_base64 in pdf_pages_base64:
            page_number+=1
            print ("Convert page to text Page #"+str(page_number))
            kkey_page=self.generate_page_key(case_id,full_filename,page_number)

            pdf_content=base64.b64decode(pdf_content_base64)

            ## All content pages to text (various extract methods)
            #extracted['method']=text one page or multiple
            extracted=local_pdfcontent2text_pages(pdf_content) #results['method']=pages

            ## Store processed
            self.store_pdf_page(kkey_page,filename=full_filename,page_num=page_number,pdf_content_base64=pdf_content_base64,security_key=security_key)

            self.store_pdf_texts(kkey_page,extracted=extracted,security_key=security_key)

            status='done'
            meta['count_pages']=page_number

        logging.info("[full_process_pdf] done: "+str(full_filename)+" at page count: "+str(meta.get('count_pages',0)))
        return status,meta

    def get_page_meta_realtime(self,full_filename,case_id='',page_num=0,auto_process=True,verbose=False):
        # Auto split pdf pages
        # Auto convert pdf to text
        page_meta={}

        ## Source from storage
        ## Source from file
        ## Source from page load storage
        page_meta={}

        kkey_page=self.generate_page_key(case_id,full_filename,page_num)

        if verbose:
            logging.info("[get meta key]: "+str(kkey_page))

        ## Get text
        extracted_texts,meta=self.load_pdf_texts(kkey_page)
        if extracted_texts:
            page_meta['extracted']=extracted_texts
        elif os.path.exists(full_filename):
            ## Real-time generate
            if auto_process:
                self.full_process_pdf(full_filename,case_id)
                extracted_texts,meta=self.load_pdf_texts(kkey_page)
                if extracted_texts:
                    page_meta['extracted']=extracted_texts
        else:
            pass

        return page_meta

    def store_pdf_texts(self,kkey,extracted={},security_key=None):
        # extracted['method']=pages
        dd={}
        dd['id']=kkey
        dd['extracted']=extracted
        dd['security_key']=security_key
        Storage.db_put(kkey,'texts',dd,name='pdf_texts')

        dd={}
        dd['security_key']=security_key
        Storage.db_put(kkey,'security_key',dd,name='pdf_security_keys')
        return
    def load_pdf_texts(self,kkey):
        ## Get from file or pre-computed page
        meta={}
        extracted={}
        dd=Storage.db_get(kkey,'texts',name='pdf_texts')
        if dd:
            extracted=dd.pop('extracted',None) #extracted['method']=pages
            meta=dd
        return extracted,meta

    def store_pdf_page(self,kkey,page_num=0,filename='',pdf_content_base64='', security_key=None):
        if pdf_content_base64:
            dd={}
            dd['id']=kkey
            dd['page_num']=page_num
            dd['filename']=os.path.basename(filename)
            dd['security_key']=security_key

            dd['pdf_content_base64']=pdf_content_base64
            Storage.db_put(kkey,'pdf_page',dd,name='pdf_pages')

            dd={}
            dd['security_key']=security_key
            Storage.db_put(kkey,'security_key',dd,name='pdf_security_keys')
        return

    def load_pdf_page(self,case_id,full_filename,page_num):
        meta={}
        fp=None
        ## Get from file or pre-computed page
        filename=os.path.basename(full_filename)
        
        kkey_page=self.generate_page_key(case_id,filename,page_num)

        dd=Storage.db_get(kkey_page,'pdf_page',name='pdf_pages')
        
        ## No page cache so local auto generate and try again [ ] 
        if not dd:
            print ("[warning] page not found! (auto try to generate)")
            print ("[dev] try auto generating real-time")
            status,meta=self.full_process_pdf(full_filename,case_id,check_if_exists=False)
            count_pages=meta.get('count_page',0)
            print ("{gen status}: "+str(status)+" and: "+str(meta))

            dd=Storage.db_get(kkey_page,'pdf_page',name='pdf_pages')
        
        if dd:
            security_key=dd.get('security_key',None)

            pdf_content_bytes = base64.b64decode(dd['pdf_content_base64'])
            fp = BytesIO(pdf_content_bytes)
            meta.update(dd)
            meta.pop('pdf_content_base64',None)


        ## Security key
        dd=Storage.db_get(kkey_page,'security_key',name='pdf_security_keys')
        if dd:
            meta['security_key']=dd.get('security_key',None)

        return fp,meta

    def load_all_pdf_pages(self):
        #Not as file but pages
        return
    
    def load_all_text_page_versions(self):
        ## Assume pdf2txt via various ways, load back all as text
        return

    def store_pdf(self,full_filename,kkey=None, case_id='case_default',security_key=None):
        file_size=0
        filename=os.path.basename(full_filename)

        if os.path.exists(full_filename):
            if not kkey:
                kkey=self.generate_key(case_id,filename=filename)
            file_size=Storage.add_file(kkey,full_filename,name='pdfs')

            dd={}
            dd['security_key']=security_key
            Storage.db_put(kkey,'security_key',dd,name='pdf_security_keys')

        return kkey,file_size

    def generate_key(self,case_id,full_filename='',filename=''):
        ## Just filename used (not full path) (but can still pass it)
        if full_filename:
            filename=os.path.basename(full_filename)
        kkey=case_id+"-"+filename
        return kkey

    def generate_page_key(self,case_id,full_filename,page_number):
        ## Just filename used (not full path) (but can still pass it)
        filename=os.path.basename(full_filename)
        kkey=case_id+"-"+filename+"-"+str(page_number)
        return kkey

    def load_pdf_fp(self,kkey='',case_id='',full_filename='',filename=''):
        if full_filename:
            filename=os.path.basename(full_filename)
        if not kkey and case_id and filename:
            kkey=self.generate_key(case_id,filename=filename)
        fp,meta=Storage.get_file(kkey,name='pdfs')
        
        ## Security key
        dd=Storage.db_get(kkey,'security_key',name='pdf_security_keys')
        if dd:
            meta['security_key']=dd.get('security_key',None)
        
        #fp.content
        #fp.getvalue() #io binary bytes
        return fp,meta



def dev1():
    print ("filename path to storage")

    case_id='case_dev'
    full_filename='C:/scripts-23/watchtower/Watchtower Solutions AI/Bank Statements - for Beta Testing/SGM BOA statement december 2021.pdf'
    filename=re.sub(r'.*[\\\/]','',full_filename)

    kkey=case_id+"-"+filename

    file_size=Storage.add_file(kkey,full_filename,name='pdfs')
    fp,meta=Storage.get_file(kkey,name='pdfs')
    content=fp.read()
    print ("PDF LENGTH: "+str(len(content)))

    out_filename=re.sub(r'\.pdf','_OUT.pdf',full_filename)

    new=fp=open(out_filename,'wb')
    new.write(content)
    fp.close()
    new.close()
    print ("wrote to: "+str(out_filename))

    ## WRITE PAGES?
    ## WRITE TEXT?

    return


def dev_try_large_pdf_to_stored_pages():
    #700+ pages may not load correctly??
    filename='__________________________________________________________e_manager/storage/chase_2_barcenas/Chase Statements 2.pdf'
    case_id='chase_2_barcenas'

    FS=File_Storage()
    FS.full_process_pdf(filename,case_id=case_id)

    return


def top_highlight_terms(amount,description):
    ## Highlight (see entry: general_router.py -> /pdf/ )
    # Get the 3 longest words in description
    #0v2# urlencode
    #[ ] add test
    
    ## Description sourced
    BAD_WORDS=['check','amount','description','date','reference'] #Too common in header
    lwords=[]
    for word in description.split(" "):
        
        word=quote_plus(word)
        
        ## Easy filter
        if word.lower() in BAD_WORDS:
            continue

        lwords+=[(len(word),word)]

    lwords=sorted(lwords,reverse=True)
    lwords=[tup[1] for tup in lwords[:3]]

    ## Amount sourced
    if amount:
        amount=str(amount)
        # If 2.0 --> 2.00
        amount = re.sub(r'\.([0-9])$', r'.\g<1>0', amount)
        if len(amount)>3: #longer then .23
            terms=[str(amount)]+lwords
        else:
            terms=lwords

    else:
        terms=lwords
        
    ## Remove non alpha-numeric chars from start of terms (ie/ negatives)
    terms=[re.sub(r'^[^a-zA-Z0-9]+','',term) for term in terms]

    search_strs="|".join(terms)
    return search_strs

    
def dev_url_encode_words():
    amount='2.0'
    description='This longe/est should sti(beallowed to go. 2.0'
    ss=top_highlight_terms(amount,description)
    print ("GOT: "+str(ss))

    return

if __name__=='__main__':
    branches=['dev1']
    branches=['dev_try_large_pdf_to_stored_pages']
    branches=['dev_url_encode_words']

    for b in branches:
        globals()[b]()




"""

"""
