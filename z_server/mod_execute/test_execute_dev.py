import os,sys

import re
import unittest


from mod_execute import The_Execute_Command

#0v1# JC Apr 21, 2023

#UNITTEST
#https://docs.python.org/2/library/unittest.html
#- Use widget template to initialize once


LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"



def dev_mod_execute_parameters():
    EC=The_Execute_Command()

    workon=''

    b=['direct']
    b=['direct','kwargs','args','argskwargs']

    got=''
    if 'direct' in b:
        got=EC.call_venv_function(workon,'test_script1.py','run_print_return_hello_world')
        if not got:
            raise Exception("No direct")

    if 'kwargs' in b:
        kk={'name':'joe'}
        got=EC.call_venv_function(workon,'test_script1.py','run_print_return_hello_world_kwargs',kwargs=kk)
        print ("Got: "+str(got))
        if not got:
            raise Exception("No kwargs")

    if 'args' in b:
        args=['joe']
        got=EC.call_venv_function(workon,'test_script1.py','run_print_return_hello_world_args',args=args)
        print ("Got: "+str(got))
        if not got:
            raise Exception("No args")

    if 'argskwargs' in b:
        args=['joe1']
        kwargs={'name':'joe'}
        got=EC.call_venv_function(workon,'test_script1.py','run_print_return_hello_world_args_kwargs',args=args,kwargs=kwargs)
        print ("Got: "+str(got))
        if not got:
            raise Exception("No argskwargs")

    return


if __name__ == '__main__':
    dev_mod_execute_parameters()
        
        
        