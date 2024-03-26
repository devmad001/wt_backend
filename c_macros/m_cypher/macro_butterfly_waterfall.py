import os,sys
import time
import re
import json
import copy
import pandas as pd
import datetime
import matplotlib.pyplot as plt

import configparser as ConfigParser

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../../")

from w_utils import similarity_string

from w_storage.gstorage.gneo4j import Neo
from w_chatbot.wt_brains import Bot_Interface

from a_algs.ner_algs.alg_normalize_entity_name import alg_normalize_entity_name

from macro_queries import alg_resolve_main_account_NAMES
from macro_queries import alg_resolve_opening_balance
from macro_queries import alg_get_main_account_names
from macro_queries import get_normalized_name_mapping


from get_logger import setup_logging
logging=setup_logging()



#0v2# JC  Dec 16, 2023  Migrate generic queries to macro_queries
#0v1# JC  Nov 24, 2023  Setup


"""
    MACROS FOR AUTO WRITING CYPHER QUERIES

    [todo1]: handle main account
    [todo2]: transactions always unique, right?
"""

def cypher_query_account_flows(case_id=''):
    ## Return  SENDER (DEBIT_FROM) -> Transaction - (CREDIT_TO) RECEIVER
    # Entity == SENDER/RECEIVER or loosely account
    stmt = f"""
MATCH (DebitEntity:Entity)-[:DEBIT_FROM]->(Transaction:Transaction)-[:CREDIT_TO]->(CreditEntity:Entity)
WHERE
    Transaction.case_id = '{case_id}'
RETURN
    Transaction,DebitEntity,CreditEntity
ORDER BY Transaction.transaction_date
    """
    if not 'ORDER BY' in stmt:
        raise Exception("ORDER BY required because waterfall dates")
    return stmt

def local_iter_run_query(stmt):
    c=0
    #for dd in Neo.iter_stmt(stmt,verbose=True):   #response to dict
    #    yield dd
    data_response,df,tx,meta=Neo.run_stmt_to_normalized(stmt,tx='')
    return data_response
    
def local_ask_question(question,case_id):
    Bot=Bot_Interface()
    Bot.set_case_id(case_id=case_id)
    answer,answer_dict=Bot.handle_bot_query(question)

    print (" answer> "+str(answer_dict))
    print (" answer> "+str(answer))

    return


def experiments_on_visualizing_waterfall():

    #NOTES:  first visual ok,  second is fine but bars not attached to moving line
    
    # VISUALIZE DATES (waterfall try two ways)
    #############################################
    #> VISUALIZE WATERFALL
    ############################
    ## Visual 1:  date,entity,debit,credit  (expanded stacked on waterfall)
    # Sort the DataFrame for visualization
    df_date_sorted = df_date.sort_values(by=['date', 'debit_total', 'credit_total'])
    # Display the DataFrame
    print(df_date_sorted.head(10))  # Adjust number of rows to display as needed
    
    ## Visual 2:  waterfall simple up/down bars
    # Visual 2: Group by date and sum amounts

    # Visualize Visual 2 -- standard bar ok
    #  -----------------

    if 'standard bar' in []:
        df_date_grouped = df_date.groupby('date').agg({'debit_total': 'sum', 'credit_total': 'sum'}).reset_index()
        df_date_grouped.plot(x='date', y=['debit_total', 'credit_total'], kind='bar', stacked=True)
        plt.title('Daily Debit and Credit Totals')
        plt.xlabel('Date')
        plt.ylabel('Amount')
        plt.show()
    


    if 'running balance with sum per day' in []: #ok just not fancy looking

        # Group by date and sum amounts
        df_date_grouped = df_date.groupby('date').agg({'debit_total': 'sum', 'credit_total': 'sum'}).reset_index()
    
        # Calculate net change for each date
        df_date_grouped['net_change'] = df_date_grouped['credit_total'] - df_date_grouped['debit_total']
    
        # Calculate running balance
        df_date_grouped['running_balance'] = df_date_grouped['net_change'].cumsum()
    
        # Prepare data for waterfall chart
        df_waterfall = pd.DataFrame({
            'date': df_date_grouped['date'],
            'increase': df_date_grouped['net_change'].clip(lower=0),
            'decrease': df_date_grouped['net_change'].clip(upper=0).abs(),
        })
    
        # Plot waterfall chart
        fig, ax = plt.subplots()
        df_waterfall.plot(x='date', y=['increase', 'decrease'], kind='bar', stacked=True, color=['green', 'red'], ax=ax)
        
        # Create a secondary Y-axis for the running balance
        ax2 = ax.twinx()
        ax2.plot(df_date_grouped['date'], df_date_grouped['running_balance'], color='blue', marker='o')
        
        ax.set_title('Waterfall Chart of Daily Net Change and Running Balance')
        ax.set_xlabel('Date')
        ax.set_ylabel('Net Change Amount')
        ax2.set_ylabel('Running Balance')
        plt.show()
            

    #############################################

    ## CUSTOM QUERY
    if 'custom query' in []:
        question='Show me the payee name and amount'
        local_ask_question(question,case_id)
    

    print ("DONE")
    return


"""
 DATA DEFINITION FOR WATERFALL:
V1

[ ] these definitions and assumptions need to roll up to larger graphs + data usages.


[ top assumptions / definitions ]
1.  Main account absolute resolution is pending.  So base off name could be:
-  ‘main_account’
-  Account holder name from statement
-  Top used name (freq/size) that matches account holder name from statement.

2.  Opening balance
- zero?
- alg_get_case_opening balance? (tbd where)
- alg_get_related_case_statement_opening_balance?

3.  Closing balance
- alg_get_case_closing balance? (tbd where)
- alg_get_related_case_statement_closing_balance?
- closing as calculated between opening +/- credits

4.  Line balance
- Use is_credit flag to calculate? (that’s the hard wired better way).
- Use name of main_account based to calculate?  Fine but not absolute and won’t match is_credit assumption at MAIN ACCOUNT.

- waterfall debit/credit simple
- recall, on a date basis.  Should match line balance calc depending on assumptions there.

- waterfall debit/credit stacked
>> leave some logic in but don’t refine give above.
"""

def local_is_credit(sender_name,receiver_name,main_names,record={}):
    #** patch when is_credit missing (don't assume)
    is_credit=False
    if sender_name in main_names:
        is_credit=True
    elif receiver_name in main_names:
        is_credit=False
    else:
        logging.warning("[unknown credit (main) status for raw transaction]: "+str(record))
        logging.dev("[unknown credit (main) status for raw transaction]: "+str(record))
        #raise Exception("unknown credit (main) status for raw transaction")
#        raise Exception("unknown credit (main) status for raw transaction")
        #on_method_id': 'Xxxxxx7903'}, 'DebitEntity': {'role': 'SENDER', 'name': 'unknown', 'label': 'Entity', 'id': '6570af77949fdfbf2c5810e8-Xxxxxx7903', 'type': 'check', 'entity_id': 'Xxxxxx7903'}, 'CreditEntity': {'role': 'SENDER', 'name': 'unknown', 'label': 'Entity', 'id': '6570af77949fdfbf2c5810e8-unknown', 'type': 'bank', 'entity_id': 'unknown'}}
    return is_credit

def waterfall_graphs_process_flow(case_id=''):
    ## AKA:  Balance line graph with debit/credit view
    #- two parts here:  1/  balance line graph  2/  debit/credit view
    # waterfall is the debit/credit view which is both _simple or _stacked
    #- practically, stacked isn't displayable (too many accounts but keep here incase want to group later)
    #- balance requires balance against MAIN ACCOUNT
    #   - main account absolution resolution (stored) is tbd so do on a NAME basis
    
    ## Get main account names (as part of main account normalization)
    main_account_names=alg_resolve_main_account_NAMES(case_id=case_id)
    logging.info("[main account names (forms balance line)]: "+str(main_account_names))
    
    ## TBD
    opening_balance_assumption=alg_resolve_opening_balance(case_id=case_id) #[ ] get from statement or own alg
    
    ## Write cypher query to get account flows
    stmt=cypher_query_account_flows(case_id=case_id)
    
    ####################################
    ## Rollup stats from raw results
    #b)  sum debit/credits by entity by date: stats_date={}      -- for waterfall (stacked option)

    c = 0
    print("RUNNING: " + str(stmt))

    balance_by_date={}
    waterfall_by_date={}  #but not stacked just debit/credit category

    ## Query sorts oldest to newest
    balance=opening_balance_assumption

    ## Append old balance.  No.
    for record in local_iter_run_query(stmt):
        c += 1
    
        # Extract data from record
        the_date = record['Transaction']['transaction_date']
        amount = abs(record['Transaction']['transaction_amount'])
        ## Amount round to 2 decimals (possible rounding error but fine)
    
        # SENDER ACCOUNT NAME
        sender_name = record['DebitEntity']['name']
        sender_entry = {'debit_total': 0, 'credit_total': 0}
        
        # RECEIVER ACCOUNT NAME
        receiver_name = record['CreditEntity']['name']
        receiver_entry = {'debit_total': 0, 'credit_total': 0}
        
        #**see assumptions and definition for waterfall
        # Locally, base of is_credit where assume main account is always involved in transaction
        #[ ] optionally check Entity.name in main_account_names but add as option
        if not 'is_credit' in record['Transaction']:
            ## Patch value
            is_main_credit_assumption=local_is_credit(sender_name,receiver_name,main_account_names,record=record)
        else:
            is_main_credit_assumption=record['Transaction']['is_credit']
            

        if is_main_credit_assumption:
            amount=amount
        else:
            amount=-amount


        ### BUILD DATA FOR LINE
        balance+=amount
            
        if not the_date in balance_by_date:
            balance_by_date[the_date]=balance  #First time date gets value its' balance (otherwise change in balance)
        else:
            # Date has balance so update with new balance via amount
            balance_by_date[the_date]+=amount
            

        ### BUILD DATA FOR WATERFALL
        categories=[] #Ideally they could be stacked bar-graph of account NAMES like but keep SIMPLE for now
        categories+=['debit','credit']
        
        ## Entries for both sender and receiver (debit/credit amounts) but that's equal unless main
        # ** recall, amount is negative for debits (per above)
        if is_main_credit_assumption:
            ## Main is credit so apply amount to 'credit' category (ignore other account name)
            if not the_date in waterfall_by_date:
                waterfall_by_date[the_date]={'debit':0,'credit':amount}
            else:
                waterfall_by_date[the_date]['credit']+=amount
        else:
            ## Main is debit so apply amount to 'debit' category (ignore other account name)
            if not the_date in waterfall_by_date:
                waterfall_by_date[the_date]={'debit':amount,'credit':0}
            else:
                waterfall_by_date[the_date]['debit']+=amount
                
    print("Loaded " + str(c) + " records into date count: " + str(len(waterfall_by_date)))
    
    ## Styling iteration of data (round numbers)
    for the_date in waterfall_by_date:
        waterfall_by_date[the_date]['debit']=round(waterfall_by_date[the_date]['debit'],2)
        waterfall_by_date[the_date]['credit']=round(waterfall_by_date[the_date]['credit'],2)
    for the_date in balance_by_date:
        balance_by_date[the_date]=round(balance_by_date[the_date],2)

    
    ## WATERFALL
    if False: #True:
        print ("LINE AMOUNTS: "+str(json.dumps(balance_by_date,indent=4)))
        print ("WATERFALL AMOUNTS: "+str(json.dumps(waterfall_by_date,indent=4)))
    

    data={}
    data['balance_by_date']=balance_by_date
    data['waterfall_by_date']=waterfall_by_date

    return data
    

def butterfly_graphs_process_flow(case_id=''):
    ## AKA:  INFLOW / OUTFLOWS
    
    ## [1]  CYPHER to dump all transactions with source and target nodes "account flows"
    stmt=cypher_query_account_flows(case_id=case_id)
    
    ## [2]  PROCESS RAW RECORDS TO BASIC STATS
    print ("RUNNING: "+str(stmt))
    data = []
    stats={}
    record_count=0
    
    
    earliest_date = None
    latest_date = None

    for record in local_iter_run_query(stmt):
        record_count += 1
        
        ## GET DATE AND TRACK EARLIEST AND LATEST
        the_date = record['Transaction']['transaction_date']  # 'transaction_date': '2021-06-28',
        
        # Convert the string date to a datetime object for comparison
        try:
            transaction_date = datetime.datetime.strptime(the_date, "%Y-%m-%d")
        except: transaction_date=''
        
        if transaction_date:
            # Update earliest and latest dates
            if earliest_date is None or transaction_date < earliest_date:
                earliest_date = transaction_date
            if latest_date is None or transaction_date > latest_date:
                latest_date = transaction_date
        

        amount = abs(record['Transaction']['transaction_amount'])
    
        # SENDER ACCOUNT NAME
        sender_name = record['DebitEntity']['name']
        if sender_name not in stats:
            stats[sender_name] = {'debit_total': 0, 'credit_total': 0}
        stats[sender_name]['debit_total'] += amount
    
        # RECEIVER ACCOUNT NAME
        receiver_name = record['CreditEntity']['name']
        if receiver_name not in stats:
            stats[receiver_name] = {'debit_total': 0, 'credit_total': 0}
        stats[receiver_name]['credit_total'] += amount
    
        # Append to data list for DataFrame creation
        data.append({'name': sender_name, 'debit_total': stats[sender_name]['debit_total'], 'credit_total': stats[sender_name]['credit_total']})
        data.append({'name': receiver_name, 'debit_total': stats[receiver_name]['debit_total'], 'credit_total': stats[receiver_name]['credit_total']})
    

    # Convert dates back to strings for output, if they exist
    earliest_date_str = earliest_date.strftime("%Y-%m-%d") if earliest_date else ""
    latest_date_str = latest_date.strftime("%Y-%m-%d") if latest_date else ""


    print(f"Loaded {record_count} records")
    if not record_count:
        logging.info("[info] no records so return empty data")
        return data,earliest_date_str,latest_date_str

    # Create DataFrame
    df_butterfly_unsorted = pd.DataFrame(data)


    ## [3]  REMAP NAMES TO CLEAN "normalized"
    #-  Real-time normalize names for UI view
    #-  require regroup of stats (sums)
    name_mapping=get_normalized_name_mapping(df_butterfly_unsorted)
    
    ## Apply name mapping to df and regroup sums
    df_butterfly_unsorted_normalized = df_butterfly_unsorted.copy()
    try:
        df_butterfly_unsorted_normalized = df_butterfly_unsorted.copy()
        df_butterfly_unsorted_normalized['name'] = df_butterfly_unsorted_normalized['name'].map(name_mapping)
        df_butterfly_unsorted_normalized= df_butterfly_unsorted_normalized.groupby('name').agg({'debit_total': 'sum', 'credit_total': 'sum'}).reset_index()
    except Exception as e:
        logging.dev("ERROR at butterfly name: "+str(df_butterfly_unsorted_normalized))
        logging.dev("ERROR at butterfly name: "+str(e))
    
    ###### 
    ## [4]  SORT BUTTERFLY by absolute size and debits and then credits
    #> If abs(debit_total) is greater than abs(credit_total), the entry should be sorted within the debits based on the value of debit_total.
    #> If abs(debit_total) is less than abs(credit_total), the entry should be sorted within the credits based on the value of credit_total.
    #> Sort Order: The entries should be sorted in ascending order within their respective groups (debits or credits).
    
    # Categorize each entry as 'debit' or 'credit' for sorting
    df_butterfly_unsorted_normalized['sort_category'] = df_butterfly_unsorted_normalized.apply(
        lambda row: 'debit' if abs(row['debit_total']) > abs(row['credit_total']) else 'credit', 
        axis=1
    )
    
    # Separate the data into two DataFrames for debits and credits
    df_debits = df_butterfly_unsorted_normalized[df_butterfly_unsorted_normalized['sort_category'] == 'debit']
    df_credits = df_butterfly_unsorted_normalized[df_butterfly_unsorted_normalized['sort_category'] == 'credit']
    
    # Sort each DataFrame
    df_debits.sort_values(by='debit_total', inplace=True)
    df_credits.sort_values(by='credit_total', inplace=True)
    
    # Combine the sorted DataFrames
    df_sorted_butterfly = pd.concat([df_debits, df_credits])
    
    # Drop the utility column
    df_sorted_butterfly.drop('sort_category', axis=1, inplace=True)
    ###### ^^^^  Create special waterfall sort

    ## [5]  OPTIONAL PRE-FILTER DATA
    #- remove main account because will skew all results (magnitude difference)
    df_sorted_butterfly=butterfly_custom_drop_entries(df_sorted_butterfly)
    
    ## [6]  FINAL STYLE
    #- to two digit floats
    df_sorted_butterfly['debit_total'] = df_sorted_butterfly['debit_total'].apply(lambda x: round(x, 2))
    df_sorted_butterfly['credit_total'] = df_sorted_butterfly['credit_total'].apply(lambda x: round(x, 2))

    # Apply currency formatting to specific columns
    df_sorted_butterfly['credit_total'] = df_sorted_butterfly['credit_total'].apply(lambda x: round(x, 2))

    df_sorted_butterfly['debit_total'] = df_sorted_butterfly['debit_total'].apply(lambda x: round(x, 2))

    # Print the formatted DataFrame
#D#    print(df_sorted_butterfly.to_string(index=False))


    data = {
        'butterfly_sorted': df_sorted_butterfly.to_dict(orient='records')
        }
    
    return data,earliest_date_str,latest_date_str


def butterfly_custom_drop_entries(df):
    """
        Drop any entries that are main account (for now a local main identifier)
    """
    main_account_names=alg_resolve_main_account_NAMES(case_id='MarnerHoldingsB')
    drop_names=["",'Unknown']+main_account_names

    df_dropped=copy.deepcopy(df)
    logging.info("[dropping main accounts from butterfly]: "+str(drop_names))
    df_dropped = df_dropped[~df_dropped['name'].isin(drop_names)]
    
    if False:
        """
        Drops the entry with the largest combined debit and credit total,
        and any entries named 'Main_Account' or 'Main Account' from the provided DataFrame.
        """
    
        # Drop entries named 'Main_Account' or 'Main Account'
        df_dropped = df_dropped[~df_dropped['name'].isin(['Main_Account', 'Main Account'])]
    
    
        # Find the name of the entry with the largest combined total
        name_of_largest = df_dropped.loc[(df_dropped['debit_total'] + df_dropped['credit_total']).idxmax(), 'name']
    
        # Drop the largest entry
        df_dropped = df_dropped[df_dropped['name'] != name_of_largest]
    
        print ("[debug] drop largest entry]: "+str(name_of_largest))
    
    return df_dropped


def dev_call_do_butterfly_graphs():
    case_id='MarnerHoldingsB'
    butterfly_graphs_process_flow(case_id=case_id)
    return

def dev_call_do_waterfall_graphs():
    case_id='MarnerHoldingsB'
    waterfall_graphs_process_flow(case_id=case_id)
    return


def alg_DEVNOTES_for_account_resolution():
    ## When main_account <> main_account
    ## When Marner Holdings Inc <> Marner Holdings Inc
    ## When main_account <> Marner Holdings Inc
    ## When Unknown <> abc
    ## When '' <> abc
    ## When abc <> abc

    return


def interface_get_waterfall(case_id):
    ## For charting
    meta={}
    data=waterfall_graphs_process_flow(case_id=case_id)
    ## Include style
    
    return data,meta

def interface_get_butterfly(case_id):
    ## For charting
    meta={}
    data,earliest_date,latest_date=butterfly_graphs_process_flow(case_id=case_id)
    
    style={}
    style['x_axis_title']='Debit/Credit Amounts'
    style['y_axis_title']='Entities'
    style['main_title']='Debit and Credit Amounts by Entity'

    style['time_period']='2022-02-1 - 2022-06-01'
    style['time_period']=earliest_date+" - "+latest_date

    big_data={}
    big_data['data']=data
    big_data['style']=style
    
    return big_data,meta


def test_call_local_graph_source():

    case_id='MarnerHoldingsB'

    data_waterfall=interface_get_waterfall(case_id)
    data_butterfly=interface_get_butterfly(case_id)
    
    print ("WATERFALL ------")
    print (str(json.dumps(data_waterfall,indent=4)))
    print ("BUTTERFLY ------")
    print (str(data_butterfly))

    return

if __name__=='__main__':
    branches=['dev1']
    branches=['call_alg_resolve_main_account_NAMES']

    branches=['dev_call_do_butterfly_graphs']
    branches=['dev_call_do_waterfall_graphs']

    branches=['test_call_local_graph_source']
    
    for b in branches:
        globals()[b]()
    




"""
 {'BankStatement': {'account_number': '000000539360823', 'account_holder_name': 'Marner Holdings Inc', 'bank_address': 'P O Box 182051, Columbus, OH 43218 - 2051', 'label': 'BankStatement', 'statement_date': '2021-06-30', 'account_holder_address': '6030 S Eastern Ave, Commerce CA 90040', 'closing_balance': 89872.11, 'case_id': 'MarnerHoldingsB', 'bank_name': 'CHASE', 'opening_balance': 113351.19, 'id': 'MarnerHoldingsB-2021-06-30-000000539360823-2021-06June-statement-0823.pdf', 'statement_period': '2021-06-09 to 2021-06-30'}}

 'statement_id': 'MarnerHoldingsB-2021-05-29-000000539360823-2021-06June-statement-0823.pdf',

"""
 

"""

 ORG WATERFALL NOTES
 *** THIS GIVES POSSIBLE STACKED BUT REMOVED FOR NOW -- until balance + main accounts are resolved

 
def waterfall_graphs_process_flow(case_id=''):
    ## AKA:  Balance line graph with debit/credit view
    #- two parts here:  1/  balance line graph  2/  debit/credit view
    # waterfall is the debit/credit view which is both _simple or _stacked
    #- practically, stacked isn't displayable (too many accounts but keep here incase want to group later)
    #- balance requires balance against MAIN ACCOUNT
    #   - main account absolution resolution (stored) is tbd so do on a NAME basis
    
    ## Get main account names (as part of main account normalization)
    main_account_names=alg_resolve_main_account_NAMES(case_id=case_id)
    logging.info("[main account names (forms balance line)]: "+str(main_account_names))
    
    ## Write cypher query to get account flows
    stmt=cypher_query_account_flows(case_id=case_id)
    
    ####################################
    ## Rollup stats from raw results
    #b)  sum debit/credits by entity by date: stats_date={}      -- for waterfall (stacked option)

    c = 0
    data_date = []  # Initialize the list for DataFrame creation
    print("RUNNING: " + str(stmt))
    
    balance_by_date=[]
    
    for record in local_iter_run_query(stmt):
        c += 1
    
        # Extract data from record
        the_date = record['Transaction']['transaction_date']
        amount = abs(record['Transaction']['transaction_amount'])
    
        # SENDER ACCOUNT NAME
        sender_name = record['DebitEntity']['name']
        sender_entry = {'debit_total': 0, 'credit_total': 0}
        sender_is_main=sender_name in main_account_names
        
        # RECEIVER ACCOUNT NAME
        receiver_name = record['CreditEntity']['name']
        receiver_entry = {'debit_total': 0, 'credit_total': 0}
        receiver_is_main=receiver_name in main_account_names
    
        # Update or create the entries for sender and receiver
        if the_date in data_date:
            sender_entry = next((item for item in data_date if item['date'] == the_date and item['name'] == sender_name), sender_entry)
            receiver_entry = next((item for item in data_date if item['date'] == the_date and item['name'] == receiver_name), receiver_entry)
    
        sender_entry['debit_total'] += amount
        receiver_entry['credit_total'] += amount
    
        # Append or update the entries in data_date
        if sender_entry not in data_date: 
            data_date.append({'date': the_date, 'name': sender_name, **sender_entry})
        if receiver_entry not in data_date: 
            data_date.append({'date': the_date, 'name': receiver_name, **receiver_entry})
    
    print("Loaded " + str(c) + " records")
    
    # Create DataFrame
    df_date = pd.DataFrame(data_date)

    # Option 1: Waterfall  (date group)
    df_waterfall_date_grouped_simple = df_date.groupby('date').agg({'debit_total': 'sum', 'credit_total': 'sum'}).reset_index()

    # Option 2: Stacked bar on waterfall (date group)
    df_waterfall_date_grouped_stacked = df_date.groupby(['date', 'name']).agg({'debit_total': 'sum', 'credit_total': 'sum'}).reset_index()
    
    ## [3]  REMAP NAMES TO CLEAN "normalized"
    #-  Real-time normalize names for UI view
    #-  require regroup of stats (sums)
    name_mapping=get_normalized_name_mapping(df_date)
    
    df_date_normalized = df_date.copy()

    # Waterfall (date group) - Simple
    df_waterfall_date_grouped_simple_normalized = df_date_normalized.groupby('date').agg({'debit_total': 'sum', 'credit_total': 'sum'}).reset_index()
    
    # Waterfall (date group) - Stacked Bar
    df_waterfall_date_grouped_stacked_normalized = df_date_normalized.groupby(['date', 'name']).agg({'debit_total': 'sum', 'credit_total': 'sum'}).reset_index()
    



    

    ## WATERFALL
    #- add balanced trend line
    print (df_waterfall_date_grouped_simple_normalized)
    a=kk


    ## Return 6 dfs as dict/json
    
    ## Continue at:
    #- waterfall to include balance line, opening and closing numbers


    
    return
    

"""
