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

from class_prompt import A_Prompt

#0v1# JC  Sep 14, 2023  Init

"""
    PROMPT
    - include extensible suggestions here based on schema
    - see b_extract/* for inspiration
"""



def Prompt_Eng():
    #tbd
    def __init__(self):
        return

def get_prompt_template(prompt_name):
    ## Hard coded lookup
    Prompt=A_Prompt(prompt_name)
    #the_prompt=Prompt.dump_prompt()
    return Prompt


def get_bullet_field_suggestions(fields,markup_goals=[],page_text='',target_records={},meta_doc={},max_bullet_examples=3):
    ## For example: if you think a section is present then suggest to extract it
    # markup_goals is main subject steerer
    # if 'Deposits and other credits' in page_text suggest 'Deposits and other credits'

    #target_records:  Can do string search as options for target *or even include page meta_doc

    ## Optional pass in sugs if have more defaults
    sugs=OrderedDict()

    ## Lookup suggestions
    for field in fields:
        sugs[field]={}

        ### PER FIELD LOGIC
        if field=='section':
            sugs[field]['default_terms']=['ATM & DEBIT CARD WITHDRAWLS','CASH TRANSACTIONS','ELECTRONIC WITHDRAWALS']
            sugs[field]['terms']=[]

            if 'Deposits and other credits' in page_text:  #BOA
                sugs[field]['terms']+=['Desposits and other credits' ]
            if 'Withdrawals and other debits' in page_text:  #BOA
                sugs[field]['terms']+=['Withdrawals and other debits']
            if 'Checks ' in page_text:  #BOA  Checks - continued
                sugs[field]['terms']+=['Checks']



        ## COMBINE INTO PHRASE  (ie/  )
        # METHOD:  pre-pend suggestons (alt is randomize etc)
        terms_list=sugs[field]['terms']+sugs[field]['default_terms']
        terms_list=terms_list[:max_bullet_examples]
        if terms_list:
            sugs[field]['terms_phrase']=" (ie/ "+", ".join(terms_list)+", etc)"
        else:
            sugs[field]['terms_phrase']=""

    return sugs


def lookup_auto_suggestion_examples(page_text,max_suggests=4):
    if not page_text:
        return []
    suggests=[]
    checks=[]

    ## LONG BANK DETAILS
    check={}
    check['keyword']=r'Orig CO Name'
    check['suggestion'] = {
        "transaction_description": "Orig CO Name:Applecard Gsbank       Orig ID:9999999999 Desc Date:081421 CO Entry\nPayment\nWeb\nTrace#:124085088814230 Eed:210816   Ind ID:12810547\nHugo Flores Trn: 2288814230Tc",
        "section": "Electronic Withdrawals",
        "payer_id": "Applecard",
        "receiver_id": "Hugo Flores"
        }
    checks+=[check]

    ## Reverse fee
    check={}
    check['regex']=r'Orig CO Name.*fee'
    check['suggestion'] = {
        "transaction_description": "Insufficient Funds Fee For A $1,582.00 Item - Details: Orig CO Name:Barclaycard US\nOrig ID:2510407970 Desc Date:       CO Entry Descr:Creditcardsec:Web\nTrace#:026002572841962 Eed:210830   Ind ID:810676570\nInd Name:Genesis\nFlores Trn: 2422841962Tc",
        "section": "FEES",
        "payer_id": "Genesis Flores",
        "receiver_id": "Barclaycard US"}
    checks+=[check]

    ## Some kind of credit card electronic withdrawl
    check={}
    check['regex']=r'Orig CO Name.*creditcardsec'
    check['suggestion']={
            "transaction_description": "Orig CO Name:Barclaycard US         Orig ID:2510407970 Desc Date:       CO Entry\nCreditcardsec:Web    Trace#:026002572841962 Eed:210830   Ind ID:810676570\nTim Jones Trn: 2422841962Tc",
            "section": "ELECTRONIC WITHDRAWALS",
            "payer_id": "Barclaycard US",
            "receiver_id": "Tim Jones",
        }
    checks+=[check]

    ## BOA Despot from
    check={}
    check['regex']=r'TRANSFER TRSF FROM'
    check['suggestion']={
            "transaction_description": "ACCOUNT TRANSFER TRSF FROM 000245202689 2128453290 906812020006984",
            "section": "Deposits and other credits",
            "payer_id": "000245202689 2128453290",
            "receiver_id": "Bank Account"
        }
    checks+=[check]

    ## BOA Despot from
    check={}
    check['regex']=r'WIRE TYPE\:'
    check['suggestion']={
            "transaction_description": "WIRE TYPE:WIRE IN DATE: 211216 TIME:1348 ET\nTRN:2021121600427147\nSEQ:5242600350JO/009620 ORIG:UNITED CALL\nCENTER SOLUTI ID:373171237 SND\nBK:JPMORGAN CHASE BANK, NA ID:021000021\nPMT DET:ATS OF 21/12/16 INVSGM154903712160427147",
            "section": "Deposits and other credits",
            "payer_id": "UNITED CALL CENTER SOLUTI",
            "receiver_id": "Bank Account"
        }
    checks+=[check]

    ## BOA withdrawl insurance
    check={}
    check['regex']=r' DES\:'
    check['suggestion']={
            "transaction_description": "CHUBB-CI         DES:INS.PREM   ID:CI  INDN:Skyview Capital Group   CO\nID:3131963496 CCD902534024864566",
            "section": "Withdrawals and other debits",
            "payer_id": "Bank Account",
            "receiver_id": "INS.PREM"
    }
    checks+=[check]

    ## BOA account transfer
    #- source it not Bank Account but account name!
    check={}
    check['regex']=r'ACCOUNT TRANSFER'
    check['suggestion']={
            "transaction_description": "ACCOUNT TRANSFER\nTRSF TO 325000623719\n906812170007790",
            "section": "Withdrawals and other debits",
            "payer_id": "TRSF",
            "receiver_id": "325000623719"
        }
    checks+=[check]

    for check in checks:
        if 'keyword' in check:
            if check['keyword'] in page_text:
                suggests+=[check['suggestion']]
        elif 'regex' in check:
            if re.search(check['regex'],page_text,re.IGNORECASE|re.DOTALL):
                suggests+=[check['suggestion']]

    if True:
        print ("[debug using special suggestion]: "+str(suggests))

    ## Dont randomize since causes cache issue

    # Limit suggests to max_suggests
    suggests=suggests[:max_suggests]
    return suggests

def programmatic_suggestions(markup_goals=[],branch=['default'],page_text='',meta_doc={},target_records={},max_overall_examples=6):
    ## Optional force_random?? But messes with cache
    ## Creates a list of example output suggestions
    # markup_goals is top level type ie/ transaction_target_entity
    #[ ] target_records={} can suggest output based on content of records to augment
    #[ ] meta or doc meta can have extra easily searchable keywords
    
    check=or_moved

    suggestions=[]
    if 'default' in branch:

        suggestions.extend([
            {
                "transaction_description": "Zelle Payment To Anthony Bro Jpm671584743",
                "section": "Electronic Withdrawals",
                "payer_id": "Zelle",
                "receiver_id": "Anthony Bro"
            },
            {
                "transaction_description": "Recurring Card Purchase 08/19 Experian* Credit Repor 479-3436237 CA Card 7413",
                "section": "ATM & Debit Card Withdrawals",
                "payer_id": "Card 7413",
                "receiver_id": "Experian"
            },
            {
                "transaction_description": "Remote Online Deposit",
                "section": "Deposits and Additions",
                "payer_id": "Online Deposit",
                "receiver_id": "Bank Account"
            },
            {
                "transaction_description": "Reversal: Orig CO id:American Express",
                "section": "Deposits and Additions",
                "payer_id": "American Express",
                "receiver_id": "Bank Account"
            },
            {
                "transaction_description": "Loan #4432 payment",
                "section": "Deposits and Additions",
                "payer_id": "Bank Account",
                "receiver_id": "Loan #4432"
            },
            {
                "transaction_description": "ATM Withdrawal 08/24 6400 Laurel Canyon B North Hollywo CA Card 7413",
                "section": "ATM & Debit Card Withdrawals",
                "payer_id": "ATM 6400 Laurel Canyon B North Hollywo CA Card 7413",
                "receiver_id": "Cash"
            }
        ])

    ## Auto add suggestions
    if page_text:
        suggests=lookup_auto_suggestion_examples(page_text,max_suggests=4)
        ## Prepend
        suggestions=suggests+suggestions

    if len(suggestions)>max_overall_examples:
        #Keep the first 6/x suggestions
        #- optionally some from default?
        logging.warning('[warning] too many suggestions (clip to '+str(max_overall_examples)+' ): '+str(len(suggestions)))
        suggestions=suggestions[:max_overall_examples]

    #*don't randomize causes issue with cache

    ## Add ids to suggestions
    full=[]
    c=0
    for s in suggestions:
        c+=1
        s['id']=c
        full+=[s]

    ## Transform it to a string WITHOUT the square brackets
    #* square brackets may enforce it thinks only needs 6 lines

    # Convert to string
    suggestion_string = json.dumps(full, indent=4)
    
    # Remove the square brackets
    #?WHY
    #suggestion_string = suggestion_string[1:-1].strip()

    return suggestions,suggestion_string


def tech_nuiances():
    ## NOTES
    nu=[]
    nu+=['Add ALL input record fields to suggested outputs (but not necessary since Records does update/merge of what comes out of here)']
    return

def prompt_authoring(records,schema={},markup_goals=['dev'],page_text='',meta_doc={}):
    """
        USE SCHEMA TO AUTHOR PROMPT
        markup_goals:  overall goal
        schema:  per field, node, class definitions
    """
    print ("[debug] prompt author at records: "+str(records))

    ## CHECK PARAMETERS

    ## SCHEMA CHECK
    # markup_goals:  overall set by top call kb update
    # schema:  specific schema defined schema_sender_entity.py, schema_*

    ## Inner meta passed
    full_doc_text=meta_doc.get('full_doc_text','') #alg_doc_meta.py multiple methods

    ## Validate schema parameters match & registered
    if 'add_sender_receiver_nodes' in markup_goals:
        if not schema['kind']=='sender_receiver_entity': stopp=check_schema
        if not schema['kb_update_type']=='node_create': stopp=check_schema

    elif 'transaction_type_method_goals' in markup_goals:
        if not schema['kind']=='transaction_type_method_goals': stopp=check_schema
    else:
        print ("[error] given markup goal: "+str(markup_goals))
        print ("[error] given schema kind: "+str(schema['kind']))
        stopp=check_schema

    #> basic flow

    opts={}
    opts['max_overall_examples']=4
    opts['max_bullet_examples']=6

    header=''

    default_bullets=[]
    dynamic_bullets=[]

    default_examples=[]
    dynamic_examples=[]


    if 'dev' in markup_goals:
        Prompt=get_prompt_template('dev')
    else:
        Prompt=get_prompt_template('dev')

    ###########################################
    ## NOTE GIVENS
    Prompt.include_data(records) #<-- examples may look at records!
    Prompt.note_full_doc_text(full_doc_text)

    ###########################################
    ## HEADER

    if 'dev' in markup_goals:
        header="""  For each bank statement transaction in the provided JSON, add the Account payer_id and receiver_id fields. The payer and receiver should be inferred from the description & section.
     Return the response in valid JSON format.
- Typical payer_ids are: Credit Card, Zelle, Check Deposits, Bank Account, Online Deposit, Credit card reversal
- Typical receiver_ids are: Cash, Business id, Bank Account
"""  #Watch space on left keep zero
    else:
        ## ASSUME SOURCE VIA SCHEMA
        header=schema['header']

    print ("[ ] check limits when bullets and examples from from external schema")

    ###########################################
    ## BULLETS
    if 'dev' in markup_goals:
        remove=old_method
        sugs=get_bullet_field_suggestions(['section'],markup_goals=markup_goals,page_text=page_text,target_records=records,meta_doc=meta_doc,max_bullet_examples=opts['max_bullet_examples'])
        dynamic_bullets+=["- A typical section field is: "+sugs['section']['terms_phrase']+"\n"]
    else:
        ## ASSUME SOURCE VIA SCHEMA
        default_bullets=[]
        dynamic_bullets=schema['bullets']

    ###########################################
    ## EXAMPLES
    if 'dev' in markup_goals:
        remove=old_method
        dynamic_examples,examples_string=programmatic_suggestions(branch=['default'],markup_goals=markup_goals,page_text=page_text,target_records=records,meta_doc=meta_doc,max_overall_examples=opts['max_overall_examples'])
    else:
        default_examples=schema['examples'] #list of dicts
        dynamic_examples=schema.get('dynamics',[])
        examples_string=''

    ###########################################
    ## HEADER FOR INPUT DATA
    data_header="""
        ALL """+str(len(records))+""" TRANSACTIONS (to process):
        =========
        """
    #{BANK TRANSACTIONS because if examples are too long (ie 8) it cant find these}
    data_header="""
        ALL """+str(len(records))+""" BANK TRANSACTIONS (to process):
        =========
        """

    ###########################################
    ## SET AND ASSEMBLE PROMPT

    Prompt.set_markup_goals(markup_goals)  #not used

    Prompt.set_header(header)

    Prompt.resolve_bullets(default_bullets,dynamic_bullets)

    Prompt.set_data_header(data_header)

    dd={}
    dd['examples_string']=examples_string
    dd['default_examples']=default_examples
    dd['dynamic_examples']=dynamic_examples
    Prompt.resolve_examples(**dd)

    the_prompt=Prompt.dump_prompt()

    print ("[ ] watch token length")
    return the_prompt


def dev1():
    prin ("call from llm_markup")
    return

if __name__=='__main__':
    branches=['dev2_prompt_dev_entity']
    for b in branches:
        globals()[b]()
