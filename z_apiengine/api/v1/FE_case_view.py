import os, sys

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi import Query

from pydantic import BaseModel, Field, Extra

from typing import List, Optional


LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")
sys.path.insert(0,LOCAL_PATH+"../../")

from get_logger import setup_logging
logging=setup_logging()


#from services.square_service import get_service_square_data_records
from services.case_service import get_case_meta
from services.finaware_services import front_create_set_case
from services.case_BE_service import get_case_report, get_case_processing_status


from d_buttons.button_hub import interface_button_hub




#0v3# JC Jan 13, 2023  New version
#0v3# JC Dec 11, 2023  Attach to d_buttons/button_hub
#0v2# JC Dec  4, 2023  Allow more info in post_case_details
#0v1# JC Nov 28, 2023


"""
    CASE VIEW
    (see excel design)
    - create case
    - start case processing
"""


router = APIRouter()

# Input Models
class CaseIDRequest(BaseModel):
    case_id: str = Field(..., description="The unique identifier of the case")



######################################################
# Output Models


class CaseReportData(BaseModel):
    account_holder_name: Optional[str] = Field(None, description="Name of the account holder")
    account_holder_address: Optional[str] = Field(None, description="Address of the account holder")
    number_of_transactions: Optional[int] = Field(None, description="Total number of transactions")
    opening_balance: Optional[float] = Field(None, description="The opening balance amount")
    closing_balance: Optional[float] = Field(None, description="The closing balance amount")
    number_of_inflows: Optional[int] = Field(None, description="Number of inflow transactions")
    number_of_outflows: Optional[int] = Field(None, description="Number of outflow transactions")
    inflow_amount: Optional[float] = Field(None, description="Total inflow amount")
    outflow_amount: Optional[float] = Field(None, description="Total outflow amount")


class DataModel(BaseModel):
    case_id: Optional[str] = Field(None, description="The unique identifier of the case")
    is_case_started: Optional[bool] = Field(None, description="Indicates if the case processing has started")
    is_case_running: Optional[bool] = Field(None, description="Indicates if the case is currently running")
    is_case_ready_to_query: Optional[bool] = Field(None, description="Indicates if the case is ready to be queried")
    last_state: Optional[str] = Field(None, description="The last recorded state of the case")
    case_status_word: Optional[str] = Field(None, description="A word describing the current status of the case")
    case_files: Optional[List[str]] = Field(None, description="A list of file identifiers associated with the case")
    estimated_case_running_time_remaining_m: Optional[int] = Field(None, description="Estimated remaining time for case processing in minutes")
    age_of_last_active_m: Optional[int] = Field(None, description="The age in minutes since the case was last active")
    has_job_ever_finished: Optional[bool] = Field(None, description="Indicates if the job associated with the case has ever finished")
    job_page_count: Optional[int] = Field(None, description="The number of pages processed in the job")

class CaseProcessingStatusResponse(BaseModel):
    status: str = Field(..., description="The status of the response")
    data: Optional[DataModel] = Field(None, description="The data containing the case processing details")

    class Config:
        schema_extra = {
            "example": {
                "status": "ok",
                "data": {
                    "case_id": "case123",
                    "is_case_started": True,
                    "is_case_running": True,
                    "is_case_ready_to_query": True,
                    "last_state": "processing",
                    "case_status_word": "active",
                    "case_files": ["file1", "file2"],
                    "estimated_case_running_time_remaining_m": 120,
                    "age_of_last_active_m": 5,
                    "has_job_ever_finished": False,
                    "job_page_count": 150,
                }
            }
        }


class CaseProcessingStartResponse(BaseModel):
    case_id: str = Field(..., description="The unique identifier of the case")
    message: str = Field(..., description="Message indicating the start of the case processing")

class CaseDetailsResponse(BaseModel):
    case_id: str = Field(..., description="The unique identifier of the case")
    message: str = Field(..., description="Message indicating the receipt of the case details")

# Endpoint Definitions


class CaseReportResponse(BaseModel):
    status: str = Field(..., description="The status of the response")
    data: Optional[CaseReportData] = Field(None, description="The data of the case report")

    class Config:
        schema_extra = {
            "example": {
                "status": "ok",
                "data": {
                    "account_holder_name": "John Doe",
                    "account_holder_address": "123 Main St, Anytown, AN",
                    "number_of_transactions": 100,
                    "opening_balance": 5000.00,
                    "closing_balance": 4500.00,
                    "number_of_inflows": 70,
                    "number_of_outflows": 30,
                    "inflow_amount": 7000.00,
                    "outflow_amount": 7500.00,
                }
            }
        }

@router.get("/{case_id}/get_case_report", response_model=CaseReportResponse, summary="Get Case Report", description="Retrieves a detailed report of the case.")
#@router.get("/{case_id}/get_case_report", summary="Get Case Report", description="Retrieves a detailed report of the case.")
async def get_case_report_handler(case_id: str,fin_session_id: str = ''):
    """
    Retrieves a detailed case report for a given case ID.
    - **case_id**: unique identifier of the case to retrieve the report for.
    """
    data={}
    if case_id:
        rr=get_case_report(case_id)
        data=rr['data']
        ## Set empty '' string to None
        for k,v in data.items():
            if v=='':
                data[k]=None

    if False and  case_id == "case_test_A":
        # Sample data to return if case_id matches 'case_test_A'
        return {
            "status": "ok",
            "data": {
                "account_holder_name": "John Doe",
                "account_holder_address": "123 Main St, Anytown, AN",
                "number_of_transactions": 100,
                "opening_balance": 5000.00,
                "closing_balance": 4500.00,
                "number_of_inflows": 70,
                "number_of_outflows": 30,
                "inflow_amount": 7000.00,
                "outflow_amount": 7500.00,
            }
        }
    
    logging.info("[debug] raw case report data: "+str(data))
    # Logic to retrieve case report for other case IDs
    return {"status": "ok", "data": data}

##@router.get("/{case_id}/get_case_processing_status", summary="Get Case Processing Status", description="Gets the processing status of the specified case.")
@router.get("/{case_id}/get_case_processing_status", response_model=CaseProcessingStatusResponse, summary="Get Case Processing Status", description="Gets the processing status of the specified case.")
async def get_case_processing_status_handler(case_id: str,fin_session_id: str = ''):
    """
    Gets the current processing status of the case with the provided case ID.
    - **case_id**: unique identifier of the case to get the processing status for.
    """

    logging.info("[debug] get case processing status: "+str(case_id))
    data={}
    if case_id:
        rr=get_case_processing_status(case_id)
        data=rr['data']
        data['case_id']=case_id

    if False and case_id == "case_test_A":
        # Sample data to return if case_id matches 'case_test_A'
        return {
            "status": "ok",
            "data": {
                "case_id": "case_test_A",
                "is_case_started": True,
                "is_case_running": True,
                "is_case_ready_to_query": True,
                "last_state": "processing",
                "case_status_word": "active",
                "case_files": ["file1", "file2"],
                "estimated_case_running_time_remaining_m": 120,
                "age_of_last_active_m": 5,
                "has_job_ever_finished": False,
                "job_page_count": 150,
            }
        }
    # Logic to get the processing status for other case IDs
    return {"status": "ok", "data": data}



# Correct the path parameter to use a scalar type directly:
@router.get("/{case_id}/start_case_processing", response_model=CaseProcessingStartResponse)
async def start_case_processing(case_id: str,fin_session_id: str = ''):  # Use simple scalar type for path parameter
    """
    Starts the processing for the case with the given case ID.
    - **case_id**: unique identifier of the case to start processing.
    """
    # Logic to start processing the case
    
    message=''
    
    if case_id:
        user_input_word='request_start_processing' #FSM is burried
        
        if False: #Update as required
            processing_status,case_state=interface_FE_user_cases_page_state(case_id,user_input=user_input_word)
            ## Pass user facing state of Case
            if processing_status['case_state']=='Processing':
                message='Case is processing!'
            else:
                message="Case is not processing, it's: "+processing_status['case_state']
        
    else:
        message='Missing case id !'

    
    return {"case_id": case_id, "message": message}




class CaseDetailsRequest(BaseModel):
    user_id: str = Field(..., description="The unique identifier of the user.")
    name: Optional[str] = Field(None, description="Name of the case.")
    originalName: Optional[str] = Field(None, description="Original name of the case.")
    size: Optional[str] = Field(None, description="Size of the case.")
    threatTagging: Optional[str] = Field(None, description="Threat tagging details.")
    publicCorruptionTag: Optional[str] = Field(None, description="Public corruption tag details.")
    description: Optional[str] = Field(None, description="Description of the case.")
    case_creation_date: Optional[str] = Field(None, description="Creation date of the case.")
    file_urls: Optional[list] = Field(None, description="URLs of files related to the case.")

    class Config:
        extra = Extra.allow  # Allow extra fields in the model
        
@router.post("/{case_id}/post_case_details", response_model=CaseDetailsResponse, summary="Post Case Details", description="Posts the details of a specific case.")
#async def post_case_details(case_id: str, request: Request, case_details: Optional[CaseDetailsRequest] = None):
async def post_case_details(case_id: str, request: Request, case_details: CaseDetailsRequest, fin_session_id: Optional[str] = ''):
    """
    Accepts and processes the details for the case with the given case ID.
    - **case_id**: the unique identifier of the case from the URL path.
    - **case_details**: the details of the case, all fields are optional.
    - **request**: the request object containing additional information about the request.
     required_fields=['user_id']
    optional_fields=['name','originalName','size','threatTagging','publicCorruptionTag','description','case_creation_date','file_urls']

    """
    
    message=''

    # If case_details is provided, process the details
    if case_details:
        # Process the case_details dictionary
        # This is a placeholder for the actual logic to process the posted case details
        #*** recall dev_finaware_services
        case_meta=case_details.dict()

        case_id=case_id
        username=case_meta.pop('user_id') #Or fail
        front_create_set_case(case_id=case_id,username=username, case_meta=case_meta)
        
        ## Assume accept case details as valid
        #DEL# user_input_word='post_case_details'
        #DEL#  processing_status,case_state=iDELnterface_FE_user_cases_page_state(case_id,user_input=user_input_word)

        message='Case details saved'

    # Respond with a confirmation message or further processed data
    return {"case_id": case_id, "message": message}
    

# GET w/ optional params requires no pydantic but Requests def




@router.get("/{case_id}/button_handler", summary="Handle Button Click", description="Handles a button click event for a specific case.")
async def button_handler(
    case_id: str,
    request: Request,
    fin_session_id: str = Query(..., description="FinAware session id"),
    button_label: Optional[str] = Query(None, description="Label of the button."),  # Made optional
    button_action: Optional[str] = Query(None, description="Action associated with the button."),  # Made optional
    button_id: str = Query(..., description="Identifier of the button.")
):
    """
    Handles a button click event for the given case ID.
    - **case_id**: The unique identifier of the case.
    - **fin_session_id**: FinAware session identifier.
    - **button_label**: Label of the button (optional).
    - **button_action**: Action associated with the button (optional).
    - **button_id**: Identifier of the button.
    Additional query parameters are accepted and will be processed.
    """
    
    #[ ] watch case_id will steer to button_hub and ws broadcast to case_id so ensure validated here
    
    # Extract additional query parameters
    additional_params = {key: value for key, value in request.query_params.items() if key not in ["fin_session_id", "button_label", "button_action", "button_id"]}
    
    user_id=additional_params.pop('user_id','u6232393')

    # Combine all parameters into inputs_dict
    inputs_dict = {
        "user_id": user_id,
        "case_id": case_id,
        "fin_session_id": fin_session_id,
        "button_label": button_label,
        "button_action": button_action,
        "button_id": button_id,
        **additional_params
    }
    
    logging.info("[debug] handle route button_handler...")

    interface_button_hub(**inputs_dict)

    # Respond with a confirmation message
    return {"message": "Button click submitted"}


@router.get("/{case_id}/get_case_details")
async def get_case_details(case_id: str, fin_session_id: str = ''):  # fin_session_id is an optional query parameter
    """
    Retrieves the details of a specific case by its case_id. Optionally, a fin_session_id can be provided.
    """
    # Logic to start processing the case
    case_dict={}

    # You can add logic here to use fin_session_id if it's provided
    if fin_session_id and case_id:
        # Logic that uses fin_session_id
        case_dict=get_case_meta(case_id=case_id)

    elif case_id:
        # Logic that uses fin_session_id
        case_dict=get_case_meta(case_id=case_id)

    return {"case_id": case_id, "data": case_dict}



