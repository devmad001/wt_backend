import os,sys

import re
import unittest

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"

#0v1# JC Apr 21, 2023



def run_print_return_hello_world():
    print ("Hello world")
    return {'hello':'world'}

def run_print_return_hello_world_args(name):
    print ("Hello world arg: "+str(name))
    return {'hello':'world arg '+str(name)}

def run_print_return_hello_world_kwargs(**kwargs):
    if kwargs:
        print ("Hello world kwargs: "+str(kwargs))
    return {'hello':'world kwargs '+str(kwargs)}

def run_print_return_hello_world_args_kwargs(*args, **kwargs):
    if kwargs:
        print ("Hello world args: "+str(args)+" kwargs: "+str(kwargs))
    return {'hello':'world args: "+str(args)+" kwargs '+str(kwargs)}

if __name__ == '__main__':
    pass
        
        
        
