import os
import sys
import codecs
import json
import re
import time
import pandas as pd

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")


from w_utils import am_i_on_server
from pretty_html_table import build_table
from w_storage.gstorage.gneo4j import Neo


from v_questions.q30_questions import q1_list_account_numbers
from v_questions.q30_questions import q13_total_inflows

from get_logger import setup_logging
logging=setup_logging()


#0v4# JC Feb 22, 2024  Dump html VERY slow -- not needed when on server!
#0v3# JC Jan 28, 2024  Allow transaction id header (for joins)
#0v2# JC Nov 24, 2023  square html table requires raw data formatted as html_data for FE
#0v1# JC Oct  3, 2023  (recall normalize_graph)


"""
    KB ANSWER 'API'
    - track answer id across various mediums?
    - answer pushes to various component views
    - what about entire QA session?
    
    - raw chatbot text response
    - output timeline
    - output table
    - output excel data dump
    - output debug view
    - output graph nodes view
    
    > assume most responses come from cypher response
    > use LLM possibly to clean up response if can't translate well

"""


#special #secret headers
HIDE_SPECIAL_HEADERS=[]
#KEEP for joins# HIDE_SPECIAL_HEADERS+=[r'transaction.*id']
HIDE_SPECIAL_HEADERS+=[r'statement.*id']
HIDE_SPECIAL_HEADERS+=[r'payee.*id']
HIDE_SPECIAL_HEADERS+=[r'payor.*id']
HIDE_SPECIAL_HEADERS+=[r'Label'] #Transaction
HIDE_SPECIAL_HEADERS+=[r'Is.*Cash']
HIDE_SPECIAL_HEADERS+=[r'Is.*Wire'] #Is Wire Transfer
HIDE_SPECIAL_HEADERS+=[r'Is.*Credit']

GLOBAL_ON_SERVER=am_i_on_server()
GLOBAL_FORCE_NO_SLOW_HTML=True

# Function to check if value is convertible to float
def is_convertible(val):
    isit=False
    try:
        float(val)
        isit=True
    except:
        pass
    return isit


class QA_Session_Answers:
    def __init__(self):
        self.answer=None
        self.answer_type=None
        return
    
    def note_question(self):
        return
    
    def note_answer(self,answer,answer_type='raw'):
        check_new=flow_uses_df_directly
        self.answer=answer
        self.answer_type=answer_type
        if self.answer_type=='raw':
            ## Try to guess
            ## See q30_questions for standard output:
            # tups: jsonl,df,qq,meta
            if len(self.answer)==4 and isinstance(self.answer[0],list):
                self.answer_type='qtup'
        return
    
    def dump_for_string_view(self):
        return str(self.answer)
    
    def dump_for_string_table_view(self):
        response=''
        if self.answer_type=='qtup':
            #response=pd2string(self.answer[1])
            #response=format_for_print2(self.answer[1])
            pass
        else:
            stopp=check_ype
        return response

    def dump_for_html_table_view(self,df=None):
        global GLOBAL_ON_SERVER
        global GLOBAL_FORCE_NO_SLOW_HTML
        # https://stackoverflow.com/questions/45422378/is-there-a-quick-way-to-turn-a-pandas-dataframe-into-a-pretty-html-table
        #html_data==> data for FE table
        #html==> html table for local
        
        ##** beware, html table generation is VERY SLOW


        html=''
        html_data={}
            
        generate_slow_html=True
        if GLOBAL_FORCE_NO_SLOW_HTML: generate_slow_html=False
        elif df is None: generate_slow_html=False
        elif GLOBAL_ON_SERVER: generate_slow_html=False


        html,html_data=pd2html(df,do_html_table=generate_slow_html) #<-- VERY SLOW (10s NAV)
        #return pd2html(self.answer[1])
        return html,html_data
    
    def dump_for_timeline(self,df=None):
        the_dict={}
        if not df is None:
            ## Optional filtering or styling
            #- use df for ease
            the_dict=df.to_dict(orient='records')
        """
         [{'transaction_date': Timestamp('2021-12-01 00:00:00'), 'sender_name': 'Integrated Call Center Solutions', 'transaction_amount': 3000000.0}, {'transaction_date': Timestamp('2021-12-02 00:00:00'), 'sender_name': '', 'transaction_amount': 0.35}, {'transaction_date': Timestamp('2021-12-07 00:00:00'), 'sender_name': 'Integrated Call Center Solutions', 'transaction_amount': 1500000.0}, {'transaction_date': Timestamp('2021-12-08 00:00:00'), 'sender_name': 'Integrated Call Center Solutions', 'transaction_amount': 7500000.0}, {'transaction_date': Timestamp('2021-12-08 00:00:00'), 'sender_name': 'JPMorgan Chase Bank NA', 'transaction_amount': 502094.95}]
        """
         
        return the_dict

    def dump_for_barchart(self,df=None):
        # (copy from dump_for_timeline -- like timeline but no date field)
        the_dict={}
        if not df is None:
            ## Optional filtering or styling
            #- use df for ease
            the_dict=df.to_dict(orient='records')
        """
         [{'transaction_date': Timestamp('2021-12-01 00:00:00'), 'sender_name': 'Integrated Call Center Solutions', 'transaction_amount': 3000000.0}, {'transaction_date': Timestamp('2021-12-02 00:00:00'), 'sender_name': '', 'transaction_amount': 0.35}, {'transaction_date': Timestamp('2021-12-07 00:00:00'), 'sender_name': 'Integrated Call Center Solutions', 'transaction_amount': 1500000.0}, {'transaction_date': Timestamp('2021-12-08 00:00:00'), 'sender_name': 'Integrated Call Center Solutions', 'transaction_amount': 7500000.0}, {'transaction_date': Timestamp('2021-12-08 00:00:00'), 'sender_name': 'JPMorgan Chase Bank NA', 'transaction_amount': 502094.95}]
        """
         
        return the_dict
    
    def dump_for_map(self,df=None):
        # lat + lng
        # icon type
        # name
        # blob:  various data
        
#D2        print (">> "+str(df))  #> beware large df print
        if df is None: return {}
        
        
        # Normalizing column headers
        # Normalizing column headers
        new_columns = {}
        for col in df.columns:
            # Check if at least one value in the column can be converted to a float
            if any(is_convertible(val) for val in df[col]):
                if re.search(r'lng', col, re.I) or re.search(r'longitude',col,re.I):  # re.I makes the search case-insensitive
                    new_columns[col] = 'Longitude'
                elif re.search(r'lat', col, re.I):
                    new_columns[col] = 'Latitude'
            else:
                pass
                #print(f"Column {col} does not contain any float-like value. It will not be renamed.")
        
        # Rename columns in the DataFrame
        df.rename(columns=new_columns, inplace=True)

        new_columns = {}
        for col in df.columns:
            if re.search(r'lng', col, re.I):  # re.I makes the search case-insensitive
                new_columns[col] = 'Longitude'
            elif re.search(r'lat', col, re.I):
                new_columns[col] = 'Latitude'
            elif re.search(r'name', col, re.I):
                new_columns[col] = 'Name'
            # Add more conditions as needed
        
        # Rename columns in the DataFrame
        df.rename(columns=new_columns, inplace=True)
        
        ## Combine other 'unknown' columns into single field
        # Create "other columns" field by concatenating values from "other" columns
        
        # Define columns to keep
        keep_columns = ['Latitude', 'Longitude', 'Name']
        
        # Check which of the specified columns actually exist in the dataframe
        existing_keep_columns = list(set(df.columns) & set(keep_columns))
        
        # Determine "other" columns that exist in the dataframe but are not in keep_columns
        existing_other_columns = [col for col in df.columns if col not in existing_keep_columns]
        
        # Remove rows where 'Latitude' is empty, None or NaN
        if 'Latitude' in df.columns:
            df = df[df['Latitude'].astype(str).str.strip() != '']
        else:
            return {}  #Empty if no latitude
        
        # If there are any existing "other" columns, create the 'Info' column
        if existing_other_columns:
            df['Info'] = df[existing_other_columns].apply(lambda row: '|'.join(row.astype(str)), axis=1)
        
            # Drop original "other" columns after creating 'Info' column
            df = df[existing_keep_columns + ['Info']]
        else:
            # If there are no other columns, keep only the specified columns that exist
            df = df[existing_keep_columns]

        df = df.drop_duplicates()  #Though if Info changes then not a duplicate

        # Print DataFrame with normalized column headers and "other columns" field
        
        the_dict={}
        if not 'Latitude' in df.columns:
            the_dict={}
        else:
            ## Optional filtering or styling
            #- use df for ease
            the_dict=df.to_dict(orient='records')

#        print(df)

        return the_dict
    
    def dump_for_chatbot():
        #** recall, LLM response + existing
        return
    
    def dump_answers(self,df,df_friendly):
        #[ ] beware slow?  cache?
        
        # "answers' formats"
        #: df_friendly:  PRIVATE_REGEX column headings removed

        dd={}
        stime=time.time()
        #!! VERY SLOW DUMP HTML
        dd['html'],dd['html_data']=self.dump_for_html_table_view(df=df_friendly)
        print ("html time: "+str(time.time()-stime))
        
        
        dd['timeline']=self.dump_for_timeline(df=df)
        stime=time.time()
        dd['barchart']=self.dump_for_barchart(df=df)
        print ("barchart time: "+str(time.time()-stime))
        dd['map']=self.dump_for_map(df=df)
        stime=time.time()
        dd['df']=pd.DataFrame()     #empty for now
        print ("df time: "+str(time.time()-stime))
        #dd['chatbot']=self.dump_for_chatbot(df=df)
        return dd


def interface_dump_answers():
    ## INPUT:  question session
    meta={}
    casee=updaetee
    case_id='case_o3_case_single'
    QA=QA_Session()
    QA.note_question()
    tups=q13_total_inflows(case_id=case_id)
    QA.note_answer(tups)
    answers=QA.dump_answers()
    return answers,meta

### VARIOUS VIEWS
# pandas table visualization: 
#   https://pandas.pydata.org/docs/user_guide/style.html

def set_pandas_display_options() -> None:
    """Set pandas display options."""
    # Ref: https://stackoverflow.com/a/52432757/
    display = pd.options.display

    display.max_columns = 1000
    display.max_rows = 1000
    display.max_colwidth = 199
    display.width = 1000
    # display.precision = 2  # set as needed
    # display.float_format = lambda x: '{:,.2f}'.format(x)  # set as needed

#set_pandas_display_options()
# >then:
#- to_markdown()
#- to_thml

def pd2markdown(df):
    return df.to_markdown(headers='keys', tablefmt='psql')
    return df.to_markdown()  #<-- uses tabulate


### SPECIAL CLEAN df column headers
# n.amount, n.name ->   Amount, Name
def clean_df_headers(df: pd.DataFrame) -> pd.DataFrame:
    """
    Removes any unique repeating prefix followed by a dot from DataFrame column names.

    Parameters:
    df (pd.DataFrame): Input DataFrame

    Returns:
    pd.DataFrame: DataFrame with updated column names
    """
    
    ### 0/  Remove special colunns
    remove_these_columns=[]
    for col_name in df.columns:
        keep_it=True
        for pattern in HIDE_SPECIAL_HEADERS:
            if re.search(pattern,col_name,re.I):
                keep_it=False
        if not keep_it:
            remove_these_columns.append(col_name)
    df=df.drop(columns=remove_these_columns)
    
    ### 1/
    # Extract prefixes and check if there's a unique and repeating prefix
    prefixes = {re.match(r'^[\w]+', col)[0] for col in df.columns if re.match(r'^[\w]+', col)}
    
    if len(prefixes) == 1:
        # Unique prefix found, proceed to remove it
        unique_prefix = prefixes.pop() + '.'
        new_columns = [col.replace(unique_prefix, '', 1) for col in df.columns]
        df.columns = new_columns
        
    
    ### 2/  BankStatement -> Bank Statement
    # Apply regex replacement to column names
    #old pandas    df.columns = df.columns.str.replace(r'(?<=[a-z])(?=[A-Z])', ' ')
    df.columns = df.columns.str.replace(r'(?<=[a-z])(?=[A-Z])', ' ', regex=True)


    ### 3/  remove underscores and make a title
    df.columns = [col.replace('_', ' ').title() for col in df.columns]
    
    return df

def clean_df_html_content(df: pd.DataFrame) -> pd.DataFrame:
    ## Final formatting of any ie/ html table content

    #/ 0. two decimal places
    float_columns = df.select_dtypes(include=['float']).columns
    df[float_columns] = df[float_columns].applymap(lambda x: '{:.2f}'.format(x))

    #/ 1.  any amounts as 0.00 not 0.0
    # Identify float columns and format them
    patterns = [r'amount', r'total']

    selected_columns = [col for col in df.columns if any(re.search(pattern, col) for pattern in patterns)]

    # 2. Validate that the selected columns have values that look like floats.
    def looks_like_float(val):
        try:
            float(val)
            return True
        except ValueError:
            return False
    
    for col in selected_columns:
        if all(df[col].apply(looks_like_float)):
            # 3. Format those float values to the desired format.
            df[col] = df[col].astype(float).apply(lambda x: f'{x:.2f}')

            #/ 2.  Optionally, if you want to add a dollar sign to the values
            df[col] = df[col].applymap(lambda x: f'${x}')
    
    #/ 3.  If only one column and <3 unique then group as unique
    if len(df.columns) == 1:
        # Convert lists to tuples (or strings) for hashing
        df.iloc[:, 0] = df.iloc[:, 0].apply(lambda x: tuple(x) if isinstance(x, list) else x)
        
        if df.iloc[:, 0].nunique() < 3:
            df = df.drop_duplicates()

    #/ 4.  Drop all duplicates?
    try:
        df = df.drop_duplicates()  #Though if Info changes then not a duplicate
    except Exception as e:
        logging.info("[warning] could not drop duplicates (ie/ if list): "+str(e))
        
    #/ 5.  Capitalize the first letter of each word in the column (if it's a string)
    df = df.applymap(lambda x: x.title() if isinstance(x, str) else x)
    
    return df


def normalize_timestamps(df):
    """
    Convert all Timestamp fields in a DataFrame to string dates.
    :param df: Pandas DataFrame
    :return: DataFrame with Timestamps converted to date strings
    """
    for col in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            df[col] = df[col].dt.strftime('%Y-%m-%d')
    return df
    

def pd2html(df,do_html_table=True):
    #!!! VERY SLOW for large data on build_table (html!)
    table=''
    df_json={}

    stime=time.time()

    #*AKA /square_data  raw data for FE table
    # preview: https://codebeautify.org/htmlviewer/cbec3fa1
    
    df_copy = df.copy()
    
    df_copy=clean_df_headers(df_copy)
    
    df_copy=clean_df_html_content(df_copy)
    
    df_copy=normalize_timestamps(df_copy)
    
    try:
        df_json=df_copy.to_dict(orient='records') #Recall possible dup so error
    except Exception as e:
        logging.error("[error] could not convert to json (html_data) in kb_answer.py: "+str(e))
        df_json={}
        
    if do_html_table:
        stimer=time.time()
        table=build_table(df_copy, 'blue_light')
        loging.warning("[warning] pd 2 html slow for large data took: "+str(time.time()-stimer))

    logging.info("[info] pd 2 html slow for large data took: "+str(time.time()-stime))
    return table, df_json
    
    ## OK BUT BASIC:
    #return df_copy.to_html()

def pd2string(df):
   return df.to_string(index=False)

def format_for_print2(df):    
    table = PrettyTable(list(df.columns))
    for row in df.itertuples():
        table.add_row(row[1:])
    return str(table)

    
def dev1():
    devv=onlyy
    case_id='case_o3_case_single'

    print ("Start QA session")
    print ("get question")
    print ("kb ask")
    print ("get raw answer (possibly iterative)")

    print ("start answer pushing")
    
    print ("**recall, some of this in kb_ask or call_kbai so keep slim answer focused!")

    QA=QA_Session()

    QA.note_question()
    
    # Assume answer ready or real-time ask
    
    tups=q1_list_account_numbers(case_id=case_id)
    
    QA.note_answer(tups)

    print ("ANSWER: "+str(QA.dump_for_string_view()))
    print ("ANSWER: "+str(QA.dump_for_string_table_view()))

    print ("ANSWER html: "+str(QA.dump_for_html_table_view()))

    return


def try_specific():
    case_id='case_o3_case_single'

    QA=QA_Session()
    tups=q13_total_inflows(case_id=case_id)

    QA.note_answer(tups)
    print ("ANSWER: "+str(QA.dump_for_string_view()))
    print ("-"*25)
    print ("ANSWER: "+str(QA.dump_for_string_table_view()))
    print ("-"*25)
    print ("ANSWER html: "+str(QA.dump_for_html_table_view()))
    print ("-"*25)
    print ("ANSWER timeline: "+str(QA.dump_for_timeline()))

    return

if __name__=='__main__':
    branches=['dev1']
    branches=['try_specific']
    for b in branches:
        globals()[b]()
