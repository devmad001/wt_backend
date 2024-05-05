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

from get_logger import setup_logging
logging=setup_logging()


#0v1# JC  Nov  7, 2023  Init



"""
    EXTENDED DETAILS FOR EACH QUESTION OPTION
    - hard code guildance etc.
    - v_questions/*
"""


qq={}
qq['id']='q1'
qq['org_desc']='How many transactions?'
qq['variations']=['How many transactions?','How many transactions','How many transactions are there?']
qq['question_id_tag']='q1_how_many_t'
qq['llm_helpers']=['[llm_prompt] inject prompt bullets','[llm_prompt] inject Q&A cypher samples'] 
qq['cypher_query']='match (n:main_account) return count(n)'
qq['cypher_query_samples']=['match (n:main_account) return count(n)','match (n:main_account) return count(n) limit 1']
qq['answer_score']=0.50
qq['answer']='There are 100 transactions'
qq['multimodal']={}


def get_qq(id):
    qq={}
    qq['org_desc']=''
    qq['variations']=[]
    qq['question_id_tag']='' #id_*
    qq['llm_helpers']={} #['[llm_prompt] inject prompt bullets','[llm_prompt] inject Q&A cypher samples'] 
    qq['cypher_query']='' #'match (n:main_account) return count(n)'
    qq['cypher_query_variations']=[] #'match (n:main_account) return count(n)','match (n:main_account) return count(n) limit 1']
    qq['cypher_query_samples']=[] #'match (n:main_account) return count(n)','match (n:main_account) return count(n) limit 1']
    qq['answer_score']=0  #0.50
    qq['answer']='' #There are 100 transactions'
    qq['multimodal']={}
    
    ## Extra:
    #(ie likely not hard coded)
    qq['difficulty']=0.50
    return qq

## Q1:  What is the account holder?
qq=get_qq('q1')
qq['org_desc']='What is the Primary account number for bank statement?")'
qq['variations']=['What are the account numbers?']
qq['question_id_tag']='q1_account_number'
qq['llm_helpers']=['- The account number is usually on the first page']
qq['cypher_query']='match (n:main_account) return count(n)'
qq['cypher_query_variations']=['match (n:main_account) return count(n)','match (n:main_account) return count(n) limit 1']
qq['cypher_query_samples']=['match (n:main_account) return count(n)','match (n:main_account) return count(n) limit 1']
qq['answer_score']=0.85
qq['answer']='The primary account number is: 002323421111'
qq['multimodal']={}
guides[qq['id']]=qq


############################################
############################################

guildes={}

## Q1: What is the Primary account number for bank statement?
qq = get_qq('q1')
qq['org_desc'] = "What is the Primary account number for bank statement?"
qq['variations'] = ["What are the account numbers?"]
qq['question_id_tag'] = 'q1_account_number'
qq['llm_helpers'] = ["- The account number is usually on the first page"]
qq['cypher_query'] = 'MATCH (n:main_account) RETURN n.account_number'
qq['cypher_query_variations'] = ['MATCH (n:main_account) RETURN n.account_number', 'MATCH (n:main_account) RETURN n.account_number LIMIT 1']
qq['cypher_query_samples'] = ['MATCH (n:main_account) RETURN n.account_number', 'MATCH (n:main_account) RETURN n.account_number LIMIT 1']
qq['answer_score'] = 0.85
qq['answer'] = 'The primary account number is: 002323421111'
qq['multimodal'] = {}
guides[qq['question_id_tag']] = qq

## Q2: What is the beginning monthly balance?
qq = get_qq('q2')
qq['org_desc'] = "What is the beginning monthly balance?"
qq['variations'] = ["What's the starting balance for the month?"]
qq['question_id_tag'] = 'q2_beginning_balance'
qq['llm_helpers'] = ["- Look for the 'beginning balance' or 'previous balance' on the statement."]
qq['cypher_query'] = 'MATCH (n:BankStatement) RETURN n.beginning_balance'
qq['cypher_query_variations'] = ['MATCH (n:BankStatement) RETURN n.beginning_balance', 'MATCH (n:BankStatement) RETURN n.beginning_balance LIMIT 1']
qq['cypher_query_samples'] = ['MATCH (n:BankStatement) RETURN n.beginning_balance', 'MATCH (n:BankStatement) RETURN n.beginning_balance LIMIT 1']
qq['answer_score'] = 0.85
qq['answer'] = 'The beginning monthly balance is: $3,250.00'
qq['multimodal'] = {}
guides[qq['question_id_tag']] = qq

## Q3: What is the date the Account Opened?
qq = get_qq('q3')
qq['org_desc'] = "What is the date the Account Opened?"
qq['variations'] = ["On what date was the account first opened?"]
qq['question_id_tag'] = 'q3_account_open_date'
qq['llm_helpers'] = ["- The opening date may be found in the account's details section or contract."]
qq['cypher_query'] = 'MATCH (n:Account) RETURN n.opened_date'
qq['cypher_query_variations'] = ['MATCH (n:Account) RETURN n.opened_date', 'MATCH (n:Account) RETURN n.opened_date LIMIT 1']
qq['cypher_query_samples'] = ['MATCH (n:Account) RETURN n.opened_date', 'MATCH (n:Account) RETURN n.opened_date LIMIT 1']
qq['answer_score'] = 0.85
qq['answer'] = 'The account was opened on: 01/06/2015'
qq['multimodal'] = {}
guides[qq['question_id_tag']] = qq

## Q4: What are the total deposits and additions?
qq = get_qq('q4')
qq['org_desc'] = "What are the total deposits and additions?"
qq['variations'] = ["What's the total amount of deposits and additions?"]
qq['question_id_tag'] = 'q4_total_deposits_additions'
qq['llm_helpers'] = ["- Sum up all deposit transactions listed on the statement."]
qq['cypher_query'] = 'MATCH (n:Transaction {type: "Deposit"}) RETURN SUM(n.amount)'
qq['cypher_query_variations'] = ['MATCH (n:Transaction {type: "Deposit"}) RETURN SUM(n.amount)', 'MATCH (n:Transaction {type: "Deposit"}) RETURN SUM(n.amount) LIMIT 10']
qq['cypher_query_samples'] = ['MATCH (n:Transaction {type: "Deposit"}) RETURN SUM(n.amount)', 'MATCH (n:Transaction {type: "Deposit"}) RETURN SUM(n.amount) LIMIT 10']
qq['answer_score'] = 0.85
qq['answer'] = 'The total of deposits and additions is: $10,000'
qq['multimodal'] = {}
guides[qq['question_id_tag']] = qq

## Q5: What is the total deposits and additions for the Month?
qq = get_qq('q5')
qq['org_desc'] = "What is the total deposits and additions for the Month?"
qq['variations'] = ["What's the sum of monthly deposits and additions?"]
qq['question_id_tag'] = 'q5_monthly_deposits_additions'
qq['llm_helpers'] = ["- Total monthly deposits and additions can be calculated by summing all deposits within the month."]
qq['cypher_query'] = 'MATCH (n:Transaction {type: "Deposit"}) WHERE n.date >= "2023-01-01" AND n.date < "2023-02-01" RETURN SUM(n.amount)'
qq['cypher_query_variations'] = ['MATCH (n:Transaction {type: "Deposit"}) WHERE n.date >= "2023-01-01" AND n.date < "2023-02-01" RETURN SUM(n.amount)']
qq['cypher_query_samples'] = ['MATCH (n:Transaction {type: "Deposit"}) WHERE n.date >= "2023-01-01" AND n.date < "2023-02-01" RETURN SUM(n.amount)']
qq['answer_score'] = 0.85
qq['answer'] = 'The total deposits and additions for the month are: $5,000'
qq['multimodal'] = {}
guides[qq['question_id_tag']] = qq

## Q6: What is the total deposits and additions for the Year?
qq = get_qq('q6')
qq['org_desc'] = "What is the total deposits and additions for the Year?"
qq['variations'] = ["What's the annual total of deposits and additions?"]
qq['question_id_tag'] = 'q6_annual_deposits_additions'
qq['llm_helpers'] = ["- To find the annual total, add all deposits listed from the start to the end of the year."]
qq['cypher_query'] = 'MATCH (n:Transaction {type: "Deposit"}) WHERE n.date >= "2023-01-01" AND n.date <= "2023-12-31" RETURN SUM(n.amount)'
qq['cypher_query_variations'] = ['MATCH (n:Transaction {type: "Deposit"}) WHERE n.date >= "2023-01-01" AND n.date <= "2023-12-31" RETURN SUM(n.amount)']
qq['cypher_query_samples'] = ['MATCH (n:Transaction {type: "Deposit"}) WHERE n.date >= "2023-01-01" AND n.date <= "2023-12-31" RETURN SUM(n.amount)']
qq['answer_score'] = 0.85
qq['answer'] = 'The total deposits and additions for the year are: $60,000'
qq['multimodal'] = {}
guides[qq['question_id_tag']] = qq

## Q7: What is the total deposits and additions for the Quarter?
qq = get_qq('q7')
qq['org_desc'] = "What is the total deposits and additions for the Quarter?"
qq['variations'] = ["What's the quarterly sum of deposits and additions?"]
qq['question_id_tag'] = 'q7_quarterly_deposits_additions'
qq['llm_helpers'] = ["- Quarterly totals can be obtained by adding all deposits for each three-month period."]
qq['cypher_query'] = 'MATCH (n:Transaction {type: "Deposit"}) WHERE n.date >= "2023-04-01" AND n.date < "2023-07-01" RETURN SUM(n.amount)'
qq['cypher_query_variations'] = ['MATCH (n:Transaction {type: "Deposit"}) WHERE n.date >= "2023-04-01" AND n.date < "2023-07-01" RETURN SUM(n.amount)']
qq['cypher_query_samples'] = ['MATCH (n:Transaction {type: "Deposit"}) WHERE n.date >= "2023-04-01" AND n.date < "2023-07-01" RETURN SUM(n.amount)']
qq['answer_score'] = 0.85
qq['answer'] = 'The total deposits and additions for the quarter are: $15,000'
qq['multimodal'] = {}
guides[qq['question_id_tag']] = qq

## Q8: What is the total deposits and additions for the Day?
qq = get_qq('q8')
qq['org_desc'] = "What is the total deposits and additions for the Day?"
qq['variations'] = ["What's the daily total of deposits and additions?"]
qq['question_id_tag'] = 'q8_daily_deposits_additions'
qq['llm_helpers'] = ["- Daily deposit totals are found by summing the deposits for a specific day."]
qq['cypher_query'] = 'MATCH (n:Transaction {type: "Deposit"}) WHERE n.date = "2023-01-15" RETURN SUM(n.amount)'
qq['cypher_query_variations'] = ['MATCH (n:Transaction {type: "Deposit"}) WHERE n.date = "2023-01-15" RETURN SUM(n.amount)']
qq['cypher_query_samples'] = ['MATCH (n:Transaction {type: "Deposit"}) WHERE n.date = "2023-01-15" RETURN SUM(n.amount)']
qq['answer_score'] = 0.85
qq['answer'] = 'The total deposits and additions for the day are: $1,000'
qq['multimodal'] = {}
guides[qq['question_id_tag']] = qq

## Q9: What are the total deposits for the Month?
qq = get_qq('q9')
qq['org_desc'] = "What are the total deposits for the Month?"
qq['variations'] = ["What's the amount of deposits for the month?"]
qq['question_id_tag'] = 'q9_monthly_deposits'
qq['llm_helpers'] = ["- To calculate monthly deposits, sum all deposit transactions for the month."]
qq['cypher_query'] = 'MATCH (n:Transaction {type: "Deposit"}) WHERE n.date >= "2023-01-01" AND n.date < "2023-02-01" RETURN SUM(n.amount)'
qq['cypher_query_variations'] = ['MATCH (n:Transaction {type: "Deposit"}) WHERE n.date >= "2023-01-01" AND n.date < "2023-02-01" RETURN SUM(n.amount)']
qq['cypher_query_samples'] = ['MATCH (n:Transaction {type: "Deposit"}) WHERE n.date >= "2023-01-01" AND n.date < "2023-02-01" RETURN SUM(n.amount)']
qq['answer_score'] = 0.85
qq['answer'] = 'The total deposits for the month are: $4,500'
qq['multimodal'] = {}
guides[qq['question_id_tag']] = qq

## Q10: What are the total deposits for the Year?
qq = get_qq('q10')
qq['org_desc'] = "What are the total deposits for the Year?"
qq['variations'] = ["What's the total annual deposit amount?"]
qq['question_id_tag'] = 'q10_annual_deposits'
qq['llm_helpers'] = ["- Annual deposits are totaled by adding up each deposit transaction throughout the year."]
qq['cypher_query'] = 'MATCH (n:Transaction {type: "Deposit"}) WHERE n.date >= "2023-01-01" AND n.date <= "2023-12-31" RETURN SUM(n.amount)'
qq['cypher_query_variations'] = ['MATCH (n:Transaction {type: "Deposit"}) WHERE n.date >= "2023-01-01" AND n.date <= "2023-12-31" RETURN SUM(n.amount)']
qq['cypher_query_samples'] = ['MATCH (n:Transaction {type: "Deposit"}) WHERE n.date >= "2023-01-01" AND n.date <= "2023-12-31" RETURN SUM(n.amount)']
qq['answer_score'] = 0.85
qq['answer'] = 'The total deposits for the year are: $55,000'
qq['multimodal'] = {}
guides[qq['question_id_tag']] = qq

## Q11: What are the total deposits for the Quarter?
qq = get_qq('q11')
qq['org_desc'] = "What are the total deposits for the Quarter?"
qq['variations'] = ["What's the total deposit amount for the quarter?"]
qq['question_id_tag'] = 'q11_quarterly_deposits'
qq['llm_helpers'] = ["- Quarterly deposits can be computed by summing all deposit transactions within the three-month period."]
qq['cypher_query'] = 'MATCH (n:Transaction {type: "Deposit"}) WHERE n.date >= "2023-04-01" AND n.date < "2023-07-01" RETURN SUM(n.amount)'
qq['cypher_query_variations'] = ['MATCH (n:Transaction {type: "Deposit"}) WHERE n.date >= "2023-04-01" AND n.date < "2023-07-01" RETURN SUM(n.amount)']
qq['cypher_query_samples'] = ['MATCH (n:Transaction {type: "Deposit"}) WHERE n.date >= "2023-04-01" AND n.date < "2023-07-01" RETURN SUM(n.amount)']
qq['answer_score'] = 0.85
qq['answer'] = 'The total deposits for the quarter are: $14,000'
qq['multimodal'] = {}
guides[qq['question_id_tag']] = qq

## Q12: What are the total deposits for the Day?
qq = get_qq('q12')
qq['org_desc'] = "What are the total deposits for the Day?"
qq['variations'] = ["What's the total amount deposited today?"]
qq['question_id_tag'] = 'q12_daily_deposits'
qq['llm_helpers'] = ["- Daily deposits are the sum of all deposits made on a specific day."]
qq['cypher_query'] = 'MATCH (n:Transaction {type: "Deposit"}) WHERE n.date = "2023-01-15" RETURN SUM(n.amount)'
qq['cypher_query_variations'] = ['MATCH (n:Transaction {type: "Deposit"}) WHERE n.date = "2023-01-15" RETURN SUM(n.amount)']
qq['cypher_query_samples'] = ['MATCH (n:Transaction {type: "Deposit"}) WHERE n.date = "2023-01-15" RETURN SUM(n.amount)']
qq['answer_score'] = 0.85
qq['answer'] = 'The total deposits for the day are: $1,200'
qq['multimodal'] = {}
guides[qq['question_id_tag']] = qq

## Q13: What are the total inflows?
#[x] qa ok 1
qq = get_qq('q13')
qq['org_desc'] = "What are the total inflows?"
qq['variations'] = ["What's the sum of all incoming transactions?"]
qq['question_id_tag'] = 'q13_total_inflows'
qq['llm_helpers'] = ["- Inflows refer to all money received; sum all transactions categorized as 'inflow'."]
qq['cypher_query'] = 'MATCH (n:Transaction {direction: "Inflow"}) RETURN SUM(n.amount)'
qq['cypher_query_variations'] = ['MATCH (n:Transaction {direction: "Inflow"}) RETURN SUM(n.amount)']
qq['cypher_query_samples'] = ['MATCH (n:Transaction {direction: "Inflow"}) RETURN SUM(n.amount)']
qq['answer_score'] = 0.85
qq['answer'] = 'The total inflows are: $75,000'
qq['multimodal'] = {}
guides[qq['question_id_tag']] = qq

## Q14: What is the total number of outflows? (Defined as money going out, so leaving the account)
qq = get_qq('q14')
qq['org_desc'] = "What is the total number of outflows? (Defined as money going out, so leaving the account)"
qq['variations'] = ["How many outflow transactions have there been?"]
qq['question_id_tag'] = 'q14_total_outflows'
qq['llm_helpers'] = ["- Count all transactions that are categorized as 'outflow'."]
qq['cypher_query'] = 'MATCH (n:Transaction {direction: "Outflow"}) RETURN COUNT(n)'
qq['cypher_query_variations'] = ['MATCH (n:Transaction {direction: "Outflow"}) RETURN COUNT(n)']
qq['cypher_query_samples'] = ['MATCH (n:Transaction {direction: "Outflow"}) RETURN COUNT(n)']
qq['answer_score'] = 0.85
qq['answer'] = 'The total number of outflows is: 150'
qq['multimodal'] = {}
guides[qq['question_id_tag']] = qq

## Q15: What is the total number of outflows via cash withdrawal?
qq = get_qq('q15')
qq['org_desc'] = "What is the total number of outflows via cash withdrawal?"
qq['variations'] = ["How many cash withdrawals have been made?"]
qq['question_id_tag'] = 'q15_cash_withdrawals'
qq['llm_helpers'] = ["- Sum up all transactions labeled as 'cash withdrawal'."]
qq['cypher_query'] = 'MATCH (n:Transaction {method: "Cash Withdrawal"}) RETURN COUNT(n)'
qq['cypher_query_variations'] = ['MATCH (n:Transaction {method: "Cash Withdrawal"}) RETURN COUNT(n)']
qq['cypher_query_samples'] = ['MATCH (n:Transaction {method: "Cash Withdrawal"}) RETURN COUNT(n)']
qq['answer_score'] = 0.85
qq['answer'] = 'The total number of outflows via cash withdrawal is: 30'
qq['multimodal'] = {}
guides[qq['question_id_tag']] = qq

## Q16: What is the total number of outflows via check?
qq = get_qq('q16')
qq['org_desc'] = "What is the total number of outflows via check?"
qq['variations'] = ["How many checks have been issued?"]
qq['question_id_tag'] = 'q16_checks_issued'
qq['llm_helpers'] = ["- Count all transactions made by check."]
qq['cypher_query'] = 'MATCH (n:Transaction {method: "Check"}) RETURN COUNT(n)'
qq['cypher_query_variations'] = ['MATCH (n:Transaction {method: "Check"}) RETURN COUNT(n)']
qq['cypher_query_samples'] = ['MATCH (n:Transaction {method: "Check"}) RETURN COUNT(n)']
qq['answer_score'] = 0.85
qq['answer'] = 'The total number of outflows via check is: 45'
qq['multimodal'] = {}
guides[qq['question_id_tag']] = qq

## Q17: What is the total number of outflows via credit card payments?
qq = get_qq('q17')
qq['org_desc'] = "What is the total number of outflows via credit card payments?"
qq['variations'] = ["How many credit card payments have been made?"]
qq['question_id_tag'] = 'q17_credit_card_payments'
qq['llm_helpers'] = ["- Tally up all credit card payment transactions."]
qq['cypher_query'] = 'MATCH (n:Transaction {method: "Credit Card Payment"}) RETURN COUNT(n)'
qq['cypher_query_variations'] = ['MATCH (n:Transaction {method: "Credit Card Payment"}) RETURN COUNT(n)']
qq['cypher_query_samples'] = ['MATCH (n:Transaction {method: "Credit Card Payment"}) RETURN COUNT(n)']
qq['answer_score'] = 0.85
qq['answer'] = 'The total number of outflows via credit card payments is: 25'
qq['multimodal'] = {}
guides[qq['question_id_tag']] = qq

## Q18: What is the total number of outflows via Zelle, and what is the ID number?
qq = get_qq('q18')
qq['org_desc'] = "What is the total number of outflows via Zelle, and what is the ID number?"
qq['variations'] = ["How many Zelle transactions have there been, and what are their ID numbers?"]
qq['question_id_tag'] = 'q18_zelle_transactions'
qq['llm_helpers'] = ["- Count the Zelle transactions and retrieve their ID numbers."]
qq['cypher_query'] = 'MATCH (n:Transaction {method: "Zelle"}) RETURN COUNT(n), n.id'
qq['cypher_query_variations'] = ['MATCH (n:Transaction {method: "Zelle"}) RETURN COUNT(n), n.id']
qq['cypher_query_samples'] = ['MATCH (n:Transaction {method: "Zelle"}) RETURN COUNT(n), n.id']
qq['answer_score'] = 0.85
qq['answer'] = 'The total number of outflows via Zelle is: 20, with ID numbers ranging from Z001 to Z020'
qq['multimodal'] = {}
guides[qq['question_id_tag']] = qq

## Q19: What is the total number of outflows via Wire?
qq = get_qq('q19')
qq['org_desc'] = "What is the total number of outflows via Wire?"
qq['variations'] = ["How many wire transfers have been made?"]
qq['question_id_tag'] = 'q19_wire_transfers'
qq['llm_helpers'] = ["- Add up all transactions conducted via wire transfer."]
qq['cypher_query'] = 'MATCH (n:Transaction {method: "Wire Transfer"}) RETURN COUNT(n)'
qq['cypher_query_variations'] = ['MATCH (n:Transaction {method: "Wire Transfer"}) RETURN COUNT(n)']
qq['cypher_query_samples'] = ['MATCH (n:Transaction {method: "Wire Transfer"}) RETURN COUNT(n)']
qq['answer_score'] = 0.85
qq['answer'] = 'The total number of outflows via wire transfer is: 10'
qq['multimodal'] = {}
guides[qq['question_id_tag']] = qq

## Q20: What is the total number of outflows via bank fees?
qq = get_qq('q20')
qq['org_desc'] = "What is the total number of outflows via bank fees?"
qq['variations'] = ["How many transactions were for bank fees?"]
qq['question_id_tag'] = 'q20_bank_fees'
qq['llm_helpers'] = ["- Count all transactions that are labeled as bank fees."]
qq['cypher_query'] = 'MATCH (n:Transaction {type: "Bank Fee"}) RETURN COUNT(n)'
qq['cypher_query_variations'] = ['MATCH (n:Transaction {type: "Bank Fee"}) RETURN COUNT(n)']
qq['cypher_query_samples'] = ['MATCH (n:Transaction {type: "Bank Fee"}) RETURN COUNT(n)']
qq['answer_score'] = 0.85
qq['answer'] = 'The total number of outflows via bank fees is: 15'
qq['multimodal'] = {}
guides[qq['question_id_tag']] = qq

## Q21: What % of the withdrawals are ATM vs debit card?
qq = get_qq('q21')
qq['org_desc'] = "What % of the withdrawals are ATM vs debit card?"
qq['variations'] = ["What is the percentage breakdown of ATM withdrawals compared to debit card withdrawals?"]
qq['question_id_tag'] = 'q21_atm_vs_debit'
qq['llm_helpers'] = ["- Calculate the proportion of ATM withdrawals against debit card withdrawals and express it as a percentage."]
qq['cypher_query'] = 'MATCH (atm:Transaction {method: "ATM"}), (debit:Transaction {method: "Debit Card"}) RETURN COUNT(atm), COUNT(debit)'
qq['cypher_query_variations'] = ['MATCH (atm:Transaction {method: "ATM"}), (debit:Transaction {method: "Debit Card"}) RETURN COUNT(atm), COUNT(debit']
qq['cypher_query_samples'] = ['MATCH (atm:Transaction {method: "ATM"}), (debit:Transaction {method: "Debit Card"}) RETURN COUNT(atm), COUNT(debit']
qq['answer_score'] = 0.85
qq['answer'] = 'ATM withdrawals are 40%, and debit card withdrawals are 60%.'
qq['multimodal'] = {}
guides[qq['question_id_tag']] = qq

## Q22: How many electronic withdrawals occurred in total by day, month, year and quarter?
qq = get_qq('q22')
qq['org_desc'] = "How many electronic withdrawals occurred in total by day, month, year and quarter?"
qq['variations'] = ["Can you provide the total number of electronic withdrawals for each day, month, year, and quarter?"]
qq['question_id_tag'] = 'q22_electronic_withdrawals'
qq['llm_helpers'] = ["- Tally electronic withdrawals daily, monthly, annually, and quarterly."]
qq['cypher_query'] = 'MATCH (n:Transaction {type: "Electronic Withdrawal"}) RETURN n.date, COUNT(n)'
qq['cypher_query_variations'] = ['MATCH (n:Transaction {type: "Electronic Withdrawal"}) RETURN n.date, COUNT(n)']
qq['cypher_query_samples'] = ['MATCH (n:Transaction {type: "Electronic Withdrawal"}) RETURN n.date, COUNT(n)']
qq['answer_score'] = 0.85
qq['answer'] = 'Total electronic withdrawals: Daily: 5, Monthly: 150, Annually: 1800, Quarterly: 450.'
qq['multimodal'] = {}
guides[qq['question_id_tag']] = qq

## Q23: How many electronic withdrawals occurred by Wire
qq = get_qq('q23')
qq['org_desc'] = "How many electronic withdrawals occurred by Wire"
qq['variations'] = ["What is the number of wire withdrawal transactions?"]
qq['question_id_tag'] = 'q23_wire_withdrawals'
qq['llm_helpers'] = ["- Count the transactions classified as wire withdrawals."]
qq['cypher_query'] = 'MATCH (n:Transaction {method: "Wire Transfer"}) RETURN COUNT(n)'
qq['cypher_query_variations'] = ['MATCH (n:Transaction {method: "Wire Transfer"}) RETURN COUNT(n)']
qq['cypher_query_samples'] = ['MATCH (n:Transaction {method: "Wire Transfer"}) RETURN COUNT(n)']
qq['answer_score'] = 0.85
qq['answer'] = 'The number of electronic withdrawals by wire is: 20.'
qq['multimodal'] = {}
guides[qq['question_id_tag']] = qq

## Q24: How many electronic withdrawals occurred by Zelle
qq = get_qq('q24')
qq['org_desc'] = "How many electronic withdrawals occurred by Zelle"
qq['variations'] = ["Can you count the number of Zelle withdrawals?"]
qq['question_id_tag'] = 'q24_zelle_withdrawals'
qq['llm_helpers'] = ["- Sum up all the withdrawal transactions made through Zelle."]
qq['cypher_query'] = 'MATCH (n:Transaction {method: "Zelle"}) RETURN COUNT(n)'
qq['cypher_query_variations'] = ['MATCH (n:Transaction {method: "Zelle"}) RETURN COUNT(n)']
qq['cypher_query_samples'] = ['MATCH (n:Transaction {method: "Zelle"}) RETURN COUNT(n)']
qq['answer_score'] = 0.85
qq['answer'] = 'The total number of Zelle withdrawals is: 25.'
qq['multimodal'] = {}
guides[qq['question_id_tag']] = qq

## Q25: What is the ending balance of the statement by Date?
qq = get_qq('q25')
qq['org_desc'] = "What is the ending balance of the statement by Date?"
qq['variations'] = ["What are the final balances on the statements for each date?"]
qq['question_id_tag'] = 'q25_ending_balance_by_date'
qq['llm_helpers'] = ["- Retrieve the closing balance for each date on bank statements."]
qq['cypher_query'] = 'MATCH (n:BankStatement) RETURN n.date, n.ending_balance'
qq['cypher_query_variations'] = ['MATCH (n:BankStatement) RETURN n.date, n.ending_balance']
qq['cypher_query_samples'] = ['MATCH (n:BankStatement) RETURN n.date, n.ending_balance']
qq['answer_score'] = 0.85
qq['answer'] = 'Ending balances are: Date 1: $2,000, Date 2: $2,500, ...'
qq['multimodal'] = {}
guides[qq['question_id_tag']] = qq

## Q26: How many book transfer credits occurred? Between which entity? From which bank? On which date, for how much money?
qq = get_qq('q26')
qq['org_desc'] = "How many book transfer credits occurred? Between which entity? From which bank? On which date, for how much money?"
qq['variations'] = ["What are the details of book transfer credits?"]
qq['question_id_tag'] = 'q26_book_transfer_credits'
qq['llm_helpers'] = ["- List all book transfer credits, including entities involved, banks, dates, and amounts."]
qq['cypher_query'] = 'MATCH (n:Transaction {type: "Book Transfer Credit"}) RETURN n.entity, n.from_bank, n.date, n.amount'
qq['cypher_query_variations'] = ['MATCH (n:Transaction {type: "Book Transfer Credit"}) RETURN n.entity, n.from_bank, n.date, n.amount']
qq['cypher_query_samples'] = ['MATCH (n:Transaction {type: "Book Transfer Credit"}) RETURN n.entity, n.from_bank, n.date, n.amount']
qq['answer_score'] = 0.85
qq['answer'] = 'There were 10 book transfer credits, from various entities and banks, on dates ranging from 01/01 to 12/31, for amounts between $500 to $5,000.'
qq['multimodal'] = {}
guides[qq['question_id_tag']] = qq

## Q27: How many book transfer credits occurred? Between which entity? From which bank? On which date, for how much money?
qq = get_qq('q27')
qq['org_desc'] = "How many book transfer credits occurred? Between which entity? From which bank? On which date, for how much money?"
qq['variations'] = ["Can you detail the book transfer credits, including entities, banks, dates, and amounts?"]
qq['question_id_tag'] = 'q27_book_transfer_details'
qq['llm_helpers'] = ["- Look for transactions classified as 'Book Transfer Credit' and provide the count and details."]
qq['cypher_query'] = 'MATCH (t:Transaction {type: "Book Transfer Credit"}) RETURN t.entity, t.from_bank, t.date, t.amount'
qq['cypher_query_variations'] = ['MATCH (t:Transaction {type: "Book Transfer Credit"}) RETURN t.entity, t.from_bank, t.date, t.amount']
qq['cypher_query_samples'] = ['MATCH (t:Transaction {type: "Book Transfer Credit"}) RETURN t.entity, t.from_bank, t.date, t.amount']
qq['answer_score'] = 0.85
qq['answer'] = 'There were 5 book transfer credits between Entity A and Entity B from XYZ Bank on various dates for amounts ranging from $1,000 to $5,000.'
qq['multimodal'] = {}
guides[qq['question_id_tag']] = qq

## Q28: How many Zelle payments were made over the course of the month? Id Accounts sent and received?
qq = get_qq('q28')
qq['org_desc'] = "How many Zelle payments were made over the course of the month? Id Accounts sent and received?"
qq['variations'] = ["What's the count of Zelle payments this month, and can you identify the accounts involved?"]
qq['question_id_tag'] = 'q28_zelle_payments_details'
qq['llm_helpers'] = ["- Tally the Zelle payments and identify the sending and receiving accounts."]
qq['cypher_query'] = 'MATCH (t:Transaction {method: "Zelle"}) WHERE t.date >= "2023-01-01" AND t.date <= "2023-01-31" RETURN COUNT(t), t.from_account, t.to_account'
qq['cypher_query_variations'] = ['MATCH (t:Transaction {method: "Zelle"}) WHERE t.date >= "2023-01-01" AND t.date <= "2023-01-31" RETURN COUNT(t), t.from_account, t.to_account']
qq['cypher_query_samples'] = ['MATCH (t:Transaction {method: "Zelle"}) WHERE t.date >= "2023-01-01" AND t.date <= "2023-01-31" RETURN COUNT(t), t.from_account, t.to_account']
qq['answer_score'] = 0.85
qq['answer'] = 'There were 20 Zelle payments made in the month, involving accounts IDs ranging from 1001 to 1020.'
qq['multimodal'] = {}
guides[qq['question_id_tag']] = qq

## Q29: How many Fed Wire credits came in during the month? ID accounts sent and received.
qq = get_qq('q29')
qq['org_desc'] = "How many Fed Wire credits came in during the month? ID accounts sent and received."
qq['variations'] = ["Can you provide the number of Fed Wire credits this month along with the account IDs?"]
qq['question_id_tag'] = 'q29_fed_wire_credits'
qq['llm_helpers'] = ["- Count the number of Fed Wire credits received and the accounts involved."]
qq['cypher_query'] = 'MATCH (t:Transaction {method: "Fed Wire"}) WHERE t.date >= "2023-01-01" AND t.date <= "2023-01-31" RETURN COUNT(t), t.from_account, t.to_account'
qq['cypher_query_variations'] = ['MATCH (t:Transaction {method: "Fed Wire"}) WHERE t.date >= "2023-01-01" AND t.date <= "2023-01-31" RETURN COUNT(t), t.from_account, t.to_account']
qq['cypher_query_samples'] = ['MATCH (t:Transaction {method: "Fed Wire"}) WHERE t.date >= "2023-01-01" AND t.date <= "2023-01-31" RETURN COUNT(t), t.from_account, t.to_account']
qq['answer_score'] = 0.85
qq['answer'] = '30 Fed Wire credits were received this month, with account IDs from 2001 to 2030.'
qq['multimodal'] = {}
guides[qq['question_id_tag']] = qq

## Q30: What is the payment ID on Zelle Transfers?
qq = get_qq('q30')
qq['org_desc'] = "What is the payment ID on Zelle Transfers?"
qq['variations'] = ["Can you list the payment IDs for Zelle transfers?"]
qq['question_id_tag'] = 'q30_zelle_payment_ids'
qq['llm_helpers'] = ["- Retrieve the payment IDs for all Zelle transfer transactions."]
qq['cypher_query'] = 'MATCH (t:Transaction {method: "Zelle"}) RETURN t.payment_id'
qq['cypher_query_variations'] = ['MATCH (t:Transaction {method: "Zelle"}) RETURN t.payment_id']
qq['cypher_query_samples'] = ['MATCH (t:Transaction {method: "Zelle"}) RETURN t.payment_id']
qq['answer_score'] = 0.85
qq['answer'] = 'Payment IDs for Zelle transfers are ZL100, ZL101, ..., ZL120.'
qq['multimodal'] = {}
guides[qq['question_id_tag']] = qq

## Q31: List of all companies where monies were sent and received?
qq = get_qq('q31')
qq['org_desc'] = "List of all companies where monies were sent and received?"
qq['variations'] = ["Can you provide a list of companies involved in financial transactions?"]
qq['question_id_tag'] = 'q31_companies_transactions'
qq['llm_helpers'] = ["- Compile a list of all companies that have sent or received money."]
qq['cypher_query'] = 'MATCH (t:Transaction) WHERE EXISTS(t.company) RETURN DISTINCT t.company'
qq['cypher_query_variations'] = ['MATCH (t:Transaction) WHERE EXISTS(t.company) RETURN DISTINCT t.company']
qq['cypher_query_samples'] = ['MATCH (t:Transaction) WHERE EXISTS(t.company) RETURN DISTINCT t.company']
qq['answer_score'] = 0.85
qq['answer'] = 'Companies involved in transactions include ABC Corp, XYZ Inc., and 123 Ltd.'
qq['multimodal'] = {}
guides[qq['question_id_tag']] = qq

## Q32: List of all banks and amounts sent and received?
qq = get_qq('q32')
qq['org_desc'] = "List of all banks and amounts sent and received?"
qq['variations'] = ["What are the transaction amounts associated with each bank?"]
qq['question_id_tag'] = 'q32_banks_transactions'
qq['llm_helpers'] = ["- Generate a list of banks involved in transactions along with the amounts sent and received."]
qq['cypher_query'] = 'MATCH (t:Transaction) WHERE EXISTS(t.bank) RETURN t.bank, SUM(t.amount)'
qq['cypher_query_variations'] = ['MATCH (t:Transaction) WHERE EXISTS(t.bank) RETURN t.bank, SUM(t.amount)']
qq['cypher_query_samples'] = ['MATCH (t:Transaction) WHERE EXISTS(t.bank) RETURN t.bank, SUM(t.amount)']
qq['answer_score'] = 0.85
qq['answer'] = 'Banks and transaction amounts: Bank A - $50,000 sent, $45,000 received; Bank B - $30,000 sent, $35,000 received.'
qq['multimodal'] = {}
guides[qq['question_id_tag']] = qq

## Q33: Top ATM used, Top bank used, Top Loan accounts, Top Credit Card Accounts
qq = get_qq('q33')
qq['org_desc'] = "Top ATM used, Top bank used, Top Loan accounts, Top Credit Card Accounts"
qq['variations'] = ["Can you identify the most frequently used ATMs, banks, loan accounts, and credit card accounts?"]
qq['question_id_tag'] = 'q33_top_used_services'
qq['llm_helpers'] = ["- Determine the most frequently used ATMs, banks, loan and credit card accounts based on transaction counts."]
qq['cypher_query'] = 'MATCH (t:Transaction) WHERE EXISTS(t.atm_id) OR EXISTS(t.bank) OR EXISTS(t.loan_account) OR EXISTS(t.credit_card_account) RETURN t.atm_id, t.bank, t.loan_account, t.credit_card_account, COUNT(t) ORDER BY COUNT(t) DESC'
qq['cypher_query_variations'] = ['MATCH (t:Transaction) WHERE EXISTS(t.atm_id) OR EXISTS(t.bank) OR EXISTS(t.loan_account) OR EXISTS(t.credit_card_account) RETURN t.atm_id, t.bank, t.loan_account, t.credit_card_account, COUNT(t) ORDER BY COUNT(t) DESC']
qq['cypher_query_samples'] = ['MATCH (t:Transaction) WHERE EXISTS(t.atm_id) OR EXISTS(t.bank) OR EXISTS(t.loan_account) OR EXISTS(t.credit_card_account) RETURN t.atm_id, t.bank, t.loan_account, t.credit_card_account, COUNT(t) ORDER BY COUNT(t) DESC']
qq['answer_score'] = 0.85
qq['answer'] = 'Top ATM ID: ATM123, Top Bank: Bank A, Top Loan Account: LN456, Top Credit Card Account: CC789.'
qq['multimodal'] = {}
guides[qq['question_id_tag']] = qq

## Q34: List top 10 payees for time-period with totals for each
qq = get_qq('q34')
qq['org_desc'] = "List top 10 payees for time-period with totals for each"
qq['variations'] = ["Who are the top 10 payees for the selected time-period and what are the total amounts paid to each?"]
qq['question_id_tag'] = 'q34_top_payees'
qq['llm_helpers'] = ["- Extract the top 10 payees based on the total amount paid to each during the specified time-period."]
qq['cypher_query'] = 'MATCH (t:Transaction {direction: "Outflow"}) RETURN t.payee, SUM(t.amount) ORDER BY SUM(t.amount) DESC LIMIT 10'
qq['cypher_query_variations'] = ['MATCH (t:Transaction {direction: "Outflow"}) RETURN t.payee, SUM(t.amount) ORDER BY SUM(t.amount) DESC LIMIT 10']
qq['cypher_query_samples'] = ['MATCH (t:Transaction {direction: "Outflow"}) RETURN t.payee, SUM(t.amount) ORDER BY SUM(t.amount) DESC LIMIT 10']
qq['answer_score'] = 0.85
qq['answer'] = 'Top payees and amounts: Payee1 - $10,000, Payee2 - $9,000, ..., Payee10 - $1,000.'
qq['multimodal'] = {}
guides[qq['question_id_tag']] = qq

## Q35: List top 10 payors for time-period with totals for each
qq = get_qq('q35')
qq['org_desc'] = "List top 10 payors for time-period with totals for each"
qq['variations'] = ["Who are the top 10 payors for the selected time-period and what are the total amounts received from each?"]
qq['question_id_tag'] = 'q35_top_payors'
qq['llm_helpers'] = ["- Identify the top 10 payors based on the total amount received from each during the specified time-period."]
qq['cypher_query'] = 'MATCH (t:Transaction {direction: "Inflow"}) RETURN t.payor, SUM(t.amount) ORDER BY SUM(t.amount) DESC LIMIT 10'
qq['cypher_query_variations'] = ['MATCH (t:Transaction {direction: "Inflow"}) RETURN t.payor, SUM(t.amount) ORDER BY SUM(t.amount) DESC LIMIT 10']
qq['cypher_query_samples'] = ['MATCH (t:Transaction {direction: "Inflow"}) RETURN t.payor, SUM(t.amount) ORDER BY SUM(t.amount) DESC LIMIT 10']
qq['answer_score'] = 0.85
qq['answer'] = 'Top payors and amounts: Payor1 - $12,000, Payor2 - $11,000, ..., Payor10 - $2,000.'
qq['multimodal'] = {}
guides[qq['question_id_tag']] = qq

## Q36: List all payments to IRS and total amount.
qq = get_qq('q36')
qq['org_desc'] = "List all payments to IRS and total amount."
qq['variations'] = ["What are all the payments made to the IRS and their total sum?"]
qq['question_id_tag'] = 'q36_irs_payments'
qq['llm_helpers'] = ["- Summarize all payments made to the IRS."]
qq['cypher_query'] = 'MATCH (t:Transaction {payee: "IRS"}) RETURN t.date, t.amount'
qq['cypher_query_variations'] = ['MATCH (t:Transaction {payee: "IRS"}) RETURN t.date, t.amount']
qq['cypher_query_samples'] = ['MATCH (t:Transaction {payee: "IRS"}) RETURN t.date, t.amount']
qq['answer_score'] = 0.85
qq['answer'] = 'Payments to IRS: $2,500 on 01/15, $3,000 on 02/15, ..., Total: $20,000.'
qq['multimodal'] = {}
guides[qq['question_id_tag']] = qq

## Q37: List all payees/payors that paid/received with the last five digits of amount as 000.00 and list the amount.
qq = get_qq('q37')
qq['org_desc'] = "List all payees/payors that paid/received with the last five digits of amount as 000.00 and list the amount."
qq['variations'] = ["Can you provide a list of transactions where the amounts end in 000.00, along with the payees and payors?"]
qq['question_id_tag'] = 'q37_specific_amount_transactions'
qq['llm_helpers'] = ["- Filter transactions where amounts end in '000.00' and provide the associated payees and payors."]
qq['cypher_query'] = 'MATCH (t:Transaction) WHERE t.amount % 1000 = 0 RETURN t.payee, t.payor, t.amount'
qq['cypher_query_variations'] = ['MATCH (t:Transaction) WHERE t.amount % 1000 = 0 RETURN t.payee, t.payor, t.amount']
qq['cypher_query_samples'] = ['MATCH (t:Transaction) WHERE t.amount % 1000 = 0 RETURN t.payee, t.payor, t.amount']
qq['answer_score'] = 0.85
qq['answer'] = 'Transactions with amounts ending in 000.00: Payee1 received $5,000, Payor1 paid $10,000, ...'
qq['multimodal'] = {}
guides[qq['question_id_tag']] = qq


## Q38: List all ATM transactions by location.
qq = get_qq('q38')
qq['org_desc'] = "List all ATM transactions by location."
qq['variations'] = ["What are the ATM transactions sorted by location?"]
qq['question_id_tag'] = 'q38_atm_transactions_location'
qq['llm_helpers'] = ["- Provide a list of ATM transactions categorized by the location of the ATM."]
qq['cypher_query'] = 'MATCH (t:Transaction {method: "ATM"}) RETURN t.location, t.amount'
qq['cypher_query_variations'] = ['MATCH (t:Transaction {method: "ATM"}) RETURN t.location, t.amount ORDER BY t.location']
qq['cypher_query_samples'] = ['MATCH (t:Transaction {method: "ATM"}) RETURN t.location, t.amount ORDER BY t.location']
qq['answer_score'] = 0.85
qq['answer'] = 'ATM transactions: Location1 - $200, Location2 - $150, ...'
qq['multimodal'] = {}
guides[qq['question_id_tag']] = qq

## Q39: List all ATM transactions in order of amounts.
qq = get_qq('q39')
qq['org_desc'] = "List all ATM transactions in order of amounts."
qq['variations'] = ["Can you list ATM transactions by the amount in descending order?"]
qq['question_id_tag'] = 'q39_atm_transactions_amount'
qq['llm_helpers'] = ["- Sort ATM transactions by the amount from highest to lowest."]
qq['cypher_query'] = 'MATCH (t:Transaction {method: "ATM"}) RETURN t.amount ORDER BY t.amount DESC'
qq['cypher_query_variations'] = ['MATCH (t:Transaction {method: "ATM"}) RETURN t.amount ORDER BY t.amount DESC']
qq['cypher_query_samples'] = ['MATCH (t:Transaction {method: "ATM"}) RETURN t.amount ORDER BY t.amount DESC']
qq['answer_score'] = 0.85
qq['answer'] = 'ATM transaction amounts: $300, $250, $200, ...'
qq['multimodal'] = {}
guides[qq['question_id_tag']] = qq

## Q40: List credit card payments in order of amount and total.
qq = get_qq('q40')
qq['org_desc'] = "List credit card payments in order of amount and total."
qq['variations'] = ["What are the credit card payments sorted by amount with a total sum?"]
qq['question_id_tag'] = 'q40_credit_card_payments'
qq['llm_helpers'] = ["- Enumerate credit card payments sorted by amount along with a cumulative total."]
qq['cypher_query'] = 'MATCH (t:Transaction {method: "Credit Card Payment"}) RETURN t.amount ORDER BY t.amount DESC'
qq['cypher_query_variations'] = ['MATCH (t:Transaction {method: "Credit Card Payment"}) RETURN t.amount ORDER BY t.amount DESC']
qq['cypher_query_samples'] = ['MATCH (t:Transaction {method: "Credit Card Payment"}) RETURN t.amount ORDER BY t.amount DESC']
qq['answer_score'] = 0.85
qq['answer'] = 'Credit card payments: $500, $450, $300, ..., Total: $5,000.'
qq['multimodal'] = {}
guides[qq['question_id_tag']] = qq

## Q41: List all Debit transactions by location.
qq = get_qq('q41')
qq['org_desc'] = "List all Debit transactions by location."
qq['variations'] = ["Can you provide a list of Debit transactions categorized by location?"]
qq['question_id_tag'] = 'q41_debit_transactions_location'
qq['llm_helpers'] = ["- List all Debit transactions and group them by the location where they occurred."]
qq['cypher_query'] = 'MATCH (t:Transaction {method: "Debit"}) RETURN t.location, t.amount'
qq['cypher_query_variations'] = ['MATCH (t:Transaction {method: "Debit"}) RETURN t.location, t.amount ORDER BY t.location']
qq['cypher_query_samples'] = ['MATCH (t:Transaction {method: "Debit"}) RETURN t.location, t.amount ORDER BY t.location']
qq['answer_score'] = 0.85
qq['answer'] = 'Debit transactions: Store1 - $150, Gas Station - $75, ...'
qq['multimodal'] = {}
guides[qq['question_id_tag']] = qq

## Q42: List all Debit transactions by amount.
qq = get_qq('q42')
qq['org_desc'] = "List all Debit transactions by amount."
qq['variations'] = ["What are the Debit transaction amounts in descending order?"]
qq['question_id_tag'] = 'q42_debit_transactions_amount'
qq['llm_helpers'] = ["- Sort all Debit transactions by the transaction amount from highest to lowest."]
qq['cypher_query'] = 'MATCH (t:Transaction {method: "Debit"}) RETURN t.amount ORDER BY t.amount DESC'
qq['cypher_query_variations'] = ['MATCH (t:Transaction {method: "Debit"}) RETURN t.amount ORDER BY t.amount DESC']
qq['cypher_query_samples'] = ['MATCH (t:Transaction {method: "Debit"}) RETURN t.amount ORDER BY t.amount DESC']
qq['answer_score'] = 0.85
qq['answer'] = 'Debit transaction amounts: $200, $150, $100, ...'
qq['multimodal'] = {}
guides[qq['question_id_tag']] = qq

## Q43: List Venmo transactions by top recipient/receiver
qq = get_qq('q43')
qq['org_desc'] = "List Venmo transactions by top recipient/receiver"
qq['variations'] = ["Who are the top recipients for Venmo transactions?"]
qq['question_id_tag'] = 'q43_venmo_transactions'
qq['llm_helpers'] = ["- Identify the top recipients of Venmo transactions and list the related transaction details."]
qq['cypher_query'] = 'MATCH (t:Transaction {method: "Venmo"}) RETURN t.receiver, COUNT(t) ORDER BY COUNT(t) DESC'
qq['cypher_query_variations'] = ['MATCH (t:Transaction {method: "Venmo"}) RETURN t.receiver, COUNT(t) ORDER BY COUNT(t) DESC']
qq['cypher_query_samples'] = ['MATCH (t:Transaction {method: "Venmo"}) RETURN t.receiver, COUNT(t) ORDER BY COUNT(t) DESC']
qq['answer_score'] = 0.85
qq['answer'] = 'Top Venmo transaction recipients: Receiver1 - 10 transactions, Receiver2 - 8 transactions, ...'
qq['multimodal'] = {}
guides[qq['question_id_tag']] = qq

## Q44: List all Credit Cards paid.
qq = get_qq('q44')
qq['org_desc'] = "List all Credit Cards paid."
qq['variations'] = ["Can you list all the credit card accounts that have been paid off?"]
qq['question_id_tag'] = 'q44_credit_cards_paid'
qq['llm_helpers'] = ["- Compile a list of all credit card accounts to which payments have been made."]
qq['cypher_query'] = 'MATCH (t:Transaction {type: "Credit Card Payment"}) RETURN DISTINCT t.credit_card_account'
qq['cypher_query_variations'] = ['MATCH (t:Transaction {type: "Credit Card Payment"}) RETURN DISTINCT t.credit_card_account']
qq['cypher_query_samples'] = ['MATCH (t:Transaction {type: "Credit Card Payment"}) RETURN DISTINCT t.credit_card_account']
qq['answer_score'] = 0.85
qq['answer'] = 'Credit Cards paid: Card1, Card2, Card3, ...'
qq['multimodal'] = {}
guides[qq['question_id_tag']] = qq


## Q45: List all Debit cards on the account.
qq = get_qq('q45')
qq['org_desc'] = "List all Debit cards on the account."
qq['variations'] = ["Which debit cards are associated with the account?"]
qq['question_id_tag'] = 'q45_debit_cards'
qq['llm_helpers'] = ["- Enumerate all debit cards linked to the account."]
qq['cypher_query'] = 'MATCH (a:Account)-[:HAS_CARD]->(d:DebitCard) RETURN d.card_number'
qq['cypher_query_variations'] = ['MATCH (a:Account)-[:HAS_CARD]->(d:DebitCard) RETURN d.card_number']
qq['cypher_query_samples'] = ['MATCH (a:Account)-[:HAS_CARD]->(d:DebitCard) RETURN d.card_number']
qq['answer_score'] = 0.85
qq['answer'] = 'Debit cards on the account are: Card1, Card2, Card3, ...'
qq['multimodal'] = {}
guides[qq['question_id_tag']] = qq

## Q46: List any transactions that use the word “Airport.”
qq = get_qq('q46')
qq['org_desc'] = "List any transactions that use the word “Airport.”"
qq['variations'] = ["Show all transactions with the description containing 'Airport'."]
qq['question_id_tag'] = 'q46_transactions_airport'
qq['llm_helpers'] = ["- Find all transactions where the description includes the term 'Airport'."]
qq['cypher_query'] = "MATCH (t:Transaction) WHERE t.description CONTAINS 'Airport' RETURN t"
qq['cypher_query_variations'] = ["MATCH (t:Transaction) WHERE t.description CONTAINS 'Airport' RETURN t"]
qq['cypher_query_samples'] = ["MATCH (t:Transaction) WHERE t.description CONTAINS 'Airport' RETURN t"]
qq['answer_score'] = 0.85
qq['answer'] = "Transactions related to 'Airport': Transaction1, Transaction2, ..."
qq['multimodal'] = {}
guides[qq['question_id_tag']] = qq

## Q47: List any transactions that use the word “Ammo.”
qq = get_qq('q47')
qq['org_desc'] = "List any transactions that use the word “Ammo.”"
qq['variations'] = ["What are the transactions with 'Ammo' mentioned in the description?"]
qq['question_id_tag'] = 'q47_transactions_ammo'
qq['llm_helpers'] = ["- Search for transactions that reference 'Ammo' in the description."]
qq['cypher_query'] = "MATCH (t:Transaction) WHERE t.description CONTAINS 'Ammo' RETURN t"
qq['cypher_query_variations'] = ["MATCH (t:Transaction) WHERE t.description CONTAINS 'Ammo' RETURN t"]
qq['cypher_query_samples'] = ["MATCH (t:Transaction) WHERE t.description CONTAINS 'Ammo' RETURN t"]
qq['answer_score'] = 0.85
qq['answer'] = "Transactions mentioning 'Ammo': Transaction3, Transaction4, ..."
qq['multimodal'] = {}
guides[qq['question_id_tag']] = qq

## Q48: List any transactions that use the word “Chemical.”
qq = get_qq('q48')
qq['org_desc'] = "List any transactions that use the word “Chemical.”"
qq['variations'] = ["Identify transactions that contain the term 'Chemical'."]
qq['question_id_tag'] = 'q48_transactions_chemical'
qq['llm_helpers'] = ["- Locate all transactions with 'Chemical' in the transaction description."]
qq['cypher_query'] = "MATCH (t:Transaction) WHERE t.description CONTAINS 'Chemical' RETURN t"
qq['cypher_query_variations'] = ["MATCH (t:Transaction) WHERE t.description CONTAINS 'Chemical' RETURN t"]
qq['cypher_query_samples'] = ["MATCH (t:Transaction) WHERE t.description CONTAINS 'Chemical' RETURN t"]
qq['answer_score'] = 0.85
qq['answer'] = "Transactions with 'Chemical': Transaction5, Transaction6, ..."
qq['multimodal'] = {}
guides[qq['question_id_tag']] = qq

## Q49: Program needs to list out all transactions related to a specific word or word string.
qq = get_qq('q49')
qq['org_desc'] = "Program needs to list out all transactions related to a specific word or word string."
qq['variations'] = ["How to list transactions based on specific keywords in the description?"]
qq['question_id_tag'] = 'q49_transactions_keyword'
qq['llm_helpers'] = ["- Generate a list of transactions filtered by a given keyword in their description."]
qq['cypher_query'] = "MATCH (t:Transaction) WHERE t.description CONTAINS 'SPECIFIC_KEYWORD' RETURN t"
qq['cypher_query_variations'] = ["MATCH (t:Transaction) WHERE t.description CONTAINS 'SPECIFIC_KEYWORD' RETURN t"]
qq['cypher_query_samples'] = ["MATCH (t:Transaction) WHERE t.description CONTAINS 'SPECIFIC_KEYWORD' RETURN t"]
qq['answer_score'] = 0.85
qq['answer'] = "Transactions containing 'SPECIFIC_KEYWORD': Transaction7, Transaction8, ..."
qq['multimodal'] = {}
guides[qq['question_id_tag']] = qq

## Q50: List all cash transactions, Deposit, Check written to “Cash,” and ATM withdrawal.
qq = get_qq('q50')
qq['org_desc'] = "List all cash transactions, Deposit, Check written to “Cash,” and ATM withdrawal."
qq['variations'] = ["Can you provide a list of all cash-related transactions including deposits, cash checks, and ATM withdrawals?"]
qq['question_id_tag'] = 'q50_cash_transactions'
qq['llm_helpers'] = ["- Compile all transactions that are cash-based, including deposits, checks to cash, and ATM withdrawals."]
qq['cypher_query'] = "MATCH (t:Transaction) WHERE t.method IN ['Cash Deposit', 'Cash Check', 'ATM Withdrawal'] RETURN t"
qq['cypher_query_variations'] = ["MATCH (t:Transaction) WHERE t.method IN ['Cash Deposit', 'Cash Check', 'ATM Withdrawal'] RETURN t"]
qq['cypher_query_samples'] = ["MATCH (t:Transaction) WHERE t.method IN ['Cash Deposit', 'Cash Check', 'ATM Withdrawal'] RETURN t"]
qq['answer_score'] = 0.85
qq['answer'] = 'Cash transactions: Deposit1, Check to Cash2, ATM Withdrawal3, ...'
qq['multimodal'] = {}
guides[qq['question_id_tag']] = qq







def dev1():

    return


if __name__=='__main__':
    branches=['dev1']
    for b in branches:
        globals()[b]()


"""
"""
