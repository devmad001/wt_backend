import boto3

class S3Wrapper:
    def __init__(self, bucket_name):
        self.bucket_name = bucket_name
        self.s3 = boto3.client('s3')

    def upload_fileobj(self, file_obj, object_name):
        self.s3.upload_fileobj(file_obj, self.bucket_name, object_name)

    def get_file_content(self, object_name):
        response = self.s3.get_object(Bucket=self.bucket_name, Key=object_name)
        return response['Body'].read()

    def delete_file(self, object_name):
        self.s3.delete_object(Bucket=self.bucket_name, Key=object_name)
