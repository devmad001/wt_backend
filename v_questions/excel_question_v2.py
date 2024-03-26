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
from normalize_date_range import statement_range_to_objects
from normalize_date_range import str2date

from get_logger import setup_logging
logging=setup_logging()


#0v5# JC  Jan  2, 2024  Opening balance option
#0v4# JC  Jan  1, 2024  Highlight terms to url
#0v3# JC  Dec 15, 2023  Get base endpoint
#0v2# JC  Oct 27, 2023  Migrate to generalized debit/credit classifier
#0v1# JC  Oct 13, 2023  Init

"""
    Answer the Excel 'Question'
"""

#[ ] move to config file
BASE_PDF_STORAGE_URL=get_base_endpoint() #'https://core.epventures.co'


def get_all_first_transactions_on_statement(jsonl,verbose=False):
    #v2:  Jan 3, 2024:
    #- For each bank statement, identify the first transaction found to reconcile the opening balance
    
    saw_first_mem={}
    first_transactions={}
    for record in jsonl:
        
        ### Bank Statement
        bankstatement=record.get('bs',{})
        bs_open_obj=None
        bs_close_obj=None
        account_number=bankstatement.get('account_number','')
        opening_balance=normalize_number(bankstatement.get('opening_balance',0))

        ## Normalize bank statement dates
        start_date_obj, end_date_obj = statement_range_to_objects(bankstatement.get('statement_period',''),bankstatement.get('statement_date',''))
#D3        print ("[raw statement]: "+str(bankstatement))
         
        ## Bank statement id (local unique)
        bid=account_number+"-"+str(start_date_obj)+"-"+str(end_date_obj)  #unique

        
        transaction_id=record['n']['id']
        ### Transaction date
        #i)  possible of NO date or NO amount
        if not record['n'].get('transaction_date',''):
            continue
        else:
            try:
                transaction_date_obj=datetime.strptime(record['n']['transaction_date'], "%Y-%m-%d").date()
            except:
                if record['n'].get('transaction_amount',''):
                    logging.warning("[could not process transaction date (have amount)]: "+str(record['n']))
                    raise Exception("[could not process transaction date (have amount)]: "+str(record['n']))
                else:
                    logging.info("[info] skip transaction without amount]: "+str(record['n']))
                    continue
        
        flag_is_first=False
        if not bid in saw_first_mem and transaction_date_obj and end_date_obj and start_date_obj:
            ## Candidate first transaction for statement
            ## If Transaction date is within statement period
            if transaction_date_obj>=start_date_obj and transaction_date_obj<=end_date_obj:
                
                if True:
                    print ("FIRST DETAILS:")
                    print ("Statement: "+str(bankstatement))
                    print ("Transaction: "+str(record['n']))

                ## First entry
                saw_first_mem[bid]=True
                
                ## Balance at first entry is opening balance plus/minus
                first_transactions[transaction_id]=opening_balance
                flag_is_first=True
            else:
                if False: #debug
                    print ("Why not first...")
                    print ("transaction_date_obj: "+str(transaction_date_obj))
                    print ("end_date_obj: "+str(end_date_obj))
                    print ("start_date_obj: "+str(start_date_obj))
                
        else:
            ## Why is not first?
            if False: #debug
                print ("bid in saw_first_mem: "+str(bid in saw_first_mem))
                print ("transaction_date_obj: "+str(transaction_date_obj))
                print ("end_date_obj: "+str(end_date_obj))
                print ("start_date_obj: "+str(start_date_obj))
                print ("[warning] [ ] why is not first?  "+str(record['n']))

        ### VERBOSE
        if not start_date_obj:
            print ("<BS no start date object> : "+str(bankstatement))
        if flag_is_first:
            print (">> FIRST: "+str(transaction_id))
        else:
            pass
#D1            print ("NOT FIRST: "+str(record['n']))
    return first_transactions


def answer_excel_2(case_id,verbose=False):
    ### NOTES:
    #- Debit + Credit fields are related to main_account !
    #- opening and closing balances are off the statement!
    #- ? watch for overlapping opening balances on overlapping statements

    logging.info("Running excel for: "+str(case_id))
    
    ## Get balances
    print ("[ASSUME]  opening balances across various brands of statements don't overlap!")
    print ("[TODO]    rebase balance at next period if opening balances don't match!! [ ] AUDITABLE!")

    cols=[]
    cols+=['account_number']
    cols+=['Eff Date']
    cols+=['Posted Date']
    cols+=['Description']
    cols+=['Check #']
    cols+=['Debit']
    cols+=['Credit']
    cols+=['Balance']
    cols+=['Locate']
    
    ## Transactions on case
    stmt="""
        MATCH (n:Transaction {case_id: '""" + str(case_id) + """'})
        RETURN n
        ORDER BY n.transaction_date
    """
    
    ## Full transaction details
    #v2:  Include statement balance
    stmt="""
    MATCH (n:Transaction {case_id: '""" + str(case_id) + """'})
    OPTIONAL MATCH (entity_sender:Entity)-[:DEBIT_FROM]->(n)
    OPTIONAL MATCH (n)<-[:CREDIT_TO]-(entity_receiver:Entity)
    OPTIONAL MATCH (n)-[:PROCESSED_BY]->(processor:Processor)
    OPTIONAL MATCH (n)<-[:HAS_TRANSACTION]-(bs:BankStatement)
    RETURN n, entity_sender, entity_receiver, processor,bs
    ORDER BY n.transaction_date
    """

    jsonl,df,tx,meta=Neo.run_stmt_to_normalized(stmt)
    
    ## Pre-compute first transactions on statement
    first_statement_transactions=get_all_first_transactions_on_statement(jsonl,verbose=verbose)
    
    ## Headers with mapping
    headers=[]
    headers+=['Acct #']
    headers+=['Eff Date']
    headers+=['Posted Date']
    headers+=['Description']
    headers+=['Check #']
    headers+=['Debit']
    headers+=['Credit']
    headers+=['Balance']
    headers+=['Locate']
    
    ### NOTES:
    #- Debit + Credit fields are related to main_account !
    #- [ ] watch when main account is not involved

    logging.info ("> "+"\t".join(headers))
    running_balance=0
    erows=[]
    seen_transactions={}
    for record in jsonl:

        ## Full record
#D3        if verbose: logging.info ("> "+str(record))
            
        ## High-level filter
        #i)  possible of NO date or NO amount (skip)
        if not record['n']['transaction_date']:
            logging.info('[excel skip transaction no date]: '+str(record['n']))
            continue


        ## LOAD VARS
        n=record.get('n',{})
        entity_sender=record.get('entity_sender',{})
        entity_receiver=record.get('entity_receiver',{})
        processor=record.get('processor',{})
        bankstatement=record.get('bs',{})
        
        transaction_id=n['id']
        
        ## Watch for duplicate (possible if re-run but flip DEBIT/CREDIT direction)
        if transaction_id in seen_transactions:
            logging.info ("[warning] [ ] root cause?  skipping duplicate transaction (possibly sender<>receiver thing?): "+str(transaction_id))
            continue
        seen_transactions[transaction_id]=True
        
        rr=[]
        rr+=[('Acct #',n['account_number'])]
        rr+=[('Eff Date','')]
        rr+=[('Posted Date',n['transaction_date'])]
        rr+=[('Description',n['transaction_description'])]
        rr+=[('Check #', n.get('check_num',''))]

        ## DEBIT OR CREDIT?
        is_credit,is_debit,amount=resolve_debit_credit_main_account(n,entity_sender,entity_receiver)
        balance_change=0
        if is_credit:
            rr+=[('Debit','')]
            rr+=[('Credit',round(amount,2))]
            balance_change+=abs(amount)
        else:
            # Debit
            balance_change-=abs(amount)
            rr+=[('Debit',round(amount,2))]
            rr+=[('Credit','')]


        ## RESOLVE RUNNING BALANCES
        # [ ] JON:  Check on overlapping dates between statements from different banks/kinds (may need to rebase balance or group-by account first)

        #[1] Grab more transaction details
        transaction_date_obj=str2date(n['transaction_date'])
            
        #[2] Check if transaction is FIRST on statement
        if transaction_id in first_statement_transactions:
            ## This first transaction on the statement reconciles balance based on opening for that statement
            logging.info("[first transaction on statement BELOW]------------------------------------")
            opening_balance=first_statement_transactions[transaction_id]
            running_balance=round(opening_balance+balance_change,2)
        else:
            ## Standard balance modifier
            running_balance=round(running_balance+balance_change,2)
        
        rr+=[('Balance',running_balance)]
        

        ## locate hyperlink
        locate=generate_transaction_hyperlink(case_id,n['filename'],page_num=n.get('filename_page_num',0),amount=amount,description=n['transaction_description'])
        rr+=[('Locate',locate)]
#        rr+=[('id',n['id'])]

        ## All row values view
        values = [tup[1] for tup in rr]
        logging.info("> " + "\t".join([str(value) for value in values]))
            
        ## Map back to dict
        dict_rr = {key: value for key, value in rr}
        erows+=[dict_rr]

    return erows


def normalize_number(vv):
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
    
def DELTHIS_get_opening_balances(case_id,verbose=False):
    #v1
     
    ## Transactions on case
    ## Transaction with matching bank statement
    logging.info("[fetching opening balances]...")
    stmt="""
        MATCH (n:Transaction {case_id: '""" + str(case_id) + """'})<-[:HAS_TRANSACTION]-(bs:BankStatement)
        RETURN n, bs
        ORDER BY n.transaction_date
    """
    
    balances=[]

    jsonl,df,tx,meta=Neo.run_stmt_to_normalized(stmt)
    for rr in jsonl:
        t=rr['n']
        bs=rr['bs']
#        print ("[t]: "+str(t))
#        print ("[bs]: "+str(bs))
        start_date_obj, end_date_obj = statement_range_to_objects(bs.get('statement_period',''),bs.get('statement_date',''))
        
        ## Balances
        sb={}
        sb['start_date_obj']=start_date_obj
        sb['end_date_obj']=end_date_obj
        sb['start_balance']=normalize_number(bs['opening_balance'])
        
        if not sb in balances:
            balances+=[sb]
    
    if verbose:
        for sb in balances:
            print ("balance> "+str(sb))

    return balances

def generate_transaction_hyperlink(case_id,filename,page_num=0,amount='',description=''):
    global BASE_PDF_STORAGE_URL #='https://storage.epventures.co'

    #url='http://127.0.0.1:5009/case/case_atm_location/pdf/07A210E6-B60D-46B6-9D40-9B3239237F05-list.pdf?page=3&key=123
    #case_id='case_atm_location'
    #filename='07A210E6-B60D-46B6-9D40-9B3239237F05-list.pdf'
    #page=3
    
    ## SECURITY KEY
    security_key=interface_get_security_key(case_id,filename)
    
    ## HIGHLIGHT TERM
    search_strs=top_highlight_terms(amount,description)

    ## http://127.0.0.1:5009/case/case_atm_location/pdf/07A210E6-B60D-46B6-9D40-9B3239237F05-list.pdf?page=3&key=123
    #base_url='http://127.0.0.1:5009'
    #base_url='https://storage.epventures.co'
    base_url=BASE_PDF_STORAGE_URL
    if page_num:
        app_url=base_url+"/api/v1/case/"+case_id+"/pdf/"+filename+"?page="+str(page_num)+"&key="+str(security_key)+"&highlight="+str(search_strs)
    else:
        app_url=base_url+"/api/v1/case/"+case_id+"/pdf/"+filename+"?key="+str(security_key)+"&highlight="+str(search_strs)
    return app_url


def dev_run_audit_excel():
    case_id='case_atm_location'
    case_id='case_wells_fargo_small'
    
    ### RUN
    erows=answer_excel_2(case_id)
    
    ### AUDIT
    
    ##> Again, tests for content but keep local again
    
    possibles=[]
    possibles+=['more then 1 account in single month on single statement?']  #case_atm_location august 
    possibles+=['identical descriptions on same day with same amount?']      #case_atm_location august
    possibles+=['check closing balance matches calculated balance']

    return

def extend_for_reconcile():
    ## Validate at opening and closing balances at the statement level
    #ii)  optional daily closing but not extracted
    case_id='case_wells_fargo_small'
    erows=answer_excel_2(case_id,verbose=True)

    return



if __name__=='__main__':
    branches=['dev_run_audit_excel']
    branches=['extend_for_reconcile']

    for b in branches:
        globals()[b]()




"""

"""
