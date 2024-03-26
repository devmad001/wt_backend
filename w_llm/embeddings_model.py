import time
import os
import sys
import codecs
import copy
import json
import re
import datetime


LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")


#use langchain#  import openai
#use langchain#  from openai import OpenAI

from langchain.embeddings.openai import OpenAIEmbeddings

from llm_accounts import interface_get_valid_openai_key


from get_logger import setup_logging
logging=setup_logging()


#0v2# JC Jan 10, 2024  Possible quote error
#0v1# JC Nov 27, 2023  Init
 


class Embeddings_Model:
    def __init__(self):
        apikey=interface_get_valid_openai_key()
        
        if 'openai way' in []:
            self.client=OpenAI(openai_api_key=apikey)
            self.client = OpenAI()

        self._refresh_connection()
        
        return
    
    def _refresh_connection(self):
        apikey=interface_get_valid_openai_key()
        self.embeddings = OpenAIEmbeddings(model="text-embedding-ada-002",openai_api_key=apikey)
        return
    
    def get_embedding(self,text):
        #model="text-embedding-ada-002"):
        text = text.replace("\n", " ")
        
        try:
            vector=self.embeddings.embed_query(text)  # Possible quota error
        except:
            logging.error("[embeddings_model.py] Quota error at get embeddings")
            self._refresh_connection()
            try:
                vector=self.embeddings.embed_query(text)  # Possible quota error
            except:
                vector=None
        
        if 'openai way' in []:
            vector=client.embeddings.create(input = [text], model=model)['data'][0]['embedding']
        return vector
    


def get_embedding(text, model="text-embedding-ada-002"):
   text = text.replace("\n", " ")
   return client.embeddings.create(input = [text], model=model)['data'][0]['embedding']


def dev1():
    df['ada_embedding'] = df.combined.apply(lambda x: get_embedding(x, model='text-embedding-ada-002'))
    df.to_csv('output/embedded_1k_reviews.csv', index=False)
    return

def dev2():
    EM=Embeddings_Model()
    

    text='Hello world'
    vector=EM.get_embedding(text)

    print ("Vector: ", vector)
    return




if __name__=='__main__':
    branches=['dev2']
    for b in branches:
        globals()[b]()




