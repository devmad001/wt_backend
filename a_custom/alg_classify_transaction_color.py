import os
import sys
import codecs
import time
import json
import re
import ast
import random
import pandas as pd

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")

from alg_classify_debit_credit import resolve_debit_credit_main_account_v2
from w_storage.gstorage.gneo4j import Neo
from kb_ask.kb_answer_multimodal import prepare_timeline_data


from get_logger import setup_logging
logging=setup_logging()


#0v3# JC  Jan 16, 2024  dump_color_palette no longer called by default (FE team static the colors)
#0v2# JC  Nov 18, 2023  Add prepare_timeline_data if transaction value column not transaction_amount
#0v1# JC  Oct 27, 2023  Init

"""
    Mostly for timeline node colors
    - org the obs had logic on some lookup

"""

def count_unique_debit_credits(all_transactions):
    #** called once per
    
    list_unique_debit=[]
    list_unique_credit=[]
    for t in all_transactions:
        is_t_credit,is_t_debit=resolve_debit_credit_main_account_v2(t)
        if is_t_debit:
            if not t['section'] in list_unique_debit:
                list_unique_debit.append(t['section'])
        else:
            if not t['section'] in list_unique_credit:
                list_unique_credit.append(t['section'])
                
    if True:
        print ("DEBITS because: "+str(list_unique_debit))
        print ("CREDITS because: "+str(list_unique_credit))

    return list_unique_debit,list_unique_credit
    
def alg_map_transaction_to_color(tt,all_transactions=[],list_unique_debit=[],list_unique_credit=[]):
    #; list_unique_*  used to determine if multiple colors needed (essentially list of sections)
    
    ## See default d3 styling in beeswarm?
    
    ## Recall
    #  .attr('fill', d => d.datum.color ? d.datum.color : (d.datum.value === 1 ? '#4e79a7' : '#f28e2c'));
   
    # original blue (a bit too dark): #4e79a7
    # original orange: #f28e2c
    
    ### DEFAULTS?

    ### LOGIC:
    #- if only 1 type of debit or credit then leave as default
    #** see all_transactions
    
    is_credit,is_debit=resolve_debit_credit_main_account_v2(tt)
    
    ## SPECIFIC TYPE MAP OR JUST GENERAL?
    
    ## ORANGE
    debit_colors={}
    debit_colors['tbd1']='#f28e2c'
    debit_colors['tbd2']='#b08f6d' # grey orange https://www.w3schools.com/colors/colors_picker.asp
    debit_colors['tbd3']='#ab8f73' # grey orange 25%
    debit_colors['tbd4']='#f2c02c' # yellowish orange
    debit_colors['tbd5']='#f22c2c' # red orange

    ## BLUE CREDIT
    credit_colors={}
    credit_colors['tbd1']='#4e79a7'
    credit_colors['tbd2']='#a8bed6'  #light blue
    credit_colors['tbd3']='#6e7a87'  # dark blue grey
    credit_colors['tbd4']='#afbfcf'  # light blue grey
    credit_colors['tbd5']='#4e79a7'  # dark blue
    
    d_colors=list(debit_colors.values())
    c_colors=list(credit_colors.values())
    
    ## Assign per count of sections for each
    
    ## Count unique sections per type
    if not list_unique_debit and not list_unique_credit:
        list_unique_debit,list_unique_credit=count_unique_debit_credits(all_transactions)

    cdebit=len(list_unique_debit)
    ccredit=len(list_unique_credit)
    
    if is_debit and cdebit==1:
        color='#f28e2c'
    elif is_credit and ccredit==1:
        color='#4e79a7'
    else:
        ## Choose color based on where the section matches index in the list
        if is_debit:
            if tt['section'] in list_unique_debit:
                section_index=list_unique_debit.index(tt['section'])
            else:
                section_index=0
            color=d_colors[section_index%len(d_colors)]
        else:
            if tt['section'] in list_unique_credit:
                section_index=list_unique_credit.index(tt['section'])
            else:
                section_index=0
            color=c_colors[section_index%len(c_colors)]
    
    return color,list_unique_debit,list_unique_credit


def local_cypher_transactions(case_id=''):
    #** via z_apiengine/services/timeline_service

    stmt="""
    MATCH (t:Transaction)
    WHERE t.case_id='"""+str(case_id)+"""'
    return t
    """
    jsonl,df,tx,meta=Neo.run_stmt_to_normalized(stmt)
    records=[]
    for record in jsonl:
        records.append(record['t'])
    return records
    
def dev1():
    ## Simulate timeline query (see api core likely)
    case_id='ColinFCB1'
    ts=local_cypher_transactions(case_id=case_id)
    
    for record in ts:
        color,meta=alg_map_transaction_to_color(record)
        

    return

#REF: https://m2.material.io/design/color/the-color-system.html#tools-for-picking-colors
colors = {
    "Green": {
        "50": "#E8F5E9",
        "100": "#C8E6C9",
        "200": "#A5D6A7",
        "300": "#81C784",
        "400": "#66BB6A",
        "500": "#4CAF50",
        "600": "#43A047",
        "700": "#388E3C",
        "800": "#2E7D32",
        "900": "#1B5E20",
    },
    "Blue": {
        "50": "#E3F2FD",
        "100": "#BBDEFB",
        "200": "#90CAF9",
        "300": "#64B5F6",
        "400": "#42A5F5",
        "500": "#2196F3",
        "600": "#1E88E5",
        "700": "#1976D2",
        "800": "#1565C0",
        "900": "#0D47A1",
    },
    "Blue Gray": {
        "50": "#ECEFF1",
        "100": "#CFD8DC",
        "200": "#B0BEC5",
        "300": "#90A4AE",
        "400": "#78909C",
        "500": "#607D8B",
        "600": "#546E7A",
        "700": "#455A64",
        "800": "#37474F",
        "900": "#263238",
    },

    "Red": {
        "50": "#FFEBEE",
        "100": "#FFCDD2",
        "200": "#EF9A9A",
        "300": "#E57373",
        "400": "#EF5350",
        "500": "#F44336",
        "600": "#E53935",
        "700": "#D32F2F",
        "800": "#C62828",
        "900": "#B71C1C",
    },
    "Deep Purple": {
        "50": "#EDE7F6",
        "100": "#D1C4E9",
        "200": "#B39DDB",
        "300": "#9575CD",
        "400": "#7E57C2",
        "500": "#673AB7",
        "600": "#5E35B1",
        "700": "#512DA8",
        "800": "#4527A0",
        "900": "#311B92",
    },
}

##########
# COLORS PLACED IN AMOUNT FREQUENCY ORDER
##########

## LOAD FOR PREVIEW:


selected_colors_green = [
    "#005d57", # Ralley 1/4 good on dark grey
    "#007d51", # Ralley 2/4
    "#1eb980", # Ralley 3/4
    "#37efba", # 4.4
    "#43A047", #colors["Green"]["600"],
    "#1B5E20", #colors["Green"]["900"], # Dark green
    "#81C784", #colors["Green"]["300"],
    "#0D47A1", #colors["Blue"]["900"],
    "#1E88E5", #colors["Blue"]["600"],
    "#64B5F6", #colors["Blue"]["300"],
    "#263238", # blue gray"900": "#263238",
    "#546E7A", #colors["Blue Gray"]["600"],
    "#90A4AE"  #colors["Blue Gray"]["300"],
]


#** these are close
selected_colors_red = [
    "#E53935",  # Red 600
    "#B71C1C",  # Red 900 - Dark red
    "#E57373",  # Red 300
    "#311B92",  # Deep Purple 900
    "#5E35B1",  # Deep Purple 600
    "#9575CD",  # Deep Purple 300
    "#263238",  # Blue Gray 900
    "#546E7A",  # Blue Gray 600
    "#90A4AE",  # Blue Gray 300
]

#####################
# v3:  rally mostly

## RED:
# NOTES:  Mostly red, orange then some purple not bad
#https://projects.susielu.com/viz-palette?colors=[%22#ff0600%22,%22#ff6859%22,%22#b50000%22,%22#ff7000%22,%22#ffac12%22,%22#ffcf44%22,%22#9200c8%22,%22#b15dff%22]&backgroundColor=%22white%22&fontColor=%22black%22&mode=%22normal%22
selected_colors_red= ["#ff0600", "#ff6859", "#b50000", "#ff7000", "#ffac12", "#ffcf44", "#9200c8", "#b15dff"]

## GREEN:
# Green colors: #005d57 #007d51 #1eb980 #37efba #43A047 #1B5E20 #81C784 #0D47A1 #1E88E5 #64B5F6 #263238 #546E7A #90A4AE
# ["#005d57", "#007d51", "#1eb980", "#37efba", "#43A047", "#1B5E20", "#81C784", "#0D47A1", "#1E88E5", "#64B5F6", "#263238", "#546E7A", "#90A4AE", "#E53935", "#B71C1C", "#E57373", "#311B92", "#5E35B1", "#9575CD", "#263238", "#546E7A", "#90A4AE"]
# Green colors:
#https://projects.susielu.com/viz-palette?colors=[%22#43A047%22,%22#007d51%22,%22#005d57%22,%22#1eb980%22,%22#81C784%22,%22#37efba%22,%22#0D47A1%22,%22#1E88E5%22,%22#64B5F6%22,%22#263238%22,%22#546E7A%22,%22#90A4AE%22]&backgroundColor=%22white%22&fontColor=%22black%22&mode=%22normal%22
selected_colors_green=["#43A047","#007d51","#005d57","#1eb980","#81C784","#37efba","#0D47A1","#1E88E5","#64B5F6","#263238","#546E7A","#90A4AE"]




## Nov 3 rally finance:  https://m2.material.io/design/material-studies/rally.html#color-theme-creation

def local_resolve_amount_column(records):
    category_col=None
    value_col=None
    is_timelineable=False

    if records:
        if not 'transaction_amount' in records[0]:
            df=pd.DataFrame(records)
            category_col, value_col, is_timelineable=prepare_timeline_data(df)
    return value_col
    
def dump_color_palette(records=[],case_id='chase_3_66_big',class_field='transaction_type'):
    
    if not records:
        logging.info("[dump_color_palette] sourcing possible colors cause don't know records data")
        records=local_cypher_transactions(case_id=case_id)

    color_choice='green_red'
    color_choice='fixed_categories'
    color_choice='by_frequency'
    color_choice='by_amount'

    count_credit_type_freq={}
    count_debit_type_freq={}
    count_credit_type_amount={}
    count_debit_type_amount={}

    
    cmap_red={}
    cmap_green={}
    
    ## Patch if dynamically set column headers
    value_col=local_resolve_amount_column(records)

    for record in records:
        # section
        # transaction_type
        
        top_class=record.get(class_field,'') # Because section Transaction Details not that interesting
        
        ## Dynamically resolve amount column (may be dynamically generated ie: Total Transaction Amount)
        if not 'transaction_amount' in record:
            if value_col is None:
                logging.warning("[warning] no transaction_amount or value_col in record: "+str(record))
                transaction_amount=0
            else:
                ## Source from data preparer
                transaction_amount=abs(record[value_col])
        else:
            transaction_amount=abs(record['transaction_amount'])
        
        if not 'is_credit' in record or not 'transaction_type' in record:
            pass # give warning but likely bad

        elif record['is_credit']:
            count_credit_type_freq[top_class]=count_credit_type_freq.get(top_class,0)+1
            count_credit_type_amount[top_class]=count_credit_type_amount.get(top_class,0)+transaction_amount
        else:
            count_debit_type_freq[top_class]=count_debit_type_freq.get(top_class,0)+1
            count_debit_type_amount[top_class]=count_debit_type_amount.get(top_class,0)+transaction_amount
            
    ## Sort count_debit_type_amount by value descending
    count_debit_type_amount=dict(sorted(count_debit_type_amount.items(), key=lambda item: item[1],reverse=True))
    c=-1
    for k,v in count_debit_type_amount.items():
        c+=1
        if c>len(selected_colors_red)-1:
            c=len(selected_colors_red)-1
        cmap_red[k]=selected_colors_red[c]
#        logging.info("[info] (delthis) debit color: "+str(k)+" "+str(v)

    count_credit_type_amount=dict(sorted(count_credit_type_amount.items(), key=lambda item: item[1],reverse=True))
    c=-1
    for k,v in count_credit_type_amount.items():
        c+=1
        if c>len(selected_colors_green)-1:
            c=len(selected_colors_green)-1
        cmap_green[k]=selected_colors_green[c]
#        logging.info("[info] (delthis) debit color: "+str(k)+" "+str(v)

    return cmap_red,cmap_green

if __name__=='__main__':
    branches=['dev1']
    branches=['dev_colors_v2']
    for b in branches:
        globals()[b]()


"""
*** OLD credit class but now down in top level

    ### Recall, formalizes in terms of main account
    is_credit=[]
    is_debit=[]
    is_credit_plus=[]
    is_debit_plus=[]

    #(ii)  otherwise infer vs section
    ## SECTION: Deposit and Addition
    if re.search(r'deposit',tt['section'],re.IGNORECASE): is_credit+=['section']
    if re.search(r'withdraw',tt['section'],re.IGNORECASE): is_debit+=['section']
    if re.search(r'paid',tt['section'],re.IGNORECASE): is_debit+=['section']
    if re.search(r'debits',tt['section'],re.IGNORECASE): is_debit+=['section']
    

    #(iii)  otherwise infer vs transaction type (withdrawl or deposit)
    ## transaction type
    # 'transaction_type': 'refund',
    if re.search(r'refund',tt.get('transaction_type',''),re.IGNORECASE): is_credit+=['type']
    if re.search(r'deposit',tt.get('transaction_type',''),re.IGNORECASE): is_credit+=['type']
    if re.search(r'withdraw',tt.get('transaction_type',''),re.IGNORECASE): is_debit+=['type']

    #** extra for ties
    if re.search(r'deposit',tt.get('transaction_description',''),re.IGNORECASE): is_credit_plus+=['description']
    if re.search(r'withdraw',tt.get('transaction_description',''),re.IGNORECASE): is_debit_plus+=['description']
    if re.search(r'debit',tt.get('transaction_description',''),re.IGNORECASE): is_debit_plus+=['description']

   
    credit=False
    debit=False
    if len(is_credit)>len(is_debit):
        credit=True
        debit=False
    elif len(is_credit)==len(is_debit):
        ## SPECIAL CASE LOGIC
        if re.search(r'fee',tt['transaction_description'],flags=re.I):
            debit=True
            credit=False
            
        ## Check for tie breakder
        elif len(is_credit_plus) and len(is_credit_plus)>len(is_debit_plus):
            credit=True
            debit=False

        elif len(is_debit_plus) and len(is_debit_plus)>len(is_credit_plus):
            credit=False
            debit=True

        else:
            if False:
                print ("******** BEWARE THINK BOTH SENDER AND RECEIVER?")
                print ("AT: "+str(tt))
                print ("[debug] credit cause: "+str(is_credit))
                print ("[debug] debit cause: "+str(is_debit))
                logging.error("[error] debit/credit is both sender and receiver at: "+str(tt))
                logging.dev("[error] debit/credit is both sender and receiver at: "+str(tt))
    else:
        credit=False
        debit=True
        
    if False:
        print ("[debug] credit cause: "+str(is_credit))
        print ("[debug] debit cause: "+str(is_debit))

    return is_credit,is_debit

"""
