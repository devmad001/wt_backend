from s3_wrapper import S3Wrapper

class FileStorage:
    def __init__(self):
        self.s3 = S3Wrapper()

    def save_file(self, object_name, content):
        try:
            self.s3.upload_fileobj(content, object_name)
            return object_name
        except Exception as e:
            print(f"Failed to save file {object_name} to S3: {e}")
            return None

    def read_file(self, object_name):
        try:
            return self.s3.get_file_content(object_name)
        except Exception as e:
            print(f"Failed to read file {object_name} from S3: {e}")
            return None

    def delete_file(self, object_name):
        try:
            self.s3.delete_file(object_name)
            return True
        except Exception as e:
            print(f"Failed to delete file {object_name} from S3: {e}")
            return False
