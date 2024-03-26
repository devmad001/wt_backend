import os
import sys
import codecs
import copy
import json
import re
import threading  #future multi

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")
sys.path.insert(0,LOCAL_PATH+"../../")

from w_utils import util_get_modified_keys
from w_storage.gstorage.gneo4j import Neo

from a_query.cypher_helper import cypher_create_relationship

from a_query.queryset1 import query_transactions_with_relations
from a_query.cypher_helper import cypher_create_update_node #Just like markup_alg_cypher_CLEAN.py

from get_logger import setup_logging
logging=setup_logging()

from schemas.SCHEMA_kbai import gold_schema_definition


#0v1# JC  Oct 31, 2023  Front-level debit/credit classifier

"""
    Classify transaction as debit/credit  (in relation to main account)
    - seems easy but a bit fuzzy to condense to 1 account
    - also affects a lot of downstream graphs so better to be formal
"""


def do_cypher_markup_EASY_DEBIT_CREDIT(*args,**vars):
    ####
    # (follow _PROCESSED_BY logic flow)
    ### RECALL:
    #** follow do_logic_markup flow
    
    ## GIVEN RECALL:
    # markup_goals == which alg here to run
    # Records      == bite sized list of dumped records from KB to markup!
    # schema       == essentially a bunch of parameters
    #                 ^^^*** separate logical tweaks from this routine!
    #                     ^^^ ie/ schema regex examples to apply when
    #                             looking for check number. default here tweaks there.
    # meta_doc     == other meta not available in raw transaction "Records"
    
    ## Recall, cypher update & field versions are handled external call_kbai.py
    #- version tracking  (like do_llm_markup) #- cypher update     (like do_llm_markup)
    meta={}
    finished_records=[]
    unfinished_records=[]
    
    """
        dd={}
        dd['case_id']=ptr['case_id']
        dd['schema']=ptr['schema']
        dd['Records']=Records
        dd['markup_goals']=ptr['markup_goals']
        dd['meta_doc']=meta_doc
        dd['DEFAULT_LLM_GROUP_SIZE']=options['DEFAULT_LLM_GROUP_SIZE']  #10 a big 
        dd['markup_version'] ** cause doing update to db
        dd['commit']
    """
    
    ## Map back to va
    # touch givens
    vars['markup_goals']=vars['markup_goals'] #ie/ alg to run
    
    
    ## CHECK GOAL or do direct
    if 'easy_credit_debit_main_goal' in vars['markup_goals']:
        meta_out=dev_local_easy_credit_debit(case_id=vars['case_id'],commit=vars.get('commit',True))
        meta.update(meta_out)

    return finished_records,unfinished_records,meta


def is_transaction_credit(tt,tcredit={},verbose=False):
    reasons=[]
    transaction_id=tt['id']

    if True:
     
        ## Extra checks  (or move)
        #[ ] don't modify if already decided?
        ## Easy logic 0
        # Check sign of amount (does not happen for every statement but if it's negative then assume debit from main [ ] optional catch)
        if tt['transaction_amount']<0:
            tcredit[transaction_id]=False
            reasons+=['False: transaction_amount<0']

        
        ## Easy logic 2
        #- transaction_type -> see schema
        #"transaction_type": ["withdrawal", "deposit", "loan_disbursement", "loan_repayment", "transfer", "reversal", "refund", "fee", "interest_received", "interest_paid", "other"],
        #if not transaction_id in tcredit:
        
        #####
        # SPECIAL CASES:
        #- is transfer a credit?  Depends so don't look at transaction_type
        #
        unused_transaction_types=['transfer'] #ambiguous
        #####
        if True:
            org_class=tcredit.get(transaction_id,None)
            ## Load schema from SCHEMA_kbai-> transaction_type
            if tt.get('transaction_type','unknown') in ['deposit','loan_disbursement','refund','interest_received']:
                tcredit[transaction_id]=True
                reasons+=['True: transaction_type: '+str(tt['transaction_type'])]
            elif tt.get('transaction_type','unknown') in ['purchase','payment','withdrawal','loan_repayment','reversal','fee','interest_paid']:
                tcredit[transaction_id]=False
                reasons+=['False: transaction_type: '+str(tt['transaction_type'])]
            else:
                pass
                #print ("WHAT? "+str(tt['transaction_type']))
                #a=okk
            if not org_class is None and not tcredit[transaction_id]==org_class:
                logging.warning("[Account relation different then transaction type direction]: "+str(reasons)+" ORG: "+str(org_class)+" new: "+str(tcredit[transaction_id]))
                
        ## Easy logic 3
        #> keywords (like alg)
        #> overwrite even if already set well above
        #[ ] may need to refine CREDIT_TO/DEBIT_FROM logic or transaction_type logic.
        #- for now, hardcode most obvious ones.
        #[ ] add more from alg?
        if re.search(r'reversal',tt['transaction_description'],flags=re.I):
            tcredit[transaction_id]=True
            reasons+=['True: deposit']

        if re.search(r'deposit',tt['transaction_description'],flags=re.I):
            tcredit[transaction_id]=True
            reasons+=['True: deposit']

        if re.search(r'refund',tt['transaction_description'],flags=re.I): 
            tcredit[transaction_id]=True
            reasons+=['True: refund']

        if re.search(r'withdraw',tt['transaction_description'],flags=re.I): 
            tcredit[transaction_id]=False
            reasons+=['False withdraw']

        if re.search(r'\bpaid\b',tt['transaction_description'],flags=re.I): 
            tcredit[transaction_id]=False
            reasons+=['False paid']

        ## SECTION LOGIC
        section=tt.get('section','')
        if re.search(r'\bpaid\b',section,flags=re.I): 
            tcredit[transaction_id]=False
            reasons+=['False section paid']
        if re.search(r'withdraw',section,flags=re.I): 
            tcredit[transaction_id]=False
            reasons+=['False section withdrawl']
        if re.search(r'deposit',section,flags=re.I): 
            tcredit[transaction_id]=True
            reasons+=['True section deposit']

        ## logic 4 (so less common ie/ could not classify per above so through error + custom patch)
        if not transaction_id in tcredit:
            if re.search(r'\bcheck\b',tt.get('transaction_method',''),flags=re.I):  #Check would be out
                tcredit[transaction_id]=False
                reasons+=['False check']
                
        ## LOGIC 5
        #> hard logic
        
        ## Transfers can be ambiguous within main account credit/debit but if must:
        # 'Online Transfer To Chk' is_credit=False
        if 'Online Transfer To Chk' in str(tt):
            tcredit[transaction_id]=False
            reasons+=['False: Online Transfer To Chk']
            
        ## Logic:  If orignal statement is SIGNED then hard enforce as plus or minus
        #[ ] add logic check if above not matches org
        if tt.get('amount_sign','')=='-': #Negative
            tcredit[transaction_id]=False
        elif tt.get('amount_sign','')=='+': #Pos
            #* only + if signed transactions (ie/ there exists some -, so should not be false)
            if tcredit.get(transaction_id,None) is False:
                logging.warning("[Signed transaction but classified as debit]: "+str(reasons))
                logging.dev("[Signed transaction but classified as debit]: "+str(reasons))
            tcredit[transaction_id]=True

                
        ## FINAL DEBUG OPTION
        if False:
            if 'Online Transfer' in str(tt):
                print ("AT: "+str(tt))
                print ("REASONS: "+str(reasons))
                a=okkk
                
        if verbose:
            print ("[desc]: "+str(tt['transaction_description'])+" is_credit: "+str(tcredit.get(transaction_id,None))+" reasons: "+str(reasons))
            
   
    is_credit=None
    if not transaction_id in tcredit:
        reasons+=['Warning could not classify credit/debit']
    else:
        is_credit=tcredit[transaction_id]

    return is_credit,tcredit,reasons


def dev_local_easy_credit_debit(case_id='chase_3_66_b3', commit=True,verbose=False):

    ## GIVEN CASE ID do update is really all it is!
    #alg_classify_debit_credit originally but only looks at transaction logic
    #- instead, consider the SENDER + RECEIVER ENTITIES
    meta={}
    meta['qa_notes']=[]
    
    
    if not case_id:
        raise Exception ("No case id at easy_credit_debit")

    ### LOGIC LEVEL 1:  PURE transaction
    # but query for full data needed
    # transaction_type: deposit ** sure but

    mem_credit_debit={}
    results=[]
    for result in query_transactions_with_relations(case_id=case_id):
        results+=[result]
        if result[1] in ['CREDIT_TO','DEBIT_FROM']:
            mem_credit_debit[result[0]['t']['id']]=True
    
    tcredit={}
    all_ids={}
    for aa,relationship_type,related_id in results:

        reasons=[]

        tt=aa['t']
        transaction_id=tt['id']
        transaction_amount=tt['transaction_amount']
        print ("AMOUNTS: "+str(transaction_amount))
        

        if not transaction_id in mem_credit_debit:
            #[ ] add to std QA
            print ("[warning] NO CREDIT_TO or DEBIT_FROM at transaction: "+str(tt))
            logging.dev("[markup_alg_cypher_EASY_CREDIT_DEBIT warning] NO CREDIT_TO or DEBIT_FROM at transaction: "+str(tt))
#            raise Exception ("NO CREDIT_TO or DEBIT_FROM at transaction: "+str(tt))

        elif relationship_type in ['PROCESSED_BY']:
            continue
        elif not relationship_type in ['CREDIT_TO','DEBIT_FROM']:
            ## Look specifically at relationship info (not just transaction info)
            #[ ] optionally classify just on transaction but at this point should have full rel nodes
            print ("SKIP TYPE: "+str(relationship_type))
            continue


        print ("TT> "+str(tt))
        all_ids[transaction_id]=tt
        
        is_credit,tcredit,inner_reasons=is_transaction_credit(tt,tcredit=tcredit,verbose=verbose)
        reasons+=inner_reasons
        if verbose:
            print ("^^ is_credit: "+str(is_credit)+" reasons: "+str(reasons))
        

    ################################################
    ## Check all resolved
    ids_not_found=[]
    for id in all_ids:
        if not id in tcredit and all_ids[id].get('transaction_amount',0):
            meta['qa_notes']+=['[odd_credit_debit_classification (none)]: "+str(all_ids[id])']
            logging.dev("NOT CLASSIFIED as main debit/credit: "+str(all_ids[id]))
            ids_not_found.append(id)


    ## Push updates!  (recall graph style so all updates done here)
    print ("! REUSE CONNECTION!")
    tx=''
    for id in tcredit:
        tt=all_ids[id]
        
        if not tt.get('is_credit',None) is None and tt['is_credit']==tcredit[id]:
            # Exists
            continue
        
        ## UPDATE is_credit
        ## UPDATE transaction_amount to absolute value (assume done most kb needing)
        nn={}
        nn['id']=tt['id']
        nn['is_credit']=tcredit[id]

## Rerun or check elsewhere like in sums or final step??j
        if tt['transaction_amount']<0:
            nn['transaction_amount']=abs(tt['transaction_amount'])
            nn['transaction_raw']=tt['transaction_amount']

        print ("[update] "+str(tt['id'])+" is_credit: "+str(nn['is_credit']))
        
        if commit:
            query=cypher_create_update_node('Transaction',nn)
    
            #for results,tx in Neo.run_stmt(query,tx=tx,verbose=True):
            results,tx= Neo.run_stmt(query,tx=tx,verbose=True)
            #        print ("[debug] got results: "+str(results))
        else:
            logging.info("[skip commit update on easy credit debit (testing)]")
        
        #a=okk
        #cypher_update_transaction(tt)
        #cypher_update_transaction(tt)

    #meta['qa_notes']=[]
    meta['commit']=commit
    return meta


def test_call_classifier_locally():
    # Per transaction or kind?
    case_id='chase_4_a'
    case_id='chase_4_a_33'
    case_id='MarnerHoldingsJune'

    dev_local_easy_credit_debit(case_id=case_id,verbose=True)

    return



if __name__=='__main__':
    
    branches=['QA_transactions_without_debit_credit']
    branches=['dev_local_easy_credit_debit']
    branches=['test_call_classifier_locally']

    for b in branches:
        globals()[b]()
