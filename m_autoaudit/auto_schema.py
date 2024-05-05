import os
import sys
import codecs
import json
import copy
import re
import time
import datetime


LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")


#from get_logger import setup_logging
#logging=setup_logging()



#0v1# JC  Mar  7, 2023  Auto schema audit


"""
    SCHEMA AUDIT + TRANSFORMER
    - Stand-alone field validation
    *recall, auto_auditor is bigger picture
    
    - pydantic models preferred where formalization required
        - recall: @root_validation or @validation

"""

## Flexible data model for QA
class NestedDict(dict):
    def __getitem__(self, key):
        if key in self: return self.get(key)
        return self.setdefault(key, NestedDict())


class AutoSchema:
    """
        data:  raw data (usually doc_meta + records pieces)
        qa:    field-level evaluation metrics ie: {'temperature':{'quality':0.6,'reason':'out of range'}}
                - watch sync'ing qa entry with data field
        context: non data but information that helps resolution
    """

    def __init__(self):
        self.data_org={}
        self.data={}
        self.qa=NestedDict()
        self.context={}
        self.report={}
        return
    
    def set_data_context(self,data,context):
        self.data_org=copy.deepcopy(data)
        self.data=copy.deepcopy(data)
        self.context=context
        return
    
    def load_schema(self):
        return {}
    
    def run_check(self):
        ## Data at doc_data level (ie/ statement date range or balance total)
        ## Data at records level  (ie/ transactions)
        
        ## No transforms here

        return
    
    def run_normalize(self):
        ## Modify data to fit schema if necessary
        
        ##LOCAL FOR DEV TEST
        for field in self.data:
            if field=='temperature':
                if self.data[field]<-200:
                    self.data[field]=-200
                    self.qa[field]['quality']=0.6
                    self.qa[field]['quality_reason']='out of range'  #ideally list but can roll up later
                if self.data[field]>200:
                    self.data[field]=200

        return
    
    def output_data(self):
        return self.data
    
    def get_report(self):
        ## Assemble data AND QA report
        
        report={}
        report['data']=self.data
        report['qa']=self.qa

        return report


def dev1():

    ## Simulate given

    dd={}
    dd['temperature']=-300
    
    context={}
    context['case_id']='65cd06669b6ff316a77a1d21'

    AS=AutoSchema()
    AS.set_data_context(dd,context)
    schema=AS.load_schema()
    
    AS.run_check()
    AS.run_normalize()
    AS.run_check()
    report=AS.get_report()
    data=AS.output_data()

    print ("GOT: "+str(data))
    print ("REPORT: "+str(report))
    
    
    return

if __name__=='__main__':
    branches=['dev1']
    for b in branches:
        globals()[b]()





