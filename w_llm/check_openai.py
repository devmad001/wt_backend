import time
import os
import sys
import codecs
import copy
import json
import re
import datetime
import hashlib
import random
import threading
import pandas as pd

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)

import langchain
from langchain.llms import OpenAI #pip install langchain
from langchain.chat_models import ChatOpenAI  #New ? timeout?

from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate, PromptTemplate
from langchain.prompts.chat import SystemMessage

import tiktoken #pip isntall tiktoken  https://github.com/openai/tiktoken

sys.path.insert(0,LOCAL_PATH+"..")

from get_logger import setup_logging
from w_admin.load_credentials import get_creds
from w_storage.ystorage.ystorage_handler import Storage_Helper

logging=setup_logging()


#0v1# JC  Jan  5, 2023  Init


"""
    openai version:
    VERSION: 0.27.5  (Nov 11)
"""

"""
USE LANGCHAIN FOR NOW
llm_portal.py

check version
print(f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")

REF:
https://github.com/langchain-ai/langchain/blob/master/libs/langchain/langchain/llms/openai.py
"""



def dev1():
    import openai
    
    
    openai.api_key = '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'

    print ("CHECKING API KEY")
    
    completion = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello!"}
        ],
        temperature=0.7,
        max_tokens=50,
        stop=None,
    )
    
    print(completion.choices[0].message)

    return



if __name__=='__main__':
    branches=['dev1']
    for b in branches:
        globals()[b]()

