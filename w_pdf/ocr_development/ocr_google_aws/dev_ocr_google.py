import os
import sys

import time
import json
import re

from google.cloud import vision
from google.cloud import storage

##?
# python -m pip install gcloud
#gcloud config set project YOUR_PROJECT_ID
#gcloud config set project driveproject321


LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"


#0v1# JC Oct 21, 2023  Base setup



#python -m pip install --upgrade google-cloud-vision
#python -m pip install --upgrade google-cloud-storage



key_filename=LOCAL_PATH+"jon_watchtower_google_driveproject321-2affc0debbc4.json"
cmd="set GOOGLE_APPLICATION_CREDENTIALS="+key_filename
print ("cmd: "+str(cmd))
os.system(cmd)

#https://console.developers.google.com/apis/api/vision.googleapis.com/overview?project=344915644134
print ("! not sure why but it thinks project id is: https://console.developers.google.com/apis/api/vision.googleapis.com/overview?project=344915644134")


def upload_blob(bucket_name, source_file_name, destination_blob_name):
    """Uploads a file to the bucket."""
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(source_file_name)

    # Constructing the GCS path
    gcs_path = f"gs://{bucket_name}/{destination_blob_name}"
    
    print(
        "File {} uploaded to {}.".format(
            source_file_name, destination_blob_name
        )
    )
    print(f"GCS Path: {gcs_path}")


def async_detect_document(gcs_source_uri, gcs_destination_uri):
    """OCR with PDF/TIFF as source files on GCS"""
    # Supported mime_types are: 'application/pdf' and 'image/tiff'
    mime_type = 'application/pdf'

    # How many pages should be grouped into each json output file.
    batch_size = 2

    client = vision.ImageAnnotatorClient()

    #feature = vision.Feature( type_=vision.Feature.Type.DOCUMENT_TEXT_DETECTION)
    feature = vision.Feature( type_=vision.Feature.Type.TEXT_DETECTION)

    gcs_source = vision.GcsSource(uri=gcs_source_uri)
    input_config = vision.InputConfig(
        gcs_source=gcs_source, mime_type=mime_type)

    gcs_destination = vision.GcsDestination(uri=gcs_destination_uri)
    output_config = vision.OutputConfig(
        gcs_destination=gcs_destination, batch_size=batch_size)

    async_request = vision.AsyncAnnotateFileRequest(
        features=[feature], input_config=input_config,
        output_config=output_config)

    operation = client.async_batch_annotate_files(
        requests=[async_request])

    print('Waiting for the operation to finish.')
    operation.result(timeout=420)

    # Once the request has completed and the output has been
    # written to GCS, we can list all the output files.
    storage_client = storage.Client()

    match = re.match(r'gs://([^/]+)/(.+)', gcs_destination_uri)
    bucket_name = match.group(1)
    prefix = match.group(2)

    bucket = storage_client.get_bucket(bucket_name)

    # List objects with the given prefix.
    blob_list = list(bucket.list_blobs(prefix=prefix))
    print('Output files:')
    for blob in blob_list:
        print(blob.name)

    # Process the first output file from GCS.
    # Since we specified batch_size=2, the first response contains
    # the first two pages of the input file.
    output = blob_list[0]

    json_string = output.download_as_string()
    response = json.loads(json_string)

    # The actual response for the first page of the input file.
    first_page_response = response['responses'][0]
    annotation = first_page_response['fullTextAnnotation']

    # Here we print the full text from the first page.
    # The response contains more information:
    # annotation/pages/blocks/paragraphs/words/symbols
    # including confidence scores and bounding boxes
    print('Full text:\n')
    print(annotation['text'])

def dev4():
    # DOWNLOAD 403 GET https://storage.googleapis.com/storage/v1/b/watchtower_ocr_bucket?projection=noAcl&prettyPrint=false: watchtower@driveproject321.iam.gserviceaccount.com does not have storage.buckets.get access to the Google Cloud Storage bucket. Permission 'storage.buckets.get' denied on resource (or it may not exist).

    bucket_name='watchtower_ocr_bucket'

    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    print ("GOT BUCKET: "+str(bucket))

    return

def dev1():
    # Example usage:
    upload_blob('your-bucket-name', '/path/to/local/file.pdf', 'path/in/gcs/file.pdf')
    
    
    gcs_source_uri = "gs://your-bucket-name/path/in/gcs/file.pdf"
    gcs_destination_uri = "gs://your-bucket-name/path/to/output/"
    
    async_detect_document(gcs_source_uri, gcs_destination_uri)

    return


def dev2():
    #(in jc)
    project_name='321driveproject'
    bucket_name='watchtower_ocr_bucket'
    ## Get project key
    # key id:  2affc0debbc48d4b47cbfe92af3328d59f3769d5
    # see json!!

    return


def dev3():
    bucket_name='watchtower_ocr_bucket'

    b=['upload']
    b=['ocr']


    ## SETTINGS
    local_input_pdf_filename=LOCAL_PATH+"../pdf_samples/ORG_IMAGE_FIRST_PAGE_Management-Properties-v-Brusko-Copy-of-First-Citizens-Bank-Checks-2020.pdf"
    cloud_input_filename='input_pdfs/'+os.path.basename(local_input_pdf_filename)
    cloud_output_dir='output_pdfs/'
    #cloud_output_filename=cloud_output_dir+'/'+os.path.basename(local_input_pdf_filename)
    
    if 'upload' in b:
        upload_blob(bucket_name,local_input_pdf_filename,cloud_input_filename)
        
    if 'ocr' in b:
        #PUT TO: gs://watchtower_ocr_bucket/input_pdfs/ORG_IMAGE_FIRST_PAGE_Management-Properties-v-Brusko-Copy-of-First-Citizens-Bank-Checks-2020.pdf

        gcs_source_uri = "gs://"+bucket_name+"/"+cloud_input_filename
        gcs_destination_uri = "gs://"+bucket_name+"/"+cloud_output_dir
        async_detect_document(gcs_source_uri, gcs_destination_uri)

    print ("DONE: "+str(b))
    return



if  __name__=='__main__':
    branches=['dev4']
    branches=['dev3']

    for b in branches:
        globals()[b]()


"""

watchtower-ocr project??

https://console.cloud.google.com/home/dashboard?authuser=1&project=driveproject321

cloud vision api

For the task of performing OCR on PDFs using Google Cloud Vision API and storing the files in Google Cloud Storage, you need to enable the following APIs:

Google Cloud Vision API: This is used for performing OCR on images and PDFs.
Google Cloud Storage: While this doesn’t have a specific API to enable, you need to have billing enabled on your project to use Cloud Storage services.
You can enable these APIs by going to the Google Cloud Console, navigating to your project, and using the “API & Services > Library” section.

Managing Credentials:
Credentials are managed at the project level. Here’s how you can create and manage them:

========================
Create a Service Account: Go to the “IAM & Admin > Service accounts” section in the Google Cloud Console, and create a new service account.
========================
Download the Private Key: After creating the service account, create a new private key (in JSON format) for this account and download it. This key file will be used to authenticate your application with Google Cloud services.
Set Environment Variable: On the machine where your application is running, set the GOOGLE_APPLICATION_CREDENTIALS environment variable to point to the path of your downloaded private key JSON file. This is how Google libraries know which credentials to use when interacting with Google Cloud services.
bash
Copy code
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your-service-account-file.json"


"""

"""
GIVE SERVICE ACCOUNT ACCESS TO CLOUD & vision
Navigate to “IAM & Admin” > “IAM.”
2. Add Permissions to Your Service Account
For Cloud Storage:
Click on “Add.”
In the “New members” field, enter the email address of your service account (it looks like service-account-name@project-id.iam.gserviceaccount.com).
In the “Role” dropdown, select the appropriate role. For file upload, you might need roles like Storage Object Creator (to create objects) or Storage Object Admin (for full control over objects).
Click “Save.”
For Vision API:
Still in the “IAM & Admin” > “IAM” section, click “Add.”
Enter the email address of your service account in the “New members” field.
In the “Role” dropdown, select Vision User or Vision Admin, depending on your needs.

"""























