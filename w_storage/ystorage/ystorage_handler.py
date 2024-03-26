#!/usr/bin/env python
# encoding: utf-8

import os,sys
import datetime
import random
import json
import time

import base64
import io

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
from key_storage import SqliteDict_Wrap
from key_storage import NestedDict


#**add auto refresh

#1v3# JC Sep 18, 2023  File support
#1v2# JC Jan 17, 2023  Add db size method
#1v1# JC Mar  3, 2022  execnet as option
#1v0# JC Jan 14, 2022  Require py2 to py3 migration option (sqlitedict / pickle restriction on bytes)
#0v9# JC Mar 18, 2021  Return record at db_update
#0v8# JC Dec  3, 2020  Add is_exists
#0v7# JC Oct  6, 2020  Flexible storage mount point
#0v6# JC Dec 10, 2019  Randomize pop
#0v5# JC Dec  4, 2019  Return removed record
#0v4# JC Aug 20, 2019  pre-crawler migration
#0v3# JC Jul 31, 2019  Include update dict
#0v2# JC Apr 26, 2019  Extend from xstorage


def utfy_dict(dic):
    if isinstance(dic,unicode):
        return(dic.encode("utf-8"))
    elif isinstance(dic,dict):
        for key in dic:
            dic[key] = utfy_dict(dic[key])
        return(dic)
    elif isinstance(dic,list):
        new_l = []
        for e in dic:
            new_l.append(utfy_dict(e))
        return(new_l)
    else:
        return(dic)
    
def decode_dict(d):
    ## Dict can't have byte keys
    ## Remove byte keys from dictionary
    #>> need to work with lists too
    ENC='latin1'
    result = {}
    for key, value in d.items():
        if isinstance(key, bytes):
            key = key.decode(ENC)
        if isinstance(value, bytes):
            value = value.decode(ENC)
        elif isinstance(value, dict):
            value = decode_dict(value)
        result.update({key: value})
    return result

class Storage_Helper(object):
    def __init__(self,storage_dir=''):
        #self.db_html=SqliteDict_Wrap(name='html')
        #self.db_meta=SqliteDict_Wrap(name='meta')
        self.dbs={}
        self.default_name='noname'
        self.storage_dir=storage_dir
        return
    
    def init_db(self,name):
        self.dbs[name]=SqliteDict_Wrap(name=name,storage_dir=self.storage_dir)
        self.default_name=name
        return
    
    def db_update(self,idx,the_key,the_value,name=''):
        ## Possibly issues with this?
        ## ** this works at ie dict level (not field level persay)
        #At given index.  Allows the key to be added to the dictionary without overwriting dict

        ##1/  Get dict
        if not name: require=name_stop

        org_dd=self.dbs[name].get_dd(idx)

        org_dd[the_key]=the_value
        org_dd['the_date']=datetime.datetime.now()
        
        print (" UPDATE> "+str(org_dd))

        self.dbs[name].set_dd(idx,org_dd)
        print (" UPDATE2> "+str(org_dd))
        ## Not returned because is entire dd
        return
    
    def db_put(self,idx,the_key,the_value,name=''):
        try:
            test_dump=json.dumps(the_value) ## Check prior to sqlite
        except Exception as e:
            print ("[warning @db_put]: could not json dump at: "+str(idx)+": "+str(e)+" keys: "+str(the_value.keys()))
#D1            print ("[DEBUG FULL DATA]: "+str(the_value.keys()))
#D1            print ("[DEBUG FULL DATA]: "+str(the_value))
#D1            hard=copp_check

        if not name: name=self.default_name
        if not name in self.dbs: self.init_db(name)
        dd=NestedDict()
        dd[the_key]=the_value
        dd['the_date']=datetime.datetime.now()
        self.dbs[name].set_dd(idx,dd)
        return
    
    def db_get_the_date_obj(self,idx,name=''):
        #[ ] not sure why
        dd={}
        the_date=''
        try:
            dd=self.dbs[name].get_dd(idx) ## BEWAY py2 vs py3
        except Exception as e: pass
        if dd:
            the_date=dd.get('the_date','')
            # datetimee.datetime.now back to date obj
            the_date=datetime.datetime.strptime(the_date, '%Y-%m-%d %H:%M:%S.%f')
        return the_date
    
    def db_get(self,idx,the_key,name=''):
        the_value=None
        if not name: name=self.default_name
        if not name in self.dbs:
            the_value=None
        else:
            try:
                dd=self.dbs[name].get_dd(idx) ## BEWAY py2 vs py3
            except Exception as e:
                print ("[bug py2py3 bug]: "+str(e))
                if 'UnicodeDecodeError' in str(e):
                    print ("[error] likely py2 saved trying to get with py3")
                    dd=self.dbs[name].get_dd(idx) ## BEWAY py2 vs py3
                else:
                    dd=self.dbs[name].get_dd(idx) ## BEWAY py2 vs py3
            #print ("TYPE IS: "+str(type(dd)))
            #print ("TYPE IS: "+str(type(dd['json'])))
            #print ("DF1: "+str(dd))
            ## Converting
            #dd=decode_dict(dd)
            ##simple dict# for key, value in dd.items(): dd[key.decode("utf-8")] = value.decode("utf-8")
            #print ("DF1.5: "+str(dd))
            #print ("DF2: "+str(dd))
            the_value=dd.get(the_key,None)
        return the_value
    
    def iter_database(self,name):
        for the_key in self.dbs[name]:
            yield the_key
        return

    def random_choice(self,name):
        the_key=''
        if self.dbs[name]:
            the_key=random.choice(self.dbs[name].keys())
        return the_key

    def db_remove(self,idx,name=''):
        dd=None
        the_value=None
        if not name: name=self.default_name
        if not name in self.dbs:
            the_value=None
        else:
            size_before=len(self.dbs[name])
            dd=self.dbs[name].remove_dd(idx)
            size_after=len(self.dbs[name])
            if size_before==size_after and dd: #and exists
                print ("[error] did not remove at index: "+str(idx)+" size before: "+str(size_before)+" size after: "+str(size_after))
                dd=self.dbs[name].get_dd(idx)
                print ("RAW RECORD: "+str(dd))
                print ("New fun exists: "+str(self.is_exists(idx,name=name)))
                #stopp=no_removal
        return dd
    
    def is_exists(self,idx,name=''):
        exists=False
        if not name: name=self.default_name
        if idx in self.dbs[name]: exists=True
        return exists
    
    def size(self,name):
        return len(self.dbs[name])

    def add_file(self,idx,full_path='',content_base64='',meta={},name=''):
        #base64 (33% premium, other option is sqlite blob field)
        dd=meta  #Extra options

        if full_path:
            if not os.path.exists(full_path):
                raise Exception("File does not exist: "+str(full_path))
            dd['base64']=file_to_base64(full_path)
        elif content_base64:
            dd['base64']=content_base64
        else:
            raise Exception("Must provide either full_path or content_base64")

        dd['filename']=os.path.basename(full_path)
        dd['full_path']=full_path  #More for meta purpose

        self.db_put(idx,'file',dd,name=name)

        file_size=os.path.getsize(full_path)

        return file_size

    def get_file(self,idx,name=''):
        meta={}
        dd=self.db_get(idx,'file',name=name)
        if dd:
            base64_str=dd.pop('base64','')
            meta=dd
            #content = file_pointer.read()
            return base64_to_filepointer(base64_str),meta
        else:
            return None,meta


def file_to_base64(filepath):
    """Convert a file to its Base64 representation."""
    with open(filepath, 'rb') as file:
        file_content = file.read()
    return base64.b64encode(file_content).decode('utf-8')

def base64_to_filepointer(base64_str):
    """Convert a Base64 string to a file-like object."""
    binary_content = base64.b64decode(base64_str)
    return io.BytesIO(binary_content)

def interface_get(id,the_key,name,storage_dir,SH):
    if not SH:
        SH=Storage_Helper(storage_dir=storage_dir)
        SH.init_db(name)
    return SH.db_get(id,the_key,name=name) #No serial,SH

def interface_put(id,the_key,the_value,name,storage_dir,SH):
    if not SH:
        SH=Storage_Helper(storage_dir=storage_dir)
        SH.init_db(name)
    return SH.db_put(id,the_key,the_value,name=name)#No return unserializable,SH

def interface_test(*args,**kwargs):
    storage_dir=LOCAL_PATH+"../ystorage_dbs"
    SH=Storage_Helper(storage_dir=storage_dir)
    return
    

def test_storage():
    # Jan 14, 2022 Error loading py2 values from py3 encoding issues
    from a2py3 import call_python_version

    sys.path.insert(0,LOCAL_PATH+"../../") #mod_storeall key here
    id='ChIJ_______skogR0YwYKuifo-I'
    storage_dir=LOCAL_PATH+"../ystorage_dbs"
    the_key='json'
    table='ccms'
    SH=''
    dd=interface_get(id,the_key,table,storage_dir,SH)
    print ("OK: "+str(dd))
    
    ## Put this via py3!
    new_id='delthis1'
    dd['id']=new_id
    
    id=new_id
    
    ## NORMAL
    SH=''
    
    if False:
        dd,SH=interface_put(id,the_key,the_value,table,storage_dir,SH)
        
    ## PATCH SERIALIZE PANDAS
    #depre# t = pd.tslib.Timestamp('2016-03-03 00:00:00')
    #t = pd.Timestamp('2016-03-03 00:00:00')
    #dd['updated']=dd['updated'].to_pydatetime() #pandas to py

#    dd['updated']=dd['updated'].to_pydatetime() #pandas to py
    dd['updated']=str(dd['updated'].to_pydatetime()) #pandas to py
        
    the_value=dd

    SH='' #Can't serialize
    argumentlist=[id,the_key,the_value,table,storage_dir,SH]

    print ("ARGS: "+str(argumentlist))
    print ("[debug] calling python 3 -- serialize first I think...")

    results=call_python_version('3','ystorage_handler','interface_put',argumentlist)
    #results=call_python_version('3','ystorage_handler','interface_put',argumentlist)
    print ("done put with 3")
    print ("-----------------")
    
    ## Try to get with 3
    argumentlist=[id,the_key,table,storage_dir,SH]
    results=call_python_version('3','ystorage_handler','interface_get',argumentlist)
    print ("GOT RE: "+str(results))

    #** test
#    if not json.dumps(results)==json.dumps(the_value):
#        print ("NOT EQUAL STOP")
#        stopp=not_got
    
    print ("NOW...")

#    dd,SH=interface_get(id,the_key,table,storage_dir,SH)
#    print ("result get with 2 from saved 3: "+str(dd))

    print ("DONE")
    return


def migrate_py2_to_py3():
    ## watch must be serializeable
    ## Ensure target python has required libraries
    import execnet  #For py2 to py3 conversion


    sys.path.insert(0,LOCAL_PATH+"../../") #mod_storeall key here
    
    python_path="C:/Users/jon/Envs/mitm_py36/Scripts/python"
    
    
    #group = execnet.Group()
    #gw      = group.makegateway("popen//python="+python_path)
    gw      = execnet.makegateway("popen//python="+python_path)

    module='ystorage_handler'
    function='interface_put'

    channel = gw.remote_exec("""
        from %s import %s as the_function
        channel.send(the_function(*channel.receive()))
    """ % (module, function))
    
    
    storage_dir=LOCAL_PATH+"../ystorage_dbs"
    name='ccms'
    the_key='json'

    SH=Storage_Helper(storage_dir=storage_dir)
    SH.init_db(name)
    
    do_continue=False
    c=0
    for idx in SH.iter_database(name):
        c+=1
        if idx=='edcc150f6f0411ec9f3e2079185ef8c0': do_continue=True
        if not do_continue:continue
        
        if not c%10 or c<100: print ("[debug] migratin 2py3 for: "+str(idx))

        try:dd=SH.db_get(idx,the_key,name=name)
        except Exception as e:
            if 'unsupported pickle' in str(e):  #Already py3
                continue
            else:
                print ("[error] stop: "+str(e))
                dd=SH.db_get(idx,the_key,name=name)

        if not dd: stopp=no_dd

        if not dd: stopp=no_dd
        
        ## Transform to serializeable
        if dd.get('updated',''):
            dd['updated']=str(dd['updated'].to_pydatetime()) #pandas to py
        
        argumentlist=[idx,the_key,dd,name,storage_dir,'']
        
        #print ("FO: "+str(dd))
        #test=json.dumps(dd)

        ## BRING LOCALLY!
        if False:
            from a2py3 import call_python_version
            results=call_python_version_local('3','ystorage_handler','interface_put',argumentlist)
        else:
            channel.send(argumentlist)
            
#            channel.waitclose(1)
#            channel.close()
            
            #channel.receive()
            ## Recreate because exits every ~4 otherwise
            channel = gw.remote_exec("""
                from %s import %s as the_function
                channel.send(the_function(*channel.receive()))
            """ % (module, function))

    #group.terminate(timeout=1.0)
    return

def repair_corrupt_db():
    
    db_dir=LOCAL_PATH+"../../w_datasets"
    db_name='cache_llm'
    record_name='record'
    
    Storage=Storage_Helper(storage_dir=db_dir)
    Storage.init_db(db_name)
    c=0
    for idx in Storage.iter_database(db_name):
        c+=1
        dd=Storage.db_get(idx,record_name,name=db_name)
    print ("COUNT: "+str(c))
    
    """
    sqlite3 your_database.db
Dump the Database Contents: Use the .dump command to export the entire contents of the database to a SQL text file. This command tries to read and export as much data as possible, even from a corrupted database.

.output dump.sql
.dump
.exit

This will create a file named dump.sql in the current directory containing the SQL commands to recreate the database.

Create a New Database: Now, create a new, clean database file and import the dump.sql file into it. This can be done with the following commands:

sqlite3 new_database.db < dump.sql
**if it didn't work ensure the .sql file ends with "COMMIT;"

    """
    return

if __name__=='__main__':
    branches=['upgrade_py2_py3']
    branches=['test_storage']
    branches=['migrate_py2_to_py3']
    branches=['repair_corrupt_db']

    for b in branches:
        globals()[b]()
    print ("Done.")



