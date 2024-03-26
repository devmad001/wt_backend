#all the tables are on your side
#https://github.com/WatchtowerGroup/wt_cognitive/blob/main/backend/application.py
#Oh good.  Was the get_faqs_from_db in the bank_azure_api?
#https://github.com/WatchtowerGroup/wt_cognitive/blob/main/backend/db_connections.py

# from flask import Flask,request ,Response
# from bank_azure_api import *
# from pdf_processor import process_pdf_using_myocrpdf , process_pdf_normal_to_zoom , extract_pdfs_documents_from_single_pdf_documents , glob
# from adobe_auto_tag import *
# from flask_httpauth import HTTPBearerAuth
# from flask_restful import Api 
# application = app = Flask(__name__)
# Configure logging to write to a file

# conda activate azure_test_6
# uvicorn application:app --reload

# curl command with header and auth
# curl --location 'https://flask-bank-webapp-service.azurewebsites.net/process_document/' \
# --header 'Authorization: ncft4T9QZTTe6WhPxIT3H1wlwoilslLpynstOsHvf9bFACazWOXaUEHUZOvMgZMPemQiFJFXne0myjL1QJfiQR06BotYlqohxdLgQZIzyOD3VIKEcJHme6pZjFYuZ2Pg' \
# --header 'Content-Type: application/json' \
# --header 'Cookie: ARRAffinity=ae33af1282de204ef61be9b4896306f4ed15ebf42fd3542a6a6c6964ad202b14; ARRAffinitySameSite=ae33af1282de204ef61be9b4896306f4ed15ebf42fd3542a6a6c6964ad202b14' \
# --data 'chase_statement_4_output_13 copy.pdf'

# from fastapi.middleware.cors import CORSMiddleware
# from static_data import get_questions #, get_faqs

# origins = [ 
#     "http://localhost",
#     "http://localhost:8080",
#     "http://127.0.0.1:8000",
#     "http://localhost:3000"
# ]

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

from bank_azure_api import ProcessDocument , connect_mysql , UploadToDatabase , ProcessQuerywithAzureLanguageAIModel, cleanup_table ,add_processed_file_to_db , get_processed_files , add_log_to_activity_db , get_recent_log_message, get_faqs_from_db , get_questions_from_db , add_faqs_to_db, delete_faqs_from_db , get_wt_faqs_from_db , add_wt_faqs_to_db , delete_wt_faqs_from_db , get_wt_short_cut_buttons_from_db , delete_wt_short_cut_buttons_from_db , add_wt_short_cut_buttons_to_db
from azure_storage_api import upload_to_azure_blob , download_blob_from_azure , list_blobs_from_container 
from fastapi import Depends, FastAPI, HTTPException, Header, Security , UploadFile
from fastapi.security import APIKeyHeader
from fastapi import Request
from fastapi.responses import JSONResponse
from config_logger import logger , set_print_logging ,clear_logging #, get_most_recent_log_message  
import subprocess

application = app = FastAPI() 
log_status = "app start" 
 
global output_pdf_dir
output_pdf_dir = 'output_pdfs'
download_documents_folder = "Documents"
bank_type = "chase"

auth_token ="ncft4T9QZTTe6WhPxIT3H1wlwoilslLpynstOsHvf9bFACazWOXaUEHUZOvMgZMPemQiFJFXne0myjL1QJfiQR06BotYlqohxdLgQZIzyOD3VIKEcJHme6pZjFYuZ2Pg"
API_KEY_NAME = "Authorization_H"
# API_KEY = 'Api-Key ' + auth_token
API_KEY = auth_token
api_key_header = APIKeyHeader(name=API_KEY_NAME)
HTTP_403_FORBIDDEN = 403
headers = {"Content-Type": "application/custom+json"} 

async def get_api_key(api_key_header: str = Security(api_key_header)):
    #print(f"api header - {api_key_header}")
    if api_key_header != API_KEY:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN, detail="Could not validate credentials"
        )
    return api_key_header  
    
@app.post("/answer/",dependencies=[Depends(get_api_key)])
async def process_query(request: Request):
# def process_query():
    query = await request.body()
    query = query.decode("utf-8") 
    answer = ProcessQuerywithAzureLanguageAIModel(query) 
    return JSONResponse(content=answer, headers=headers)

@app.get("/get_auth_token/")
def get_auth_token():
    return auth_token

@app.get("/get_log_status/")
async def get_log_status():
    return get_recent_log_message()

@app.get("/get_questions_list/")
def get_questions_list():
    questions = str(get_questions_from_db()) #str(get_questions())
    return JSONResponse(content=questions, headers=headers)

@app.get("/get_wt_faqs_list/")
def get_wt_faqs_list():
    faqs = get_wt_faqs_from_db()# get_faqs()
    return JSONResponse(content=faqs, headers=headers)

@app.post("/save_wt_faqs_to_db/",dependencies=[Depends(get_api_key)])
async def save_wt_faqs_to_db(request: Request):
    question_answer = await request.form() 
    question = question_answer["question"]
    answer = question_answer["answer"] 
    result = add_wt_faqs_to_db(question,answer) 
    return JSONResponse(content=result, headers=headers)

@app.post("/delete_wt_faqs_db/",dependencies=[Depends(get_api_key)])
async def delete_wt_faqs_db(request: Request):
    data = await request.form() 
    index = data["faq_index"] 
    result = delete_wt_faqs_from_db(index) 
    return JSONResponse(content=result, headers=headers)

@app.post("/delete_wt_short_cut_buttons/",dependencies=[Depends(get_api_key)])
async def delete_wt_short_cut_buttons(request: Request):
    data = await request.form() 
    index = data["shortcut_id"] 
    result = delete_wt_short_cut_buttons_from_db(index) 
    return JSONResponse(content=result, headers=headers)

@app.post("/save_wt_short_cut_buttons/",dependencies=[Depends(get_api_key)])
async def save_wt_short_cut_buttons(request: Request):
    name_question = await request.form() 
    question = name_question["question"]
    name = name_question["name"] 
    result = add_wt_short_cut_buttons_to_db(name,question) 
    return JSONResponse(content=result, headers=headers)

@app.get("/get_wt_short_cut_list/")
def get_wt_faqs_list():
    buttons = get_wt_short_cut_buttons_from_db()# get_faqs()
    return JSONResponse(content=buttons, headers=headers)
    
@app.get("/get_faqs_list/")
def get_faqs_list():
    faqs = get_faqs_from_db()# get_faqs()
    return JSONResponse(content=faqs, headers=headers)

@app.post("/save_faqs_to_db/",dependencies=[Depends(get_api_key)])
async def save_faqs_to_db(request: Request):
    question_answer = await request.form() 
    question = question_answer["question"]
    answer = question_answer["answer"] 
    result = add_faqs_to_db(question,answer) 
    return JSONResponse(content=result, headers=headers)

@app.post("/delete_faqs_db/",dependencies=[Depends(get_api_key)])
async def delete_faqs_db(request: Request):
    data = await request.form() 
    index = data["faq_index"] 
    result = delete_faqs_from_db(index) 
    return JSONResponse(content=result, headers=headers)

@app.get("/get_blob_objects/",dependencies=[Depends(get_api_key)])
async def get_blob_objects():
    blob_list = list_blobs_from_container()
    return JSONResponse(content=blob_list, headers=headers)

@app.get("/get_azure_processed_files/",dependencies=[Depends(get_api_key)])
async def get_azure_processed_files():
    blob_list = get_processed_files()
    return JSONResponse(content=blob_list, headers=headers)

# curl -X POST -F "file=@local_file_name.pdf" https://flask-bank-webapp-service.azurewebsites
@app.post("/upload_documents/",dependencies=[Depends(get_api_key)])
async def upload_documents(file: UploadFile):
    # Check if a file was provided
    if not file:
        return JSONResponse(content={"message": "No file provided"}, status_code=400)

    # Save the uploaded file to a directory (e.g., ./uploads)
    with open(f"Documents/{file.filename}", "wb") as f:
        f.write(file.file.read())
    
    upload_to_azure_blob(file.filename)
    
    return JSONResponse(content={"message": "File uploaded successfully", "filename": file.filename})
            
def add_log_to_file_and_activity_db(document_file_name,log_text):
    set_print_logging(log_text)
    add_log_to_activity_db(document_file_name,log_text)

@app.post("/process_document/",dependencies=[Depends(get_api_key)])
async def process_document(request: Request):     
    status = "document processed successfully"
    global download_documents_folder 
    try:
        # process_document_name = request.json['process_document_name'] 
        process_document_name = await request.body()  
        process_document_name = document_file_name = process_document_name.decode("utf-8") 
        # subprocess.call(["python3","test.py",document_file_name], shell=False)
        process = subprocess.Popen(['python3', 'bg_document_process.py', document_file_name])
        # clear_logging()
    except Exception as e:  
        set_print_logging(e) 
        status = str(e) 
    return JSONResponse(content=status, headers=headers)

@app.post("/clean_documents/",dependencies=[Depends(get_api_key)]) 
async def clean_documents(request: Request): 
    status = "All documents deleted successfully"
    try: 
      delete_files_by_extension('./'+ download_documents_folder, '.pdf')
    except Exception as e:  
        set_print_logging(e)
        status = str(e) 
    headers = {"Content-Type": "application/custom+json"} 
    return JSONResponse(content=status, headers=headers)
    
@app.post("/clean_db/",dependencies=[Depends(get_api_key)]) 
async def clean_database(request: Request): 
    status = "All data deleted in database successfully"
    try: 
        cleanup_table()
    except Exception as e:  
        set_print_logging(e)
        status = str(e) 
    headers = {"Content-Type": "application/custom+json"} 
    return JSONResponse(content=status, headers=headers)

    
# run the app.
# if __name__ == "__main__": #comment it while running on azure
#     # Setting debug to True enables debug output. This line should be
#     # removed before deploying a production app.
#      application.debug = True
#      application.run(host="0.0.0.0") 

# def generate_key(self):
#     return binascii.hexlify(os.urandom(20)).decode()
    
# def process_with_azure_save_to_database(document_file_name):
#     global output_pdf_dir
#     connect_mysql()
#     file_paths = (glob.glob(os.path.join(output_pdf_dir, '*.pdf')))
#     for page_no in range(1, len(file_paths)+1): 
#         file_name = f'{output_pdf_dir}/output_{page_no}.pdf' # custom folder
#         file_path = os.path.join(file_name)   # custom folder
#         if page_no < 1: # custom folder
#             continue 
#         if os.path.isfile(file_path):
#             # set_print_logging(f"\n Processing File - {file_path} \n")  #
#             # set_print_logging("Processing OCR Extraction  - Started - [10%]")
#             output_ocr = process_pdf_using_myocrpdf(file_path)
#             pdf_zoom_path = process_pdf_normal_to_zoom(file_path)  
#             add_log_to_file_and_activity_db(document_file_name,f"Processing OCR Extraction Completed. Processing Transaction Entities from Document- {page_no} / {len(file_paths)} - Started [60%]")
#             # set_print_logging("Processing Documents  - Started - [40%]")
#             #pdf_zoom_path = Adobe_Process_pdf(output_ocr,output_pdf_dir) 
#             output_json_file = ProcessDocument(pdf_zoom_path)  
#             add_log_to_file_and_activity_db(document_file_name,"Processing Transaction Entities from Documents Completed. Saving to Azure database - Started [90%]")
#             #output_json_file = f"{output_pdf_dir}/output_{page_no}_zoom.pdf_data.json" 
#             # set_print_logging("Saving to Azure database - Started")
#             UploadToDatabase(output_json_file)
    
# @app.post("/process_document/",dependencies=[Depends(get_api_key)])
# async def process_document(request: Request):     
#     status = "document processed successfully"
#     global download_documents_folder 
#     try:
#         # process_document_name = request.json['process_document_name'] 
#         process_document_name = await request.body()  
#         process_document_name = document_file_name = process_document_name.decode("utf-8")
#         # set_print_logging(f"uploaded document name - {process_document_name}")  
#         add_log_to_file_and_activity_db(document_file_name,"Downloading documents from Azure - Started - [10%]")
#         download_blob_from_azure(process_document_name,download_documents_folder)
#         process_document_name = download_documents_folder + "/" + process_document_name 
#         add_log_to_file_and_activity_db(document_file_name,"Downloading documents from Azure Completed. Extracting monthly statements from Documents - Started [20%]")
#         extract_pdfs_documents_from_single_pdf_documents(process_document_name,bank_type,output_pdf_dir)
#         add_log_to_file_and_activity_db(document_file_name,"Extracting monthly statements from Documents Completed. Processing OCR Extraction  - Started - [40%]")
#         process_with_azure_save_to_database(document_file_name) 
#         add_log_to_file_and_activity_db(document_file_name,"Saving to Azure database - Completed - [100%]")
#         add_processed_file_to_db(document_file_name)
#         # clear_logging()
#     except Exception as e:  
#         set_print_logging(e) 
#         status = str(e) 
#     return JSONResponse(content=status, headers=headers)
