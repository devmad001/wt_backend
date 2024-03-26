import os
import sys
import time
import codecs
import datetime
import json
import re
import uuid

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")
sys.path.insert(0,LOCAL_PATH+"../../")


from w_storage.gstorage.gneo4j import Neo


from get_logger import setup_logging
logging=setup_logging()


#0v1# JC  Nov  7, 2023  Init


## RECALL TIMELINE:
# http://127.0.0.1:8008/api/v1/case/chase_4_a_6/timeline


"""
    IDEAL G20
    - Address the hardest 20 styles of questions
"""



def STEP_THROUGH_general():
    from ideal_answer import dev_local_Bot_Interface 
    manuals={}

    #[x] added as sample
    gg={}
    gg['id']='G1'
    gg['question']='List all payments to the IRS and total amount'
    gg['cases']=['chase_4_a']
    gg['raw_sample']='12/22 Irs Usataxpymt 220475655216495 CCD ID: 3387702000 1,038.24' #chase_4_a
    
    gg['attempts']=[]
    gg['attempts']=["""
 MATCH (Transaction:Transaction {case_id: 'chase_4_a'})-[ct:CREDIT_TO]->(Payee:Entity)
WHERE
    Transaction.case_id = 'chase_4_a'
    AND
    Payee.name CONTAINS 'IRS'
RETURN Transaction, sum(Transaction.transaction_amount) as total_IRS_payments, COLLECT(Payee) AS Payees
"""]

#rewrite 2
    gg['attempts']+=["""
MATCH (Transaction:Transaction {case_id: 'chase_4_a'})-[ct:CREDIT_TO]->(Payee:Entity)
WHERE
    Transaction.case_id = 'chase_4_a'
    AND
    (Payee.name CONTAINS 'IRS' OR Transaction.transaction_description CONTAINS 'IRS')
RETURN Transaction, sum(Transaction.transaction_amount) as total_IRS_payments, COLLECT(Payee) AS Payees
    """]

    
    answer,adict=dev_local_Bot_Interface(gg['question'],gg['cases'][0])
    
    print ("GOT: "+str(answer))


    return

def dev_try_single_question(question='List online transfers deposits',case_id='chase_4_a'):
    from ideal_answer import dev_local_Bot_Interface 
    #question='List online transfers deposits'
    
    answer,adict=dev_local_Bot_Interface(question,case_id)
    print ("QUESTION: "+str(question))
    print ("ANSWER: "+str(answer))
    
    return answer

def dev_try_cypher_queries():
    logging.info("STart...")
    print ("CYPHERS...")
    return
    
    #RETURN t.statement_id as StatementID, collect(t) as Transactions
    stmt="""
        MATCH (t:Transaction)
        WHERE t.case_id='"""+str(case_id)+"""'
        RETURN DISTINCT t.statement_id as StatementID
        ORDER BY StatementID;
        """
    record={}
    a=kk
    
    ## Run statements when different styles of output!
    results,tx=Neo.run_stmt(stmt,tx='',parameters={})
    results=results.data() #<-- standard normalize as list too
    for record in results:
        yield record['StatementID'] #  #{'StatementID'}
    return


def dev2():
    case_id=case_id
    print ("** not throwing error?!")
    print ("HELLO")
    stmt="""
        MATCH (t:Transaction)
        WHERE t.case_id='"""+str(case_id)+"""'
        RETURN DISTINCT t.statement_id as StatementID
        ORDER BY StatementID;
        """
    record={}
    
    ## Run statements when different styles of output!
    results,tx=Neo.run_stmt(stmt,tx='',parameters={})
    results=results.data() #<-- standard normalize as list too
    for record in results:
        yield record['StatementID'] #  #{'StatementID'}
    return


def devv():
    print ("GENERAL:  Can be answered by searching original transaction description")
    #** bit of a fall-back
    
    ## IRS total
    
    case_id='chase_4_a'

    ## REGEX NOTES:
    #> (?i) = case insensitive
    pattern="\\\WIRS\\\W" #!! TRIPLE SLASHES !!

    ## REGEX
    stmt="""
        MATCH (t:Transaction)
        WHERE
            t.case_id='"""+str(case_id)+"""'
        AND
            t.transaction_description =~ '(?i).*"""+pattern+""".*'  // Double slashes!
        RETURN
            t.transaction_amount as Amount,
            t.transaction_description as Description,
            t.is_credit as IsCredit
        """

    ## CONTAINS  NO BECAUSE NO lower case and no word boundaries!
    stmt="""
        MATCH (t:Transaction)
        WHERE
            t.case_id='"""+str(case_id)+"""'
        AND
            toLower(t.transaction_description ) CONTAINS toLower('IRS')

        RETURN
            t.transaction_amount as Amount,
            t.transaction_description as Description,
            t.is_credit as IsCredit
        """

    print ("[run cypher]: "+str(stmt))
    jsonl,df,tx,meta=Neo.run_stmt_to_normalized(stmt)
    
    for record in jsonl:
        print ("> "+str(record))
    
    return


def GET_tip_regex_description():
    tip=["""
        - If a keyword is involved, try searching the transaction description (it contains most info)
            - For example, to find all payments to the IRS use:
        WHERE
            t.transaction_description =~ '(?i).*\\WIRS\\W.*'
        AND
            t.is_credit = false
        """]
    return tip[0]


def unconventional_cypher_tips():
    
    ### SUGGEST THESE IF FIRST PASS FAILS TO RETURN RECORDS
    
    ## REGEXES:
    #- when it should be suggested

    ## LEVERAGE REGEX ON DESCRIPTION FOR KEYWORDS
    tip={}
    tip['description']='Regex search description'
    tip['regexes']=['\WIRS\W']
    tip['applies_to']='Keyword based transaction description'
    tip['questions']=['List all payments to the IRS']

    tip['cypher tips']=["""
        - If a keyword is involved, try searching the transaction description (it contains most info)
            - For example, to find all payments to the IRS:
        WHERE
            t.transaction_description =~ '(?i).*\\WIRS\\W.*'
        AND
            t.is_credit = false
        """]
                    
    
    return


if __name__=='__main__':
    branches=['dev1']
    branches=['dev_try_cypher_queries']
    branches=['dev2']

    branches=['unconventional_cypher_tips']
    branches=['devv']
    branches=['STEP_THROUGH_general']

    branches=['dev_try_single_question']

    for b in branches:
        print ("RUNNING: "+str(b))
        globals()[b]()
        


"""
"""
