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
sys.path.insert(0,LOCAL_PATH+"../../")

from get_logger import setup_logging
logging=setup_logging()


from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence import DocumentIntelligenceClient #pip install azure-ai-documentintelligence

# Your provided key and endpoint
KEY = "daea17b7fe35431d9e048c854e1f3af1"
ENDPOINT = "https://eastus.api.cognitive.microsoft.com/"



#0v1# JC  Mar 18, 2023  Generic Azure OCR model


"""
    DOCUMENT INTELLIGENCE
    - (previously known as Form Recognizer - 2024 new)

"""


"""
DEV NOTES:

print ("python -m pip install azure-ai-documentintelligence")
#https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/documentintelligence/azure-ai-documentintelligence/README.md
Azure AI Document Intelligence client library for Python
Azure AI Document Intelligence (previously known as Form Recognizer) is a cloud service that uses machine learning to analyze text and structured data from your documents. It includes the following main features:

Layout - Extract content and structure (ex. words, selection marks, tables) from documents.
Document - Analyze key-value pairs in addition to general layout from documents.
Read - Read page information from documents.
Prebuilt - Extract common field values from select document types (ex. receipts, invoices, business cards, ID documents, U.S. W-2 tax documents, among others) using prebuilt models.
Custom - Build custom models from your own data to extract tailored field values in addition to general layout from documents.
Classifiers - Build custom classification models that combine layout and language features to accurately detect and identify documents you process within your application.
Add-on capabilities - Extract barcodes/QR codes, formulas, font/style, etc. or enable high resolution mode for large documents with optional parameters.
[Source code][python-di-src] | [Package (PyPI)][python-di-pypi] | [Samples][python-di-samples]
Model			v3.1
Request URL prefix			https://{your-form-recognizer-endpoint}/formrecognizer
General document			/documentModels/prebuilt-document:analyze
Layout			/documentModels/prebuilt-layout:analyze
Custom			/documentModels/{modelId}:analyze
Invoice			/documentModels/prebuilt-invoice:analyze
Receipt			/documentModels/prebuilt-receipt:analyze
ID document			/documentModels/prebuilt-idDocument:analyze
Business card			/documentModels/prebuilt-businessCard:analyze
W-2			/documentModels/prebuilt-tax.us.w2:analyze
Health insurance card			/documentModels/prebuilt-healthInsuranceCard.us:analyze
Contract			/documentModels/prebuilt-contract:analyze


"""

class DocumentIntelligence:
    def __init__(self):
        global KEY,ENDPOINT
        self.key = KEY
        # Initialize the Document Intelligence Client
        self.client= DocumentIntelligenceClient(endpoint=ENDPOINT, credential=AzureKeyCredential(KEY))
        
    def doc2txt(self,filename,page_num=0):
        with open(filename, "rb") as f:
            poller = self.client.begin_analyze_document(
                "prebuilt-layout", analyze_request=f, locale="en-US", content_type="application/octet-stream"
            )
        
        # Wait for the analysis to complete and extract the result
        print ("[debug] waiting for azure OCR result...")
        result = poller.result() #echos 200 every 5s?
        
        # Process and print the result line by line
        pages=[]
        for page in result.pages:
            content=''
            for line in page.lines:
#                print(line.content)
                content+=line.content+"\n"
            meta={}
            pages+=[(content,meta)]
        
        return pages



def dev1():
    path_to_sample_documents='image snapshot of page.jpg'
    path_to_sample_documents='aac18e37-dc9e-4343-9c73-4cebbc08c043_page_162.pdf'
    path_to_sample_documents='aac18e37-dc9e-4343-9c73-4cebbc08c043.pdf'

    sample_filename=LOCAL_PATH+path_to_sample_documents
    
    DI=DocumentIntelligence()

    start_time=time.time()
    pages=DI.pdf2txt(sample_filename)
    
    for content,meta in pages:
        try: print ("[debug] content:",content)
        except: pass
#        print ("[debug] meta:",meta)

    run_time=time.time()-start_time
    avg_time_per_page=run_time/len(pages)
    print ("[debug] time taken: "+str(run_time)+" for page count:"+str(len(pages))+" avg page time:"+str(avg_time_per_page))
    
    return



if __name__=='__main__':
    branches=['dev1']
    for b in branches:
        globals()[b]()







