import os
import sys
import codecs
import json
import re
from datetime import datetime


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

from a_custom.alg_classify_debit_credit import resolve_debit_credit_main_account

from w_file_repo.filerepo import interface_get_security_key
from w_file_repo.filerepo import top_highlight_terms

from w_utils import get_base_endpoint

from get_logger import setup_logging
logging=setup_logging()


#0v1# JC  Jan  3, 2024  Opening balance option

"""
    RECONCILED BALANCES
    - v1 includes resolve_running_balance.
"""




def normalize_number(vv):
    ## Remove commas and dollar signs
    #[x] done at extraction but again here
    if isinstance(vv,str):
        vv=re.sub(r'[\, \$]',"",vv)
        try: vv=float(vv)
        except Exception as e:
            logging.error("[error] could not normalize number: "+str(e)+": "+str(vv))
    try:
        vv=float(vv)
    except:
        vv=0
    return vv


def statement_range_to_objects(statement_period,statement_date):

    start_date_obj=None
    end_date_obj=None
    
    ## ASSUME ALWAYS START OF THE MONTH??
    ## TRY via single statement_date

    ASSUME_STATEMENT_STARTS_ON_DAY_1=True
    if ASSUME_STATEMENT_STARTS_ON_DAY_1 and statement_date:
        # Convert string to date object
        date_obj = datetime.strptime(statement_date, "%Y-%m-%d").date()

        # If day is not 1, adjust it to 1
        if date_obj.day != 1:
            end_date_obj=date_obj
            start_date_obj = end_date_obj.replace(day=1)
        
        # Format the date to "YYYY MM DD"
        formatted_date = date_obj.strftime("%Y %m %d")
        
    else:
        ## i)   2022-01-01 to 2022-01-31
        ## ii) 'July 31, 2021 through August 31, 2021'}
        
        #i)
        # Split the string into start and end dates
        start_str, end_str = map(str.strip, statement_period.split("to"))
        # Convert strings to date objects
        start_date_obj = datetime.strptime(start_str, "%Y-%m-%d").date()
        end_date_obj = datetime.strptime(end_str, "%Y-%m-%d").date()
        
        #ii) tbd
    
    return start_date_obj, end_date_obj
    
def dev_get_opening_balances(case_id,verbose=False):
    #v2
     
    ## Transactions on case
    ## Transaction with matching bank statement
    logging.info("[fetching opening balances]...")
    stmt="""
        MATCH (n:Transaction {case_id: '""" + str(case_id) + """'})<-[:HAS_TRANSACTION]-(bs:BankStatement)
        RETURN n, bs
        ORDER BY n.transaction_date
    """
    
    """
        Bank statement
        {'statement_date': '2019-01-09', 'account_holder_address': '125 BEVINGTON LN WOODSTOCK GA 30188-5421', 'account_number': '1010083000401', 'closing_balance': 10065.02, 'account_holder_name': 'DOUGLAS MIKULA JONATHAN W MIKULA', 'case_id': 'case_wells_fargo_small', 'bank_name': 'Wells Fargo', 'label': 'BankStatement', 'opening_balance': 4011.86, 'id': 'case_wells_fargo_small-2019-01-09-1010083000401-Wells Fargo Bank Statement-pages-2-5.pdf', 'statement_period': '2019-01-09 to 2019-02-07'}
    """
    
    balances=[]

    bs_mem={}
    jsonl,df,tx,meta=Neo.run_stmt_to_normalized(stmt)
    for rr in jsonl:
        t=rr['n']
        bs=rr['bs']

        if bs['id'] in bs_mem:
            continue #Saw
        else:
            bs_mem[bs['id']]=True

#        print ("[t]: "+str(t))
        print ("[bs]: "+str(bs))

        start_date_obj, end_date_obj = statement_range_to_objects(bs.get('statement_period',''),bs.get('statement_date',''))
        
        ## Known balances
        if bs['opening_balance']:
            sb={}
            sb['date_obj']=start_date_obj
            sb['balance']=normalize_number(bs['opening_balance'])
            sb['btype']='opening_balance'
            sb['account_number']=bs.get('account_number','')

        if bs['closing_balance']:
            sb={}
            sb['date_obj']=end_date_obj
            sb['balance']=normalize_number(bs['closing_balance'])
            sb['btype']='closing_balance'
            sb['account_number']=bs.get('account_number','')

        if not sb in balances:
            balances+=[sb]
    
    if verbose:
        for sb in balances:
            print ("balance> "+str(sb))

    return balances
    
def itemize_known_balances(case_id):
    
    ## Get firm mentioned balances:
    #a)  Opening balance
    #b)  Closing balance
    #c)  Balance at the end of the month
    #d)  Balance at the end of the year
    #e)  Daily balances

    return


def call_reconcile_balances():
    
    case_id='case_atm_location'
    case_id='case_wells_fargo_small'
    
    dev_get_opening_balances(case_id,verbose=True)

    return


def note_balance_logic_and_assumptions():
    """
    1.  Query for all transactions for case_id order by date
    2.  Firm credit & debit against main account
          i )  {existing}  Option use function resolve_debit_credit_main_account
          ii)  {better  }  Option use transaction variable is_credit
    3.  Hard code balance start (opening balance) for each match at account number and date
         - Is transaction on statement?
            i ) If graph link from transaction to statement then yes.
            ii) If account_number match and transaction date within statement period then yes. 
            
    """


    return

#moved#def get_all_first_transactions(jsonl,verbose=False):
#moved#    #v2:  Jan 3, 2024:
#moved#    #- For each bank statement, identify the first transaction found to reconcile the opening balance
#moved#
#moved#    saw_first_mem={}
#moved#    first_transactions={}
#moved#    for record in jsonl:
#moved#        
#moved#        ### Bank Statement
#moved#        bankstatement=record.get('bs',{})
#moved#        bs_open_obj=None
#moved#        bs_close_obj=None
#moved#        account_number=bankstatement.get('account_number','')
#moved#        opening_balance=normalize_number(bankstatement.get('opening_balance',0))
#moved#
#moved#        ## Normalize bank statement dates
#moved#        start_date_obj, end_date_obj = statement_range_to_objects(bankstatement.get('statement_period',''),bankstatement.get('statement_date',''))
#moved#         
#moved#        bid=account_number+"-"+str(start_date_obj)+"-"+str(end_date_obj)  #unique
#moved#
#moved#        
#moved#        ### Transaction
#moved#        transaction_id=record['n']['id']
#moved#        try: transaction_date_obj=datetime.strptime(record['n']['transaction_date'], "%Y-%m-%d").date()
#moved#        except: pass
#moved#        
#moved#        flag_is_first=False
#moved#        if not bid in saw_first_mem and transaction_date_obj and end_date_obj and start_date_obj:
#moved#            ## Candidate first transaction for statement
#moved#            ## If Transaction date is within statement period
#moved#            if transaction_date_obj>=start_date_obj and transaction_date_obj<=end_date_obj:
#moved#
#moved#                ## First entry
#moved#                saw_first_mem[bid]=True
#moved#                
#moved#                ## Balance at first entry is opening balance plus/minus
#moved#                first_transactions[transaction_id]=opening_balance #On statement (don't do transaction +/- here)
#moved#                flag_is_first=True
#moved#
#moved#        ### VERBOSE
#moved#        if not start_date_obj:
#moved#            print ("<BS no start date object> : "+str(bankstatement))
#moved#        if flag_is_first:
#moved#            print (">> FIRST: "+str(transaction_id))
#moved#        else:
#moved#            print ("NOT FIRST: "+str(transaction_id))
#moved#    return first_transactions


def single_query_attempt():

    case_id='case_wells_fargo_small'
    
    ## Full transaction details
    stmt="""
    MATCH (n:Transaction {case_id: '""" + str(case_id) + """'})
    OPTIONAL MATCH (entity_sender:Entity)-[:DEBIT_FROM]->(n)
    OPTIONAL MATCH (n)<-[:CREDIT_TO]-(entity_receiver:Entity)
    OPTIONAL MATCH (n)-[:PROCESSED_BY]->(processor:Processor)
    RETURN n, entity_sender, entity_receiver, processor
    ORDER BY n.transaction_date
    """

    stmt="""
        MATCH (n:Transaction {case_id: '""" + str(case_id) + """'})<-[:HAS_TRANSACTION]-(bs:BankStatement)
        RETURN n, bs
        ORDER BY n.transaction_date
    """

    stmt="""
        MATCH (n:Transaction {case_id: '""" + str(case_id) + """'})
        OPTIONAL MATCH (entity_sender:Entity)-[:DEBIT_FROM]->(n)
        OPTIONAL MATCH (n)<-[:CREDIT_TO]-(entity_receiver:Entity)
        OPTIONAL MATCH (n)-[:PROCESSED_BY]->(processor:Processor)
        OPTIONAL MATCH (n)<-[:HAS_TRANSACTION]-(bs:BankStatement)
        RETURN n, entity_sender, entity_receiver, processor, bs
        ORDER BY n.transaction_date
    """

    print ("QUERY: "+str(stmt))

    jsonl,df,tx,meta=Neo.run_stmt_to_normalized(stmt)
    
    print ("GOT COUNT: "+str(len(jsonl)))
    
    first_transactions=get_all_first_transactions(jsonl)
    

    return



if __name__=='__main__':

    branches=['extend_for_reconcile']
    branches=['call_reconcile_balances']
    branches=['single_query_attempt']

    for b in branches:
        globals()[b]()




"""

"""
