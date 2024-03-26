import os
import sys
import time
import datetime
import codecs
import json
import re
import pandas as pd

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")

from w_storage.gstorage.gneo4j import Neo
from w_chatbot.wt_brains import Bot_Interface


from get_logger import setup_logging
logging=setup_logging()


#0v2# JC  Nov 18, 2023  **see run_autotune for more indepth
#0v1# JC  Oct 12, 2023  Init

"""
    AUTO RUN 50

"""


# Set display options
pd.set_option('display.max_rows', None)  # None means all rows
pd.set_option('display.max_columns', None)  # None means all columns
pd.set_option('display.width', None)  
pd.set_option('display.max_colwidth', None)

def auto_run_50q():
    case_id='case_atm_location'
    case_id='case_wells_fargo_small'

    print ("="*30)
    print ("= RUNNING 50q against case: "+str(case_id))
    print ("="*30)

    Bot=Bot_Interface()
    Bot.set_case_id(case_id)
    
    if 'singleq' in []:
        #[ ok but long dup list ]#  question='What is the account number?' #[ ] possibly group
        ## OK::
        question='How many transactions are there?'
        question='What is the total of cash transactions?'  # ok but required sample
        question='What are the dates and amounts of cash transactions?'
        question='Where are the ATMs?'
        question='List of all banks and amounts sent and received?' #err on Union 
        
        # Multiple questions really:
        question='Top ATM used, Top bank used, Top Loan accounts, Top Credit Card Accounts'
        question='List checks written to cash'
        
        print ("[asking]: ",question)
        answer,answer_dict=Bot.handle_bot_query(question)
        print ("[asking]: ",question)
        print ("[answer]: ",answer)
        print ("[answer]: ",answer_dict)
        #  fp.write(df.to_string(index=False))
        if 'df' in answer_dict:
            print(answer_dict['df'].to_string(index=False))
        a=kkk

    date = str(time.strftime("%Y-%m-%d-%H:%M"))
    date=re.sub(r'\:','-',str(date))
    report_filename=LOCAL_PATH+"dev_reports/50qs-"+case_id+"-"+date+".txt"
    
    fp=codecs.open(report_filename,"w","utf-8")
    fp.write("[50Q Report for: "+case_id+" ran on: "+str(datetime.datetime.now()))
    fp.write("\n")
    
    mega_start=time.time()
    c=0
    for question in q50:
        c+=1
        print ("for question: "+str(question))
        fp.write(str(c)+"="*50+"\n")
        fp.write("[question]: "+question+"\n")
        start_time=time.time()
        answer,answer_dict=Bot.handle_bot_query(question,allow_cached=False)
        fp.write("[runtime]: "+str(time.time()-start_time)+"\n")
        print ("ANSWER: "+str(answer))
        fp.write("[answer]: "+str(answer)+"\n")
        if 'df' in answer_dict:
            fp.write("[df]: "+str(answer_dict['df'].to_string(index=False))+"\n")
        
        fp.flush()

    full_runtime=time.time()-mega_start
    print ("FUll runtime: "+str(full_runtime))
    fp.write("FUll runtime: "+str(full_runtime)+"\n")
    fp.close()
    print ("WROTE TO: "+str(report_filename))

    return


q50=[]
q50+=["What is the Primary account number for bank statement? "]
q50+=["What is the beginning monthly balance?  "]
q50+=["What is the date the Account Opened? "]
q50+=["What are the total deposits and additions?  "]
q50+=["What is the total deposits and additions for the Month?  "]
q50+=["What is the total deposits and additions for the Year?  "]
q50+=["What is the total deposits and additions for the Quarter? "]
q50+=["What is the total deposits and additions for the Day? "]
q50+=["What are the total deposits for the Month?  "]
q50+=["What are the total deposits for the Year? "]
q50+=["What are the total deposits for the Quarter? "]
q50+=["What are the total deposits for the Day?  "]
q50+=["What are the total inflows? "]
q50+=["What is the total number of outflows? (Defined as money going out, so leaving account)  "]
q50+=["What is the total number of outflows via cash withdrawal? "]
q50+=["What is the total number of outflows via check?  "]
q50+=["What is the total number of outflows via credit card payments? "]
q50+=["What is the total number of outflows via Zelle, and what is the ID number? "]
q50+=["What is the total number of outflows via Wire? "]
q50+=["What is the total number of outflows via bank fees? "]
q50+=["What % of the withdrawals are ATM vs debit card? "]
q50+=["How many electronic withdrawals occurred in total by day, month, year and quarter? "]
q50+=["How many electronic withdrawals occurred by Wire "]
q50+=["How many electronic withdrawals occurred by Zelle,  "]
q50+=["What is the ending balance of the statement by Date? "]
q50+=["How many book transfer credits occurred? Between which entity? From which bank? On which date, for how much money?  "]
q50+=["How many Zelle payments were made over the course of the month? Id Accounts sent and received? "]
q50+=["How many Fed Wire credits came in during the month? ID accounts sent and received. "]
q50+=["What is the payment ID on Zelle Transfers? "]
q50+=["List of all companies where monies were sent and received? "]
q50+=["List of all banks and amounts sent and received? "]
q50+=["Top ATM used, Top bank used, Top Loan accounts, Top Credit Card Accounts "]
q50+=["List top 10 payees for time-period with totals for each"]
q50+=["List top 10 payors for time-period with totals for each"]
q50+=["List all payments to IRS and total amount."]
q50+=["List all payees/payors that paid/received with the last five digits of amount as 000.00 and list the amount."]
q50+=["List all ATM transactions by location."]
q50+=["List all ATM transactions in order of amounts."]
q50+=["List credit card payments in order of amount and total."]
q50+=["List all Debit transactions by location."]
q50+=["List all Debit transactions by amount."]
q50+=["List Venmo transactions by top recipient/receiver"]
q50+=["List all Credit Cards paid."]
q50+=["List all Debit cards on the account."]
q50+=["List any transactions that use the word “Airport.”"]
q50+=["List any transactions that use the word “Ammo.”"]
q50+=["List any transactions that use the word “Chemical.”"]
q50+=["Program needs to list out all transactions related to a specific word or word string. "]
q50+=["List all cash transactions, Deposit, Check written to “Cash,” and ATM withdrawal. "]

if __name__=='__main__':
    branches=['auto_run_50q']
    for b in branches:
        globals()[b]()








