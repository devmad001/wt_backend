import os,sys
import time
import re
import json
import copy
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt

import configparser as ConfigParser

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")
sys.path.insert(0,LOCAL_PATH+"../../")

from w_utils import similarity_string
from w_storage.gstorage.gneo4j import Neo
#from w_chatbot.wt_brains import Bot_Interface

from a_algs.ner_algs.alg_normalize_entity_name import alg_normalize_entity_name

from w_storage.gstorage.gneo4j import Neo

from a_algs.ner_algs.alg_normalize_entity_name import alg_normalize_entity_name

from z_apiengine.database import SessionLocal
from z_apiengine.database_models import CaseReports

from m_cypher.macro_queries import alg_get_account_holder_name
from m_cypher.macro_queries import alg_resolve_opening_balance
from m_cypher.macro_queries import alg_get_statement_nodes

from m_cypher.macro_queries import alg_resolve_main_account_NAMES
from m_cypher.macro_queries import alg_get_main_account_names
from m_cypher.macro_queries import get_normalized_name_mapping

from a_query.queryset1 import query_transactions


from get_logger import setup_logging
logging=setup_logging()



#0v1# JC  Dec 16, 2023  Setup


"""
    REPORT GENERATION
    - use system to create reports or "macro" approach
"""

"""
    SPEC FOR FINAL REPORT
    - keep key-value pairs where possible
    

                "account_holder_name": "John Doe",
                "account_holder_address": "123 Main St, Anytown, AN",
                "number_of_transactions": 100,
                "opening_balance": 5000.00,
                "closing_balance": 4500.00,
                "number_of_inflows": 70,
                "number_of_outflows": 30,
                "inflow_amount": 7000.00,
                "outflow_amount": 7500.00,

                number_of_transactions
                number_of_pages
                number_of_files
                fraud_score x

"""


class Report_Helper():
    ## Top-level useability
    #- eventually into common use Class
    def __init__(self):
        return


#   MATCH (t:Transaction)
#        WHERE t.case_id='"""+str(case_id)+"""'
#        RETURN DISTINCT t.statement_id as StatementID
#        ORDER BY StatementID;


def QUERY_all_transactions(case_id):
    #case_id, statement_id, filename,
    return list(query_transactions(case_id=case_id))

def QUERY_all_transaction_flows(case_id):
    """
    see macro)queries.py
     stmt=cypher_query_account_flows(case_id=case_id)
    entries=[]
    for record in local_iter_run_query(stmt):
#D        print ("TR: "+str(record['Transaction']))
    """
    return


def query_number_of_inflows(case_id):
    # Placeholder for querying the number of inflows
    return {'number_of_inflows': 0}

def query_number_of_outflows(case_id):
    # Placeholder for querying the number of outflows
    return {'number_of_outflows': 0}

def query_inflow_amount(case_id):
    # Placeholder for querying the total inflow amount
    return {'inflow_amount': 0.0}

def query_outflow_amount(case_id):
    # Placeholder for querying the total outflow amount
    return {'outflow_amount': 0.0}

def query_fraud_score(case_id):
    # Placeholder for querying the fraud score
    return {'fraud_score': 0.0}


def dev1():
    case_id='MarnerHoldingsB'

    ## Need:
    fields=[]
    fields+=["account_holder_name"]
    fields+=["account_holder_address"]
    fields+=["number_of_transactions"]
    fields+=["opening_balance"]
    fields+=["closing_balance"]
    fields+=["number_of_inflows"]
    fields+=["number_of_outflows"]
    fields+=["inflow_amount"]
    fields+=["outflow_amount"]
    fields+=["number_of_transactions"]
    fields+=["number_of_pages"]
    fields+=["number_of_files"]
    fields+=["fraud_score"]
    
    ## Field need to query
    
    results={}

    results.update(query_account_holder_name(case_id))
    results.update(query_account_holder_address(case_id))
    results.update(query_number_of_transactions(case_id))
    results.update(query_opening_balance(case_id))
    results.update(query_closing_balance(case_id))
    results.update(query_number_of_inflows(case_id))
    results.update(query_number_of_outflows(case_id))
    results.update(query_inflow_amount(case_id))
    results.update(query_outflow_amount(case_id))
    results.update(query_number_of_pages(case_id))
    results.update(query_number_of_files(case_id))
    results.update(query_fraud_score(case_id))


#    statement_node=alg_get_statement_node(case_id=case_id)
    
    results['num_statements']=0
    for statement in alg_get_statement_nodes(case_id=case_id):
        print ("Statement node: "+str(statement))
        results['num_statements']+=1
        
    print ("REPORT: "+str(json.dumps(results,indent=4)))
    

    return


def dev_statement_fields():
    #> see /a_query, macro_queries, etc.
    
    """
    Statement node:
    {'BankStatement': {'account_number': '000000539360823', 'account_holder_name': 'Marner Holdings Inc', 'bank_address': 'P O Box 182051, Columbus, OH 43218 - 2051', 'label': 'BankStatement', 'statement_date': '2021-05-29', 'account_holder_address': '6030 S Eastern Ave, Commerce CA 90040', 'closing_balance': 89872.11, 'case_id': 'MarnerHoldingsB', 'bank_name': 'CHASE', 'opening_balance': 113351.19, 'id': 'MarnerHoldingsB-2021-05-29-000000539360823-2021-06June-statement-0823.pdf', 'statement_period': '2021-05-29 to 2021-06-30'}}
    """
    
    return



def local_normalize_statement_period(period_str):
    ## Statement to periods
    #  (i)   xx to yy
    #  (ii)  April 14, 2017 through May 11, 2017

    period_start=''
    period_end=''


    try:
        if ' to ' in period_str:
            # Case (i): xx to yy
            period_start, period_end = period_str.split(' to ')
            try:
                # Try parsing as 'Y-m-d' format
                period_start = datetime.strptime(period_start, '%Y-%m-%d')
                period_end = datetime.strptime(period_end, '%Y-%m-%d')
            except ValueError:
                # If parsing as 'Y-m-d' fails, try parsing as 'Month day, Year' format
                period_start = datetime.strptime(period_start, '%B %d, %Y')
                period_end = datetime.strptime(period_end, '%B %d, %Y')

        elif ' through ' in period_str:
            # Case (ii): April 14, 2017 through May 11, 2017
            start_str, end_str = period_str.split(' through ')
            period_start = datetime.strptime(start_str, '%B %d, %Y')
            period_end = datetime.strptime(end_str, '%B %d, %Y')

    except ValueError as e:
        logging.info(f"Could not find statement period: {period_str}")
        print(f"Could not find statement period: {period_str}")
        print(f"Error details: {e}")
        #jc=debggg


    return period_start,period_end

def find_balance_extremes(bank_statements, echo_caps=False):
    #: echo_caps dumps a description of what the function does  (part of knowing whether it should be used)
    ## Include queryable description of function
    caps={}
    caps['description']="Find the earliest opening balance and latest closing balance for each account"
    caps['input']={"bank_statements": "list of bank statement nodes"}
    if echo_caps: return caps

    """
    ## DEFINE AS
    # Assumes on a per account opening/closing balance too
    # Opening balance:  earliest statement opening balance
    # Closing balance: latest statement closing balance
    ## Calcuated balance:
    #- for each transaction after opening balance +/- adjust
    #** watch for additive errors
    """

    account_balances = {}

    for statement in bank_statements:
        account_info = statement['BankStatement']
        if not 'account_number' in account_info:
            logging.info("[warning] no account number at: "+str(statement))
            continue
        account_number = account_info['account_number']
        if not 'opening_balance' in account_info:
            logging.info("[warning] no opening balance at: "+str(statement))
            opening_balance = None
            continue
        else:
            opening_balance = account_info.get('opening_balance','')

        closing_balance = account_info.get('closing_balance','')

        ## Statement to periods
        period_start,period_end=local_normalize_statement_period(account_info.get('statement_period',''))

        
        if account_number not in account_balances:
            account_balances[account_number] = {
                'first_opening_balance': (opening_balance, period_start),
                'last_closing_balance': (closing_balance, period_end)
            }
        else:
            if period_start:
                # Update the first opening balance if this statement starts earlier
                try:
                    if period_start < account_balances[account_number]['first_opening_balance'][1]:
                        account_balances[account_number]['first_opening_balance'] = (opening_balance, period_start)
                except:
                    logging.info("Could not track opening balance: "+str(account_balances[account_number]['first_opening_balance'][1]))
            
            if period_end:
                # Update the last closing balance if this statement ends later
                try:
                    if period_end > account_balances[account_number]['last_closing_balance'][1]:
                        account_balances[account_number]['last_closing_balance'] = (closing_balance, period_end)
                except:
                    logging.info("Could not track closing balance: "+str(account_balances[account_number]['last_closing_balance'][1]))


    # Format the results
    for account, balances in account_balances.items():
        # Format first opening balance if it's a datetime object
        if isinstance(balances['first_opening_balance'][1], datetime):
            balances['first_opening_balance'] = (
                balances['first_opening_balance'][0],
                balances['first_opening_balance'][1].strftime('%Y-%m-%d')
            )
    
        # Format last closing balance if it's a datetime object
        if isinstance(balances['last_closing_balance'][1], datetime):
            balances['last_closing_balance'] = (
                balances['last_closing_balance'][0],
                balances['last_closing_balance'][1].strftime('%Y-%m-%d')
            )

#ORG#    for account, balances in account_balances.items():
#ORG#        balances['first_opening_balance'] = (balances['first_opening_balance'][0], balances['first_opening_balance'][1].strftime('%Y-%m-%d'))
#ORG#        balances['last_closing_balance'] = (balances['last_closing_balance'][0], balances['last_closing_balance'][1].strftime('%Y-%m-%d'))

    return account_balances

def alg_get_account_holder_name(statements):
    for statement in statements:
        account_holder_name=statement['BankStatement'].get('account_holder_name','')
        if account_holder_name:
            return account_holder_name
    return None    

def alg_get_account_holder_address(statements):
    for statement in statements:
        account_holder_address=statement['BankStatement'].get('account_holder_address','')
        if account_holder_address:
            return account_holder_address
    return None    

def alg_number_of_pages(transactions):
    ## ** note on statements parser only transactions
    # could do off statement_id but at this level its' filename specific
    total_pages=0
    mem={}
    for transaction in transactions:
        filename=transaction.get('filename','')
        if filename and not filename in mem:
            mem[filename]=True
            try: total_pages+=transaction['filename_page_num']
            except: pass
    return total_pages

def alg_number_of_files(transactions):
    total_files=0
    mem={}
    for transaction in transactions:
        filename=transaction.get('filename','')
        if filename and not filename in mem:
            mem[filename]=True
            total_files+=1
    return total_files

def alg_get_filenames(case_id):
    # (for export)
    transactions=QUERY_all_transactions(case_id=case_id)
    filenames=list(set([t['filename'] for t in transactions if t['filename']]))
    return filenames

def ALG_generate_report_v1(case_id='MarnerHoldingsB'):
    ## ASSUMPTIONS:
    #[balances] ignore account numbers just take first and last
    
    b=[]
    b+=['balances']
    b+=['account_holder_name']
    b+=['account_holder_address']
    b+=['number_of_transactions']
    b+=['filenames']

    b=[]
    b+=['number_of_pages']
    b+=['number_of_files']
    b+=['filenames']

    b=[]
    b+=['all']

    ## BASIC INIT
    report={}
    report['opening_balance']=0
    report['closing_balance']=0
    report['account_holder_name']=''
    report['account_holder_address']=''
    report['number_of_transactions']=0
    report['number_of_pages']=0
    report['number_of_files']=0
    

    ###########################################
    ## GATHER BASE QUERIES
    statements=[]
    for statement in alg_get_statement_nodes(case_id=case_id):
        statements+=[statement]
        
    transactions=[]
    transactions=QUERY_all_transactions(case_id=case_id)
#D1    print ("Sample transaction: "+str(json.dumps(transactions[0],indent=4)))
    ###########################################
        

    ## OPENING - CLOSING BALANCES
    if 'balances' in b or 'all' in b:
        balances=find_balance_extremes(statements)
#D        print ("BALANCES: "+str(json.dumps(balances,indent=4)))
        
        for account_number in balances:
            if report.get('opening_balance'):
                logging.warning("[assumption opening balance is on one account but MULTIPLE found!]")
            report['opening_balance']=balances[account_number]['first_opening_balance'][0]
            report['closing_balance']=balances[account_number]['last_closing_balance'][0]

    ## ACCOUNT HOLDER NAME
    if 'account_holder_name' or 'all' in b:
        report['account_holder_name']=alg_get_account_holder_name(statements)
    
    ## ACCOUNT HOLDER ADDRESS
    if 'account_holder_address' or 'all' in b:
        report['account_holder_address']=alg_get_account_holder_address(statements)
        
    ## NUMBER OF TRANSACTIONS
    if 'number_of_transactions' or 'all' in b:
        report['number_of_transactions']=len(transactions)
        
    ## NUMBER OF PAGES
    if 'number_of_pages' or 'all' in b:
        report['number_of_pages']=alg_number_of_pages(transactions)
        
    ## NUMBER OF FILES
    if 'number_of_files' or 'all' in b:
        report['number_of_files']=alg_number_of_files(transactions)
        
    ## FILENAMES
    if 'filenames' or 'all' in b:
        report['filenames']= list(set([t['filename'] for t in transactions if t['filename']]))

    if True: #Auto save
        local_save_report(case_id=case_id,report_dict=report,report_name='case_summary_v1')
    return report


def local_save_report(case_id,report_dict,report_name='case_summary_v1'):
    ## Include creation date[ ]
    # case_id, user_id (optional), meta {}, reports {}!
    with SessionLocal() as db:
        ## Get all reports
        report_obj=db.query(CaseReports).filter(CaseReports.case_id==case_id).first()
        
        ## Set or update
        if report_obj: #exists
            reports=report_obj.reports
            existing_report=reports.get(report_name,{})
            ## Ok overwrite
            report_obj.reports[report_name]=report_dict

            ## Time modified
            report_date_key='report_date_'+str(report_name)
            report_obj.meta[report_date_key]=time.time()

            db.commit()
        else:
            # New entire report obj
            report_obj=CaseReports()
            report_obj.case_id=case_id
            report_obj.reports={report_name:report_dict}

            report_date_key='report_date_'+str(report_name)
            if not report_obj.meta: report_obj.meta={} #Init even though should be
            report_obj.meta[report_date_key]=time.time()

            db.add(report_obj)
            db.commit()
    logging.info("[saved case summary report]")
    return

def INTERFACE_generate_get_report(case_id,report_name='case_summary_v1'):
    ## Get if existss
    ASSUME_GET_IF_EXISTS=True
    report_dict={}
    if ASSUME_GET_IF_EXISTS:
        with SessionLocal() as db:
            ## Get all reports
            report_obj=db.query(CaseReports).filter(CaseReports.case_id==case_id).first()
            if report_obj:
                report_dict=report_obj.reports.get(report_name,{})
    if not report_dict:
        report_dict=ALG_generate_report_v1(case_id=case_id)
        
    ## FINAL ensure blank values if no key
    must_keys=["account_holder_name","account_holder_address","number_of_transactions","opening_balance","closing_balance","number_of_inflows","number_of_outflows","inflow_amount","outflow_amount"]
    for kky in must_keys:
        if not kky in report_dict:
            report_dict[kky]=''

    return report_dict


def dev_call_report():
    case_id='MarnerHoldingsB'
    report=ALG_generate_report_v1(case_id=case_id)
    print ("REPORT: "+str(json.dumps(report,indent=4)))
    return



if __name__=='__main__':
    branches=['dev1']
    branches=['dev_call_report']
    
    for b in branches:
        globals()[b]()
        


        
