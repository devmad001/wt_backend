import os, sys
import urllib.parse
import re

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi import Query


from fastapi.responses import FileResponse, JSONResponse
#from sqlalchemy.orm import Session


LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")

from services.general_services import generate_excel
from services.general_services import serve_pdf_content


from get_logger import setup_logging
logging=setup_logging()



#0v4# JC Jan 23, 2024  filename encoding error?!  Sanitize
#0v3# JC Jan 11, 2024  Reverse quote plus urlencoding
#0v2# JC Dec  8, 2023  Send via buttons ws_spawn_download
#0v1# JC Nov  5, 2023



"""
    GENERAL SERVICES ROUTER

"""


router = APIRouter()


###############################################################
#  EXCEL
###############################################################
@router.get("/{case_id}/generate_excel")
async def generate_excel_handler(case_id):
    rr=await generate_excel(case_id=case_id)

    if 'error' in rr:
        logging.error("[ERROR CREATING EXCEL] " + str(rr))
        return JSONResponse(content={"error": str(rr)}, status_code=500)
    elif not 'full_filename' in rr:
        logging.error("[ERROR CREATING EXCEL] " + str(rr))
        return JSONResponse(content={"error": str(rr)}, status_code=500)
    else:
        pass
    
    logging.info("[ready to dump excel?]")
    if os.path.exists(rr['full_filename']):
        print("[debug] want to dump excel: " + str(rr['full_filename']))
        # Continue with your logic and replace send_from_directory
        directory = os.path.dirname(rr['full_filename'])
        filename = os.path.basename(rr['full_filename'])
        
        return FileResponse(path=rr['full_filename'], filename=rr['case_filename'], media_type='application/vnd.ms-excel')

    else:
        logging.warning("[WARNING] excel file does not exist: " + str(rr['full_filename']))
        return JSONResponse(content={
            "status": f"Dumping Excel for {case_id}",
            "warning": "Excel file not produced"
        }, status_code=404)



# Example function to sanitize filename
def sanitize_filename(filename):
    # Remove or replace non-latin-1 characters
    # This is a simple example; you might need a more sophisticated method
    if filename:
        filename=re.sub(r'[^\x00-\xFF]', '_', filename)
    return filename

###############################################################
#  PDF VIEWER
###############################################################
"""
(For D3 see: alg_generate_transaction_hyperlink.py)
http://127.0.0.1:8008/api/v1/case/chase_3_66_5ktransfer/pdf/Chase%20Statements%203%2012.pdf?page=1&key=0da450fb3141c2097d1b60398886459aff428fe302cc3157f85d3599495fe956
"""
@router.get("/{case_id}/pdf/{filename}/{page_num:path}")
@router.get("/{case_id}/pdf/{filename}", include_in_schema=False)
async def view_pdf(case_id: str, filename: str, request: Request, page_num: str = "0", highlight: str = ""):
    logging.info("[debug] at PDF viewer")

    # Extracting 'page' and 'key' query parameters
    page_param = request.query_params.get('page')
    key_param = request.query_params.get('key')  # <A HREF="...myfile.pdf?page=4&key=123">

    # If 'page' query parameter exists, use it instead of path 'page_num'
    page_num = page_param if page_param else page_num
    
    ## For highlighting
    search_strs = highlight.split("|") if highlight else []
    #* remove urlencoding (See: filerepo.py urllib.parse.quote_plus)
    search_strs=[urllib.parse.unquote_plus(x) for x in search_strs]


    # Your existing logic to decide whether to fetch the full PDF or just a page
    try:
        pdf_content, pdf_key, page_content, page_key = await serve_pdf_content(
            case_id, filename=filename, page_num=int(page_num), search_strs=search_strs
        )
        response_content = pdf_content if not page_num or page_num == "0" else page_content
    except Exception as e:
        logging.error(str(e))
        raise HTTPException(status_code=500, detail=str(e))

    logging.info("[debug content length]: " + str(len(response_content)))
    logging.info("[pdf key]: " + str(pdf_key))

    ## Sanitize filename (bad encoding or latin-1)
    filename=sanitize_filename(filename)

    # Create a FastAPI Response object to send the PDF data with appropriate headers
    headers = {
        "Content-Type": "application/pdf",
        "Content-Disposition": f"inline; filename={filename}"
    }
    return Response(content=response_content, headers=headers)





