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


#0v4# JC  Jan  1, 2024  Highlight terms to url
#0v3# JC  Dec 15, 2023  Get base endpoint
#0v2# JC  Oct 27, 2023  Migrate to generalized debit/credit classifier
#0v1# JC  Oct 13, 2023  Init

"""
    Answer the Excel 'Question'
"""

#[ ] move to config file
BASE_PDF_STORAGE_URL=get_base_endpoint() #'https://core.epventures.co'


def answer_excel_1(case_id,verbose=False):
    ### NOTES:
    #- Debit + Credit fields are related to main_account !
    #- opening and closing balances are off the statement!
    #- ? watch for overlapping opening balances on overlapping statements

    logging.info("Running excel for: "+str(case_id))
    
    ## Get balances
    print ("[ASSUME]  opening balances across various brands of statements don't overlap!")
    print ("[TODO]    rebase balance at next period if opening balances don't match!! [ ] AUDITABLE!")

    balances=dev_get_opening_balances(case_id)

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
    stmt="""
    MATCH (n:Transaction {case_id: '""" + str(case_id) + """'})
    OPTIONAL MATCH (entity_sender:Entity)-[:DEBIT_FROM]->(n)
    OPTIONAL MATCH (n)<-[:CREDIT_TO]-(entity_receiver:Entity)
    OPTIONAL MATCH (n)-[:PROCESSED_BY]->(processor:Processor)
    RETURN n, entity_sender, entity_receiver, processor
    ORDER BY n.transaction_date
    """

    jsonl,df,tx,meta=Neo.run_stmt_to_normalized(stmt)
    
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

    print ("> "+"\t".join(headers))
    running_balance=None
    last_transaction_date_obj=None
    erows=[]
    seen_transactions={}
    for record in jsonl:

        ## Full record
        if verbose:
            print ("> "+str(record))

        n=record.get('n',{})
        entity_sender=record.get('entity_sender',{})
        entity_receiver=record.get('entity_receiver',{})
        processor=record.get('processor',{})
        
        ## Watch for duplicate (possible if re-run but flip DEBIT/CREDIT direction)
        if n['id'] in seen_transactions:
            print ("[warning] [ ] root cause?  skipping duplicate transaction (possibly sender<>receiver thing?): "+str(n['id']))
            continue
        seen_transactions[n['id']]=True
        

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
        try: transaction_date_obj=datetime.strptime(n['transaction_date'], "%Y-%m-%d").date()
        except:
            logging.warning("[could not process date skip excel row]: "+str(n))
            logging.dev("[could not process date skip row]: "+str(n))
            continue

        running_balance=resolve_running_balance(running_balance,balance_change,balances,last_transaction_date_obj, transaction_date_obj)
        
#causes fault        running_balance='' #JC

#        running_balance='' #JC

        rr+=[('Balance',running_balance)]
        
        ## locate hyperlink
        locate=generate_transaction_hyperlink(case_id,n['filename'],page_num=n.get('filename_page_num',0),amount=amount,description=n['transaction_description'])
        rr+=[('Locate',locate)]
#        rr+=[('Locate','looocate')]
#        rr+=[('id',n['id'])]

        ## All row values view
        values = [tup[1] for tup in rr]
        print("> " + "\t".join([str(value) for value in values]))
            
        ## Track date objs
        last_transaction_date_obj=transaction_date_obj
        
        ## Map back to dict
        dict_rr = {key: value for key, value in rr}
        erows+=[dict_rr]

    return erows

def resolve_running_balance(running_balance,balance_change,balances,last_balance_date_obj, this_balance_date_obj):
    ## NORMAL CASE
    if running_balance is None:
        ## Look for opening balance then is less then current date
        for balance in balances:
            if balance['start_date_obj']<=this_balance_date_obj:
                running_balance=balance['start_balance'] # Will choose last one that is closest
        print ("[debug] choosing running balance init: "+str(running_balance))

        ## Default if not found
        if running_balance is None:
            running_balance=0

    running_balance+=balance_change
    
    running_balance=round(running_balance, 2)
    return running_balance

def inject_opening_balance(balances,last_balance_date_obj, this_balance_date_obj, running_balance):
    
    ##i)
    # If   [last balance date] < [opening balance date]
    # AND  [this balance date] >= [opening balance date] 
    
    ##ii) {OR}  if running_balance is None

    # then inject opening balance
    rr={}
    return rr



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
    
def dev_get_opening_balances(case_id):
     
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
    
#D1#    for sb in balances: print ("balance> "+str(sb))

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
    erows=answer_excel_1(case_id)
    
    ### AUDIT
    
    ##> Again, tests for content but keep local again
    
    possibles=[]
    possibles+=['more then 1 account in single month on single statement?']  #case_atm_location august 
    possibles+=['identical descriptions on same day with same amount?']      #case_atm_location august
    possibles+=['check closing balance matches calculated balance']

    return

if __name__=='__main__':
    branches=['dev_run_audit_excel']
    for b in branches:
        globals()[b]()




"""

"""
