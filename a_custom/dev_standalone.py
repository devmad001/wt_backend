import os
import sys
import codecs
import json
import re
import ast
import random

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")

from w_llm.llm_interfaces import LazyLoadLLM
from algs_extract import alg_json2dict

from get_logger import setup_logging
logging=setup_logging()


#0v1# JC  Sep  6, 2023  Init

#dev_llm2 sample

samples=[]

samples+=['\n*start*deposits and additions\nDEPOSITS AND ADDITIONS\n  (continued)\nDATE\nDESCRIPTION\nAMOUNT\n08/26\nRemote Online Deposit              1\n200.00\n08/27\n08/26/2021 Reversal: Orig CO Name:American Express\n4,213.77\n08/31\nRemote Online Deposit              1\n500.00\nTotal Deposits and Additions\n$20,117.77\n*end*deposits and additions\n*start*atm debit withdrawal\nATM & DEBIT CARD WITHDRAWALS\n DATE\nDESCRIPTION\nAMOUNT\n08/02\nCard Purchase           08/01 Fitness Mania Riverside CA Card 7397\n$49.99\n08/03\nCard Purchase           08/02 Www.Paystubsnow.Com Www.Paystubsn TX Card 7413\n7.99\n08/09\nRecurring Card Purchase 08/07 Uber   Pass Help.Uber.Com CA Card 7397\n24.99\n08/18\nCard Purchase           08/17 Fedex 940635302952 Memphis TN Card 7413\n8.20\n08/19\nRecurring Card Purchase 08/19 Experian* Credit Repor 479-3436237 CA Card 7413\n24.99\n08/24\nATM Withdrawal          08/24 6400 Laurel Canyon B North Hollywo CA Card 7413\n700.00\n08/30\nRecurring Card Purchase 08/28 Dnh*Godaddy.Com Https://Www.G AZ Card 7413\n10.99\nTotal ATM & Debit Card Withdrawals\n$827.15\n*end*atm debit withdrawal\n*start*atm and debit card summary\nATM & DEBIT CARD SUMMARY\nHugo Arturo Flores Card 7397\nTotal ATM Withdrawals & Debits\n$0.00\nTotal Card Purchases\n$74.98\nTotal Card Deposits & Credits\n$0.00\nAnthony Joseph Guillen Card 7413\nTotal ATM Withdrawals & Debits\n$700.00\nTotal Card Purchases\n$52.17\nTotal Card Deposits & Credits\n$500.00\nATM & Debit Card Totals  \nTotal ATM Withdrawals & Debits\n$700.00\nTotal Card Purchases\n$127.15\n*end*atm and debit card summary\n*start*electronic withdrawal\nTotal Card Deposits & Credits\n$500.00\nELECTRONIC WITHDRAWALS\nDATE\nDESCRIPTION\nAMOUNT\n08/02\nZelle Payment To Anthony Bro Jpm665864367\n$3,000.00\n08/02\nZelle Payment To Jennifer Nell Jpm667436915\n10.00\n08/02\nZelle Payment To Jennifer Nell Jpm667437893\n200.00\n08/02\nZelle Payment To Jennifer Nell Jpm667438464\n10.00\n08/04\nZelle Payment To Lil Bro Alex Jpm669535918\n350.00\n08/04\nZelle Payment To Meher Jpm669604904\n60.00\n08/04 Orig CO Name:Citi Autopay           Orig ID:Citicardap Desc Date:210803 CO Entry\n105.53\nDescr:Payment   Sec:Tel    Trace#:091409685898393 Eed:210804   Ind ID:080502002630039\nInd Name:Hugo Flores Trn: 2165898393Tc\n08/05\nZelle Payment To Paris Sugi Dba 12323832406\n500.00\n08/06\nZelle Payment To Anthony Bro Jpm671584743\n300.00\n08/09\nZelle Payment To Lil Bro Alex Jpm674243402\n200.00\n08/12\nZelle Payment To Teisy Jpm677655611\n172.00\n08/13\nZelle Payment To Melissa Fw Jpm678129044\n1,000.00\n*end*']

samples+=['deposits and additions\n*start*atm debit withdrawal\nATM & DEBIT CARD WITHDRAWALS\n DATE\nDESCRIPTION\nAMOUNT\n08/02\nCard Purchase           08/01 Fitness Mania Riverside CA Card 7397\n$49.99\n08/03\nCard Purchase           08/02 Www.Paystubsnow.Com Www.Paystubsn TX Card 7413\n7.99\n08/09\nRecurring Card Purchase 08/07 Uber   Pass Help.Uber.Com CA Card 7397\n24.99\n08/18\nCard Purchase           08/17 Fedex 940635302952 Memphis TN Card 7413\n8.20\n08/19\nRecurring Card Purchase 08/19 Experian* Credit Repor 479-3436237 CA Card 7413\n24.99\n08/24\nATM Withdrawal          08/24 6400 Laurel Canyon B North Hollywo CA Card 7413\n700.00\n08/30\nRecurring Card Purchase 08/28 Dnh*Godaddy.Com Https://Www.G AZ Card 7413\n10.99\nTotal ATM & Debit Card Withdrawals\n$827.15\n*end*atm debit withdrawal\n*start*atm and debit card summary\nATM & DEBIT CARD SUMMARY\nHugo Arturo Flores Card 7397\nTotal ATM Withdrawals & Debits\n$0.00\nTotal Card Purchases\n$74.98\nTotal Card Deposits & Credits\n$0.00\nAnthony Joseph Guillen Card 7413\nTotal ATM Withdrawals & Debits\n$700.00\nTotal Card Purchases\n$52.17\nTotal Card Deposits & Credits\n$500.00\nATM & Debit Card Totals  \nTotal ATM Withdrawals & Debits\n$700.00\nTotal Card Purchases\n$127.15\n*end*atm and debit card summary\n*start*electronic withdrawal\nTotal Card Deposits & Credits\n$500.00\nELECTRONIC WITHDRAWALS\nDATE\nDESCRIPTION\nAMOUNT\n08/02\nZelle Payment To Anthony Bro Jpm665864367\n$3,000.00\n08/02\nZelle Payment To Jennifer Nell Jpm667436915\n10.00\n08/02\nZelle Payment To Jennifer Nell Jpm667437893\n200.00\n08/02\nZelle Payment To Jennifer Nell Jpm667438464\n10.00\n08/04\nZelle Payment To Lil Bro Alex Jpm669535918\n350.00\n08/04\nZelle Payment To Meher Jpm669604904\n60.00\n08/04 Orig CO Name:Citi Autopay           Orig ID:Citicardap Desc Date:210803 CO Entry\n105.53\nDescr:Payment   Sec:Tel    Trace#:091409685898393 Eed:210804   Ind ID:080502002630039\nInd Name:Hugo Flores Trn: 2165898393Tc\n08/05\nZelle Payment To Paris Sugi Dba 12323832406\n500.00\n08/06\nZelle Payment To Anthony Bro Jpm671584743\n300.00\n08/09\nZelle Payment To Lil Bro Alex Jpm674243402\n200.00\n08/12\nZelle Payment To Teisy Jpm677655611\n172.00\n08/13\nZelle Payment To Melissa Fw Jpm678129044\n1,000.00\n*end*']
## Global (heavy libs)
    return

def test_extract():
    global samples
    LLM=LazyLoadLLM.get_instance()

    page=samples[0]

    ## Ask for no double quotes

    ## CHANGE 1:
    # Cash transaction to
    prompts={}
    prompts['page2transactions1']="""
    Please retrieve details about the transactions from the following bank statement page.
    If you cannot find the information from this text then return "".  Do not make things up. Always return your response as a valid json (no single quotes).
    - Include any section heads (ie/ ATM & DEBIT CARD WITHDRAWALS, CASH TRANSACTIONS, ELECTRONIC WITHDRAWALS, etc)
    All the transactions should be included in a list:

    {"all_transactions":[{"transaction_id": "id or blank", "transaction_description": "some description", "transaction_amount": "123.45", "transaction_date": "2021-01-01",'section':'Cash transactions']}

    Bank Statement Page:
    =====================

    """

    prompt=prompts['page2transactions1']+page

    print ("PROMPT: "+str(prompt))
    print (str(prompt))

    transactions=LLM.prompt(prompt,json_validate=True)
    print ("TRANSACTIONS: ")
    print (str(transactions))

    ## DO to cypher

    prompt_insert="""
    Here is a list of bank statement transactions. Convert them to cypher statements.
    - Ensure the node and relation variables are correct (not reused since they will be executed as one cypher query).
    - Each node should be defined with MERGE command on it's own line.
    - Don't infer transaction_id if it doesn't exist in the data.
     ie/
    MERGE (node1:Entity {name: "Zelle", role: "Payer"})
    MERGE (node2:Entity {name: "Lil Bro Alex", role: "Recipient"})
    CREATE (node1)-[rel1:TRANSFERRED_TO { 
        transaction_id: "Jpm674243402", 
        transaction_description: "Zelle Payment To Lil Bro Alex Jpm674243402", 
        transaction_amount: 200.00, 
        transaction_date: date("2021-08-09"),
        section: "Cash transactions"
}]->(node2)
    =====

    """

    #MOD 1:  look for account style change

    prompt_insert="""
    Here is a list of bank statement transactions. Convert them to cypher statements.
    - Ensure the node and relation variables are correct (not reused since they will be executed as one cypher query).
    - Infer an account type: (ie/ CASH, ACCOUNT, CREDIT_CARD, LOAN, MAIN, INTERMEDIARY)
    - Infer the change in account balance (ie/ INCREASES, DECREASES)
     ie/
    MERGE (node1:Entity {name: "Zelle", account_type: "INTERMEDIARY", change: "DECREASES" })
    MERGE (node2:Entity {name: "Lil Bro Alex", account_type: "ACCOUNT", change: "INCREASES"})
    MERGE (node1)-[rel1:TRANSFERRED_TO { 
        transaction_id: "Jpm674243402", 
        transaction_description: "Zelle Payment To Lil Bro Alex Jpm674243402", 
        transaction_amount: 200.00, 
        transaction_date: date("2021-08-09"),
        section: "Cash transactions"
}]->(node2)
    =====

    """

    prompt_insert="""
    Here is a list of bank statement transactions. Convert them to cypher statements.
    - Infer whether the Entity is a source of money. Recall a source Account may be virtual (cash, credit card)
     ie/
    MERGE (node1:Entity {name: "Zelle", is_source: true})
    MERGE (node2:Entity {name: "Lil Bro Alex", is_source: false})
    MERGE (node1)-[rel1:TRANSFERRED_TO { 
        transaction_id: "Jpm674243402", 
        transaction_description: "Zelle Payment To Lil Bro Alex Jpm674243402", 
        transaction_amount: 200.00, 
        transaction_date: date("2021-08-09"),
        section: "Cash transactions"
}]->(node2)
    =====
    """

    ## Bad:  uses id for zelle
    prompt_insert="""
    Here is a list of bank statement transactions. Convert them to cypher statements.
    - Don't infer transaction_id if it doesn't exist in the data.
    - Infer whether the Entity is a source of money. Recall a source Account may be virtual (cash, intermediary, credit card)
     ie/
    MERGE (node1:Entity {name: "Zelle", is_source: true})
    MERGE (node2:Entity {name: "Lil Bro Alex", is_source: false})
    MERGE (node1)-[rel1:TRANSFERRED_TO { 
        transaction_id: "Jpm674243402", 
        transaction_description: "Zelle Payment To Lil Bro Alex Jpm674243402", 
        transaction_amount: 200.00, 
        transaction_date: date("2021-08-09"),
        section: "Cash transactions"
}]->(node2)
    =====
    """

    #- Infer whether the Entity is a source of money. (cash is not, intermediary Zelle is, credit card)
    #- Infer whether the Entity account increases (atm cash widthrawl increases cash account, intermediary, credit card reversals increase)
    #- Infer whether the Entity account increases (atm cash widthrawl increases cash account, intermediary, credit card reversals increase)

    # the bad:  a payment to a business is not a source
    prompt_insert="""
    Here is a list of bank statement transactions. Convert them to cypher statements.
    - Each Entity node should be defined with MERGE command on it's own line.
    - Don't infer transaction_id if it doesn't exist in the data.
     ie/
    MERGE (node1:Entity {name: "Zelle", is_source: true})
    MERGE (node2:Entity {name: "Lil Bro Alex", is_source: false})
    MERGE (node1)-[rel1:TRANSFERS_TO { 
        transaction_id: "Jpm674243402", 
        transaction_description: "Zelle Payment To Lil Bro Alex Jpm674243402", 
        transaction_amount: 200.00, 
        transaction_date: date("2021-08-09"),
        section: "Cash transactions"
}]->(node2)
    =====
    """

    ## still gets confused on payer
    prompt_insert="""
    Here is a list of bank statement transactions. Convert them to cypher statements.
    - Each Entity node should be defined with MERGE command on it's own line.
    - Don't infer transaction_id if it doesn't exist in the data.
    - For double-entry bookkeeping, identify if Entity is_debit (cash is false, intermediary is true)
     ie/
    MERGE (node1:Entity {name: "Zelle", is_payer: true})
    MERGE (node2:Entity {name: "Lil Bro Alex", is_payer: false})
    MERGE (node1)-[rel1:TRANSFERS_TO { 
        transaction_id: "Jpm674243402", 
        transaction_description: "Zelle Payment To Lil Bro Alex Jpm674243402", 
        transaction_amount: 200.00, 
        transaction_date: date("2021-08-09"),
        section: "Cash transactions"
}]->(node2)
    =====
    """

    # Bad not on each line
    prompt_insert="""
    Here is a list of bank statement transactions. Convert them to cypher statements.
    Use the description to infer the source and target Account Entities:
     ie/
    MERGE (node1:Entity {name: "Zelle", is_payer: true})
    MERGE (node2:Entity {name: "Lil Bro Alex", is_payer: false})
    MERGE (node1)-[rel1:TRANSFERS_TO { 
        transaction_id: "Jpm674243402", 
        transaction_description: "Zelle Payment To Lil Bro Alex Jpm674243402", 
        transaction_amount: 200.00, 
        transaction_date: date("2021-08-09"),
        section: "Cash transactions"
}]->(node2)
    =====
    """
    
    ## Use gpt4 tips
    prompt_insert="""
    For each transaction in the provided JSON, generate a cypher statement. The transaction source and target should be inferred from the description.
    - Each Entity node should be defined with MERGE command on it's own line.
     ie/
    MERGE (node1:Entity {name: "Zelle", is_payer: true})
    MERGE (node2:Entity {name: "Lil Bro Alex", is_payer: false})
    MERGE (node1)-[rel1:TRANSFERS_TO { 
        transaction_id: "Jpm674243402", 
        transaction_description: "Zelle Payment To Lil Bro Alex Jpm674243402", 
        transaction_amount: 200.00, 
        transaction_date: date("2021-08-09"),
        section: "Cash transactions"
}]->(node2)
    =====
    """


    cleant=json.dumps(transactions)
    cleant=re.sub(r'\\"','"',cleant)
    
    print ("CLEAN: "+str(cleant))

    prompt_insert=prompt_insert+cleant

    print ("PROMPT INSERT:")
    print (str(prompt_insert))

    cypher_response=LLM.prompt(prompt_insert)

    print ("CYPHER RESPONSE:")
    print (str(cypher_response))

    print ("REmove slash quote from transactions in main code[ ] ] ] ")
    return

def test_extract_just_dicts():
    global LLM
    global samples

    init_llm()

    page=samples[0]

    ## Ask for no double quotes

    ## CHANGE 1:
    # Cash transaction to
    prompts={}
    prompts['page2transactions1']="""
    Please retrieve details about the transactions from the following bank statement page.
    If you cannot find the information from this text then return "".  Do not make things up. Always return your response as a valid json (no single quotes).
    - Include any section heads (ie/ ATM & DEBIT CARD WITHDRAWALS, CASH TRANSACTIONS, ELECTRONIC WITHDRAWALS, etc)
    All the transactions should be included in a list:

    {"all_transactions":[{"transaction_id": "id or blank", "transaction_description": "some description", "transaction_amount": "123.45", "transaction_date": "2021-01-01","section":"Cash transactions"]}

    Bank Statement Page:
    =====================

    """

    prompt=prompts['page2transactions1']+page

    print ("PROMPT: "+str(prompt))
    print (str(prompt))

    transactions=LLM.prompt(prompt,json_validate=True)
    print ("TRANSACTIONS: ")
    print (str(transactions))

    ## Markup dict (cypher later)
    prompt_insert="""
    For each transaction in the provided JSON, add the Account source name and type fields:
    - The source and target should be inferred from the description & section
    - {source_name:"Zelle", target_name:"Lil Bro Alex", source_type:"INTERMEDIARY", target_type:"ACCOUNT", transaction_id='JPG33222'}

    =====
    """

    prompt_insert="""
    For each transaction in the provided JSON, add the Account source name and type fields:
    - The source and target should be inferred from the description & section
    - Also update the transaction_id
    - {source_name:"Zelle", target_name:"Lil Bro Alex", source_type:"INTERMEDIARY", target_type:"ACCOUNT", "transaction_id":"JPG33222"}

    =====
    """

    #experiment:  better transaction id
    prompt_insert="""
    For each transaction in the provided JSON, add the Account source name and type fields:
    - The source and target should be inferred from the description & section
    - Also update the transaction_id which may also be inferred from the description
    - {source_name:"Zelle", target_name:"Lil Bro Alex", source_type:"INTERMEDIARY", target_type:"ACCOUNT", "transaction_id":"JPG33222"}

    =====
    """

    #experiment:  more account types AND samples
    prompt_insert="""
    For each transaction in the provided JSON, add the Account source name and type fields:
    - The source and target should be inferred from the description & section
    - Account types could be: MAIN (the bank account), CARD, CASH, INTERMEDIARY, ACCOUNT, LOAN, CREDIT_CARD
    - Also update the transaction_id which may also be inferred from the description

    GIVEN:  {transaction_description: "Zelle Payment To Lil Bro Alex Jpm674243402", transaction_amount: 200.00, transaction_date: date("2021-08-09"), section: "Electronic Transfers"}

    RETURN:  {source_name:"Zelle", target_name:"Lil Bro Alex", source_type:"INTERMEDIARY", target_type:"ACCOUNT", "transaction_id":"Jpm674243402", transaction_description: "Zelle Payment To Lil Bro Alex Jpm674243402", transaction_amount: 200.00, transaction_date: date("2021-08-09"), section: "Electronic Transfers"}

    =========
    """

    prompt_insert="""
    For each transaction in the provided JSON, add the Account source name and type fields:
    - The source and target should be inferred from the description & section
    - Also update the transaction_id which may also be inferred from the description

    {source_name:"Zelle", target_name:"Lil Bro Alex", source_type:"INTERMEDIARY", target_type:"ACCOUNT", "transaction_id":"Jpm674243402", transaction_description: "Zelle Payment To Lil Bro Alex Jpm674243402", transaction_amount: 200.00, transaction_date: date("2021-08-09"), section: "Electronic Transfers"}

    =========
    """

    #Asking for json does not help
    prompt_insert="""
    For each transaction in the provided JSON, add the Account source name and type fields:
    - The source and target should be inferred from the description & section
    - Also update the transaction_id which may also be inferred from the description
    ie/

    {source_name:"Zelle", target_name:"Lil Bro Alex", source_type:"INTERMEDIARY", target_type:"ACCOUNT", "transaction_id":"Jpm674243402", transaction_description: "Zelle Payment To Lil Bro Alex Jpm674243402", transaction_amount: 200.00, transaction_date: date("2021-08-09"), section: "Electronic Transfers"}

    =========
    """

    #NOPE
    prompt_insert="""
    For each transaction in the provided JSON, add the Account source and target names. The source and target should be inferred from the description & section. Also update the transaction_id which may also be inferred from the description.
    ie/

    {source_name:"Zelle", target_name:"Lil Bro Alex", "transaction_id":"Jpm674243402", transaction_description: "Zelle Payment To Lil Bro Alex Jpm674243402", transaction_amount: 200.00, transaction_date: date("2021-08-09"), section: "Electronic Transfers"}

    =========
    """

    ## experiment lean (online writes python)
    prompt_insert="""
    For each transaction in the provided JSON, add the Account source_name and target_name fields. The source and target should be inferred from the description & section.

    =========
    """

    ## experiment lean
    prompt_insert="""
    Add source_name and target_name to these transaction. The source and target should be inferred from the description & section.

    =========
    """



    ## experiment:
    #- fewer max 5
    if not isinstance(transactions,dict):
        transactions=json.loads(transactions)
    allt=transactions['all_transactions']
    keept=[]
    id=0
    for tt in allt:
        id+=1
        ## Pop non essentials
        tt['id']=str(id)
        tt.pop('transaction_date','')
        tt.pop('transaction_amount','')
        keept+=[tt]
    allt=keept

    if False:
        transactions['all_transactions']=allt[0:5]
        transactions['all_transactions']=allt[5:10]
        transactions['all_transactions']=allt[10:15]
        transactions['all_transactions']=allt[15:20]
    random.shuffle(allt)

    ## experiment lean (online writes python)
    prompt_insert="""
    For each transaction in the provided JSON, add the Account source_name and target_name fields. The source and target should be inferred from the description & section.

    =========
    """

    prompt_insert="""
    For each bank statement transaction in the provided JSON, add the Account source_name and target_name fields. The source and target should be inferred from the description & section.
    - If the transaction is an ATM withdrawl, the target_name should be "Cash"
    - If the transaction involves a bank account deposit the target_name would be 'Bank Account'

    For example:
    {
        "transaction_description": "Zelle Payment To Anthony Bro Jpm671584743",
        "transaction_amount": "300.00",
        "transaction_date": "2021-08-06",
        "section": "Electronic Withdrawals",
        "source_name": "Zelle",
        "target_name": "Anthony Bro Jpm671584743"
    }

    TRANSACTIONS:
    =========
    """

    ## experiment: payer_name
    #For each transaction in the provided JSON, add the Account payer_name and receiver_name fields. The payer and receiver t should be inferred from the description & section
    
    prompt_insert="""
    For each transaction in the provided JSON, add the Account payer_name and receiver_name fields.

    =========
    """

    prompt_insert="""
    For each bank statement transaction in the provided JSON, add the Account source_name and target_name fields. The source and target should be inferred from the description & section.
    - Typical payer_names are: Credit Card, Zelle, Bank Account, Online Deposit, Credit card reversal
    - Typical receiver_names are: Cash, Business Name

    For example:
    {
        "transaction_description": "Zelle Payment To Anthony Bro Jpm671584743",
        "transaction_amount": "300.00",
        "transaction_date": "2021-08-06",
        "section": "Electronic Withdrawals",
        "payer_name": "Zelle",
        "receiver_name": "Anthony Bro Jpm671584743"
    }

    TRANSACTIONS:
    =========
    """

    ## POP excess
    prompt_insert="""
    For each bank statement transaction in the provided JSON, add the Account payer_name and receiver_name fields. The payer and receiver should be inferred from the description & section.
    - Typical payer_names are: Credit Card, Zelle, Bank Account, Online Deposit, Credit card reversal
    - Typical receiver_names are: Cash, Business Name

    EXAMPLES:
    {
        "transaction_description": "Zelle Payment To Anthony Bro Jpm671584743",
        "section": "Electronic Withdrawals",
        "payer_name": "Zelle",
        "id": "22",
        "receiver_name": "Anthony Bro"
    },
    {
        "transaction_description": "Recurring Card Purchase 08/19 Experian* Credit Repor 479-3436237 CA Card 7413",
        "section": "ATM & Debit Card Withdrawals",
        "id": "8",
        "payer_name": "Card",
        "receiver_name": "Experian"
    },
    {
        "transaction_description": "Remote Online Deposit",
        "section": "Deposits and Additions",
        "id": "1",
        "payer_name": "Online Deposit",
        "receiver_name": "Bank Account"
    },
    {
        "transaction_description": "Reversal: Orig CO Name:American Express",
        "section": "Deposits and Additions",
        "id": "2",
        "payer_name": "American Express",
        "receiver_name": "Bank Account"
    },
    {
        "transaction_description": "Loan #4432 payment",
        "section": "Deposits and Additions",
        "id": "2",
        "payer_name": "Bank Account",
        "receiver_name": "Loan #4432"
    },
    {
        "transaction_description": "ATM Withdrawal 08/24 6400 Laurel Canyon B North Hollywo CA Card 7413",
        "section": "ATM & Debit Card Withdrawals",
        "id": "9",
        "payer_name": "ATM 6400 Laurel Canyon B North Hollywo CA Card 7413" 
        "receiver_name": "Cash"
    },


    TRANSACTIONS:
    =========
    """

    prompt_insert="""
    For each bank statement transaction in the provided JSON, add the Account payer_id and receiver_id fields. The payer and receiver should be inferred from the description & section.
    - Typical payer_ids are: Credit Card, Zelle, Bank Account, Online Deposit, Credit card reversal
    - Typical receiver_ids are: Cash, Business id

    EXAMPLES:
    {
        "transaction_description": "Zelle Payment To Anthony Bro Jpm671584743",
        "section": "Electronic Withdrawals",
        "payer_id": "Zelle",
        "receiver_id": "Anthony Bro"
    },
    {
        "transaction_description": "Recurring Card Purchase 08/19 Experian* Credit Repor 479-3436237 CA Card 7413",
        "section": "ATM & Debit Card Withdrawals",
        "id": "8",
        "payer_id": "Card 7413",
        "receiver_id": "Experian"
    },
    {
        "transaction_description": "Remote Online Deposit",
        "section": "Deposits and Additions",
        "id": "1",
        "payer_id": "Online Deposit",
        "receiver_id": "Bank Account"
    },
    {
        "transaction_description": "Reversal: Orig CO id:American Express",
        "section": "Deposits and Additions",
        "id": "2",
        "payer_id": "American Express",
        "receiver_id": "Bank Account"
    },
    {
        "transaction_description": "Loan #4432 payment",
        "section": "Deposits and Additions",
        "id": "2",
        "payer_id": "Bank Account",
        "receiver_id": "Loan #4432"
    },
    {
        "transaction_description": "ATM Withdrawal 08/24 6400 Laurel Canyon B North Hollywo CA Card 7413",
        "section": "ATM & Debit Card Withdrawals",
        "id": "9",
        "payer_id": "ATM 6400 Laurel Canyon B North Hollywo CA Card 7413" 
        "receiver_id": "Cash"
    }


    TRANSACTIONS:
    =========
    """

    ## remove ids and extend count
    prompt_insert="""
    For each bank statement transaction in the provided JSON, add the Account payer_id and receiver_id fields. The payer and receiver should be inferred from the description & section.
    - Typical payer_ids are: Credit Card, Zelle, Bank Account, Online Deposit, Credit card reversal
    - Typical receiver_ids are: Cash, Business id

    EXAMPLES:
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
        "payer_id": "ATM 6400 Laurel Canyon B North Hollywo CA Card 7413" 
        "receiver_id": "Cash"
    }


    ALL TRANSACTIONS:
    =========
    """

    ## MOVE TO CORE?
    ####  GOLD
    cleant=json.dumps(transactions)
    cleant=re.sub(r'\\"','"',cleant)
    # remove transaction_id if blank
    cleant=re.sub(r'"transaction_id": "",','',cleant)
    ##############
    
    
    prompt_insert=prompt_insert+cleant

    print ("PROMPT INSERT:")
    print (str(prompt_insert))

    cypher_response=LLM.prompt(prompt_insert)

    print ("CYPHER RESPONSE:")
    print (str(cypher_response))

    print ("REmove slash quote from transactions in main code[ ] ] ] ")
    return


if __name__=='__main__':
    branches=['test_extract']
    branches=['test_extract_just_dicts']
    for b in branches:
        globals()[b]()


"""
"""
