#all the tables are on your side
#https://github.com/WatchtowerGroup/wt_cognitive/blob/main/backend/application.py
#Oh good.  Was the get_faqs_from_db in the bank_azure_api?
#https://github.com/WatchtowerGroup/wt_cognitive/blob/main/backend/db_connections.py

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# db_host = "bank-transaction.mysql.database.azure.com" #mine
# db_host = "mysql-bank-transaction.mysql.database.azure.com"  # evan
# db_username = "azure_admin"
# db_password = "mybestpassworD#" 
# db_port = "3306"
# db_name = "bank" 

## load the below the variables from .env file (hidden in the folder)
db_host = os.getenv("db_host") # evan
db_username = os.getenv("db_username")
db_password = os.getenv("db_password")
db_port = os.getenv("db_port")
db_name = os.getenv("db_name")

wt_db_host = os.getenv("wt_db_host") # evan
wt_db_username = os.getenv("wt_db_username")
wt_db_password = os.getenv("wt_db_password")
wt_db_port = os.getenv("wt_db_port")
wt_db_name = os.getenv("wt_db_name")

cognitive_anguage_model_endpoint = os.getenv("cognitive_anguage_model_endpoint")
Azure_language_model_credential = os.getenv("Azure_language_model_credential")
knowledge_base_project = os.getenv("knowledge_base_project")
azure_key = os.getenv("azure_key")
azure_endpoint = os.getenv("azure_endpoint")
model_id = os.getenv("model_id")
 
db_url = f"mysql+pymysql://{db_username}:{db_password}@{db_host}:{db_port}/{db_name}"
 
wt_db_url = f"mysql+pymysql://{wt_db_username}:{wt_db_password}@{wt_db_host}:{wt_db_port}/{wt_db_name}"
# engine = None

def connect_mysql(): 
    # global engine
    engine = create_engine(db_url,connect_args={'ssl':{'fake_flag_to_enable_tls': True},'connect_timeout': 10})
    return engine 

def wt_connect_mysql(): 
    # global engine
    engine = create_engine(wt_db_url,connect_args={'ssl':{'fake_flag_to_enable_tls': True},'connect_timeout': 10})
    return engine 

def add_log_to_activity_db(file_name,log_text):  
    # global engine
    try:
        # if engine is None:
        engine = connect_mysql()
        with engine.begin() as conn:
            sql_insert = f"INSERT INTO activity_logs(`filename`,`log_text`) VALUES ( '{file_name}','{log_text}')"
            conn.execute(text(sql_insert))
    except Exception as e:   
         print(e) #if log_print else None  
         return False 
    return True

def get_recent_log_message(): 
    log_result = ""
    try:   
        engine = connect_mysql()
        with engine.begin() as conn:
            cur_result = conn.execute(text("select log_text from bank.activity_logs order by my_row_id desc limit 1"))  
            for row in cur_result: 
                 log_result = str(row[0])
    except Exception as e:   
         print(e) #if log_print else None  
         return str(e)
    return log_result


def get_wt_faqs_from_db():  
    faqs_list = ""
    try:   
        engine = wt_connect_mysql() 
        with engine.begin() as conn:
            cur_result = conn.execute(text("select faq_index, question, answer from wtengine.faqs_data order by faq_index")) 
            for row in cur_result: 
                 index = str(row[0])
                 question = str(row[1])
                 answer = str(row[2])
                 faqs_list += index+":"+question+":"+answer + "|" 
        #faqs_list = faqs_list.replace("||","")
    except Exception as e:   
         print(e) #if log_print else None  
         return str(e)
    return faqs_list
  
def add_wt_faqs_to_db(question, answer):  
    faqindex = 0
    try:   
        engine = wt_connect_mysql()  
        with engine.begin() as conn: 
            cur_result = conn.execute(text("select faq_index from wtengine.faqs_data order by faq_index desc limit 1"))  
            for row in cur_result: 
                 faqindex = int(row[0]) + 1
            query = f"insert into wtengine.faqs_data(faq_index,question,answer) values({faqindex},'{question}','{answer}')"
            #print(query)
            conn.execute(text(query))  
    except Exception as e:   
         print(e) #if log_print else None  
         return str(e)
    return faqindex

def add_wt_short_cut_buttons_to_db(name, question):  
    shortcut_id = 0
    try:   
        engine = wt_connect_mysql()  
        with engine.begin() as conn: 
            cur_result = conn.execute(text("select shortcut_id from wtengine.short_cut_button_management order by shortcut_id desc limit 1"))  
            for row in cur_result: 
                 shortcut_id = int(row[0]) + 1
            query = f"insert into wtengine.short_cut_button_management(shortcut_id,name,question) values({shortcut_id},'{name}','{question}')"
            #print(query)
            conn.execute(text(query))  
    except Exception as e:   
         print(e) #if log_print else None  
         return str(e)
    return shortcut_id

def delete_wt_short_cut_buttons_from_db(shortcut_id):   
    try:   
        engine = wt_connect_mysql()  
        with engine.begin() as conn: 
            conn.execute(text(f"delete from wtengine.short_cut_button_management where shortcut_id = {shortcut_id}"))   
    except Exception as e:   
         print(e) #if log_print else None  
         return str(e)
    return "Deleted Successfully"

def get_wt_short_cut_buttons_from_db():  
    faqs_list = ""
    try:   
        engine = wt_connect_mysql() 
        with engine.begin() as conn:
            cur_result = conn.execute(text("select shortcut_id, name, question from wtengine.short_cut_button_management order by shortcut_id")) 
            for row in cur_result: 
                 index = str(row[0])
                 name = str(row[1])
                 question = str(row[2])
                 faqs_list += index+":"+name+":"+question + "|" 
        #faqs_list = faqs_list.replace("||","")
    except Exception as e:   
         print(e) #if log_print else None  
         return str(e)
    return faqs_list
    
def delete_wt_faqs_from_db(faq_index):  
    try:   
        engine = wt_connect_mysql()  
        with engine.begin() as conn: 
            conn.execute(text(f"delete from wtengine.faqs_data where faq_index = {faq_index}"))   
    except Exception as e:   
         print(e) #if log_print else None  
         return str(e)
    return "Deleted Successfully"
    
    
def get_faqs_from_db():  
    faqs_list = ""
    try:   
        engine = connect_mysql() 
        with engine.begin() as conn:
            cur_result = conn.execute(text("select faq_index, question, answer from bank.faqs_data order by faq_index")) 
            for row in cur_result: 
                 index = str(row[0])
                 question = str(row[1])
                 answer = str(row[2])
                 faqs_list += index+":"+question+":"+answer + "|" 
        #faqs_list = faqs_list.replace("||","")
    except Exception as e:   
         print(e) #if log_print else None  
         return str(e)
    return faqs_list
  
def add_faqs_to_db(question, answer):  
    faqindex = 0
    try:   
        engine = connect_mysql()  
        with engine.begin() as conn: 
            cur_result = conn.execute(text("select faq_index from bank.faqs_data order by faq_index desc limit 1"))  
            for row in cur_result: 
                 faqindex = int(row[0]) + 1
            query = f"insert into bank.faqs_data(faq_index,question,answer) values({faqindex},'{question}','{answer}')"
            #print(query)
            conn.execute(text(query))  
    except Exception as e:   
         print(e) #if log_print else None  
         return str(e)
    return faqindex

def delete_faqs_from_db(faq_index):  
    faqindex = 0
    try:   
        engine = connect_mysql()  
        with engine.begin() as conn: 
            conn.execute(text(f"delete from bank.faqs_data where faq_index = {faq_index}"))   
    except Exception as e:   
         print(e) #if log_print else None  
         return str(e)
    return "Deleted Successfully"

def get_questions_from_db(): 
    questions_list = []
    try:   
        engine = connect_mysql() 
        with engine.begin() as conn:
            cur_result = conn.execute(text("select question from bank.questions order by q_index")) 
            for row in cur_result:  
                 question = str(row[0]) 
                 questions_list.append(question) 
    except Exception as e:   
         print(e) #if log_print else None  
         return str(e)
    return questions_list   
        
# def cleanup_table():
#     global engine
#     # try: exception is caught in application.py
#     connect_mysql()  
#     with engine.begin() as conn:
#          conn.execute(text("""truncate table  bank.bank_atm_debit_withdrawal"""))
#          conn.execute(text("""truncate table  bank.bank_deposits_additions"""))
#          conn.execute(text("""truncate table  bank.bank_checkingsummary"""))
#          conn.execute(text("""truncate table  bank.bank_electronic_withdrawal""")) 
#          conn.execute(text("""truncate table  bank.checks_paid""")) 
#          conn.execute(text("""truncate table  bank.bank_fees""")) 
#          conn.execute(text("""truncate table  bank.file_processed""")) 
#     # except Exception as e:   
#           # print(e) #if log_print else None  
#           # return False 
#     return True


