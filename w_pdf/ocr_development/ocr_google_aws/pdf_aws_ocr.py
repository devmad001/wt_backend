import time
import os
import sys
import codecs
import json
import re
import uuid
import watchtower #python -m pip install watchtower

import boto3
from botocore.exceptions import ClientError


LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"..")

from get_logger import setup_logging
import logging as logging_sys
logging=setup_logging()


#0v1# JC  Oct 13, 2023  AWS Textract wrapper


"""
    EXPECT TEXTRACT to be better and faster then current
    - TextractWrapper from:  https://github.com/awsdocs/aws-doc-sdk-examples/blob/main/python/example_code/textract/textract_wrapper.py
    - PDFTextExtractor with queues etc boilerplate from gpt

"""



# snippet-start:[python.example_code.textract.TextractWrapper]
class TextractWrapper:
    """Encapsulates Textract functions."""

    def __init__(self, textract_client, s3_resource, sqs_resource):
        """
        :param textract_client: A Boto3 Textract client.
        :param s3_resource: A Boto3 Amazon S3 resource.
        :param sqs_resource: A Boto3 Amazon SQS resource.
        """
        self.textract_client = textract_client
        self.s3_resource = s3_resource
        self.sqs_resource = sqs_resource

    # snippet-end:[python.example_code.textract.TextractWrapper]

    # snippet-start:[python.example_code.textract.DetectDocumentText]
    def detect_file_text(self, *, document_file_name=None, document_bytes=None):
        """
        Detects text elements in a local image file or from in-memory byte data.
        The image must be in PNG or JPG format.

        :param document_file_name: The name of a document image file.
        :param document_bytes: In-memory byte data of a document image.
        :return: The response from Amazon Textract, including a list of blocks
                 that describe elements detected in the image.
        """
        if document_file_name is not None:
            with open(document_file_name, "rb") as document_file:
                document_bytes = document_file.read()
        try:
            response = self.textract_client.detect_document_text(
                Document={"Bytes": document_bytes}
            )
            logging.info("Detected %s blocks.", len(response["Blocks"]))
        except ClientError:
            logging.exception("Couldn't detect text.")
            raise
        else:
            return response

    # snippet-end:[python.example_code.textract.DetectDocumentText]

    # snippet-start:[python.example_code.textract.AnalyzeDocument]
    def analyze_file(
        self, feature_types, *, document_file_name=None, document_bytes=None
    ):
        """
        Detects text and additional elements, such as forms or tables, in a local image
        file or from in-memory byte data.
        The image must be in PNG or JPG format.

        :param feature_types: The types of additional document features to detect.
        :param document_file_name: The name of a document image file.
        :param document_bytes: In-memory byte data of a document image.
        :return: The response from Amazon Textract, including a list of blocks
                 that describe elements detected in the image.
        """
        if document_file_name is not None:
            with open(document_file_name, "rb") as document_file:
                document_bytes = document_file.read()
        try:
            response = self.textract_client.analyze_document(
                Document={"Bytes": document_bytes}, FeatureTypes=feature_types
            )
            logging.info("Detected %s blocks.", len(response["Blocks"]))
        except ClientError:
            logging.exception("Couldn't detect text.")
            raise
        else:
            return response

    # snippet-end:[python.example_code.textract.AnalyzeDocument]

    # snippet-start:[python.example_code.textract.helper.prepare_job]
    def prepare_job(self, bucket_name, document_name, document_bytes):
        """
        Prepares a document image for an asynchronous detection job by uploading
        the image bytes to an Amazon S3 bucket. Amazon Textract must have permission
        to read from the bucket to process the image.

        :param bucket_name: The name of the Amazon S3 bucket.
        :param document_name: The name of the image stored in Amazon S3.
        :param document_bytes: The image as byte data.
        """
        try:
            bucket = self.s3_resource.Bucket(bucket_name)
            bucket.upload_fileobj(document_bytes, document_name)
            logging.info("Uploaded %s to %s.", document_name, bucket_name)
        except ClientError:
            logging.exception("Couldn't upload %s to %s.", document_name, bucket_name)
            raise

    # snippet-end:[python.example_code.textract.helper.prepare_job]

    # snippet-start:[python.example_code.textract.helper.check_job_queue]
    def check_job_queue(self, queue_url, job_id):
        """
        Polls an Amazon SQS queue for messages that indicate a specified Textract
        job has completed.

        :param queue_url: The URL of the Amazon SQS queue to poll.
        :param job_id: The ID of the Textract job.
        :return: The status of the job.
        """
        status = None
        try:
            queue = self.sqs_resource.Queue(queue_url)
            messages = queue.receive_messages()
            if messages:
#D#                print ("[check job queue raw]: "+str(messages))
                msg_body = json.loads(messages[0].body)
                if 'Message' in msg_body:
                    
                    try: msg = json.loads(msg_body["Message"])
                    except:
                        logging.warning("[sqs] could not read message")
#                        print ("[error] DELETING MSG could not load as json: "+str(msg_body['Message']))
#                        msg={}
#                        messages[0].delete()

                    if msg.get("JobId") == job_id:
                        messages[0].delete()
                        status = msg.get("Status")
                        logging.info(
                            "Got message %s with status %s.", messages[0].message_id, status
                        )
                else:
                    print ("[error] bad msg_body: "+str(msg_body))

            else:
                logging.info("No messages in queue %s.", queue_url)
        except ClientError:
            logging.exception("Couldn't get messages from queue %s.", queue_url)
        else:
            return status

    # snippet-end:[python.example_code.textract.helper.check_job_queue]

    # snippet-start:[python.example_code.textract.StartDocumentTextDetection]
    def start_detection_job(
        self, bucket_name, document_file_name, sns_topic_arn, sns_role_arn
    ):
        """
        Starts an asynchronous job to detect text elements in an image stored in an
        Amazon S3 bucket. Textract publishes a notification to the specified Amazon SNS
        topic when the job completes.
        The image must be in PNG, JPG, or PDF format.

        :param bucket_name: The name of the Amazon S3 bucket that contains the image.
        :param document_file_name: The name of the document image stored in Amazon S3.
        :param sns_topic_arn: The Amazon Resource Name (ARN) of an Amazon SNS topic
                              where the job completion notification is published.
        :param sns_role_arn: The ARN of an AWS Identity and Access Management (IAM)
                             role that can be assumed by Textract and grants permission
                             to publish to the Amazon SNS topic.
        :return: The ID of the job.
        """
        client_request_token = str(uuid.uuid4())
        try:
            response = self.textract_client.start_document_text_detection(
                DocumentLocation={
                    "S3Object": {"Bucket": bucket_name, "Name": document_file_name}
                },
                NotificationChannel={
                    "SNSTopicArn": sns_topic_arn,
                    "RoleArn": sns_role_arn,
                },
                ClientRequestToken=client_request_token, #Cloudwatch
            )
            job_id = response["JobId"]
            logging.info(
                "Started text detection job %s on %s.", job_id, document_file_name
            )
        except ClientError:
            logging.exception("Couldn't detect text in %s.", document_file_name)
            raise
        else:
            return job_id

    # snippet-end:[python.example_code.textract.StartDocumentTextDetection]

    # snippet-start:[python.example_code.textract.GetDocumentTextDetection]
    def get_detection_job(self, job_id):
        """
        Gets data for a previously started text detection job.

        :param job_id: The ID of the job to retrieve.
        :return: The job data, including a list of blocks that describe elements
                 detected in the image.
        """
        try:
            response = self.textract_client.get_document_text_detection(JobId=job_id)
            job_status = response["JobStatus"]
            logging.info("Job %s status is %s.", job_id, job_status)
        except ClientError:
            logging.exception("Couldn't get data for job %s.", job_id)
            raise
        else:
            return response

    # snippet-end:[python.example_code.textract.GetDocumentTextDetection]

    # snippet-start:[python.example_code.textract.StartDocumentAnalysis]
    def start_analysis_job(
        self,
        bucket_name,
        document_file_name,
        feature_types,
        sns_topic_arn,
        sns_role_arn,
    ):
        """
        Starts an asynchronous job to detect text and additional elements, such as
        forms or tables, in an image stored in an Amazon S3 bucket. Textract publishes
        a notification to the specified Amazon SNS topic when the job completes.
        The image must be in PNG, JPG, or PDF format.

        :param bucket_name: The name of the Amazon S3 bucket that contains the image.
        :param document_file_name: The name of the document image stored in Amazon S3.
        :param feature_types: The types of additional document features to detect.
        :param sns_topic_arn: The Amazon Resource Name (ARN) of an Amazon SNS topic
                              where job completion notification is published.
        :param sns_role_arn: The ARN of an AWS Identity and Access Management (IAM)
                             role that can be assumed by Textract and grants permission
                             to publish to the Amazon SNS topic.
        :return: The ID of the job.
        """
        print ("[debug] bucket: "+str(bucket_name))
        print ("[debug] Filename: "+str(document_file_name))

        client_request_token = str(uuid.uuid4())
        try:
            response = self.textract_client.start_document_analysis(
                DocumentLocation={
                    "S3Object": {"Bucket": bucket_name, "Name": document_file_name}
                },
                NotificationChannel={
                    "SNSTopicArn": sns_topic_arn,
                    "RoleArn": sns_role_arn,
                },
                FeatureTypes=feature_types,
                ClientRequestToken=client_request_token, #Cloudwatch
            )
            job_id = response["JobId"]
            logging.info(
                "Started text analysis job %s on %s.", job_id, document_file_name
            )
        except ClientError:
            logging.exception("Couldn't analyze text in %s.", document_file_name)
            raise
        else:
            return job_id

    # snippet-end:[python.example_code.textract.StartDocumentAnalysis]

    # snippet-start:[python.example_code.textract.GetDocumentAnalysis]
    def get_analysis_job(self, job_id):
        """
        Gets data for a previously started detection job that includes additional
        elements.

        :param job_id: The ID of the job to retrieve.
        :return: The job data, including a list of blocks that describe elements
                 detected in the image.
        """
        try:
            response = self.textract_client.get_document_analysis(JobId=job_id)
            job_status = response["JobStatus"]
            logging.info("Job %s status is %s.", job_id, job_status)
        except ClientError:
            logging.exception("Couldn't get data for job %s.", job_id)
            raise
        else:
            return response

#1149
class PDFTextExtractor:
    
    def __init__(self, bucket_name, sns_topic_arn, sns_role_arn, queue_url, aws_access_key_id=None, aws_secret_access_key=None, region_name='us-east-2'):
        self.bucket_name = bucket_name
        self.sns_topic_arn = sns_topic_arn
        self.sns_role_arn = sns_role_arn
        self.queue_url = queue_url
        self.region_name=region_name

        self.session = boto3.Session(
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=region_name
        )

        self.textract_client = self.session.client('textract')
        self.s3_resource = self.session.resource('s3')
        self.sqs_resource = self.session.resource('sqs')

#cloudwatch        logger=self.setup_logging(aws_access_key_id, aws_secret_access_key, region_name)

        self.wrapper = TextractWrapper(self.textract_client, self.s3_resource, self.sqs_resource)

    def setup_logging(self,aws_access_key_id, aws_secret_access_key, region_name):
        ## Cloudwatch not needed
        #logging.basicConfig(level=logging.INFO)
        #logger = logging.getLogger(__name__)
        logger=logging
        
        # Setup Watchtower logging handler to send logs to CloudWatch

        cw_handler = watchtower.CloudWatchLogHandler(
#            boto3_session=self.session,
            log_group="YourLogGroupName",  # Name your log group
            stream_name="YourStreamName",  # Optionally, name your log stream
            create_log_group=True
        )

        logger.addHandler(cw_handler)
        
        # Boto3 logs
        boto3.set_stream_logger(name='boto3', level=logging_sys.INFO)
        boto3.set_stream_logger(name='botocore', level=logging_sys.INFO)
        return logger


    def extract_from_pdfs(self, pdf_paths):
        # Initialize an empty dictionary to store the jobs.
        jobs = {}
    
        # Iterate through each provided path in the pdf_paths list.
        for pdf_path in pdf_paths:
            # Extract the document name from the given path.
            document_name = pdf_path.split('/')[-1]
    
            # Open the PDF file in binary read mode.
            with open(pdf_path, 'rb') as file:
                # Use the wrapper to prepare the job with the necessary resources.
                self.wrapper.prepare_job(self.bucket_name, document_name, file)
    
            # Define the types of features to extract from the document.
            feature_types = ["TABLES", "FORMS"]
    
            # Start an analysis job using the wrapper.
            job_id = self.wrapper.start_analysis_job(self.bucket_name, document_name, feature_types, 
                                                     self.sns_topic_arn, self.sns_role_arn)
            
            print ("[debug] using job id (created from start_analysis_job... ): "+str(job_id))
    
            # Store the job ID and its corresponding PDF path.
            jobs[job_id] = pdf_path
    
        # Initialize an empty dictionary to store the results.
        results = {}
    
        # Placeholder for future functionality.
    
        # Continue processing as long as there are jobs left.
        start_time=time.time()
        while jobs:
            run_time=time.time()-start_time
            if run_time>60*30:
                logging.error("[warning] run time exceeded 30 minutes.  breaking.")
                break
            # Iterate through each job in the jobs dictionary.
            for job_id, pdf_path in list(jobs.items()):
                # Check the status of the job in the queue.
                status = self.wrapper.check_job_queue(self.queue_url, job_id)
    
                # If the job succeeded, retrieve and process the results.
                if status == 'SUCCEEDED':
                    response = self.wrapper.get_analysis_job(job_id)
                    pages = self._process_response(response)
    
                    # Store the results for the current PDF.
                    results[pdf_path] = pages
    
                    # Remove the completed job from the jobs dictionary.
                    del jobs[job_id]
                # If the status is empty, log the information and wait before checking again.
                elif not status:
#                    logging.info("[debug] job queue status is empty?: "+str(status))
                    time.sleep(2)

        # Return the results dictionary.
        return results
 
 
    def infer_line_breaks(self, blocks):
        """
        Infers line breaks for a list of text blocks based on Y-coordinate differences.
        
        Args:
        - blocks (list of dict): List containing dictionaries with 'Text' and 'Y' keys.
        
        Returns:
        - str: Processed text with inferred line breaks.
        """
        # Sort blocks by Y coordinate
        blocks = sorted(blocks, key=lambda x: x['Y'])
    
        lines = []
        current_line = blocks[0]['Text']
        
        y_diffs = [abs(blocks[i]['Y'] - blocks[i-1]['Y']) for i in range(1, len(blocks))]
    
        try:
            # Infer the line height by finding the mode of Y-coordinate differences
            inferred_line_height = mode(y_diffs)
        except:
            # If there's no distinct mode, fall back to an arbitrary threshold (like the median).
            inferred_line_height = sorted(y_diffs)[len(y_diffs) // 2]
            
        print ("Inferred_line_height: "+str(inferred_line_height))
    
        for i in range(1, len(blocks)):
            if abs(blocks[i]['Y'] - blocks[i-1]['Y']) < inferred_line_height * 1.5:  # A little tolerance can be added.
                current_line += " " + blocks[i]['Text']
            else:
                lines.append(current_line)
                current_line = blocks[i]['Text']
    
        lines.append(current_line)  # Add the last line
        
        return "\n".join(lines)


    def _process_response_ONLY_COUPLE_WORDS_PER_LINE(self, response):
        """
        Process OCR response to organize detected text by page and block type.
        
        Args:
        - response (dict): OCR response containing detected blocks.
    
        Returns:
        - dict: Dictionary with pages as keys and detected text as values.
        
        #>> 
        BLOCK:  {'BlockType': 'WORD', 'Confidence': 99.9557876586914, 'Text': 'of', 'TextType': 'PRINTED', 'Geometry': {'BoundingBox': {'Width': 0.013748216442763805, 'Height': 0.009416041895747185, 'Left': 0.8770983219146729, 'Top': 0.9321821928024292}, 'Polygon': [{'X': 0.8770983219146729, 'Y': 0.9321832656860352}, {'X': 0.8908361792564392, 'Y': 0.9321821928024292}, {'X': 0.8908465504646301, 'Y': 0.9415972232818604}, {'X': 0.877108633518219, 'Y': 0.9415982365608215}]}, 'Id': 'f0238cb9-0368-495c-a8a2-62c636aef279', 'Page': 1}
        
        """
        pages = {}
        block_map = {block['Id']: block for block in response['Blocks']}
    
        for block in response['Blocks']:
            y_coordinate = block['Geometry']['BoundingBox']['Top']
            if block['BlockType'] in ['LINE', 'WORD']:
                page = block['Page']
                
                pages.setdefault(page, []).append({'Text': block['Text'], 'Y': y_coordinate})
    
            elif block['BlockType'] == 'CELL':
                content = ""
                for relationship in block.get('Relationships', []):
                    if relationship['Type'] == 'CHILD':
                        for child_id in relationship['Ids']:
                            cell_piece = block_map[child_id]
                            if cell_piece['BlockType'] in ['WORD', 'LINE']:
                                content += cell_piece['Text'] + " "
                pages.setdefault(block['Page'], []).append({'Text': content.strip() + "|", 'Y': y_coordinate})
    
        # Process each page with infer_line_breaks
        for page in pages:
            page_blocks = pages[page]
            pages[page] = self.infer_line_breaks(page_blocks)
    
        return pages

    def _process_response_MESSES_WITH_ORDER_MOSTLY_ONE_COL(self, response):
        #REF: https://github.com/aws-samples/amazon-textract-code-samples/blob/master/python/03-reading-order.py
    
        # Detect columns and print lines
        columns = []
        lines = []
        for item in response["Blocks"]:
              if item["BlockType"] == "LINE":
                column_found=False
                for index, column in enumerate(columns):
                    bbox_left = item["Geometry"]["BoundingBox"]["Left"]
                    bbox_right = item["Geometry"]["BoundingBox"]["Left"] + item["Geometry"]["BoundingBox"]["Width"]
                    bbox_centre = item["Geometry"]["BoundingBox"]["Left"] + item["Geometry"]["BoundingBox"]["Width"]/2
                    column_centre = column['left'] + column['right']/2
        
                    if (bbox_centre > column['left'] and bbox_centre < column['right']) or (column_centre > bbox_left and column_centre < bbox_right):
                        #Bbox appears inside the column
                        lines.append([index, item["Text"]])
                        column_found=True
                        break
                if not column_found:
                    columns.append({'left':item["Geometry"]["BoundingBox"]["Left"], 'right':item["Geometry"]["BoundingBox"]["Left"] + item["Geometry"]["BoundingBox"]["Width"]})
                    lines.append([len(columns)-1, item["Text"]])
        
        lines.sort(key=lambda x: x[0])
        for line in lines:
            print (line[1])
        a=okk
        return

    def _process_response(self, response):
        #ONE_BLOB_SAMPLE_1 below
        text_blob = ""
        for item in response["Blocks"]:
            if item["BlockType"] in ["LINE", "WORD"]:
                text_blob += item["Text"] + " "
                
        print (str(text_blob))
        a=okk
        return text_blob

    def _process_response_OK_BUT_ONE_BLOG(self, response):
        #ONE_BLOB_SAMPLE_1 below
        text_blob = ""
        for item in response["Blocks"]:
            if item["BlockType"] in ["LINE", "WORD"]:
                text_blob += item["Text"] + " "
                
        print (str(text_blob))
        a=okk
        return text_blob

    def _process_response_NO_ORDER_ALL_MESSED(self, response):
        lines = []
        for item in response["Blocks"]:
            if item["BlockType"] == "LINE":
                lines.append((item["Geometry"]["BoundingBox"]["Top"], item["Text"]))
    
        # Sort lines based on their Y-coordinate
        lines.sort(key=lambda x: x[0])
        
        # Concatenate lines to create the text blob
        text_blob = "\n".join([line[1] for line in lines])
        
        print ("BLOB SOME: "+str(text_blob))
        a=kkk
        
        return text_blob

    def health_check(self):
        """
        This function checks the health of various AWS services by trying to 
        list resources or making specific calls. Any errors are logged.
        """
    
        # Check S3
        try:
            buckets = list(self.s3_resource.buckets.limit(1))
            if not buckets:
                logging.warning("No S3 buckets found.")
            else:
                logging.info("S3 is accessible.")
        except self.s3_resource.meta.client.exceptions.AccessDenied:
            logging.warning("Permission denied for S3 ListBuckets operation.")
        except Exception as e:
            logging.error(f"Error checking S3: {e}")
    
        # Check SQS
        try:
            queues = list(self.sqs_resource.queues.limit(1))
            if not queues:
                logging.warning("No SQS queues found.")
            else:
                logging.info("SQS is accessible.")
        except Exception as e:
            logging.error(f"Error checking SQS: {e}")

        # Check Textract by calling the service without making an actual detection
        try:
            # Using a non-existent S3 object to initiate a check
            self.textract_client.detect_document_text(
                Document={'S3Object': {'Bucket': 'nonexistent-bucket', 'Name': 'nonexistent-object'}}
            )
        except self.textract_client.exceptions.InvalidS3ObjectException:
            logging.info("Textract is accessible.")
        except Exception as e:
            logging.error(f"Error checking Textract: {e}")

        
        logging.info("Health check completed for all services.")
        return True  # Optionally, you can return False if any of the services are inaccessible.


def dev1():
    filename=LOCAL_PATH+'pdf_samples/new_kind_first_citizens_bank-Management-Properties-v-Brusko-Copy-of-First-Citizens-Bank-Checks-2020.pdf'
    if not os.path.exists(filename):
        raise Exception("[error] file not found: "+str(filename))

    # Usage
    S3_BUCKET_NAME='watchtowerocrbucket'
    SNS_TOPIC_ARN='arn:aws:sns:us-east-2:487320324532:watchtowersnstopic'
#NOT THIS IS THE USER#     SNS_ROLE_ARN='arn:aws:iam::487320324532:role/ocr_textract_s3_sns_sqs' #<-- SNS ROLE
    SNS_ROLE_ARN='arn:aws:iam::487320324532:role/watchtower_textract_role'
    SQS_QUEUE_URL='https://sqs.us-east-2.amazonaws.com/487320324532/watchtowersqs'


    region_name='us-east-2'
    aws_access_key = 'AKIAXC5UOBG2L6QRBC5B'
    aws_secret_key = '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'

    # SET AWS_ACCESS_KEY=AKIAXC5UOBG2L6QRBC5B
    # SET AWS_SECRET_KEY=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
    
    os.environ["AWS_ACCESS_KEY_ID"] = aws_access_key
    os.environ["AWS_SECRET_ACCESS_KEY"] = aws_secret_key

    extractor = PDFTextExtractor(S3_BUCKET_NAME, SNS_TOPIC_ARN, SNS_ROLE_ARN, SQS_QUEUE_URL, aws_access_key, aws_secret_key, region_name)
    
    
    extractor.health_check()
    
    pdf_paths = [filename]
    print ("PROCESSING: "+str(pdf_paths))

    results = extractor.extract_from_pdfs(pdf_paths)
    
    for pdf_path, pages in results.items():
        for page_num, lines in pages.items():
            print(f"--- {pdf_path} Page {page_num} ---")
            print ("LINES: "+str(lines))
#            for line in lines:
#                print(line)
    
    return


if __name__=='__main__':
    branches=['dev1']
    for b in branches:
        globals()[b]()



"""
SETTINGS:
region:  us-east-2
bucket:  watchtowerocrbucket
sqs:  watchtowersqs
    watchtowersnstopic

"""

"""
AWS CONFIG STEPS

By combining these services, you create a system where Textract processes documents, notifies SNS when done, and SNS then forwards that notification to an SQS queue, from which your application can retrieve and act upon it.


============================
1.  S3 bucket - create
-)  add policy to bucket to allow Textract to write to bucket
**updated for full access.

{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "Service": "textract.amazonaws.com"
            },
            "Action": "s3:*",
            "Resource": [
                "arn:aws:s3:::watchtowerocrbucket",
                "arn:aws:s3:::watchtowerocrbucket/*"
            ]
        }
    ]
}


============================
2.  SQS - create
)  attach policy to SQS to allow Textract to send messages:
    extend your SQS policy to allow Amazon SNS to send messages to the SQS queue, you'd want to add another statement to your policy.
    - also do (c) for sns notification.
    
    watchtowersnstopic
    
{
  "Version": "2012-10-17",
  "Id": "__default_policy_ID",
  "Statement": [
    {
      "Sid": "__owner_statement",
      "Effect": "Allow",
      "Principal": {
        "AWS": "487320324532"
      },
      "Action": [
        "SQS:*"
      ],
      "Resource": "arn:aws:sqs:us-east-2:487320324532:watchtowersqs"
    },
    {
      "Sid": "AllowSNSMessages",
      "Effect": "Allow",
      "Principal": {
        "Service": "sns.amazonaws.com"
      },
      "Action": "sqs:SendMessage",
      "Resource": "arn:aws:sqs:us-east-2:487320324532:watchtowersqs",
      "Condition": {
        "ArnEquals": {
          "aws:SourceArn": "arn:aws:sns:us-east-2:487320324532:watchtowersnstopic"
        }
      }
    }
  ]
}

============================
3.  SNS - create
watchtowersnstopic??

Certainly. If you're using Amazon Textract, SQS, SNS, and S3 in tandem and plan to manage these resources with boto3, you'd need a comprehensive set of permissions.

Here's a consolidated policy for an IAM user (or role) that encompasses permissions for Textract, S3, SQS, SNS, and boto3 operations:

    {
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowAllSNSActionsForTopic",
      "Effect": "Allow",
      "Principal": {
        "AWS": "*"
      },
      "Action": [
        "sns:Publish",
        "sns:RemovePermission",
        "sns:SetTopicAttributes",
        "sns:DeleteTopic",
        "sns:ListSubscriptionsByTopic",
        "sns:GetTopicAttributes",
        "sns:AddPermission",
        "sns:Subscribe"
      ],
      "Resource": "arn:aws:sns:us-east-2:487320324532:watchtowersnstopic",
      "Condition": {
        "StringEquals": {
          "AWS:SourceOwner": "487320324532"
        }
      }
    },
    {
      "Sid": "AllowSNSSubscribeForSQS",
      "Effect": "Allow",
      "Principal": {
        "Service": "sqs.amazonaws.com"
      },
      "Action": "sns:Subscribe",
      "Resource": "arn:aws:sns:us-east-2:487320324532:watchtowersnstopic",
      "Condition": {
        "StringEquals": {
          "AWS:SourceOwner": "487320324532"
        }
      }
    }
  ]
}



============================
4.  IAM 

AmazonS3FullAccess: Provides full access to Amazon S3. You might want to narrow this down later to just the buckets you're using.
AmazonTextractFullAccess: Provides full access to Amazon Textract.
AmazonSQSFullAccess: Pr

POLICY:  ocr_textract_s3_sns_sqs

{
	"Version": "2012-10-17",
	"Statement": [
		{
			"Effect": "Allow",
			"Action": [
				"textract:*",
				"s3:GetObject",
				"s3:PutObject",
				"s3:ListBucket",
				"s3:CreateBucket",
				"sns:CreateTopic",
				"sns:DeleteTopic",
				"sns:ListTopics",
				"sns:Publish",
				"sns:Subscribe",
				"sns:Unsubscribe",
				"sqs:CreateQueue",
				"sqs:DeleteQueue",
				"sqs:ReceiveMessage",
				"sqs:DeleteMessage",
				"sqs:GetQueueAttributes"
			],
			"Resource": "*"
		}
	]
}


============================
5.  Textract  (role needs permissiont to access s3)

** JC:  better to allow Textract from s3.
**updated s3 above

*** NO:  issue was not having region_name in boto3 




Create the Role for Textract:

Open the IAM console.
In the navigation pane, choose "Roles", then "Create role".
In the "AWS service" group, choose "Textract".
Choose "Next: Permissions".
Attach permissions policies that grant access to the S3 bucket. For full access to S3, you can attach the AmazonS3FullAccess managed policy. However, I recommend creating a custom policy that specifically grants Textract the permissions it needs.
Review the permissions, name the role (e.g., TextractAccessRole), and create the role.
Create a Custom Policy for Specific Access (Optional, but recommended):

From the IAM console, choose "Policies", then "Create policy".
Use the visual editor to grant specific S3 permissions. For Textract, you generally want:
s3:GetObject on the specific bucket and objects Textract should analyze.
s3:PutObject if you want Textract to save the results back to S3.
Review, name the policy (e.g., TextractSpecificS3Access), and create the policy.
Attach this policy to the TextractAccessRole created earlier.
Provide Textract the Role ARN:

When calling the Textract API (e.g., start_document_text_detection or start_document_analysis), you can specify the Role ARN you just created using the RoleArn parameter. This is how Textract knows which role to assume for permissions.

Bucket Permissions:

In some cases, the S3 bucket might have its own set of permissions that prevent access. Ensure that the bucket policy doesn't deny access to the Textract service or the role you've created.

Same Region:

Ensure that the Textract service, S3 bucket, and all related resources are in the same AWS region.

Update the Boto3 Code:

When invoking the Textract API via boto3, you'll need to provide the RoleArn parameter:

python
Copy code
response = textract_client.start_document_text_detection(
    DocumentLocation={'S3Object': {'Bucket': 'your_bucket_name', 'Name': 'your_document_name'}},
    RoleArn='arn:aws:iam::account-id:role/TextractAccessRole'
)
By following these steps, you should provide Textract the necessary permissions to access your S3 bucket and perform the desired operations.


============================
6.  Connect SNS to SQS via subscribe sqs to sns
Step 1: Subscribe SQS to SNS
Navigate to the Amazon SNS Console:

Open the AWS Management Console.
In the search bar, type "SNS" and select "Simple Notification Service" from the dropdown.
Select the SNS Topic:

Click on Topics from the left-hand sidebar.
Find and click on your topic named watchtowersnstopic (or the ARN if you named it differently).
Create a Subscription:

In the topic details page, select Create subscription.
In the Protocol dropdown, select "Amazon SQS".
For Endpoint, enter the ARN of your SQS queue. (You can find this in the SQS console under the "Details" tab of your queue.)
Click Create subscription.


============================
7.  add Textract to cloudwatch

 watchtower_textract_role
 >  add CloudWatchLogsFullAccess

8.  add cloudwatch id to requests:
client_request_token = str(uuid.uuid4())
 
 9.  cloudwatch from boto3 user iam
 ** while its possible with the test_aws.py ...not for normal above.
 {
	"Version": "2012-10-17",
	"Statement": [
		{
			"Effect": "Allow",
			"Action": [
				"textract:*",
				"s3:*",
				"sns:*",
				"sqs:*",
			    "logs:*"
			],
			"Resource": "*"
		}
	]
}

 10.
 To set up logging for Textract:

Enable Logging for Amazon Textract:

Unfortunately, as of my last update (January 2022), there's no direct "Settings" pane within the Textract console for logging like there are for some other services. Instead, logging for Textract would generally be set up via AWS CloudTrail. When you have CloudTrail integrated with CloudWatch Logs, API calls made on Textract are delivered to a CloudWatch Logs log group.

Set Up CloudTrail with CloudWatch Logs:

Navigate to the CloudTrail console.
Choose Trails from the navigation pane.
Either create a new trail or edit an existing one.
Under CloudWatch Logs, configure the log group and role.
Once you've done this, Textract operations will be logged to CloudWatch Logs via CloudTrail.


===============
11.  EXTRA & finale?
- since SNS to SQS works maybe Textract can't publish to SNS.
- watchtower_textract_role --> add sns:Publish permission.

FIXED WITH:
#NOT THIS IS THE USER#     SNS_ROLE_ARN='arn:aws:iam::487320324532:role/ocr_textract_s3_sns_sqs' #<-- SNS ROLE
    SNS_ROLE_ARN='arn:aws:iam::487320324532:role/watchtower_textract_role'
- the ROLE of wathctower_textract_role needs permissions to publish to SNS, cloudwatchlogsfull and maybe amazon textract service    


GREAT CLAUDE DEBUG TIPS:
Here are some things to check to troubleshoot why Textract job completions are not triggering SNS notifications:

Verify the Textract IAM role has the sns:Publish permission. This allows Textract to send messages to SNS.
In the Textract API calls or console, make sure you are specifying the SNS topic ARN and role ARN. This tells Textract which SNS topic to publish to when jobs complete.
Check the SNS topic subscription and confirm the SQS queue is subscribed.
Check the SNS topic policy allows sns.amazonaws.com to publish to the topic.
Enable CloudWatch logging for Textract and check for any errors during job processing.
Use the Textract SDK/CLI to monitor job status and completion. Verify jobs are succeeding before expecting notifications.
Check CloudTrail logs to see the Textract API calls being made. This can help reveal issues in parameters or permissions.
Try running a basic Textract example that publishes to SNS, like from the AWS docs. Get that working end-to-end before customizing.
Make sure all components (Textract, SNS, SQS) are in the same AWS region.
Add debug logging/printing to trace the program flow and output key info like ARNs.
Check for exceptions being caught and suppressed in your code.
The key is tracing each hop - Textract to SNS, SNS to SQS. Get each one working independently before chaining them. This can help narrow down where the breakage is occurring.


"""




"""
ONE_BLOB_SAMPLE_1

FirstCitizens Bank Central Bank Operations - DAC02 P.O. Box 27131 Raleigh, NC 27611-7131 IM 727 14617 MANAGEMENT PROPERTIES INC OPERATING ACCT Your Account(s) At A Glance 27286 VIA INDUSTRIA STE B TEMECULA CA 92590-3751 Checking Balance 204,755.45+ Statement Period: January 1 , 2020 Thru January 31, 2020 Account Number : 001064017308 Basic Business Checking Account Number : 001064017308 Enclosures In Statement: 0 N.ELMA MAIN ST. Beginning Balance 255,964.05+ Statement Period Days 31 3 Deposits 48,921.75+ Average Ledger Balance 242,593.00+ 0 Other Credits 0.00 37 Checks 96,927.02- 4 Other Debits 3,203.33- Monthly Service Charge 0.00 Ending Balance 204,755.45+ Deposits To Your Account Date Amount Date Amount Date Amount 01-07 151.20 01-07 48,619.35 01-28 151.20 Checks Paid From Your Account Check No. Date Amount Check No. Date Amount Check No. Date Amount 01-17 445.61 10124 01-14 639.56 10138 01-16 2,351.94 10059 01-06 2,567.64 10125 01-17 1,935.70 10139 01-15 1,543.30 10107* 01-06 9,494.07 10126 01-16 709.95 10140 01-17 2,576.12 10112* 01-09 3,000.00 10127 01-13 321.88 10141 01-24 4,596.27 10114* 01-07 350.00 10128 01-14 310.05 10143* 01-29 208.87 10116* 01-02 4,155.25 10130* 01-17 852.14 10144 01-28 270.60 10117 01-13 270.87 10131 01-17 12,900.69 10145 01-28 3,000.00 10118 01-09 151.20 10132 01-17 17,722.77 10147* 01-29 151.20 10119 01-06 3,275.75 10133 01-17 4,725.75 10148 01-31 311.42 10120 01-16 120.00 10134 01-17 393.50 10150* 01-30 173.39 10121 01-10 4,475.75 10135 01-17 1,903.22 10151 01-29 3,975.75 10122 01-17 120.00 10136 01-22 2,351.94 10123 01-30 299.12 10137 01-24 4,275.75 *Prior Check Number(s) Not Included or Out of Sequence. Other Debits From Your Account Date Description Amount 01-16 Irs Usataxpymt 7689 50.70 01-16 Irs Usataxpymt 8008 2,236.68 01-17 Employment Devel Edd Eftpmt 0768 910.95 01-31 Paper Statement Fee 5.00 Total 3,203.33 Direct Customer Inquiry Calls To UP FIRST CITIZENS DIRECT Telephone Banking At 1-888-323-4732. Page 1 of 8 FirstCitizens Bank Central Bank Operations - DAC02 P.O. Box 27131 Raleigh, NC 27611-7131 IM 727 14617 MANAGEMENT PROPERTIES INC OPERATING ACCT Your Account(s) At A Glance 27286 VIA INDUSTRIA STE B TEMECULA CA 92590-3751 Checking Balance 204,755.45+ Statement Period: January 1 , 2020 Thru January 31, 2020 Account Number : 001064017308 Basic Business Checking Account Number : 001064017308 Enclosures In Statement: 0 N.ELMA MAIN ST. Beginning Balance 255,964.05+ Statement Period Days 31 3 Deposits 48,921.75+ Average Ledger Balance 242,593.00+ 0 Other Credits 0.00 37 Checks 96,927.02- 4 Other Debits 3,203.33- Monthly Service Charge 0.00 Ending Balance 204,755.45+ Deposits To Your Account Date Amount Date Amount Date Amount 01-07 151.20 01-07 48,619.35 01-28 151.20 Checks Paid From Your Account Check No. Date Amount Check No. Date Amount Check No. Date Amount 01-17 445.61 10124 01-14 639.56 10138 01-16 2,351.94 10059 01-06 2,567.64 10125 01-17 1,935.70 10139 01-15 1,543.30 10107* 01-06 9,494.07 10126 01-16 709.95 10140 01-17 2,576.12 10112* 01-09 3,000.00 10127 01-13 321.88 10141 01-24 4,596.27 10114* 01-07 350.00 10128 01-14 310.05 10143* 01-29 208.87 10116* 01-02 4,155.25 10130* 01-17 852.14 10144 01-28 270.60 10117 01-13 270.87 10131 01-17 12,900.69 10145 01-28 3,000.00 10118 01-09 151.20 10132 01-17 17,722.77 10147* 01-29 151.20 10119 01-06 3,275.75 10133 01-17 4,725.75 10148 01-31 311.42 10120 01-16 120.00 10134 01-17 393.50 10150* 01-30 173.39 10121 01-10 4,475.75 10135 01-17 1,903.22 10151 01-29 3,975.75 10122 01-17 120.00 10136 01-22 2,351.94 10123 01-30 299.12 10137 01-24 4,275.75 *Prior Check Number(s) Not Included or Out of Sequence. Other Debits From Your Account Date Description Amount 01-16 Irs Usataxpymt 7689 50.70 01-16 Irs Usataxpymt 8008 2,236.68 01-17 Employment Devel Edd Eftpmt 0768 910.95 01-31 Paper Statement Fee 5.00 Total 3,203.33 Direct Customer Inquiry Calls To UP FIRST CITIZENS DIRECT Telephone Banking At 1-888-323-4732. Page 1 of 8
"""