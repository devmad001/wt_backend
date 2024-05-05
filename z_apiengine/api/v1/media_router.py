import os, sys
from urllib.parse import unquote
from urllib.parse import quote

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.templating import Jinja2Templates
from fastapi import HTTPException, Path, Response
from fastapi.responses import HTMLResponse
from fastapi.responses import FileResponse
from fastapi import Query


LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")
sys.path.insert(0,LOCAL_PATH+"../../")

from services.check_service import get_check_image_meta_image


#0v2# JC Feb  3, 2024  Upgrade to db based
#0v1# JC Jan 28, 2024


## TODOS:
#[ ] add pw control

"""
    SERVER VARIOUS MEDIA
    - check images
"""

## Large relative for now
CHECK_MEDIA_STORAGE_DIR=LOCAL_PATH+"../../../x_modules/k_checks/CHECK_MEDIA_STORAGE"


router = APIRouter()

#/case_id/media/check_images/pdf_filename


@router.get("/{case_id}/media/check_images/{check_identifier}")
async def serve_jpg_image(case_id: str, check_identifier: str, response: Response):
    # Optional: Add password or other authentication checks here
    # assume jpg file
    # 'check_identifier': 'December 2021 Skyview Capital Bank Statement.pdf_5092_11_0_0', 'case_id': 'case_December 2021 Skyview Capital Bank Statement', 'check_id': '5092'

    #/api/v1/case_December 2021 Skyview Capital Bank Statement/December 2021 Skyview Capital Bank Statement.pdf_5092_11_0_0


    check_identifier=unquote(check_identifier) #De urlencode
    print ("[debug] looking for check: "+str(check_identifier))
    

    ## Get check from Checks db image_bytes field via x_modules/k_checks via service
    if check_identifier:
        check_image_bytes,check_image_filename,meta=get_check_image_meta_image(check_identifier)

        if check_image_bytes:
            print ("[debug] check image size: "+str(len(check_image_bytes)))
            print ("[debug] check image filename: "+str(check_image_filename))
            safe_filename = quote(check_image_filename, safe='')

            return Response(check_image_bytes, media_type="image/jpeg", headers={"Content-Disposition": f"inline; filename=\"{safe_filename}\""})
        
    return {"error":"check image not found"}


@router.get("/{case_id}/media/FILEBASED_ORG_check_images/{image_filename}")
async def FILEBASED_ORG_serve_jpg_image(case_id: str, image_filename: str, response: Response):
    # Optional: Add password or other authentication checks here

    image_filename=unquote(image_filename) #De urlencode
    print ("[debug] looking for: "+str(image_filename))

    # Ensure the requested file is a JPG image
    if not image_filename.lower().endswith('.jpg'):
        raise HTTPException(status_code=400, detail="Only JPG images are supported")

    # Construct the relative path to the image based on `case_id` and `image_filename`
    image_path = f"relative/path/to/images/{case_id}/{image_filename}"
    
    image_path=CHECK_MEDIA_STORAGE_DIR+"/"+case_id+"/check_images_meta/"+image_filename


    # Check if the image file exists
    if not os.path.exists(image_path):
        raise HTTPException(status_code=404, detail="Image file not found")

    # Serve the image directly in the response
    return FileResponse(image_path, media_type='image/jpeg')



def local_query_dev():
    # new age evan
    case_id='65a8168eb3ac164610ea5bc2'
    url="http://127.0.0.1:8008/api/v1/case/"+case_id+"/media/check_images/NEW AGE VENDING LLC_check_81_0_5.jpg"
    url="http://127.0.0.1:8008/api/v1/case/65a8168eb3ac164610ea5bc2/media/check_images/NEW AGE VENDING LLC_check_81_0_5.jpg"
    url="https://core.epventures.co/api/v1/case/65a8168eb3ac164610ea5bc2/media/check_images/NEW AGE VENDING LLC_check_81_0_5.jpg"

    return


if __name__=='__main__':
    branches=['local_query_dev']
    for b in branches:
        globals()[b]()

"""
'check_image_filename': 'C:\\scripts-23\\watchtower\\wcodebase\\x_modules\\k_checks/CHECK_MEDIA_STORAGE/65a8168eb3ac164610ea5bc2/check_images_meta/NEW AGE VENDING LLC_check_81_0_5.jpg'}
"""
