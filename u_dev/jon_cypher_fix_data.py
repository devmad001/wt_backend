import os
import sys
import time
import codecs
import json
import re

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")

from w_storage.gstorage.gneo4j import Neo

#from a_agent.RUN_sim_wt import call_normal_full_run
#from a_agent.sim_wt import wt_main_pipeline
#
#from a_query.queryset1 import query_statements
#from a_query.queryset1 import query_transaction
#from a_query.queryset1 import query_transactions
#from a_query.admin_query import admin_remove_case_from_kb

from w_storage.gstorage.gneo4j import Neo

from get_logger import setup_logging
logging=setup_logging()


#0v1# JC  Dec 17, 2023  Init

"""
    DEV entry for asking specific questions
"""


def dev1():
    #
    case_id='657f172f9a57063d991dd88b'
    stmt="""
            MATCH (n:Transaction)
            WHERE n.case_id='"""+str(case_id)+"""'
            AND n.transaction_date>'2025-01-01'
            RETURN n
            """
        
    print ("QUERY: "+str(stmt))
    record={}
    for record in Neo.iter_stmt(stmt,verbose=False):   #response to dict
        record=record[0] #list is standard
        print ("> "+str(record))
#        break 

    return



#https://core.epventures.co/api/v1/case/657f172f9a57063d991dd88b/pdf/6fcac963-a70f-4edc-a386-5d8b98ef0832.pdf?page=151&key=800e70fb9829c74a3fbefdc1553cf2f9a2936cba4bc95b5824d0a6bfeb49569d
#https://watchdev.epventures.co/fin-aware/dashboard?case_id=657f172f9a57063d991dd88b

def dev_year_2028_fix():
    case_id = '657f172f9a57063d991dd88b'

    # Query to find and update transactions
    update_stmt = """
        MATCH (n:Transaction)
        WHERE n.case_id='{}' AND n.transaction_date>'2025-01-01'
        SET n.transaction_date = REPLACE(n.transaction_date, '2028', '2021')
        RETURN n
    """.format(case_id)

    print("UPDATE QUERY: " + update_stmt)

    # Execute the update statement
    # Assuming 'Neo.iter_stmt' is a method to execute the statement and iterate over the results
    for record in Neo.iter_stmt(update_stmt, verbose=False):
        record = record[0]  # Assuming the result is a list
        print("> " + str(record))

    return

def dev_one_no_period():
    case_id='657f172f9a57063d991dd88b'
    stmt="""
            MATCH (n:Transaction)
            WHERE n.case_id='"""+str(case_id)+"""'
            AND n.transaction_amount=242223.0
            SET n.transaction_amount=2422.23
            RETURN n
            """
        
    print ("QUERY: "+str(stmt))
    record={}
    for record in Neo.iter_stmt(stmt,verbose=False):   #response to dict
        record=record[0] #list is standard
        print ("> "+str(record))
#        break

    return


def dev_hide_case():
    old_case_id = '657f172f9a57063d991dd88b'
    new_case_id = '657f172f9a57063d991dd88b_jon'

    # Jan 5, 2024 1 page case but seemed to pull in balances as transaction??
    old_case_id='659865416c33e2599cce5b35'
    new_case_id='659865416c33e2599cce5b35_jon'
    
    
    stmt = """
            MATCH (n:Transaction)
            WHERE n.case_id='""" + str(old_case_id) + """'
            SET n.case_id = '""" + str(new_case_id) + """'
            RETURN n
            """
    
    print("QUERY: " + str(stmt))
    record = {}
    for record in Neo.iter_stmt(stmt, verbose=False):   # Response to dict
        record = record[0]  # List is standard
        print("> " + str(record))

    return

def dev_hide_monday_case():
    old_case_id = '6580cfc69a57063d991de1aa'
    new_case_id = '6580cfc69a57063d991de1aa_jon'
    
    stmt = """
            MATCH (n:Transaction)
            WHERE n.case_id='""" + str(old_case_id) + """'
            SET n.case_id = '""" + str(new_case_id) + """'
            RETURN n
            """
    
    print("QUERY: " + str(stmt))
    record = {}
    for record in Neo.iter_stmt(stmt, verbose=False):   # Response to dict
        record = record[0]  # List is standard
        print("> " + str(record))

    return


def manual_cypher():
    #
    case_id='colin_dec_21_direct_multi'
    stmt="""
            MATCH (n:Transaction)
            WHERE n.case_id='"""+str(case_id)+"""'
            RETURN n
            """
        
    print ("QUERY: "+str(stmt))
    record={}
    for record in Neo.iter_stmt(stmt,verbose=False):   #response to dict
        record=record[0] #list is standard
        print ("> "+str(record))
#        break

    return



def manual_colin():
    #
    case_id='6580cfc69a57063d991de1aa'

    stmt="""
            MATCH (n:Transaction)
            WHERE n.case_id='"""+str(case_id)+"""'

            RETURN DISTINCT n.section
            """
        
    print ("QUERY: "+str(stmt))
    rr,tx=Neo.run_stmt(stmt,verbose=False)   #response to dict
    print ("GOT: "+str(rr))
    
    for r in rr:
        print ("> "+str(r))
#        break

#    record={}
#    c=0
#    for record in Neo.iter_stmt(stmt,verbose=False):   #response to dict
#        c+=1
#        record=record[0] #list is standard
#        print ("> "+str(record))
#        
#        if c>100:
#            break
#
#        break

    return


def manual_colin_2_remove_bad_sections():
    #
    from a_query.queryset1 import delete_transaction_node

    case_id='6580cfc69a57063d991de1aa'
    

    WELLSFARGO={}
    WELLSFARGO['skip_sections']=['Summary of checks written','Activity summary','Statement period activity summary']
    WELLSFARGO['skip_sections']+=['Monthly service fee summary','Statement period activity summary']


    stmt="""
            MATCH (n:Transaction)
            WHERE n.case_id='"""+str(case_id)+"""'
            RETURN n
            """
        
    print ("QUERY: "+str(stmt))
#    rr,tx=Neo.run_stmt(stmt,verbose=False)   #response to dict
#    print ("GOT: "+str(rr))
    
    record={}
    c=0
    dcount=0
    for record in Neo.iter_stmt(stmt,verbose=False):   #response to dict
        c+=1
        record=record[0] #list is standard
        
        if 'summary' in record['section'].lower():
            pass
#            print ("sum> "+str(record))

        
        if 'summary' in record['section'].lower():
        #if se and record['section'] in WELLSFARGO['skip_sections']:
            print ("DELETE: "+str(record))
            
            delete_transaction_node(transaction_id=record['id'])
            
#            delete_stmt = """
#                          MATCH (n:Transaction { id: '""" + str(record['id']) + """' })
#                          DELETE n
#                          """
#            # Execute delete query
#            rr,tx=Neo.run_stmt(delete_stmt, verbose=False)
#            print ("GOT: "+str(rr.data()))
#            # {message: Cannot delete node<44446>, because it still has relationships. To delete this node, you must first delete its relationships.}
##            print("DELETEd: " + str(transaction_record))

#            pass
        
#        if c>10:
#            break
#
#        break

    return


def manual_boa_1():
    #
    from a_query.queryset1 import delete_transaction_node

    case_id='6582316b417c4d11647838b7' #BOA raw
    case_id='6587008b36850ea066e5843c' #BOA raw again...
    case_id='65a8168eb3ac164610ea5bc2' # new age demo # esp with section = desc.
    

    stmt="""
            MATCH (n:Transaction)
            WHERE n.case_id='"""+str(case_id)+"""'
            RETURN n
            """
        
    print ("QUERY: "+str(stmt))
#    rr,tx=Neo.run_stmt(stmt,verbose=False)   #response to dict
#    print ("GOT: "+str(rr))
    
    record={}
    c=0
    dcount=0
    for record in Neo.iter_stmt(stmt,verbose=False):   #response to dict
        c+=1
        record=record[0] #list is standard
        
        DO_DELETE=False


        ## BOA Account summary section data cleaning
        ## Account summary
        see=llm_page2t_FORhardcode_transaction_removal_ass
        if True:
            if 'Withdrawals and other debits' == record['section'] == record['transaction_description']: DO_DELETE=True
            if 'Account summary' == record['section']: DO_DELETE=True
            
            if True:
                if 'Beginning balance' == record['section']: DO_DELETE=True
                if 'Daily ledger balances' == record['section']: DO_DELETE=True
                if 'Beginning balance' in record['transaction_description']: DO_DELETE=True
                if 'Deposits and other credits' == record['section'] == record['transaction_description']: DO_DELETE=True
                if 'Service fees' == record['section'] == record['transaction_description']: DO_DELETE=True
       
                if 'Total checks' in record['transaction_description']: DO_DELETE=True #absolute?
                if 'Checks' in record['transaction_description']:
                    if 'Withdrawals' in record['transaction_description']:
                        DO_DELETE=True
   
   
                if 'Checks' == record['section'] == record['transaction_description']: DO_DELETE=True
           ## CHECK FOR DUPLICATES
                if record['section'] == record['transaction_description']:
                    print ("SECTION IS DESC: "+str(record))
           
#               if 'summary' in record['section'].lower():
#                  if se and record['section'] in WELLSFARGO['skip_sections']:

        if DO_DELETE:
            print ("DELETE: "+str(record))
#            a=kkk
            
#            delete_transaction_node(transaction_id=record['id'])
#            a=deleteddd
            

            
            
#            delete_stmt = """
#                          MATCH (n:Transaction { id: '""" + str(record['id']) + """' })
#                          DELETE n
#                          """
#            # Execute delete query
#            rr,tx=Neo.run_stmt(delete_stmt, verbose=False)
#            print ("GOT: "+str(rr.data()))
#            # {message: Cannot delete node<44446>, because it still has relationships. To delete this node, you must first delete its relationships.}
##            print("DELETEd: " + str(transaction_record))
            
#            pass
        
#        if c>10:
#            break
#
#        break

    return


#>> JC:  AUTO CLEANER REQUIRED!  Ideally no.  Need to log when that happens for EACH transactioN!
#- don't just delete it?  learn from it. (at least sqlite)


def manual_demo_jan5():
    #
    from a_query.queryset1 import delete_transaction_node

    case_id='6582316b417c4d11647838b7' #BOA raw
    case_id='6587008b36850ea066e5843c' #BOA raw again...

    case_id='65960931c8fca0cb7b70e024' #EP & Dad Demo
    case_id='659ee02b6c33e2599cce68e2' # 444k giant?

    ## COLIN MANUAL   New Age - Colin's Investigation
    case_id='6596f679c8fca0cb7b70e1fb' #COLIN
    #1.  super large mis-read item!! actually a problem. [ ] need custom fix.
    #      https://core.epventures.co/api/v1/case/6596f679c8fca0cb7b70e1fb/pdf/b584defb-db9a-42da-b612-f5a5dc9b47c2.pdf?page=137&key=75add40ae552468997b3bf96fa895406a75b8ab0936bfc5eaf6a0bef12a24663&highlight=445776.00|1D%3A323242463996|INDN%3APLANET|DES%3ADEPOSIT

    #2.  'Daily ledger balances' section :  add kind so not found. ie:  [ ]
    # https://core.epventures.co/api/v1/case/6596f679c8fca0cb7b70e1fb/pdf/b584defb-db9a-42da-b612-f5a5dc9b47c2.pdf?page=20&key=75add40ae552468997b3bf96fa895406a75b8ab0936bfc5eaf6a0bef12a24663&highlight=38363.20|38%2C363.20|01%2F15
    
    #3.  Account summary still coming up?/
    # https://core.epventures.co/api/v1/case/6596f679c8fca0cb7b70e1fb/pdf/b584defb-db9a-42da-b612-f5a5dc9b47c2.pdf?page=111&key=75add40ae552468997b3bf96fa895406a75b8ab0936bfc5eaf6a0bef12a24663&highlight=44379.79|Withdrawals|debits|other

    
    case_id='65a7d94eac045a667c77c8b1'

    case_id='65a8168eb3ac164610ea5bc2'  # new age vending demo (equal section<>descp on 1)
    case_id='65a82cc9b3ac164610ea5e64' #PJ
    case_id='65a8422cb3ac164610ea602b' #Ratt deposit in section so should be deposit [ ]  **fixed itself?!
    case_id='65a992f8201790c0d929ac0a'

    stmt="""
            MATCH (n:Transaction)
            WHERE n.case_id='"""+str(case_id)+"""'
            RETURN n
            """
        
    print ("QUERY: "+str(stmt))
    rr,tx=Neo.run_stmt(stmt,verbose=False)   #response to dict
    print ("GOT: "+str(rr))
    
    record={}
    c=0
    dcount=0
    for record in Neo.iter_stmt(stmt,verbose=False):   #response to dict
        c+=1
        record=record[0] #list is standard
        
        if not 'section' in record: record['section']=''

        
        DO_DELETE=False
        
        ## CUSTOM TO CASE:
        if False:
            beware=customm
            if '444394.62' == str(record['transaction_amount']): DO_DELETE=True
            if '445776.00' == str(record['transaction_amount']): DO_DELETE=True  #Colin custom
            if '323242463996' in str(record['transaction_description']): DO_DELETE=True  #Colin custom
            if '123.45' == str(record['transaction_amount']): DO_DELETE=True    # One of the prompt samples
            
            if 'deposit' in str(record['section']).lower() and not record['is_credit']: DO_DELETE=True
        if '2021-' in str(record['transaction_date']): DO_DELETE=True 

        ## BOA Account summary section data cleaning
        ## Account summary
        if True:
            if 'Withdrawals and other debits' == record['section'] == record['transaction_description']: DO_DELETE=True
            
            if 'Account summary' == record['section']: DO_DELETE=True
            if 'Daily ledger balances' == record['section']: DO_DELETE=True
            
            if 'Beginning balance' == record['section']: DO_DELETE=True
            if 'Daily ledger balances' == record['section']: DO_DELETE=True
            if 'Beginning balance' in record['transaction_description']: DO_DELETE=True
            if 'Deposits and other credits' == record['section'] == record['transaction_description']: DO_DELETE=True
            if 'Service fees' == record['section'] == record['transaction_description']: DO_DELETE=True

            ## ANY QUAL
            if record['section'] == record['transaction_description']: DO_DELETE=True
   
            if 'Total checks' in record['transaction_description']: DO_DELETE=True
            if 'Checks' in record['transaction_description']:
                if 'Withdrawals' in record['transaction_description']:
                    DO_DELETE=True
   
   
                if 'Checks' == record['section'] == record['transaction_description']: DO_DELETE=True
           ## CHECK FOR DUPLICATES
                if record['section'] == record['transaction_description']:
                    print ("SECTION IS DESC: "+str(record))
           
#               if 'summary' in record['section'].lower():
#                  if se and record['section'] in WELLSFARGO['skip_sections']:

        ##################################################
        if DO_DELETE:
            print ("DELETE: "+str(record))
            dcount+=1
#            a=kkk
            delete_transaction_node(transaction_id=record['id'])
        ##################################################

    print ("Dcount option: "+str(dcount))

    return


"""
TODO:
- force state to no processing
https://watchdev.epventures.co/fin-aware/dashboard?case_id=65960931c8fca0cb7b70e024#

"""



def dev_manual_fix_2026():
    ## https://core.epventures.co/api/v1/case/65cbc1849b6ff316a779fbbd/pdf/81135fd4-4076-4b3b-ba05-62c390081503.pdf?page=50&key=6a407802234eefe949cb4256ef8c441950462c059975f36491884413fa17e88d&highlight=CCD902569003262705|ID%3A372738931883|ID%3AXXXXXXXXXB
    case_id='65cbc1849b6ff316a779fbbd'
#            SET n.transaction_amount=2422.23
    stmt="""
            MATCH (n:Transaction)
            WHERE n.case_id='"""+str(case_id)+"""'
            AND n.transaction_amount=415.00
            AND n.transaction_date='2026-06-18'
            SET n.transaction_date='2021-06-18'
            RETURN n
            """
            
            #65cd00899b6ff316a77a1870
        
    print ("QUERY: "+str(stmt))
    record={}
    for record in Neo.iter_stmt(stmt,verbose=False):   #response to dict
        record=record[0] #list is standard
        print ("> "+str(record))
#        break

    return

def dev_manual_patch_bad_date():
    ## https://core.epventures.co/api/v1/case/65cbc1849b6ff316a779fbbd/pdf/81135fd4-4076-4b3b-ba05-62c390081503.pdf?page=50&key=6a407802234eefe949cb4256ef8c441950462c059975f36491884413fa17e88d&highlight=CCD902569003262705|ID%3A372738931883|ID%3AXXXXXXXXXB
    case_id='65cbc1849b6ff316a779fbbd'
    case_id='65cd00899b6ff316a77a1870' #TD1
    case_id='65cd06669b6ff316a77a1d21' #TD2
    case_id='65caaffb9b6ff316a779f525' #

#            SET n.transaction_amount=2422.23
    stmt="""
            MATCH (n:Transaction)
            WHERE n.case_id='"""+str(case_id)+"""'
            AND n.transaction_date STARTS WITH '5632-'
            SET n.transaction_date = REPLACE(n.transaction_date, '5632-', '2021-')
            RETURN n
            """

        
    print ("QUERY: "+str(stmt))
    record={}
    for record in Neo.iter_stmt(stmt,verbose=False):   #response to dict
        record=record[0] #list is standard
        print ("> "+str(record))
#        break

    return

def dev_check_query():
    stmt="""
    MATCH (Transaction:Transaction {case_id: '65caaffbW9b6ff316a779f525'})
    RETURN COUNT(Transaction) as Total_Transactions
    """
    stmt="""
    MATCH (Transaction:Transaction {case_id: '65caaffb9b6ff316a779f525'})
    RETURN Transaction
    """
    print ("QUERY: "+str(stmt))
    record={}
    for record in Neo.iter_stmt(stmt,verbose=False):   #response to dict
        record=record[0] #list is standard
        print ("> "+str(record))
#        break
    return

def dev_debug():
    import pandas as pd
    from pandas._libs.tslibs.np_datetime import OutOfBoundsDatetime
    
    data = {'date_column': ['2020-05-03', '2021-06-04', '5632-03-03', '2022-08-05']}  # Sample data with an out-of-bounds date
    df = pd.DataFrame(data)
    
    try:
        df['date_column'] = pd.to_datetime(df['date_column'])
    except OutOfBoundsDatetime:
        print("Out of bounds datetime found. Coercing to NaT...")
        df['date_column'] = pd.to_datetime(df['date_column'], errors='coerce')
    
    # Calculate the percentage of valid datetime entries
    valid_percentage = df['date_column'].notna().mean() * 100
    
    # Decision based on the threshold
    threshold = 80
    if valid_percentage >= threshold:
        print(f"Valid datetime entries percentage ({valid_percentage}%) is above the threshold ({threshold}%). Proceeding...")
        df = df.dropna(subset=['date_column'])  # Filter out NaT entries
    else:
        print(f"Valid datetime entries percentage ({valid_percentage}%) is below the threshold ({threshold}%). Consider revising the data.")
    
    print(df)

    return

def dev_start_formal_log():
    from a_query.queryset1 import delete_transaction_node
    
    #1//
    ## https://core.epventures.co/api/v1/case/65cbc1849b6ff316a779fbbd/pdf/81135fd4-4076-4b3b-ba05-62c390081503.pdf?page=50&key=6a407802234eefe949cb4256ef8c441950462c059975f36491884413fa17e88d&highlight=CCD902569003262705|ID%3A372738931883|ID%3AXXXXXXXXXB
    case_id='65d11d5f04aa751147676516'
    # 5000 node formal case 1 super large 1 date lower.
    
    #2// [ ] capture this?? as??
    #// TASKS:  get pdf page.  realize still summary issue.  due to extra (s) at ends of wording.
    case_id='65d65ae49be7358de5d1fb89'

#            SET n.transaction_amount=2422.23
    stmt="""
            MATCH (n:Transaction)
            WHERE n.case_id='"""+str(case_id)+"""'
            AND n.transaction_amount=1043000.00
            RETURN n
            """
            #AND n.transaction_amount>10000000

    ## Transaction description(s) withdrawl(s) cause error here.
    stmt = """
    MATCH (n:Transaction)
    WHERE n.case_id='""" + str(case_id) + """'
    AND toLower(n.transaction_description) CONTAINS 'other withdrawal'
    AND toLower(n.section) CONTAINS 'other withdrawal'
    RETURN n
    """
    ## single too far left [x] bad year gap, put in feedback AND n.transaction_amount=52.08

    print ("QUERY: "+str(stmt))
    record={}
    for record in Neo.iter_stmt(stmt,verbose=False):   #response to dict
        record=record[0] #list is standard
        print ("> "+str(record))
        delete_transaction_node(transaction_id=record['id'])

#        break

    return


if __name__=='__main__':
    branches=['dev_year_2028_fix']
    branches=['dev1']
    branches=['dev_one_no_period']
    
    branches=['manual_cypher']
    
    branches=['manual_colin_1_view_sections']
    branches=['manual_colin_2_remove_bad_sections']

    branches=['dev_hide_monday_case']
    branches=['manual_boa_1']


    branches=['dev_hide_case']
    branches=['manual_demo_jan5']
    branches=['dev_manual_fix_2026']

    branches=['dev_check_query']
    branches=['dev_debug']

    branches=['dev_manual_patch_bad_date']
    branches=['dev_start_formal_log']

    for b in branches:
        globals()[b]()



