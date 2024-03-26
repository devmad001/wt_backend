import os
import sys
import codecs
import json
import re

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")

from pypher import __, Pypher
from w_storage.gstorage.gneo4j import Neo

from a_agent.RUN_sim_wt import call_normal_full_run
from a_agent.sim_wt import wt_main_pipeline

from a_query.queryset1 import query_statements
from a_query.queryset1 import query_transaction
from a_query.queryset1 import query_transactions
from a_query.queryset1 import query_transaction_relations
from a_query.queryset1 import dev_query_data_focused

from get_logger import setup_logging
logging=setup_logging()


#0v1# JC  Oct 27, 2023  Init

"""
    50 Qs -- 50 queries as functions
"""


def q1_list_account_numbers(case_id='',verbose=True):
    return

def q2_beginning_monthly_balance(case_id='',verbose=True):
    return

def q3_date_account_opened(case_id='',verbose=True):
    return

def q4_total_deposits_additions(case_id='',verbose=True):
    return

def q5_total_deposits_additions_month(case_id='',verbose=True):
    return

def q6_total_deposits_additions_year(case_id='',verbose=True):
    return

def q7_total_deposits_additions_quarter(case_id='',verbose=True):
    return

def q8_total_deposits_additions_day(case_id='',verbose=True):
    return

def q9_total_deposits_month(case_id='',verbose=True):
    return

def q10_total_deposits_year(case_id='',verbose=True):
    return

def q11_total_deposits_quarter(case_id='',verbose=True):
    return

def q12_total_deposits_day(case_id='',verbose=True):
    return

def q13_total_inflows(case_id='',verbose=True):
    return

def q14_total_outflows(case_id='',verbose=True):
    return

def q15_total_outflows_cash_withdrawal(case_id='',verbose=True):
    return

def q16_total_outflows_check(case_id='',verbose=True):
    return

def q17_total_outflows_credit_card_payments(case_id='',verbose=True):
    return

def q18_total_outflows_zelle(case_id='',verbose=True):
    return

def q19_total_outflows_wire(case_id='',verbose=True):
    return

def q20_total_outflows_bank_fees(case_id='',verbose=True):
    return

def q21_percent_withdrawals_atm_vs_debit_card(case_id='',verbose=True):
    return

def q22_electronic_withdrawals_total_day_month_year_quarter(case_id='',verbose=True):
    return

def q23_electronic_withdrawals_wire(case_id='',verbose=True):
    return

def q24_electronic_withdrawals_zelle(case_id='',verbose=True):
    return

def q25_ending_balance_by_date(case_id='',verbose=True):
    return

def q26_book_transfer_credits(case_id='',verbose=True):
    return

def q27_zelle_payments(case_id='',verbose=True):
    return

def q28_fed_wire_credits(case_id='',verbose=True):
    return

def q29_payment_id_zelle(case_id='',verbose=True):
    return

def q30_list_companies(case_id='',verbose=True):
    return

def q31_list_banks(case_id='',verbose=True):
    return

def q32_top_atm_used(case_id='',verbose=True):
    return

def q33_top_bank_used(case_id='',verbose=True):
    return

def q34_top_loan_accounts(case_id='',verbose=True):
    return

def q35_top_credit_card_accounts(case_id='',verbose=True):
    return

def q36_list_top_10_payees(case_id='',verbose=True):
    return

def q37_list_top_10_payors(case_id='',verbose=True):
    return

def q38_list_all_payments_to_irs(case_id='',verbose=True):
    return

def q39_list_all_payees_payors(case_id='',verbose=True):
    return

def q40_list_all_atm_transactions(case_id='',verbose=True):
    return

def q41_list_all_atm_transactions_amount(case_id='',verbose=True):
    return

def q42_list_all_credit_card_payments(case_id='',verbose=True):
    return

def q43_list_all_debit_transactions(case_id='',verbose=True):
    return

def q44_list_all_debit_transactions_amount(case_id='',verbose=True):
    return

def q45_list_venmo_transactions(case_id='',verbose=True):
    return

### CARDS
def q46_list_all_credit_cards(case_id='',verbose=True):
    return
def q47_list_all_debit_cards(case_id='',verbose=True):
    return

### WORDS
def q48_list_all_transactions_airport(case_id='',verbose=True):
    return
def q49_list_all_transactions_ammo(case_id='',verbose=True):
    return
def q50_list_all_transactions_chemical(case_id='',verbose=True):
    return
def q51_list_all_transactions_word(case_id='',verbose=True):
    return

### CASH
def q52_list_all_cash_transactions(case_id='',verbose=True):
    return
def q53_list_all_cash_transactions_deposit(case_id='',verbose=True):
    return
def q54_list_all_cash_transactions_atm(case_id='',verbose=True):
    return
def q55_list_all_cash_transactions_withdrawal(case_id='',verbose=True):
    return
def q56_list_all_cash_transactions_check(case_id='',verbose=True):
    return
def q57_list_all_cash_transactions_cash(case_id='',verbose=True):
    return


def dev1():
    return


if __name__=='__main__':
    branches=['dev1']
    for b in branches:
        globals()[b]()




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

"""

"""
