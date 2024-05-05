import os
import re
import boto3
import json
from botocore.exceptions import ClientError


LOCAL_DIR = os.path.abspath(os.path.dirname(__file__))+"/"


class NestedDict(dict):
    def __getitem__(self, key):
        if key in self: return self.get(key)
        return self.setdefault(key, NestedDict())


class S3Dict:
    def __init__(self, bucket_name, root_dir='w_datasets', storage_dir='storage', name='default'):
        print(storage_dir)
        storage_dir = storage_dir.replace('\\', '/')
        storage_dir = re.sub(r'^([a-zA-Z]):/', r'/\1/', storage_dir)
        parts = re.split(root_dir, storage_dir)

        if len(parts) > 1:
            storage_dir = parts[-1]

        while storage_dir.endswith("/"):
            storage_dir = storage_dir[:-1]

        if storage_dir.startswith("/"):
            storage_dir = storage_dir[1:]

        storage_dir = root_dir + "/" + storage_dir + "/" + name
        storage_dir = storage_dir.replace("//", "/")
        self.key_prefix = storage_dir
        self.bucket_name = bucket_name
        self.s3 = boto3.client('s3')

        print(self)

    def __str__(self):
        return f"S3Dict(bucket_name={self.bucket_name}, key_prefix={self.key_prefix}"

    def __getitem__(self, key):
        full_key = f"{self.key_prefix}/{key}"
        try:
            response = self.s3.get_object(Bucket=self.bucket_name, Key=full_key)
            value_str = response['Body'].read().decode('utf-8')
            value = json.loads(value_str)
            return value
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchKey':
                raise KeyError(full_key)
            else:
                raise

    def __setitem__(self, key, value):
        value_str = json.dumps(value)
        value_bytes = value_str.encode('utf-8')
        full_key = f"{self.key_prefix}/{key}"
        self.s3.put_object(Bucket=self.bucket_name, Key=full_key, Body=value_bytes)

    def __delitem__(self, key):
        full_key = f"{self.key_prefix}/{key}"
        self.s3.delete_object(Bucket=self.bucket_name, Key=full_key)

    def __contains__(self, key):
        full_key = f"{self.key_prefix}/{key}"
        try:
            self.s3.head_object(Bucket=self.bucket_name, Key=full_key)
            return True
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                return False
            else:
                raise

    def keys(self):
        prefix = f"{self.key_prefix}/"
        response = self.s3.list_objects_v2(Bucket=self.bucket_name, Prefix=prefix)
        return [item['Key'][len(prefix):] for item in response.get('Contents', []) if item['Key'] != prefix]

    def pop(self, key, default=None):
        try:
            value = self.__getitem__(key)
            self.__delitem__(key)
            return value
        except KeyError:
            if default is None:
                raise
            return default

    def get_dd(self,key):
        if key in self:
            return self[key]
        else:
            return NestedDict()

    def set_dd(self,key,dd):
        self[key]=dd

    def remove_dd(self,key):
        dd={}
        if key in self:
            dd=self.pop(key)
        return dd

def dev_storage1():
    S3Dict(bucket_name="b", storage_dir="/w_datasets")
    S3Dict(bucket_name="b", storage_dir="/w_datasets/")
    S3Dict(bucket_name="b", storage_dir="/unix/absolute/path/../w_datasets")
    S3Dict(bucket_name="b", storage_dir="/unix/absolute/path/../w_datasets/")
    S3Dict(bucket_name="b", storage_dir="/unix/absolute/path/../w_datasets/sub_dir")
    S3Dict(bucket_name="b", storage_dir="/unix/absolute/path")
    S3Dict(bucket_name="b", storage_dir="/unix/absolute/path/")
    S3Dict(bucket_name="b", storage_dir="unix/path")
    S3Dict(bucket_name="b", storage_dir="unix/path/")
    S3Dict(bucket_name="b", storage_dir="unix/path/", root_dir="other_root_dir")
    S3Dict(bucket_name="b", storage_dir="unix/path/", name="other_name")
    S3Dict(bucket_name="b", storage_dir="unix/path/../w_datasets")
    S3Dict(bucket_name="b", storage_dir="unix/path/../w_datasets/")
    S3Dict(bucket_name="b", storage_dir="c:\\windows\\absolute\\path\\w_datasets")
    S3Dict(bucket_name="b", storage_dir="d:\\windows\\absolute\\path\\w_datasets\\")
    S3Dict(bucket_name="b", storage_dir="d:\\windows\\absolute\\path\\w_datasets\\subr_dir")
    S3Dict(bucket_name="b", storage_dir="window\\path\\w_datasets")
    S3Dict(bucket_name="b", storage_dir="window\\path\\w_datasets\\")
    S3Dict(bucket_name="b", storage_dir="c:\\windows\\absolute\\path")
    S3Dict(bucket_name="b", storage_dir="c:\\windows\\absolute\\path\\")
    S3Dict(bucket_name="b", storage_dir="window\\path")
    S3Dict(bucket_name="b", storage_dir="window\\path\\")

def dev_storage2():
    DB=S3Dict(bucket_name="s3-migration-test-1")
    print ("ok2")
    dd=DB.get_dd('jon1')
    dd['this']['world']=True
    DB.set_dd('jon1',dd)
    dd=DB.get_dd('jon1')
    print ("GOT: "+str(dd))
    return

if __name__=='__main__':
    branches=['dev_storage1']
    branches=['dev_storage2']
    for b in branches:
        globals()[b]()
