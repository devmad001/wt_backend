import os
import sys
import codecs
import json
import uuid
import re
import random

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")

from pypher import __, Pypher
from w_storage.gstorage.gneo4j import Neo


from w_llm.llm_interfaces import LazyLoadLLM
from w_storage.ystorage.ystorage_handler import Storage_Helper

from v_questions.auto_50q import q50
from w_chatbot.wt_brains import Bot_Interface


from get_logger import setup_logging
logging=setup_logging()

Storage=Storage_Helper(storage_dir=LOCAL_PATH+"../w_datasets")
Storage.init_db('autotune')
Storage.init_db('alt_questions')


#0v1# JC  Nov 18, 2023  Top-level admin + entrypoints



"""
    {DEVELOPER TOOL}
    
    AUTO-TUNE IS USE LLMs to generate question alternatives
    - Given a basic question -> try to rewrite it
    - A "better" question will result in "any data" 

"""




def setup_autotune():
    print ("[x] llm 4.5")
    print ("[x] storage of good results")
    print ("[x] auto load good cases")
    print ("[x] auto load existing questions")
    print ("[ ] check with u_dev, v_qa, v_questions")
    retun

def get_good_cases():
    case_ids=[]
    if True:
        stmt="""MATCH (t:Transaction)
                RETURN t.case_id AS CaseID, COUNT(*) AS TransactionCount
                ORDER BY CaseID"""
        results,tx=Neo.run_stmt(stmt,tx='',parameters={})
        results=results.data() #<-- standard normalize as list too
        for record in results:
            print ("> "+str(record))
            if record['TransactionCount']>20:
                case_ids+=[record['CaseID']]
    return case_ids

def get_all_question_candidates():
    global q50
    ## Source from root questions or already variations
    questions=q50
    return questions

def dev1():
    global Storage
    
    if 'check 4.5' in []:
        print ("LLM 4.5")
        LLM4=LazyLoadLLM.get_instance(model_name='gpt-4')
        LLM45=LazyLoadLLM.get_instance(model_name='gpt-4-1106-preview') #Nov 18, gpt-4 turb
        LLM35=LazyLoadLLM.get_instance(model_name='gpt-3.5-turbo')
        
    if 'get all good cases' in []:
        cases=get_good_cases()
        print ("CASES: "+str(cases))
        
    if 'local_questioning' in []:
        case_id='case_atm_location'
        question='How many transactions are there?'
        answer,answer_dict=local_answer_question(question,case_id)
        
    if True:
        case_id='case_atm_location'
        question='How many transactions are there?'
        new_question=create_question_variation(question,case_id)
        print ("ORG QUESTION: "+str(question))
        print ("NEW: "+str(new_question))

    return

stopp=dev_autotune
LLM45=LazyLoadLLM.get_instance(model_name='gpt-4-1106-preview') #Nov 18, gpt-4 turb
Bot=Bot_Interface()
def create_question_variation(question,case_id):
    global LLM45

    var_question=''
    
    prompt="""You are a fraud investigator who analyzes bank statements.
        You want to rewrite or reword a question so that it is more clear for writing a cypher query.  Some tips about how the data is organized:
        """
    ## RANDOMIZE TIPS
    tips=[]
    tips+=['The Transaction stored the amount']
    tips+=['Money flows from (sender) Entity DEBIT_FROM -> Transaction -> CREDIT_TO Entity (receiver)']
    tips+=['The Transaction.description contains most of the transaction details in free text']
    tips+=['The receiver of money is also the Payee or Receiver or CREDIT_TO Entity']
    tips+=['The Transaction has a PROCESSED_BY relationship to an Entity like an ATM']
    tips+=['PROCESSED_BY Entity like an ATM also has a latitude and longitude field']
    tips+=['Transaction.is_credit is a boolean field that indicates if the transaction is a credit or debit with respect to the main_account']
    tips+=['Try using CONTAINS against Transaction.description']



    #Include all basic cypher sample fields:
    tips+=["Sample field: Transaction.transaction_type, samples: withdrawal, deposit, other, transfer, fee, payment, book_transfer, online_payment, refund, reversal"]
    tips+=["Sample field: Transaction.transaction_method, samples: online_payment, other, check, debit_card, atm, zelle, zelle, wire_transfer, cash, book_transfer"]
    tips+=["Sample field: Transaction.is_wire_transfer, samples: True"]
    tips+=["Sample field: Transaction.is_cash_involved, samples: True"]
    tips+=["Sample field: Transaction.check_num, samples: 6164, 6164929912072900524"]
    tips+=["Sample field: Entity.account_holder_name, samples: GTA AUTO, INC., SKYVIEW CAPITAL GROUP MANAGEMENT LLC"]
    tips+=["Sample field: Entity.account_holder_address, samples: 6829 LANKERSHIM BLVD STE 116, NORTH HOLLYWOOD CA 91605, 125 BEVINGTON LN, WOODSTOCK GA 30188-5421"]
    tips+=["Sample field: Entity.type, samples: cash, individual, organization, bank, merchant, check, account, main_account, other, main_account_card"]
    tips+=["Sample field: BankStatement.opening_balance, samples: 0.00, 10277.6"]
    tips+=["Sample field: BankStatement.closing_balance, samples: 4,680.37, 4784.88"]
    tips+=["Sample field: Processor.lat, samples: 34.086756009649, 46.28693384"]
    tips+=["Sample field: Processor.type, samples: other, zelle, check, online_payment, wire_transfer, debit_card, book_transfer, cash, atm, fed_wire"]
    tips+=["Sample field: Processor.lng, samples: -84.481317021177, 6.099725"]
    tips+=["Sample field: Processor.location, samples: 12172 Highway 92, Woodstock, GA, 30188, USA, 01210, Versonnex, Auvergne-Rhône-Alpes, FRA"]
    
    
    tips+=["date fields are formatted: 2021-12-31"]
    tips+=["do not assume specific dates (unless told), use ordering & grouping instead"]
    tips+=["assume that 'for the time period' means: for all dates.  Don't use undefined variables"]
    tips+=['    tips+=["Funds flow from Entity aka "Payor" or "Sender" -- DEBIT_FROM --> Transaction -- CREDIT_TO --> Entity aka "Payee" or "Receiver" or "Payment to"']
    tips+=["A 'wire transfer' will have (multiple ORs):  Transaction.is_wire_transfer=True  OR  Transaction.transaction_method IN (ie) ['wire transfer', 'ach','ach transfer', 'zelle', 'paypal', 'venmo', 'cash app', 'swift', 'sepa', 'western union', 'moneygram', 'revolut', 'wise', 'cryptocurrency transfer'] etc."]
    tips+=['Relationship properties are the following: [{"type": "DEBIT_FROM", "properties": [{"property": "date", "type": "STRING"}, {"property": "amount", "type": "STRING"}]}, {"type": "CREDIT_TO", "properties": [{"property": "date", "type": "STRING"}, {"property": "amount", "type": "STRING"}]}, {"type": "HAS_TRANSACTION", "properties": [{"property": "transaction_date", "type": "DATE"}]}]"]']
    tips+=['Relationship are the following: ["(:Transaction)-[:PROCESSED_BY]->(:Processor)", "(:Transaction)-[:CREDIT_TO]->(:Entity)", "(:Entity)-[:DEBIT_FROM]->(:Transaction)", "(:BankStatement)-[:HAS_TRANSACTION]->(:Transaction)']

    
    random.shuffle(tips)
    
    # Select a random number of tips from 1 to n
    tips=tips[:random.randint(1,len(tips))]

    for tip in tips:
        prompt+="""\n- """+str(tip)

    ## FOCUS ON
    focuses=[]
    focuses+=['Focus on making the question simpler and more clear.']
    focuses+=['Focus on making the question more related to the schema.']
    focuses+=['Focus on making the question related more to Cypher (without using cypher)']
    focuses+=['Focus on making the question complex']
    focuses+=['Focus on making the question multi-step']
    focuses+=['Focus on making the question answerable by a Cypher query']
    
    prompt+="\n"+random.choice(focuses)+"\n"
    
    prompt+="""
        Using only english words re-write the following question:
        Question: """+question+"""
        Rewritten Question:
    """

    print ("PROMPT: "+str(prompt))
    answer=LLM45.prompt(prompt)
    
    var_question=answer

    return var_question

def run_autotune():
    global Bot

    ## Load base
    cases=get_good_cases()
    questions=get_all_question_candidates()
    
    running=True
    c=0
    better=0
    while running:
        c+=1
        print ("==== LOOP #"+str(c)+" count better: "+str(better))

        case_id=random.choice(cases)
        question=random.choice(questions)
        
        ## Do regular query
        answer,answer_dict,answer_good=local_answer_question(question,case_id)

        if not answer_good:
            ## If no results re-write question
            new_question=create_question_variation(question,case_id)

            ## Do re-written query
            new_answer, new_answer_dict,new_answer_good=local_answer_question(question,case_id)

            ## If results, save question and answer
            
            if new_answer_good:
                better+=1
                print("="*30)
                print ("NEW QUESTION : "+str(new_question)+" better then: "+str(question))
                print ("RAW ANSWER: "+str(new_answer))

                dd={}
                dd['id']=uuid.uuid4().hex
                dd['case_id']=case_id
                dd['the_date']=str(datetime.datetime.now())
                dd['worse_question']=question
                dd['better_question']=new_question
                dd['answer']=new_answer
                dd['answer_dict']=new_answer_dict #BUT HAS DF!!
                
                Storage.db_put(dd['id'],'autotune',dd,name='autotune')
                
            ## Eitherway, store alt question
            dd={}
            dd['id']=new_question
            dd['alt_question']=new_question
            dd['org_question']=question
            Storage.db_put(dd['id'],'alt_questions',dd,name='alt_questions')
    
    return

def local_answer_question(question,case_id):
    global Bot
    answer_good=False

    Bot.set_case_id(case_id)
    answer,answer_dict=Bot.handle_bot_query(question)
    
    # dict_keys(['run_id', 'question', 'case_id', 'rating', 'cypher', 'llm_query_make_cypher', 'data_response', 'df', 'data_response_token_length', 'human_readible', 'llm_query_make_readable', 'run_time', 'multimodal', 'response', 'the_date'])
    
    data_length=len(answer_dict['df'])
    if data_length>0:
        answer_good=True

#    print ("RAW: "+str(answer_dict))
#    print ("RAW: "+str(answer_dict.keys()))
#    print ("Data length: "+str(data_length))

    return answer,answer_dict, answer_good


def review_autotune():
    
    print ("=== AUTO TUNE RESULTS:")
    for iid in Storage.iter_database('autotune'):
        dd=Storage.db_get(iid,'autotune')
        print ("Better Question: "+str(dd['better_question'])+" || better then: "+str(dd['worse_question']))

    print ("=== ALT QUESTIONS")
    for iid in Storage.iter_database('alt_questions'):
        dd=Storage.db_get(iid,'alt_questions')
        print ("Alt Question: "+str(dd['alt_question'])+" || org: "+str(dd['org_question']))

    print ("WHERE MOST COMMON ATTEMPTS ARE THOSE HARDEST TO ANSWER!!")
    return

def manual_try_query():
    # see also:  kb_ask/better_question
    global Bot
    case_id='case_atm_location'
    
    question='What is the Entity.id of the Payee with Payee name contains Zelle?'
    Bot.set_case_id(case_id)
    answer,answer_dict=Bot.handle_bot_query(question)
    
    print ("ASKED: "+str(question))
    print ("ANSWER: "+str(answer))
    
    return

if __name__=='__main__':
    branches=[]
    branches+=['setup_autotune']

    branches=[]
    branches+=['dev1']

    branches=[]
    branches+=['run_autotune']

    branches=[]
    branches+=['review_autotune']
    #branches+=['run_autotune']
    #branches+=['manual_try_query']

    branches=[]
    branches+=['review_autotune']

    branches=[]
    branches+=['run_autotune']


    for b in branches:
        globals()[b]()
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
