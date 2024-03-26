import os
import sys
import codecs
import json
import re

#0v2# import camelot
import fitz
import pandas as pd


LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")
from alg_easy_extracts import alg_get_page_year

sys.path.insert(0,LOCAL_PATH+"../..")



from get_logger import setup_logging
logging=setup_logging()

        
#0v2# JC  Feb 14, 2023  Remove camelot requirement (hard to install)
#0v1# JC  Dec 20, 2023  Setup



#0v2#def extract_tables_from_pdf(input_file):
#0v2#    try:
#0v2#        # Read all pages using Camelot. Use "all" to read all pages
#0v2#        tables = camelot.read_pdf(input_file, pages='all', flavor='stream')
#0v2#
#0v2#        for table_index, table in enumerate(tables):
#0v2#            page_num = tables[table_index].parsing_report['page']
#0v2#            print(f"Processing page - {page_num} table - {table_index}")
#0v2#            table.df.to_csv(f'page-{page_num}-table-{table_index}.csv')
#0v2#
#0v2#    except Exception as e:
#0v2#        print(f"An error occurred: {e}")
#0v2#
#0v2###  # Example usage
#0v2###  extract_tables_from_pdf('your_pdf_file.pdf')
#0v2#"""
#0v2#view extract as plot
#0v2# if tables:
#0v2#        camelot.plot(tables[0])#, type="grid")


def alg_is_transaction_history_table(df):
    is_history_table=False
    ## Iterate over each cell of df
    cell_count=0
    for row in df.itertuples():
        for cell in row:
            cell_count+=1
            if re.search(r'Transaction[\s]{1,8}history',str(cell),flags=re.I):
                is_history_table=True
                break
            if is_history_table: break
            if cell_count>4*6: break  # 6 cols x 4 rows 

    return is_history_table


def alg_get_column_headings(df):

    ## LOGIC:
    #- Within first 5 rows
    #- row contains target phrases (always two rows?)
    #- assume fixed columns?
    #- assume two rows of headings
    
    ASSUME_HEADINGS=['Date','Check Number','Description','Deposits/Additions','Withdrawals/Subtractions','Ending daily balance']
    
    """"
    0   Transaction  history
  1                          Check                                                     Deposits/  Withdrawals/  Ending  daily
  2                   Date  Number                                        Description  Additions  Subtractions        balance
    """
    
    ## Get indexes for column headings
    
    check_col=None
    row_index=0
    heading_row_index=None


    for row in df.itertuples(index=True):  # index=True includes the row index in the tuple
        row_index = row.Index  # Get the current row index
        # Iterate through each cell in the row
        for col_index, cell in enumerate(row[1:]):  # Skip the first element which is the index
            if check_col is None and 'Check' == str(cell).strip():
                check_col = col_index
                heading_row_index = row_index
                break  # Break out of the inner loop
        if check_col is not None: break
        if row_index > 5: break


    headings={}
    cols={}
    if not check_col is None:
        ## Assume all headings based on Check location
        #- clean on the spot!
        date_col=check_col-1
        description_col=check_col+1
        deposits_col=check_col+2
        withdrawals_col=check_col+3
        balance_col=check_col+4
    
        ## Grab column heading names
        headings['date']=df.iloc[heading_row_index+1,date_col]
        headings['date']=re.sub(r'[\s]{2,}',' ',str(headings['date'])).strip() #clean
        cols['date']=date_col
        
        headings['check']=df.iloc[heading_row_index,check_col]
        headings['check']+=" "+df.iloc[heading_row_index+1,check_col]
        headings['check']=re.sub(r'[\s]{2,}',' ',str(headings['check'])).strip() #clean
        cols['check']=check_col
    
        headings['description']=df.iloc[heading_row_index+1,description_col]
        headings['description']=re.sub(r'[\s]{2,}',' ',str(headings['description'])).strip() #clean
        cols['description']=description_col
    
        headings['deposits']=df.iloc[heading_row_index,deposits_col]
        headings['deposits']+=" "+df.iloc[heading_row_index+1,deposits_col]
        headings['deposits']=re.sub(r'[\s]{2,}',' ',str(headings['deposits'])).strip() #clean
        cols['deposits']=deposits_col
    
        headings['withdrawals']=df.iloc[heading_row_index,withdrawals_col]
        headings['withdrawals']+=" "+df.iloc[heading_row_index+1,withdrawals_col]
        headings['withdrawals']=re.sub(r'[\s]{2,}',' ',str(headings['withdrawals'])).strip() #clean
        cols['withdrawals']=withdrawals_col
    
        if balance_col<len(df.columns):
            headings['balance']=df.iloc[heading_row_index,balance_col]
            headings['balance']+=" "+df.iloc[heading_row_index+1,balance_col]
            headings['balance']=re.sub(r'[\s]{2,}',' ',str(headings['balance'])).strip() #clean
            cols['balance']=balance_col
        else:
            headings['balance']=''
            cols['balance']=0

        
    ## Recap:
    #   cols['balance']=6?
    #   headings['balance']='Ending daily balance'

    return cols,headings
  

def local_extract_page_text(pdf_filename,page):
    page=int(page)
    doc = fitz.open(pdf_filename)
    try:
        page = doc.load_page(page-1)  # 0-based index
        page_text = page.get_text("text")
    except:
        page_text=''
    return page_text


def fargo_pdf_page_to_transactions(page,filename='',verbose=True,page_text='',year=''):
    """ {
    'accuracy': 99.02,
    'whitespace': 12.24,
    'order': 1,
    'page': 1
    }"""

    records=[]

    if verbose:
        # Set pandas options
        pd.set_option('display.max_rows', None)  # Set to None to display all rows
        pd.set_option('display.max_columns', None)  # Set to None to display all columns
        pd.set_option('display.width', 1000)  # Increase the width of each row
        

    ## PREPARE ODD VARS
    if not year:
        if not page_text:
            page_text=local_extract_page_text(filename,page)
        year=alg_get_page_year(page_text)
    
    
    ## AUTO SKIP PAGE CAUSE POSSIBLY ODD
    if 'Worksheet to balance your account' in page_text:
        return records


    ### PROCESS WITH camelot
    tables=camelot.read_pdf(filename, pages=str(page), flavor='stream')  #** possible errors raised.

    for table_index, table in enumerate(tables):
        page_num = tables[table_index].parsing_report['page']
        print(f"Processing page - {page_num} table - {table_index}")

        table_df=table.df
        
        #columns #        cols=table_df.columns.tolist()   #Indexes 0...6
        
        ## Remove all cid warnings (ie/ adobe or font or something)
        
        # Regular expression pattern to match "(cid:...)"
        # Apply the regex replacement to each cell in the DataFrame
        pattern = r' \(cid:\w+\)'
        table_df = table_df.replace(pattern, '', regex=True)
        
        if verbose: print (table_df)
        
        ## LOGICAL INSIGHT
        
        #[A]
        is_table_transactions=alg_is_transaction_history_table(table_df)
        
        headings={}
        if is_table_transactions:
            cols,headings=alg_get_column_headings(table_df)
            
            ## Logical check headings (ensure we got good data)
            if not 'description' in headings.get('description','').lower():
                headings={}

        if headings:

            #[B]
            #. column headings to col number mappings
            cols,headings=alg_get_column_headings(table_df)
            print ("headings: "+str(headings))

            #[C] rows to dicts
            for row in table_df.itertuples(index=True):  # index=True includes the row index in the tuple
                
                #############################
                ## Transform row to dict
                row_index = row.Index  # Get the current row index
                                       # Iterate through each cell in the row

                row_values=list(row[1:])
#D1                print ("ROW: "+str(row_values))

                try: next_row_values=list(table_df.iloc[row_index+1,0:])
                except: next_row_values=[]
                

                ## Is first line of transaction if has date
                is_line_full=False
                is_next_line_cont=False

                try:
                    if re.search(r'^\d',str(row_values[cols['date']])):
                        is_line_full=True
                except: pass

                try:
                    if not re.search(r'^\d',str(next_row_values[cols['date']])):
                        if re.search(r'\w',str(next_row_values[cols['description']])):
                            is_next_line_cont=True
                except:
                    pass


                ## Build transaction dict (including next line)
                data={}
                data['date']=row_values[cols['date']]
                data['check']=row_values[cols['check']]
                data['description']=row_values[cols['description']]
                data['deposits']=row_values[cols['deposits']]
                data['withdrawals']=row_values[cols['withdrawals']]

                if cols['balance']:
                   data['balance']=row_values[cols['balance']]
                else:
                   data['balance']=''
                

                ## Append description if two lines.
                if is_next_line_cont:
                    data['description']+=" "+next_row_values[cols['description']]
                    data['description']=data['description'].strip()


                if re.search(r'\d',data.get('date')):

                    #[D] easy clean
                    #i)  Date as 817 instead of 8/17  ** possibly common for /1 to look like just 1
                    if not '/' in data['date']:
                        data['date']=alg_auto_fix_date(data['date'])
                            
                    #ii)  No commas in currency
                    data['deposits']=re.sub(r',','',data['deposits'])
                    data['withdrawals']=re.sub(r',','',data['withdrawals'])
                    data['balance']=re.sub(r',','',data['balance'])
                    
                    #iii)  Description no \n, no double spaces
                    data['description']=re.sub(r'[\s]{2,}',' ',data['description'])
                    
                    #iv)  Check becomes description
                    check=data.pop('check','').strip()
                    ## local clean check (^ as A maybe, just remove)
                    check=re.sub(r'^\^','',check)
                    check=re.sub(r'^[A]','',check).strip()
                    if check and data.get('description',''):
                        data['description']="Check: "+check+". "+data['description']
                        #print ("CHECK TO: "+str(data['description']))
        
                    #[E] Assumed year from extracted date on page?
                    if year:
                        data['date']=alg_auto_apply_date(data['date'],year)
                        
                    keep_it=True
                    

                    print ("DATA: "+str(data))
                    records+=[data]

        else:
            if verbose:
                print ("[warning] not a transaction table: "+str(table_df))

    ## Format to match output of llm_page2transactions.py
    if records:
        meta={}
        meta['transaction_count']=len(records)
        
        ## Final map each record to target format (ideally external but here for now)
        new_records=[]
        for r in records:
            new_record={}
            new_record['transaction_date']=r['date']
            new_record['transaction_description']=r['description']

            new_record['transaction_amount']=r['deposits'] or r['withdrawals']
            try: new_record['transaction_amount']=float(new_record['transaction_amount'])
            except:
                print ("*warning fargo amount: "+str(new_record['transaction_amount']))
                new_record['transaction_amount']=0
            
            if r['deposits']:
                new_record['section']='Deposits/Additions'
                new_record['is_credit']=True
            elif r['withdrawals']:
                new_record['section']='Withdrawals/Subtractions'
                new_record['is_credit']=False
            else:
                new_record['section']=''
                
            ## is_credit or sign?
            new_records+=[new_record]

        global_transactions={'all_transactions':new_records}
            
        return global_transactions

    return [] #or none

def alg_auto_fix_date(ddate):
    #817 to 8/17 (aug)

    if not '/' in ddate:
        # mm/dd
        if re.search(r'^\d\d\d$',ddate): #817 -> 8/17
            ddate=re.sub(r'(\d{1})(\d{2})',r'\1/\2',ddate)
            
        elif re.search(r'^\d\d\d\d$',ddate):
            # If first two chars>12
            if int(ddate[0:2])>12:
                ddate=re.sub(r'(\d{1}).(\d{2})',r'\1/\2',ddate) # #2110 -> 2/10
                
        elif re.search(r'^\d\d$',ddate):  # 21 -> 2/1
            ddate=re.sub(r'(\d{1})(\d{1})',r'\1/\2',ddate)

    return ddate

def alg_auto_apply_date(ddate,year):
    # ddate:  8/15 (m/d)
    # target format:  yyyy-mm-dd
    full_date=ddate
    
    if '/' in ddate:
        mm,dd=re.split(r'/',ddate)
        mm=str(mm)
        if len(mm)==1: mm="0"+mm
        if len(dd)==1: dd="0"+dd
        full_date=str(year)+"-"+mm+"-"+dd
    return full_date



def dev1():

    b=['one_page_all']
    b=['one_page_good']

    if 'one_page_good' in b:
        sample_filename=LOCAL_PATH+'wells_fargo_1.pdf'
        page="1"
        records=fargo_pdf_page_to_transactions(page,filename=sample_filename,page_text='',year='',verbose=True)
        
    if 'one_page_all' in b:
        c=0
        while True:
            c+=1

            sample_filename=LOCAL_PATH+'wells_fargo_all.pdf'
            
            records=fargo_pdf_page_to_transactions(c,filename=sample_filename,page_text='',year='',verbose=True)
            
            print ("--------- FOUND RECORDS: "+str(len(records)))


    return





if __name__=='__main__':
    branches=['dev1']
    for b in branches:
        globals()[b]()
        


"""
FURTHER:
  [1]  dates missing slashes ie: 817 nto 8/17

                                        GA  S301225464358436  Card  4656
35                  8/16          Bill  Pay  American  Express  -  New  Biz  Gol...                 9,450.00     111,864.37
36                                                       X000000xxx42005  on  08-16
37                   817          WT  Fed#00530  Scotiabank  Inverla  /Org=Invek...  32,865.00
38                                DE  Cv  Srf#  2021081700358709  Trn#2108171190...
39                                                                         Xxxx9893
40                   817          Wire  Trans  Svc  Charge  -  Sequence:  210817...                    16.00
41                                2021081700358709  Trn#210817119017  Rfb#  x00x...
42                  8/17          Bill  Pay  American  Express  -  New  Biz  Gol...                 8,750.00     135,963.37
"""



