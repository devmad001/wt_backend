import os,sys

import re
import unittest


from mod_execute import The_Execute_Command

#0v1# JC Apr  2, 2020  

#UNITTEST
#https://docs.python.org/2/library/unittest.html
#- Use widget template to initialize once

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"


class SimpleClassInitiator(unittest.TestCase):
    def setUp(self):
        self.Executor=The_Execute_Command()
        return

    def tearDown(self):
        self.Executor=None


class TestClassess(SimpleClassInitiator):

    def aatest_spawn_background_then_kill(self):
        a=nono
        wd=LOCAL_PATH+"utils"
        script_py="bot_sleep.py"
        c=0
        for line in self.Executor.run_python_iter(script_py,cwd=wd,allow_multiple_instances=False,kill_if_running=True,background=True,spawn=True):
            c+=1
            pass
        
        print ("OK c: "+str(c))
        return

    def test_kill_regex(self):
        regex='test_execute'
        is_running=self.Executor.is_running(regex)
        print ("IS running: "+str(is_running))
        self.assertTrue(is_running)
        return

    def test_run_command_iterx(self):
        print ("[] jc: bring in other loblaw exe thing?")
        cmd="dir" #23
        cmd="wmic path win32_process get name, commandline"
        c=0
#ok        for line in self.Executor.run_command_iter_org(cmd):
        for line in self.Executor.run_command_iter(cmd):
            c+=1
        print ("Line count: "+str(c))

        self.assertTrue(c>2)
        return
    
        



if __name__ == '__main__':
    unittest.main()
        
        
        