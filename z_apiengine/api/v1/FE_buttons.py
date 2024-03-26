import os, sys

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi import Query
from typing import Optional
from pydantic import BaseModel, Field

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")


from get_logger import setup_logging
logging=setup_logging()

from services.button_service import list_buttons_as_dict
from services.button_service import create_button, update_button, delete_button
from services.button_service import get_button_as_dict



#0v2# JC Dec 11, 2023  Add button scope
#0v1# JC Dec  9, 2023


"""
    BUTTON SERVICE

"""


router = APIRouter()


### get version of ws
#@router.get("/{case_id}/get_buttons")
#async def get_dashboard(case_id: str, request: Request, fin_session_id: Optional[str]=''):
#
#    buttons=list_buttons_as_dict(case_id=case_id)
#    
#    ## Filter fields from buttons list (some fields may not exist)
#
#    filter_fields=['user_id','create','bmeta','created']
#    buttons=[{k:v for k,v in b.items() if k not in filter_fields} for b in buttons]
#
#    assumed_fields=['id','label','action','category','visible','query']
#    
#    ## Filter any null or empty fields
#    buttons=[{k:v for k,v in b.items() if v is not None and v!=''} for b in buttons]
#
#    the_json={}
#    the_json['data']=buttons
#    return the_json



# Define a Pydantic model for the button
class Button(BaseModel):
    id: int
    label: str
    query: str
    action: str
    category: str
    scope: str

# Define a Pydantic model for the response
class DashboardResponse(BaseModel):
    data: list[Button]

# Update the endpoint
@router.get("/{case_id}/get_buttons", response_model=DashboardResponse)
async def get_dashboard(user_id: str, case_id: str, request: Request, fin_session_id: Optional[str] = None):
    """
    Retrieve dashboard buttons for a given case and user.

    Args:
    - user_id (str): Unique identifier for the user.
    - case_id (str): Unique identifier for the case.
    - fin_session_id (str, optional): fin_session_id 

    Returns:
    - DashboardResponse: A list of buttons with their details.
    """
    
    #**user created category

    buttons = list_buttons_as_dict(case_id=case_id)
    
    # Filter fields from buttons list
    filter_fields = ['user_id', 'create', 'bmeta', 'created','visible']
    buttons = [{k: v for k, v in b.items() if k not in filter_fields} for b in buttons]

    # Filter any null or empty fields
    buttons = [{k: v for k, v in b.items() if v is not None and v != ''} for b in buttons]
    
    ## Allow empty on required fields
    for button in buttons:
        if not 'category' in button: button['category']=''
        if not 'action' in button: button['action']=''
        if not 'query' in button: button['query']=''
        if not 'label' in button: button['label']=''
            
        ## Auto generated field
        if not 'scope' in button: button['scope']='global' # or user
            
    ## Patch keep buttons
    keepers=[]
    for button in buttons:
        if button['scope']=='global':
            keepers.append(button)
        elif button['username']==user_id:
            keepers.append(button)
        else:
            logging.info("[debug get_buttons] skipping known button: "+str(button)+" does not match user: "+str(user_id))
    buttons=keepers

    # Construct response
    response = DashboardResponse(data=[Button(**b) for b in buttons])
    return response

#A#@router.post("/{case_id}/create_button")
#A#async def api_create_button(case_id:str, label: str, fin_session_id: Optional[str]='', query: Optional[str] = None, action: Optional[str] = None, user_id: Optional[str] = None, visible: Optional[bool] = True, category: Optional[str] = None, bmeta: Optional[dict] = None):
#A#
#A#    bmeta = bmeta if bmeta is not None else {}  # Ensure bmeta is a dictionary
#A#    button_id = create_button(case_id=case_id,label=label, query=query, username=user_id, action=action, visible=visible, category=category, bmeta=bmeta)
#A#    return {"button_id": button_id}
#A#
#A#
#A#@router.post("/{case_id}/update_button/{button_id}")
#A#async def api_update_button(case_id:str, button_id: int, fin_session_id: Optional[str]='', label: Optional[str] = '', action: Optional[str] = '', visible: Optional[bool] = True, category: Optional[str] = '', bmeta: Optional[dict] ={}):
#A#
#A#    updated_button_id = update_button(button_id=button_id, case_id=case_id,label=label, action=action, visible=visible, category=category, bmeta=bmeta)
#A#    if updated_button_id is not None:
#A#        return {"button_id": updated_button_id}
#A#    else:
#A#        raise HTTPException(status_code=404, detail="Button not found")
#A#
#A#        
#A#@router.delete("/{case_id}/delete_button/{button_id}")
#A#async def api_delete_button(case_id: str, button_id: int, fin_session_id: Optional[str] = None):
#A#    ## Validate fin_session_id
#A#    if fin_session_id:
#A#        success = delete_button(button_id)
#A#        if success:
#A#            return {"status": "success", "message": f"Button {button_id} deleted successfully"}
#A#    raise HTTPException(status_code=404, detail="Button not found")

#    
#
##@router.post("/{case_id}/create_button")
##async def api_create_button(case_id:str, label: str, fin_session_id: Optional[str]='', query: Optional[str] = None, action: Optional[str] = None, user_id: Optional[str] = None, visible: Optional[bool] = True, category: Optional[str] = None, bmeta: Optional[dict] = None):
##
###    bmeta = bmeta if bmeta is not None else {}  # Ensure bmeta is a dictionary
#    button_id = create_button(case_id=case_id,label=label, query=query, username=user_id, action=action, visible=visible, category=category, bmeta=bmeta)
##    return {"button_id": button_id}
#


# Define a Pydantic model for the request
class ButtonDetailsRequest(BaseModel):
    user_id: str  # user_id is now mandatory
    label: str
    query: Optional[str] = None
    action: Optional[str] = None


# Define the endpoint using the request model
@router.post("/{case_id}/create_button")
async def api_create_button(case_id: str, button_details: ButtonDetailsRequest, fin_session_id: Optional[str] = ''):
    """
    Create a new button for a given case.

    Args:
    - case_id (str): Unique identifier for the case.
    - button_details (ButtonDetailsRequest): Data for creating a new button.

    Returns:
    - dict: A dictionary containing the ID of the created button.
    """

    # Log the received data for debugging
    logging.info(f"Received data: {button_details.dict()}")

    # Your logic to create a button
    # Assuming create_button is a function that creates the button and returns its ID
    button_id = create_button(
        case_id=case_id,
        label=button_details.label,
        query=button_details.query,
        username=button_details.user_id,  # user_id is used here
        action=button_details.action,
        scope='user'
    )

    return {"button_id": button_id}
    


class UpdateButtonRequest(BaseModel):
    user_id: str
    label: str
    action: Optional[str] = None
    category: Optional[str] = None


@router.post("/{case_id}/update_button/{button_id}")
async def api_update_button(case_id: str, button_id: int, update_data: UpdateButtonRequest, fin_session_id: Optional[str]=''):
    ## SET BUTTONS AT A user level for now
    scope = 'user'
    
    ## Ensure matches permission to update
    button = get_button_as_dict(button_id)
    
    ## Enforce user + fin_session_id + case_id scope
    logging.info("[ ] allowing button update across scope")

    allow_update = False
    if not button:
        raise HTTPException(status_code=404, detail="Button not found")
    elif button['scope'] == 'global':
        raise HTTPException(status_code=403, detail="Global scope buttons cannot be updated by this method")
    else:
        if button.get('username','') == update_data.user_id:
            allow_update = True

    if allow_update:
        updated_button_id = update_button(
            button_id=button_id,
            label=update_data.label,
            action=update_data.action,
            category=update_data.category,
            username=update_data.user_id
            # case_id=case_id,
            # visible=update_data.visible,
            # bmeta=update_data.bmeta
        )
        if updated_button_id is not None:
            return {"button_id": updated_button_id}
        else:
            raise HTTPException(status_code=500, detail="Unable to update button")
    else:
        raise HTTPException(status_code=403, detail="Unauthorized to update this button")


class DeleteButtonRequest(BaseModel):
    user_id: str


@router.post("/{case_id}/delete_button/{button_id}")  # Use DELETE method if it's for deleting
async def api_delete_button(case_id: str, button_id: int, delete_data: DeleteButtonRequest, fin_session_id: Optional[str]=''):
    ## SET BUTTONS AT A user level for now
    scope = 'user'

    ## Ensure matches permission to delete
    button = get_button_as_dict(button_id)

    ## Enforce user + fin_session_id + case_id scope
    logging.info("[ ] allowing button delete across scope")

    reason=''
    allow_delete = False
    reason=''
    if not button:
        logging.info("[button delete] not found")
        raise HTTPException(status_code=404, detail="Button not found")
    elif button['scope'] == 'global':
        logging.info("[button delete] global scope")
        raise HTTPException(status_code=403, detail="Global scope buttons cannot be deleted by this method")
    else:
        logging.info("[button] created with user_id: "+str(button['username'])+" delete with: "+str(delete_data.user_id))
        if button['username'] == delete_data.user_id:
            allow_delete = True
        else:
            reason='Button belongs to different user'
            
    logging.info("[delete button allowed]: "+str(allow_delete))
    allow_delete = True

    if allow_delete:
        success = delete_button(button_id)
        if success:
            return {"status": "success", "message": f"Button {button_id} deleted successfully"}
        else:
            raise HTTPException(status_code=500, detail="Unable to delete button")
    else:
        raise HTTPException(status_code=403, detail="Unauthorized to delete this button "+reason)

    

#@router.post("/{case_id}/update_button/{button_id}")
#async def api_update_button(case_id:str, user_id:str, button_id: int, fin_session_id: Optional[str]='', label: Optional[str] = '', action: Optional[str] = '', visible: Optional[bool] = True, category: Optional[str] = '', bmeta: Optional[dict] ={}):
#
#    updated_button_id = update_button(button_id=button_id, case_id=case_id,label=label, action=action, visible=visible, category=category, bmeta=bmeta)
#    if updated_button_id is not None:
#        return {"button_id": updated_button_id}
#    else:
#        raise HTTPException(status_code=404, detail="Button not found")

        
#@router.delete("/{case_id}/delete_button/{button_id}")
#async def api_delete_button(case_id: str, user_id: str, button_id: int, fin_session_id: Optional[str] = None):
#    ## Validate fin_session_id
#    if fin_session_id:
#        success = delete_button(button_id)
#        if success:
#            return {"status": "success", "message": f"Button {button_id} deleted successfully"}
#    raise HTTPException(status_code=404, detail="Button not found")


def dev1():
    return



if __name__=='__main__':
    branches=['dev1']
    for b in branches:
        globals()[b]()



"""
"""



































