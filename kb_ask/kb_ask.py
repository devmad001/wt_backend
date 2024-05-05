import os
import sys
import time
import codecs
import datetime
import copy
import json
import re
import uuid
import pandas as pd


import configparser as ConfigParser

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")

from w_storage.gstorage.gneo4j import Neo
from dev_kb_ask import get_graph_schema_str
from multimodal import MultiModal_Response
from kb_router import handle_special_question_routing

from w_llm.llm_interfaces import LazyLoadLLM
from w_mindstate.mindstate import Mindstate

from w_storage.ystorage.ystorage_handler import Storage_Helper

from cypher_playground.cypher_auto import load_relevant_neo4j_samples

## More unconventional 'ideal' queries or approaches
from ideal_answer import Ideal_Answer
from kb_answer_multimodal import prepare_multimodal_insight_dict
from better_questions import Question_Guide


from get_logger import setup_logging
logging=setup_logging()


Storage=Storage_Helper(storage_dir=LOCAL_PATH+"../w_datasets")
Storage.init_db('kb_ask')


#0v9# JC  Mar  8, 2024  If cypher response is none ensure set to empty str
#0v8# JC  Jan 30, 2024  gpt-4 fix bad cypher:  cypher=re.sub(r'\|:','|',cypher)
#0v7# JC  Jan 15, 2024  Smartest LLM (gpt-4) requires template kind (bank/cypher/etc)
#0v6# JC  Nov 13, 2023  Do question similarity lookup on multiple attempt
#0v5# JC  Nov 11, 2023  multimodal_insight_dict (for barchart etc)
#0v4# JC  Nov  7, 2023  Consider ideal answer flows
#0v3# JC  Oct  6, 2023  llm4 for queries and samples included to help with cypher
#0v2# JC  Oct  3, 2023  Multi Modal (but cant normally store df)
#0v1# JC  Sep 21, 2023  Init


"""
    Ask KB questions
    - add more samples to help refine
    - watch case_id is included
"""


## Global defs
Config = ConfigParser.ConfigParser()
Config.read(LOCAL_PATH+"../w_settings.ini")
SMARTEST_MODEL_NAME=Config.get('performance','smartest_llm_name')

MAX_TOKEN_LENGTH_FOR_CYPHER_TO_SUMMARIZE=200 #600 a bit too big still, cut it to 200

##### CYPHER GENERATION NODES:
#[oct14]  cypher was assuming month = specific 2022-01-01 month (without being told) so add:
# do not assume specific dates (unless told), use ordering & grouping instead
#[oct14]  question, "for the time period" should assume the entire time period
# assume that "for the time period" means: for all dates.  Don't use undefined variables

Ideal_Answer_Global=Ideal_Answer()

def alg_insert_bullet_point(text, new_bullet):
    # 0v1#  Ensure there's a newline at the end of the new bullet
    if not new_bullet.endswith('\n'):
        new_bullet += '\n'

    # Search for the last occurrence of a bullet point
    match = list(re.finditer(r'^[ ]*\-', text, re.MULTILINE))[-1]

    # Find the end of the line where the last bullet point is
    line_end = text.find('\n', match.start())

    # Insert the new bullet point after the line of the last occurrence
    updated_text = text[:line_end+1] + '   ' + new_bullet + text[line_end+1:]
    
    return updated_text

"""

Data field samples:
Field: Transaction.transaction_method, samples: online_payment, other, check, debit_card, atm, zelle, zelle, wire_transfer, cash, book_transfer
Field: Transaction.transaction_type, samples: withdrawal, deposit, other, transfer, payment, fee, book_transfer, online_payment, refund, reversal
Field: Transaction.check_num, samples: 6164, 6164929912072900524
Field: Entity.account_holder_name, samples: GTA AUTO, INC., SKYVIEW CAPITAL GROUP MANAGEMENT LLC
Field: Entity.account_holder_address, samples: 125 BEVINGTON LN, WOODSTOCK GA 30188-5421, 6829 LANKERSHIM BLVD STE 116, NORTH HOLLYWOOD CA 91605
Field: Entity.type, samples: cash, organization, individual, bank, check, account, merchant, main_account, business, other
Field: BankStatement.opening_balance, samples: 0.00, 10277.6
Field: BankStatement.closing_balance, samples: 4,680.37, 4784.88
Field: Processor.lat, samples: 34.086756009649, 46.28693384
Field: Processor.type, samples: other, zelle, check, online_payment, wire_transfer, debit_card, book_transfer, cash, atm, fed_wire
Field: Processor.lng, samples: -84.481317021177, 6.099725
Field: Processor.location, samples: 12172 Highway 92, Woodstock, GA, 30188, USA, 01210, Versonnex, Auvergne-Rhône-Alpes, FRA
"""
#########################################################
## USEABILITY QUERIES
#Oct 17
#[A1] list all payes looks at entities (no) prefer list all transaction payes which looks at CREDIT_TO
seq_stmts=[]
seq_stmts+=['- Funds flow from Entity aka "Payor" or "Sender" -- DEBIT_FROM --> Transaction -- CREDIT_TO --> Entity aka "Payee" or "Receiver" or "Payment to"']

#[A2]  A wire transfer? is a transaction_method (suggest groups)
#?? as sample?  as core flag?
#- rather then adding is_wire_transfer field absolutely, suggest at query time
#seq_stmts+=['- A "wire transfer" would have a transaction_method like: zelle, Zelle, wire_transfer, fed_wire. or a transaction_type like: transfer.']
# WHERE Transaction.transaction_method IN ['Traditional Wire Transfer', 'ACH Transfer', 'Zelle', 'PayPal', 'Venmo', 'Cash App', 'SWIFT', 'SEPA', 'Western Union', 'MoneyGram', 'Revolut', 'Wise', 'Cryptocurrency Transfers']
seq_stmts+=["- A 'wire transfer' will have (multiple ORs):  Transaction.is_wire_transfer=True  OR  Transaction.transaction_method IN (ie) ['wire transfer', 'ach','ach transfer', 'zelle', 'paypal', 'venmo', 'cash app', 'swift', 'sepa', 'western union', 'moneygram', 'revolut', 'wise', 'cryptocurrency transfer'] etc."]


#### On retry be more lax (lower temperature)
all_tips=Ideal_Answer_Global.get_tips()  #ideal_answer.py
seq_stmts_retry=[]
#if 'regex_description' in all_tips: seq_stmts_retry+=[all_tips['regex_description']]
for item in all_tips:
    seq_stmts_retry+=[all_tips[item]]
    

## Suggest to use regex keyword search on description

#########################################################
## CYPHER GENERATION (langchain focused):
#- case_id is a must but just n. or on rel too?
#- date field cause thought other way.
#[ ] give some examples!!

CYPHER_GENERATION_TEMPLATE_WITH_SAMPLES = """Task:Generate Cypher statement to query a graph database.
Instructions:
Use only the provided relationship types and properties in the schema.
Do not use any other relationship types or properties that are not provided.
- ALWAYS filter by case_id property ie:  WHERE n.case_id = '{case_id}', Transaction.case_id = '{case_id}', Entity.case_id='{case_id}'  property filter MUST be used!
- t.is_credit=True means the main_account was credited
- date fields are formatted: 2021-12-31
- do not assume specific dates (unless told), use ordering & grouping instead
- assume that "for the time period" means: for all dates.  Don't use undefined variables
Schema:
{schema_str}

{samples_str}
Note: Do not include any explanations or apologies in your responses.
Do not respond to any questions that might ask anything else than for you to construct a Cypher statement.
Do not include any text except the generated Cypher statement.
Use descriptive variable names (Node.id rather then n.id, Transaction rather then t).
If a relationship is not needed, query the node directly.

Sample queries:
{sample_queries}

The question is:
{question}"""

####
##  Add common refinement samples
for stmt in seq_stmts: CYPHER_GENERATION_TEMPLATE_WITH_SAMPLES = alg_insert_bullet_point(CYPHER_GENERATION_TEMPLATE_WITH_SAMPLES, stmt)

#########################################################

CYPHER_GENERATION_TEMPLATE = """Task:Generate Cypher statement to query a graph database.
Instructions:
Use only the provided relationship types and properties in the schema.
Do not use any other relationship types or properties that are not provided.
- WHERE n.case_id = '{case_id}'  property filter MUST be used!
- t.is_credit=True means the main_account was credited
- date fields are formatted: 2021-12-31
- do not assume specific dates (unless told), use ordering & grouping instead
- Always use Transaction.case_id= and Entity.case_id filters
- assume that "for the time period" means: for all dates.  Don't use undefined variables
Schema:
{schema_str}
Note: Do not include any explanations or apologies in your responses.
Do not respond to any questions that might ask anything else than for you to construct a Cypher statement.
Do not include any text except the generated Cypher statement.
Use descriptive variable names (Node.id rather then n.id, Transaction rather then t).

The question is:
{question}"""
for stmt in seq_stmts: CYPHER_GENERATION_TEMPLATE = alg_insert_bullet_point(CYPHER_GENERATION_TEMPLATE, stmt)


###################################
#  RETRY NOTES TO INCLUDE:
###################################
# [ ]  a)  because it tried to use GROUP BY:
#       "GROUP BY" is NOT a cypher command (it is SQL)
#########################################################

#0v2: Include Do NOT make the same mistake...resolve error by rewriting worked

CYPHER_RETRY_GENERATION_TEMPLATE = """Task:Generate Cypher statement to query a graph database. This is a second attempt -- the first was invalid cypher.
Instructions:
You made a mistake in the cypher last time!
Use only the provided relationship types and properties in the schema.
Do not use any other relationship types or properties that are not provided.
- WHERE n.case_id = '{case_id}'  property filter MUST be used!
- t.is_credit=True means the main_account was credited
- date fields are formatted: 2021-12-31
- do not assume specific dates (unless told), use ordering & grouping instead
- Always use Transaction.case_id= and Entity.case_id filters
- assume that "for the time period" means: for all dates.  Don't use undefined variables
Schema:
{schema_str}
Note: Do not include any explanations or apologies in your responses.
Do not respond to any questions that might ask anything else than for you to construct a Cypher statement.
Do not include any text except the generated Cypher statement.
Use descriptive variable names (Node.id rather then n.id, Transaction rather then t).
The cypher response should be a single cypher query (rewrite multiples into one query)

WARNING!  Your previous attempt was not valid (or did not return data)
{invalid_cypher}

The error message was: {error_message}

Do NOT make the same mistake again! Resolve the error message by re-writing the invalid cypher.

{better_question_similarity}
The question you need to translate into cypher is:
{question}


"""

## Append special statements
for stmt in seq_stmts:
    CYPHER_RETRY_GENERATION_TEMPLATE = alg_insert_bullet_point(CYPHER_RETRY_GENERATION_TEMPLATE, stmt)

## Append special RETRY statements  (ie/ regex description)
for stmt in seq_stmts_retry:
    CYPHER_RETRY_GENERATION_TEMPLATE = alg_insert_bullet_point(CYPHER_RETRY_GENERATION_TEMPLATE, stmt)

#########################################################
CYPHER_RETRY_MULTIPLE_TIMES_GENERATION_TEMPLATE = """Task:Generate Cypher statement to query a graph database. This is a third attempt -- the first two had invalid cypher.
Instructions:
You made a mistake in the cypher last time!
Use only the provided relationship types and properties in the schema.
Do not use any other relationship types or properties that are not provided.
- WHERE n.case_id = '{case_id}'  property filter MUST be used!
- t.is_credit=True means the main_account was credited
- date fields are formatted: 2021-12-31
- do not assume specific dates (unless told), use ordering & grouping instead
- Always use Transaction.case_id= and Entity.case_id filters
- assume that "for the time period" means: for all dates.  Don't use undefined variables
Schema:
{schema_str}
Note: Do not include any explanations or apologies in your responses.
Do not respond to any questions that might ask anything else than for you to construct a Cypher statement.
Do not include any text except the generated Cypher statement.
Use descriptive variable names (Node.id rather then n.id, Transaction rather then t).
The cypher response should be a single cypher query (rewrite multiples into one query)

WARNING!  Your previous attempt was not valid:
{invalid_cypher}

The error message was: {error_message}

Do NOT make the same mistake again! Resolve the error message by re-writing the invalid cypher.
TAKE AN ENTIRELY NEW APPROACH vs. the previous cypher attempt!!  Dont make a mistake!!!

{better_question_similarity}
The question you need to translate into cypher is:
{question}


"""
for stmt in seq_stmts: CYPHER_RETRY_MULTIPLE_TIMES_GENERATION_TEMPLATE = alg_insert_bullet_point(CYPHER_RETRY_MULTIPLE_TIMES_GENERATION_TEMPLATE, stmt)




#########################################################
#########################################################
# GOOGLE FOCUSED OPTIONS:
# ** SEE BELOW!

#- Return any currency values to the nearest dollar  (13,303,072.564444)
#- Transaction amounts are in US dollars
CYPHER_QA_TEMPLATE = """You are an assistant that helps to form nice and human understandable answers.
The information part contains the provided information that you must use to construct an answer.
The provided information is authoritative, you must never doubt it or try to use your internal knowledge to correct it.
Make the answer sound as a response to the question. Do not mention that you based the result on the given information.
If the provided information is empty, say that you don't know the answer.
- Transaction amounts are in US dollars (round to the nearest dollar)
Information:
{context}

Question: {question}
Helpful Answer:"""



"""
How many transactions are over $100000?
MATCH (n:Transaction)-[:CREDIT_TO]->(:Entity)
WHERE n.case_id = 'case_schoolkids' AND toFloat(n.transaction_amount) > 100000
RETURN count(n) AS transaction_count
[AI] raw data response:
[{'transaction_count': 18}]
[debug] started llm query: 2023-09-21 17:32:30.561562 request timeout is: 180 seconds
[AI] Answer:
There are no provided transaction amounts, so I don't know the answer to your question.
"""


CYPHER_QA_TEMPLATE = """You are an assistant that helps to form nice and human understandable answers.
The information part contains the provided information that you must use to construct an answer.
The provided information is authoritative, you must never doubt it or try to use your internal knowledge to correct it.
Make the answer sound as a response to the question. Do not mention that you based the result on the given information.
If the provided information is empty, say that you don't know the answer.
- Transaction amounts are in US dollars (round to the nearest dollar)
Cypher query:
{cypher}

Cypher response:
{context}

Question: {question}
Helpful Answer:"""


def filter_raw_records():
    ## Remove unused fields (algList, filenames, etc)
    #> depends on entity type etc.

    return

def few_shot_examples(case_id=''):
    ## For harder questions or strange schema
    samples=[]
    
    ### Cash tracking is important.
    #-> cash transactions can have a source or an debit that are in cash type
    
    #** is_cash_involved is too broad because includes debit_card purchases!
    #    OR Transaction.is_cash_involved = True
    samples += [(r'cash', """
    #//no        OR (Transaction.method='debit_card' AND Transaction.is_cash_involved = True)
    // Cypher sample for total of cash transactions:
    MATCH (Transaction:Transaction {case_id: '""" + case_id + """'})
    WHERE
        (Transaction)-[:CREDIT_TO]->(:Entity {type: 'cash', case_id: '""" + case_id + """'})
        OR (Transaction)-[:DEBIT_FROM]->(:Entity {type: 'cash', case_id: '""" + case_id + """'})
        OR Transaction.method='cash'
        OR Transaction.sectiontion contains 'ATM Withdrawal'
        RETURN sum(Transaction.transaction_amount) as total_cash_transactions
    """)]

    samples+=[(r'location',"""
    // Cypher for: "Show me where the ATMs are"
    MATCH (Transaction:Transaction {case_id: 'case_atm_location', transaction_method: 'atm'})-[:PROCESSED_BY]->(Processor:Processor)
    RETURN Processor.lat as ATM_Latitude, Processor.lng as ATM_Longitude """)]
    
    ## Help guild grouping by month (without specific date range assumption)
    samples+=[(r'month',"""
    // Cypher for: "What is the total deposits and additions grouped by month?"
    MATCH (Transaction:Transaction {case_id: 'case_wells_fargo_small', transaction_type: 'deposit'})
    WITH Transaction, 
     substring(Transaction.transaction_date, 0, 4) AS year,  // Extract year
     substring(Transaction.transaction_date, 5, 2) AS month  // Extract month
    RETURN year, month, sum(Transaction.transaction_amount) as total_deposits_additions_for_the_month
    ORDER BY year, month """)]

    ## Free form payment example
    # [ ] add test at atm_locations case
    samples+=[(r'pay',"""
    // Cypher for: "Transaction payment to a specific name"
    MATCH (Transaction:Transaction {case_id: 'case_atm_location'})-[ct:CREDIT_TO]->(Payee:Entity)
    WHERE
        Transaction.case_id = 'case_atm_location'
    AND
        (Transaction.contains CONTAINS 'American Express'
         AND Transaction.transaction_type <> 'deposit'
        )
        OR
        Payee.name CONTAINS 'American Express'
        )
    RETURN Transaction, COLLECT(Payee) AS Payees
    """)]
    ##RETURN Transaction  ?? multiple
    
    ## Where transaction is processed by zelle and ends up at melissa
    samples+=[(r'zell',"""

    // Cypher for: "Transaction is processed by zelle and sent to Melissa (show me the Zelle payments to Melissa)
    MATCH (Transaction:Transaction {case_id: 'case_atm_location'})-[ct:CREDIT_TO]->(Payee:Entity)
    OPTIONAL MATCH (Transaction {case_id: 'case_atm_location'})-[:PROCESSED_BY]->(Processor)
    WHERE
        Payee.name CONTAINS 'Melissa'
        AND (
            (Processor.name IS NOT NULL AND (toLower(Processor.name) CONTAINS 'zelle'))
            OR toLower(Transaction.transaction_method) CONTAINS toLower('zelle')
        )
    RETURN Transaction, Payee, Processor """)]

    return samples


def sanitize_question(question):
    ## TOP LEVEL SCRUTINY & review
    question=re.sub(r'Zelle','zelle',question) #case_atm_location messes with transaction_method!
    return question

class KB_AI_Agent:
    ## Initially chatbot support
    #. see multimodal.py for traslation of ie/ data response to graphs or tables
    global SMARTEST_MODEL_NAME

    def __init__(self):
        self.LLM =  LazyLoadLLM.get_instance()  # Assuming LazyLoadLLM is a singleton class
        self.LLMSMART = LazyLoadLLM.get_instance(model_name=SMARTEST_MODEL_NAME)  # Assuming LazyLoadLLM is a singleton class
        self.schema_str=get_graph_schema_str()

        self.Guide=Question_Guide()
        self.Guide.preload_guides()


    def question_to_cypher(self, question,case_id, retry_dict={}):
        global CYPHER_GENERATION_TEMPLATE
        meta={}
        
        USE_SAMPLES=True

        question=sanitize_question(question)
        
        ## STANDARD QUESTION TO CYPHER

        if not retry_dict:
            if USE_SAMPLES:
                # For example:  transaction_type: ['credit', 'debit']
                all_field_samples=load_relevant_neo4j_samples()
                ## Prepare field samples
                samples_str='Data field samples:\n'
                for node_field_name in all_field_samples:
                    samples_str+='Field: '+str(node_field_name)+', samples: '
                    
                    ## Trim sample count to 3
                    if 'date' in node_field_name:
                        samples_str += ", ".join(map(str, all_field_samples[node_field_name][:3])) + "\n"
                    else:
                        samples_str += ", ".join(map(str, all_field_samples[node_field_name])) + "\n"
                        
                ## Few shot sample_queries
                sample_queries=""
                for sample in few_shot_examples(case_id=case_id):
                    sample_queries+=sample[1]+"\n"

                llm_query = CYPHER_GENERATION_TEMPLATE_WITH_SAMPLES.format(samples_str=samples_str,schema_str=self.schema_str, question=question, case_id=case_id, sample_queries=sample_queries)
#                llm_query = CYPHER_GENERATION_TEMPLATE.format(schema_str=self.schema_str, question=question, case_id=case_id)

            else:
                llm_query = CYPHER_GENERATION_TEMPLATE.format(schema_str=self.schema_str, question=question, case_id=case_id)
        else:
            ##################################
            #  RETRY WRITE CYPHER
            ##################################
            #- possibly because NO data
            
            logging.info("[retry question to cypher auto repair]")
            if retry_dict['tries']<2:

                ## Do similarity lookup for guided question {better_question_similarity}
                better_question_data,sim_value=self.Guide.search_guide(question)
                better_question=better_question_data.get('better_question','') # question|better_question|v|id|vector
                sim_stmt=''
                logging.info("[debug] better question: "+str(better_question)+" sim_value: "+str(sim_value)+" vs std question: "+str(question))
                if sim_value>0.75: # Even this a bit low tbd
                    sim_stmt="The question may be better phrased as: "+str(better_question)+"\n"

                llm_query = CYPHER_RETRY_GENERATION_TEMPLATE.format(schema_str=self.schema_str, question=question, case_id=case_id,invalid_cypher=retry_dict['bad_cypher'],error_message=retry_dict['error'],better_question_similarity=sim_stmt)

            else:
                ## Do similarity lookup for guided question {better_question_similarity}
                better_question_data,sim_value=self.Guide.search_guide(question)
                better_question=better_question_data.get('better_question','')
                sim_stmt=''
                logging.info("[debug] better question: "+str(better_question)+" sim_value: "+str(sim_value)+" vs std question: "+str(question))
                if sim_value>0.75 and better_question: # Even this a bit low tbd
                    sim_stmt="The question may be better phrased as: "+str(better_question)+"\n"

                logging.error("[retry question to cypher auto repair failed twice!]")
                llm_query = CYPHER_RETRY_MULTIPLE_TIMES_GENERATION_TEMPLATE.format(schema_str=self.schema_str, question=question, case_id=case_id,invalid_cypher=retry_dict['bad_cypher'],error_message=retry_dict['error'],better_question_similarity=sim_stmt)


        logging.info("[debug ask for question_to_cypher]: "+str(llm_query))
        
        ## EXECUTE 
        # USE gpt-4 for cypher creation?
        # LOCAL HARD CODE FOR NOW
        USE_GPT4_FOR_CYPHER_WRITING=True
        if USE_GPT4_FOR_CYPHER_WRITING:
            logging.info("[write cypher now prompting LLM4...")
            cypher = self.LLMSMART.prompt(llm_query,template_kind='cypher',verbose=True)
        else:
            cypher = self.LLM.prompt(llm_query)
        
        ## Audit or catch bad response due to over-quota?
        # if not str or bytes?
        if not isinstance(cypher, str):
            if cypher=={} or not cypher:
                cypher=''
                logging.warning("LLM response for cypher is blank!")
            else:
                logging.error("[bad response on make query]: (will fail regex below) \n"+str(cypher))
            
        ## CLEAN cypher
        cypher=self._clean_cypher(cypher)
        
        ## VALIDATE
        meta['is_valid'],meta['reasons']=self._validate_cypher(cypher,llm_query=llm_query)

        return cypher,llm_query,meta
        
    def _clean_cypher(self,cypher):
        # EXCEPTION AT RETURNED IN RECORD
        #{
        #  "query": "MATCH (Transaction:Transaction {case_id: 'case_atm_location'})-[:CREDIT_TO]->(Entity:Entity {type: 'cash'}) RETURN sum(Transaction.transaction_amount) as total_cash_transactions"
        #}
        
        ## Patch under what condition?
        try:
            cypher_oops_dict=json.loads(cypher)
            cypher=cypher_oops_dict[list(cypher_oops_dict.keys())[0]]
        except: pass

        if cypher=={} or not cypher: cypher=''
        
        ## LLM (gpt-4) was writing :
        # 0ea5bc2'})-[r:DEBIT_FROM|:CREDIT_TO]->(Entity:En
        # Instead of correctly:
        # 0ea5bc2'})-[r:DEBIT_FROM|CREDIT_TO]->(Entity:En
        cypher=re.sub(r'\|:','|',cypher)
        
        return cypher

    def _validate_cypher(self,cypher,llm_query=''):
        is_valid=True
        reasons=[]
        if not 'case_id' in cypher:
            is_valid=False
            reasons+=["cypher does not filter on parameter .case_id"] #Used as error on rewrite
            if llm_query:
                logging.warning("[bad response on make query]: \n"+str(llm_query))
            logging.warning("Cypher must include case_id: \n"+str(cypher))
            #raise Exception("Cypher must include case_id: \n"+str(cypher))
        return is_valid,reasons

    def cypher_to_data_response(self,cypher, case_id='',org_question='', allow_cached=True):
        #[ ] include label in data
        #  **allow_cached doesn't really apply here because written cypher.
        
        got_response=False
        data_response=[]
        df=pd.DataFrame() #Imported but still error?
        
        try:
            data_response,df,tx,meta=Neo.run_stmt_to_normalized(cypher,tx='')
            got_response=True
        except Exception as e:
            logging.warning("[bad cypher response] cypher: "+str(cypher)+" erro: "+str(e))
            
            retries=3
            tries=0
            while retries and not got_response:
                tries+=1

                retries-=1
                logging.info("[auto retry correct cypher]")
                retry_dict={}
                retry_dict['error']=str(e)
                retry_dict['bad_cypher']=cypher
                retry_dict['tries']=tries #If 2 then failed on retry already!
    
                new_cypher,llm_query,meta=self.question_to_cypher(org_question,case_id,retry_dict=retry_dict)
                
                logging.info("[new retry cypher is]: "+str(new_cypher))
    
                ## Catch on retry?
                try:
                    data_response,df,tx,meta=Neo.run_stmt_to_normalized(new_cypher,tx='')
                    got_response=True
                except:
                    logging.error("[failure on retry!!!]: "+str(new_cypher))

        return data_response,df

    def data_response_to_human_readable(self, question,data_response,cypher):
        global CYPHER_QA_TEMPLATE
        query=CYPHER_QA_TEMPLATE.format(context=data_response,question=question,cypher=cypher)
        response=self.LLM.prompt(query)
        return response,query

    def generate_cypher_query(self, question):
        query = CYPHER_GENERATION_TEMPLATE.format(schema_str=self.schema_str, question=question)
        cypher = self.LLM.prompt(query)
        return cypher

    def execute_cypher_query(self, cypher_query):
        outs = []
        results, tx = Neo.run_stmt(cypher_query)  # Assuming Neo is a defined Neo4j instance
        for rr in results:
            outs.append(rr.data())
        return outs

    def form_human_readable_answer(self, context, question):
        CYPHER_QA_TEMPLATE = """You are an assistant that helps to form nice and human understandable answers.
        ...
        Question: {question}
        Helpful Answer:"""
        query = CYPHER_QA_TEMPLATE.format(context=context, question=question)
        response = self.LLM.prompt(query)
        return response,query

    def process_question(self, question, context=None):
        if context:
            return self.form_human_readable_answer(context, question)
        else:
            cypher_query = self.generate_cypher_query(self.schema_str, question)
            results = self.execute_cypher_query(cypher_query)
            return results

    def store_run_info(self,run_id,meta):
        global Storage
        meta['the_date']=str(datetime.datetime.now())
        ## BEWARE multimodal responses with df cannnot be stored
        temp=copy.deepcopy(meta)
        temp.pop('multimodal',None)
        temp.pop('df',None)
        Storage.db_put(run_id,'run',temp,name='kb_ask')
        return

    def count_tokens(self,blob):
        return self.LLM.count_tokens(blob)

    def get_model_max_tokens(self):
        return self.LLM.MAX_INPUT_TOKENS


def predetermined_response(*args,**kwargs):
    ## Check context (tbd)
    run_id=kwargs.get('run_id','')

    response="Sorry, I can't answer that yet.  "

    for reason in kwargs.get('reasons',[]):
        # Capitalize start
        reason=re.sub(r'^[a-z]',lambda x:x.group(0).upper(),reason)     
        reason=re.sub(r'_',' ',reason)
        response+="("+reason+"."+")"

    response+=" [ref #"+str(run_id)+"]"
    return response

def local_push_multimodal_to_front_end(Multimodal,case_id):
    ## Use Mind as central hub
    logging.info("[pushing intermediary response to front-end multimodal]")
    
    Mind=Mindstate()
    sesh,session_id,is_created=Mind.start_or_load_session(case_id=case_id)

    stimer=time.time()
    answer_dict={}
    answer_dict['multimodal']=Multimodal.get_multimodal_response()
    print ("[debug] get multi response in (10s for NAV)"+str(time.time()-stimer))

    Mind.MIND_store_last_answer_meta(answer_dict,session_id)

    return

def AI_handle_kb_question(question,case_id, Agent=None, allow_cached=True):
    global MAX_TOKEN_LENGTH_FOR_CYPHER_TO_SUMMARIZE

    ## Original trial question to answer results
    global Storage
    
    ## Push partial response to front-end
    REALTIME_UPDATE_MULTIMODAL=True

    if not Agent:
        Agent = KB_AI_Agent()

    reasons=[]
    
    Multimodal=MultiModal_Response()

    meta={}
    meta['run_id']=str(uuid.uuid4())
    meta['question']=question
    meta['case_id']=case_id
    meta['rating']=0.50

    start_time=time.time()
    print ("[AI] Question: "+str(question))

    meta['cypher'],meta['llm_query_make_cypher'],qc_meta=Agent.question_to_cypher(question,case_id)
    print ("[AI] cypher (to execute): \n"+str(meta['cypher']))
    

    ### Pre-filter check if valid ie/ must include case_id etc. Otherwise ask for direct rewrite
    # Allow 1 rewrite if hard logic check (without running failure)
    if not qc_meta['is_valid']:
        meta['cypher'],meta['llm_query_make_cypher'],qc_meta=Agent.question_to_cypher(question,case_id)
        print ("[AI] cypher (to execute): \n"+str(meta['cypher']))
        
        retry_dict={}
        retry_dict['error']=",".join(qc_meta['reasons'])
        retry_dict['bad_cypher']=meta['cypher']
        retry_dict['tries']=1
        meta['cypher'],meta['llm_query_make_cypher'],qc_meta=Agent.question_to_cypher(question,case_id,retry_dict=retry_dict)
        
    if not qc_meta['is_valid']:
        ## For example:  not case_id or not asking a direct data question
        reasons+=qc_meta['reasons']
        print ("[AI] cypher is not valid: \n"+str(qc_meta['reasons']))
        response=predetermined_response(run_id=meta['run_id'],reasons=reasons)
        Multimodal.set_human_readible_response(response)
        meta['rating']=0.01

    else:

        ## NORMAL ENTRY FOR QUERY USING CYPHER:
        if 'do normal cypher to data query':
            logging.info("[debug] start cypher_to_data")
            
            # May take about 1s to query db
            org_cypher=meta['cypher']
            meta['data_response'],meta['df']=Agent.cypher_to_data_response(meta['cypher'],org_question=question,case_id=case_id, allow_cached=allow_cached)
            
            ### CHECK DATA RESPONSE FOR POSSIBLE IMMEDIATE RETRY
            #[ ] works well with:   question="Give me a list of all Zelle payments to Melissa"
            #     - 2nd attempt swaps name='Melissa' for name contains 'Melissa'

            if meta['data_response']==[]:
                retry_dict={}
                retry_dict['error']=[]
                retry_dict['tries']=0
                retry_dict={}  #Must be empty or will retry

                ## Local add to end quick & easy
                question+='\n**there was no data for the previous query: '+org_cypher+'\n'
                question+='  - maybe loosen the filters or assumptions (use CONTAINS on transaction_description?). Do not make the same query.'


                meta['cypher'],meta['llm_query_make_cypher'],qc_meta=Agent.question_to_cypher(question,case_id,retry_dict=retry_dict)
                
                logging.info("[NO DATA RESPONSE]  TRY IMMEDIATE 2nd Cypher write attempt: "+str(meta['cypher']))
                meta['data_response'],meta['df']=Agent.cypher_to_data_response(meta['cypher'],org_question=question,case_id=case_id, allow_cached=allow_cached)
                
                logging.info("[immediate retry response]: "+str(meta['data_response']))
            
    
            
        ## (debug): below is fast
        meta['data_response']=Multimodal.remove_private_data_headers(meta['data_response'])
        meta['df']=Multimodal.remove_private_df_headers(meta['df'])
        Multimodal.set_data_response(meta['data_response'])
        Multimodal.set_df_response(meta['df'])
        

        logging.dev("[AI] raw data response: \n"+str(meta['data_response']))
    
        
        if REALTIME_UPDATE_MULTIMODAL:
            local_push_multimodal_to_front_end(Multimodal,case_id)
        ##################################################################


        #################################
        # (SLOW)  Use LLM to explain response
        #################################
        ## WATCH LARGE DATA RESPONSE (in chat)
        #- ignore next llm input has question template 
        meta['data_response_token_length']=Agent.count_tokens(meta['data_response'])
        # This model's maximum context length is 4097 tokens. However, your messages resulted in 17339 tokens. Please reduce the length of the messages.
        
        logging.info("[explain response but could be slow] TOKENS: "+str(meta['data_response_token_length']))
        if meta['data_response_token_length']> Agent.get_model_max_tokens():
            size_diff=meta['data_response_token_length']/Agent.get_model_max_tokens()*1
            # Round to 1 decimal
            #response="Answer pushed to table! table!  (The data is "+str(round(size_diff,0))+" times larger than I can handle.)"
            response="Answer pushed to data table!"
            Multimodal.set_human_readible_response(response)
        elif meta['data_response_token_length']> MAX_TOKEN_LENGTH_FOR_CYPHER_TO_SUMMARIZE:  #** generally speaking too long to explain
            logging.info("[shorten response to explain to "+str(MAX_TOKEN_LENGTH_FOR_CYPHER_TO_SUMMARIZE)+" characters]")
            shortened=meta['data_response'][:MAX_TOKEN_LENGTH_FOR_CYPHER_TO_SUMMARIZE]
            shortened+="\n\n[...truncated.]"

            meta['human_readible'],meta['llm_query_make_readable']=Agent.data_response_to_human_readable(meta['question'],shortened,meta['cypher'])
            Multimodal.set_human_readible_response(meta['human_readible'])
            response=meta['human_readible']

        else:
            meta['human_readible'],meta['llm_query_make_readable']=Agent.data_response_to_human_readable(meta['question'],meta['data_response'],meta['cypher'])
            Multimodal.set_human_readible_response(meta['human_readible'])

            response=meta['human_readible']

        print ("[AI] Answer: \n"+str(response))
    
        meta['run_time']=time.time()-start_time
    
        print ("[meta] runtime: "+str(meta['run_time']))
        
    ## Prepare multimodal responses
    Multimodal.set_chatbot_response(response)
    meta['multimodal']=Multimodal.get_multimodal_response()
    
    ## Enhanced multimodal response
    #> checks for possible map or barchart-able data
    #- have this upstream (recall html prep) but keep here too
    logging.info("----------------------------------[ ] INTEGRATE ENHANCED RESPONSE via barchart + map trials")
    idict=prepare_multimodal_insight_dict(meta['multimodal'],question=question,case_id=case_id,meta=meta)
    meta['multimodal']['idict']=idict  #Keep in multimodal space


    ## Store run info
    meta['response']=response
    Agent.store_run_info(meta['run_id'],meta)

    return response,meta,Agent



def interface_kb_ask(question,Agent=None,case_id='case_default1',params={},allow_cached=True):
    ## Interface KB ask sits between the front-end Bot_Interface (chatbot) and backend KB  
    # - add top-level routing for special case handling!
    # answer is just text
    # meta is dict of answer multimodals
    
    ### Top level routing
    
    ##[1]  SPECIAL
    is_done,answer,meta,Agent=local_handle_special_question_routing(question,case_id,Agent=Agent)

    if not is_done:

        ##[2]  Do normal KB Q&A
        answer,meta,Agent=AI_handle_kb_question(question,case_id,Agent=Agent, allow_cached=allow_cached)
        
    ##[3]  Fallback / answer final validation or back to special?
    
    if isinstance(answer,dict):
        logging.warning("[interface_kb_ask] answer is dict!")

    return answer,meta,Agent


def local_handle_special_question_routing(question,case_id,Agent=None):
    #** use local because will have a try-except and possible fallbacks
    # - ie/ a lot of imports within the routing and don't want the main interface to fail!

    is_done=False
    answer='[special question handling]'
    meta={}

    is_done,answer,meta,Agent=handle_special_question_routing(question,case_id,Agent=Agent)

    Agent=None
    return is_done,answer,meta,Agent


def call_kb_agent():
    case_id='case_schoolkids'
    question = "What is the newest transaction?"
    question = "Tell me about the newest transaction"
    question = "What was the total of all transactions in december 2021?"

    #Agent = KB_AI_Agent()
    answer,meta,Agent=AI_handle_kb_question(question,case_id,Agent=None)

    print ("\nIn summary:")
    print ("[question]: "+str(question))
    print ("[answer]: "+str(answer))

    return


def dev_route_question():
    """

        [standard_case]  chatbot question arrives and is answered by cypher and summarized by LLM
        [prepared_case]  question has known_keyphrase -> routed to special handling


        - To different agents?
        - To different models?
        - To different data sources?

    """

    return



if __name__=='__main__':
    branches=['dev_result_data_to_response']
    branches=['dev_route_question']
    branches=['call_kb_agent']

    for b in branches:
        globals()[b]()

"""
REF:  Google approach:
https://cloud.google.com/blog/topics/partners/build-intelligent-apps-with-neo4j-and-google-generative-ai



prompt = ""You are an expert Neo4j Cypher translator who understands the question in english and convert to Cypher strictly based on the Neo4j Schema provided and following the instructions below:
1. Generate Cypher query compatible ONLY for Neo4j Version 5
2. Do not use EXISTS, SIZE keywords in the cypher. Use alias when using the WITH keyword
3. Use only Nodes and relationships mentioned in the schema
4. Always enclose the Cypher output inside 3 backticks
5. Always do a case-insensitive and fuzzy search for any properties related search. Eg: to search for a Company name use `toLower(c.name) contains 'neo4j'`
6. Candidate node is synonymous to Person
7. Always use aliases to refer the node in the query
8. Cypher is NOT SQL. So, do not mix and match the syntaxes
Schema:
(:Person {label: 'Person', id: string, role: string, description: string})-[:HAS_POSITION {}]->(:Position {label: 'Position', id: string, title: string, location: string, startDate: string, endDate: string, url: string})
(:Position {label: 'Position', id: string, title: string, location: string, startDate: string, endDate: string, url: string})-[:AT_COMPANY {}]->(:Company {label:'Company', id: string, name: string})
(:Person {label: 'Person',id: string, role: string, description: string})-[:HAS_SKILL {}]->(:Skill {label:'Skill', id: string,name: string,level: string})
(:Person {label: 'Person',id: string, role: string, description: string})-[:HAS_EDUCATION {}]->(:Education {label:'Education', id: string, degree: string, university: string, graduationDate: string, score: string, url: string})
Samples:
$samples
Question: $question
Answer:

Samples:
$samples
Question: $question
Answer:

#prompt/template 

3. Please do not use same variable names for different nodes and relationships in the query.
9. 'Answer' is NOT a Cypher keyword. Answer should never be used in a query.
10. Please generate only one Cypher query per question. 
12. Every Cypher query always starts with a MATCH keyword.

Schema:
{schema}
Samples:
Question: Which fund manager owns most shares? What is the total portfolio value?
Answer: MATCH (m:Manager) -[o:OWNS]-> (c:Company) RETURN m.managerName as manager, sum(distinct o.shares) as ownedShares, sum(o.value) as portfolioValue ORDER BY ownedShares DESC LIMIT 10

Question: Which fund manager owns most companies? How many shares?
Answer: MATCH (m:Manager) -[o:OWNS]-> (c:Company) RETURN m.managerName as manager, count(distinct c) as ownedCompanies, sum(distinct o.shares) as ownedShares ORDER BY ownedCompanies DESC LIMIT 10

Question: What are the top 10 investments for Vanguard?
Answer: MATCH (m:Manager) -[o:OWNS]-> (c:Company) WHERE toLower(m.managerName) contains "vanguard" RETURN c.companyName as Investment, sum(DISTINCT o.shares) as totalShares, sum(DISTINCT o.value) as investmentValue order by investmentValue desc limit 10

Question: What other fund managers are investing in same companies as Vanguard?
Answer: MATCH (m1:Manager) -[:OWNS]-> (c1:Company) <-[o:OWNS]- (m2:Manager) WHERE toLower(m1.managerName) contains "vanguard" AND elementId(m1) <> elementId(m2) RETURN m2.managerName as manager, sum(DISTINCT o.shares) as investedShares, sum(DISTINCT o.value) as investmentValue ORDER BY investmentValue LIMIT 10

Question: What are the top investors for Apple?
Answer: MATCH (m1:Manager) -[o:OWNS]-> (c1:Company) WHERE toLower(c1.companyName) contains "apple" RETURN distinct m1.managerName as manager, sum(o.value) as totalInvested ORDER BY totalInvested DESC LIMIT 10

"""





