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


#0v1# JC  Jan 15, 2024  Stand-alone


"""
    DEVELOPER FUNCTIONS FOR LLM
    - 
"""






def dev1():
    
    return


def chattemplate():

    ##1/
    template = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful AI bot. Your name is {name}."),
        ("human", "Hello, how are you doing?"),
        ("ai", "I'm doing well, thanks!"),
        ("human", "{user_input}"),
    ])
    
    messages = template.format_messages(
        name="Bob",
        user_input="What is your name?"
    )
    

    ##2/
    template = ChatPromptTemplate.from_messages(
    [
        SystemMessage(
            content=(
                "You transform bank statements information into valid json responses."
            )
        ),
        HumanMessagePromptTemplate.from_template("{text}"),
    ]
    )
    
    creds=get_creds()
    llm = ChatOpenAI(model_name='gpt-4', openai_api_key=creds['OPENAI_API_KEY'])
    aa=llm(template.format_messages(text='i dont like eating tasty things.'))
    
    print ("RES: "+str(aa.content))

    return


def dev_try_gptx():
    model_name='gpt-4' #ok
    model_name='gpt-4-1106-preview' #Nov 18, gpt-4 turbo

    prompt="Hello, my name is John. What is your name?"
    
    if False:
        prompt_template = PromptTemplate.from_template(prompt)

        LLML=LazyLoadLLM.get_instance(model_name=model_name)
    
        #LLML=LazyLoadLLM.get_instance(model_name='gpt-3.5-turbo')
    
        rr=LLML.prompt(prompt_template)
        print ("RES: "+str(rr))
    else:

        LLML=LazyLoadLLM.get_instance(model_name=model_name)
         #LLML=LazyLoadLLM.get_instance(model_name='gpt-3.5-turbo')

        rr=LLML.prompt(prompt)
        print ("RES: "+str(rr))

#    prompt = PromptTemplate(
#    input_variables=["question","context"],
#    template="{question} from {context}",
#)
#chain=LLMChain(llm=ChatOpenAI(openai_api_key=openai.api_key,temperature=0),prompt=prompt)

    return
    
if __name__=='__main__':
    branches=['play_chattemplate']
    for b in branches:
        globals()[b]()






"""
POSSIBLE BAD RESPONSES from standard query:
Retrying langchain.llms.openai.completion_with_retry.<locals>._completion_with_retry in 4.0 seconds as it raised APIError: HTTP code 502 from API (<html>
<head><title>502 Bad Gateway</title></head>
<body>
<center><h1>502 Bad Gateway</h1></center>
<hr><center>cloudflare</center>
</body>
</html>
).
"""

"""
py 3.8 langchain is error
import openai
import os

openai.api_key = os.getenv('OPENAI_API_KEY')

completion = openai.ChatCompletion.create(
  model = 'gpt-3.5-turbo',
  messages = [
    {'role': 'user', 'content': 'Hello!'}
  ],
  temperature = 0  
)

print(completion['choices'][0]['message']['content'])

"""


"""
    #PROMPT = PromptTemplate( template=tech_template, input_variables=["context", "question"])
    PROMPT = PromptTemplate( template=tech_template, input_variables=["context"])
    
    qa = RetrievalQA.from_chain_type(llm=ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0,
                                                    openai_api_key=OPENAI_API_KEY),
                                                    chain_type="stuff",
                                                    retriever=instance.as_retriever(),
                                                    chain_type_kwargs={"prompt": PROMPT})

    #query='what is the tallest mountain in the world'

    context="The playground is beside the indoor olympic sized pool at 100m in length."
    # process the input string here
    output_string = qa.run(context)

    print ("GOT: "+str(output_string)
"""

