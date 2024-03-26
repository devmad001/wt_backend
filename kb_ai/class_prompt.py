import os
import sys
import codecs
import json
import re
import random
from copy import deepcopy
from collections import OrderedDict

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")

from get_logger import setup_logging
logging=setup_logging()

#0v1# JC  Sep 14, 2023  Init

"""
    PROMPT
    - include extensible suggestions here based on schema
    - see b_extract/* for inspiration
"""

class A_Prompt:
    def __init__(self,name):
        self.index=name
        #Inits
        self.header=''
        self.bullets=[]
        self.examples=[]
        self.examples_string=''
        self.data=[]
        self.data_header=''

        # Givens
        self.full_doc_text=''

        self.markup_goals=[]
        return

    def note_llm_response(self,response):
        # Storage or tracking?
        return

    def set_markup_goals(self,markup_goals):
        #- unused here
        self.markup_goals=markup_goals
        return

    def set_header(self,blob):
        self.header=blob
        return

    def resolve_bullets(self,defaultb,dynamicb):
        self.bullets=defaultb+dynamicb
        return

    def note_full_doc_text(self,full_doc_text):
        self.full_doc_text=full_doc_text
        return

    def resolve_examples(self,examples_string='',default_examples=[],dynamic_examples=[]):
        ## As string
        #.examples=[] list of dicts
        #.dynamic_examples are tuples!
        #  - (   type_of_example, regex, example_dict )

        ## CHECK
        if examples_string:
            raise Exception("examples_string is dev option  Not implemented")
            self.examples_string=examples_string

        ### LOGIC ON MAX OR COMBO?


        self.examples=[]

        ## DYNAMIC
        #- A given example is used if regex against given data or document text
        if dynamic_examples:
    
            #[1] First-pass looks at target data
            print ("[dev] given dynamic example: "+str(dynamic_examples))
            for given_type,regex,example_dict in dynamic_examples:
                if given_type=='given_data' and self.data:
                   if re.search(regex,str(self.data),flags=re.I):
                       if not example_dict in self.examples:
                           self.examples.append(example_dict)
    
            #[2] Second-pass looks at source doc (or ideally page text)
            for given_type,regex,example_dict in dynamic_examples:
                if given_type=='doc_text' and self.full_doc_text:
                    if re.search(regex,self.full_doc_text,flags=re.I):
                        if not example_dict in self.examples:
                            self.examples.append(example_dict)
    
        #[3] Add dynamic examples to start! (cause may clip off)
        self.examples=self.examples+default_examples
        
        ## Ensure ids are incrmental across default + dynamic
        c=0
        for example in self.examples:
            c+=1
            example['id']=str(c)

        return

    def include_data(self,data):
        #** recall, data may be filtered to field specifics by schemas/schema_transaction_type_method or similar
        self.data=data
        return

    def set_data_header(self,data_header):
        self.data_header=data_header
        return

    def dump_prompt(self):
        MAX_EXAMPLES=6 # 8 is too many. 5 is good.  clip at 6

        print ("[class_prompt.py] DUMMY OUTLINE")
        prompt=''
        prompt+=self.header

#        prompt+='\n'
#        prompt+='Bullets:\n'
        ## Insert '\n' if last char not
        if prompt[-1]!='\n':
            prompt+='\n'

        for bullet in self.bullets:
            if not re.search(r'^[\s]{0,5}-',bullet):
                prompt+="- "+bullet+"\n"
            else:
                prompt+=bullet+"\n"
#        prompt+='\n'



        prompt+='Example output:\n'
        if self.examples_string:
            prompt+=self.examples_string+"\n"
        else:
            if isinstance(self.examples,dict) or isinstance(self.examples,list):
                limited_examples=self.examples[:MAX_EXAMPLES]
                prompt+=json.dumps(limited_examples,indent=4)+"\n"
            else:
                for example in self.examples:
                    a=stoppp+chh
                    prompt+=str(example)+"\n"
#        prompt+='\n'

        #prompt+='Data:\n'
        prompt+=self.data_header

        ## Include data
        if isinstance(self.data,dict) or isinstance(self.data,list):
            #prompt+=json.dumps(self.data,indent=4)
            prompt+=json.dumps(self.data)+"\n"
        else:
            for d in self.data:
                prompt+='- '+d+'\n'

        prompt+='\n'
        return prompt


## MOVED TO prompt_eng.py
def get_prompt_template(prompt_name):
    ## Hard coded lookup
    Prompt=A_Prompt(prompt_name)
    #the_prompt=Prompt.dump_prompt()
    return Prompt

def dev1_prompt_dev():
    print ("USE PROMPT ENGINEER TO SET THESE VALUES...this is more basic or final validation")
    print ("Recall:  prompt contains sub_group of records")
    print ("Recall:  query may entirely fail to return json")

    ## Base template or flavor
    Prompt=get_prompt_template('dev')

    ## Assemble as required

    header=''
    data=[]

    default_bullets=[]
    dynamic_bullets=[]

    default_examples=[]
    dynamic_examples=[]

    ## HEADER (applied)
    header="""  For each bank statement transaction in the provided JSON, add the Account payer_id and receiver_id fields. The payer and receiver should be inferred from the description & section.
    - Typical payer_ids are: Credit Card, Zelle, Check Deposits, Bank Account, Online Deposit, Credit card reversal
    - Typical receiver_ids are: Cash, Business id, Bank Account
    Return the response in valid JSON format."""

    ## BULLETS (applied)
    #> default
    default_bullets=[]

    #> dynamic bullet
    sugs=get_bullet_field_suggestions(['section'],page_text)
    dynamic_bullets+=["- section field "+sugs['section']['terms_phrase']+"\n"]

    ## EXAMPLES (applied)
    examples,examples_string=programmatic_suggestions(branch=['default'],page_text=page_text,target_records={},max_overall_suggestions=6)

    ## DATA

    data_header="""
        ALL TRANSACTIONS:
        =========
        """

    Prompt.set_header(header)

    Prompt.resolve_bullets(default_bullets,dynamic_bullets)

    Prompt.set_data_header(data_header)

    Prompt.resolve_examples(examples_string=examples_string,default_examples=default_examples,dynamic_examples=dynamic_exampls)

    Prompt.include_data()

    return


def dev1():
    fields=['section']
    page_text='dummy page text'
    ie_lines=get_bullet_field_suggestions(fields,page_text)
    return

if __name__=='__main__':
    branches=['dev1_prompt_dev']
    branches=['dev2_prompt_dev_entity']
    for b in branches:
        globals()[b]()
