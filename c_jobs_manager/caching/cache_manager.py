
import os
import sys
import configparser as ConfigParser
from db_storage import DbStorage
from mem_storage import MemStorage
from file_storage import FileStorage

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")

Config = ConfigParser.ConfigParser()
Config.read(LOCAL_PATH+"db_config.ini")
Config.read(LOCAL_PATH+"db_config.ini")
config={}
config['ip']=Config.get('mysql','ip')
config['username']=Config.get('mysql','username')
config['password']=Config.get('mysql','password')

dbname='wtengine'
DATABASE_URL = "mysql+mysqldb://"+config['username']+":"+config['password']+"@"+config['ip']+"/"+dbname

class CacheManager(object):
    # Shared auto-increment generator as a class attribute
    unique_number_generator = None

    def __init__(self) -> None:
        self.db_storage = DbStorage(database_url=DATABASE_URL)
        self.file_storage = FileStorage()
        self.mem_storage = MemStorage()

        if CacheManager.unique_number_generator is None:
            CacheManager.unique_number_generator = self.auto_increment()

    @staticmethod
    def auto_increment(start=1):
        """Static method generator for auto-incrementing integers."""
        counter = start
        while True:
            yield counter
            counter += 1

    def generate_unique_name(self, job_id, name):
        unique_number = next(CacheManager.unique_number_generator)  # Use the shared generator
        return f"{job_id}-{name}-{unique_number}"

    def db_get(self, job_id, name):
        return self.db_storage.get_data(job_id, name)

    def db_set(self, job_id, name, data):
        return self.db_storage.set_data(job_id, name, data)
    
    def db_delete(self, job_id, name):
        return self.db_storage.delete(job_id, name)

    def file_get(self, job_id, name):
        data = self.db_get(job_id, name)
        if data is None:
            return None
        if not data.contains("s3_object_name"):
            return None
        return self.file_storage.read_file(data["s3_object_name"])

    def file_set(self, job_id, full_path):
        filename=os.path.basename(full_path)
        name = self.generate_unique_name(job_id, filename)
        try:
            with open(full_path, 'rb')as file:
                content = file.read()
            self.file_storage.save_file(name, content)
            data = {
                "filename": filename,
                "full_path": full_path,
                "s3_object_name": name,
            }
            return self.db_set(job_id, name, data)
        except Exception as e:
            return False

    def file_delete(self, job_id, name):
        data = self.db_get(job_id, name)
        if data is None:
            return False
        if not data.contains("s3_object_name"):
            return False
        return self.file_storage.delete_file(data["s3_object_name"])

    def mem_get(self, key):
        return self.mem_storage.get_value(key)
    
    def mem_set(self, key, value):
        self.mem_storage.set_value(key, value)

    def mem_delete(self, key):
        self.mem_storage.delete_value(key)
