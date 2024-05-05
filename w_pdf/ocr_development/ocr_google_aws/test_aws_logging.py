import os
import boto3
import time

# Explicit AWS credentials (OPTIONAL: Only if not using environment variables or AWS CLI configuration)
AWS_ACCESS_KEY = 'AXXXXXXXXXXXXXXXXXXXXX'
AWS_SECRET_KEY = 'a6oaXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX/hj'
os.environ["AWS_ACCESS_KEY_ID"] = AWS_ACCESS_KEY
os.environ["AWS_SECRET_ACCESS_KEY"] = AWS_SECRET_KEY

REGION = 'us-east-2'

# Creating a logs client
logs_client = boto3.client(
    'logs', 
    region_name=REGION,
    aws_access_key_id=AWS_ACCESS_KEY, 
    aws_secret_access_key=AWS_SECRET_KEY
)

LOG_GROUP_NAME = 'TestLogGroupName'
LOG_STREAM_NAME = 'TestLogStreamName'

try:
    # Create Log Group
    logs_client.create_log_group(logGroupName=LOG_GROUP_NAME)
    print(f"Log group {LOG_GROUP_NAME} created.")
except logs_client.exceptions.ResourceAlreadyExistsException:
    print(f"Log group {LOG_GROUP_NAME} already exists.")

try:
    # Create Log Stream within the Log Group
    logs_client.create_log_stream(logGroupName=LOG_GROUP_NAME, logStreamName=LOG_STREAM_NAME)
    print(f"Log stream {LOG_STREAM_NAME} created within {LOG_GROUP_NAME}.")
except logs_client.exceptions.ResourceAlreadyExistsException:
    print(f"Log stream {LOG_STREAM_NAME} already exists within {LOG_GROUP_NAME}.")

# Push a sample log event
timestamp = int(time.time() * 1000)  # Current time in milliseconds
response = logs_client.put_log_events(
    logGroupName=LOG_GROUP_NAME,
    logStreamName=LOG_STREAM_NAME,
    logEvents=[{
        'timestamp': timestamp,
        'message': 'Hello, this is a test log message from boto3!'
    }]
)

print("Log event sent. Check AWS CloudWatch for the message!")
