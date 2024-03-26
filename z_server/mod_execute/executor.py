from __future__ import division
import sys
import re
import subprocess as sub
import os
import pickle
import time
import traceback
import io

from tempfile import TemporaryFile
from time import sleep
from subprocess import Popen, STDOUT
import copy

try: import psutil
except: pass

import signal
from contextlib import contextmanager #For timeouts

import multiprocessing.pool
import functools

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
from nbstreamreader import NonBlockingStreamReader as NBSR #nbstreamreader.py

#0v8#
from threading  import Thread
try:
    from queue import Queue, Empty
except ImportError:
    from Queue import Queue, Empty  # python 2.x

if sys.version_info >= (3,3,0):
    PY3=True
else:
    PY3=False
    
ON_WINDOWS=False
if os.name=='nt': ON_WINDOWS=True

#print ("[] if calling python tell it NOT to buffer the output")
#proc = subprocess.Popen(['python','-u', 'fake_utility.py'],stdout=subprocess.PIPE)

#1v4# JC Dec 13, 2023   Fix on windows check
#1v3# JC Apr 17, 2023   Use
#1v2# JC Apr  5, 2023   LOCAL_PATH import
#1v1# JC Apr  4, 2020   Bug at thread not exiting via timeout1 threads
#1v0# JC Apr  4, 2020   migrate to mod_execute
#0v9# JC Jan 10, 2020   Use in mod_gpu
#0v9# JC Jul 23, 2019   Fix not returning (was NOT yielding)
#0v8# JC May 15, 2019   Blocking error fix options:
#- try new: https://stackoverflow.com/questions/375427/non-blocking-read-on-a-subprocess-pipe-in-python/4896288#4896288

#0v7# JC May  5, 2019   Blocking error fix options:
#- http://eyalarubas.com/python-subproc-nonblock.html
#- https://stackoverflow.com/questions/20503671/python-c-program-subprocess-hangs-at-for-line-in-iter


#0v6# JC Aug 14, 2018   Use in new mod_proxy -- consider keeping this as base
#0v5# JC June 1, 2018   Allow workon
#0v4# JC May 22, 2018   Bring into exe module
#0v3# JC Jan 21, 2018   Use in blockchain
#0v2# JC Sept 26, 2017  Extend to cron
#0v1# JC Aug 10, 2017   Branch out of performance.py

#TODO:
#- upgrade is_running for windows like mod_truthkit or cron where does
#cmd="wmic path win32_process get name, commandline | FINDSTR python | FINDSTR .py"


LOCAL_DIR = os.path.abspath(os.path.dirname(__file__))

@contextmanager
def timeout(time):
    # Register a function to raise a TimeoutError on the signal.
    signal.signal(signal.SIGALRM, raise_timeout)
    # Schedule the signal to be sent after ``time``.
    signal.alarm(time)

    try:
        yield
    except TimeoutError:
        pass
    finally:
        # Unregister the signal so it won't be triggered
        # if the timeout is not reached.
        signal.signal(signal.SIGALRM, signal.SIG_IGN)
def raise_timeout(signum, frame):
    raise TimeoutError



def timeout1(max_timeout):
    #1v1#  Threads not closing on exit
#    print ("*** this uses memory on each browser driver ***")
    """Timeout decorator, parameter in seconds."""
    def timeout_decorator(item):
        """Wrap the original function."""
        @functools.wraps(item)
        def func_wrapper(*args, **kwargs):
            """Closure for function."""
            print ("** THIS TIMEOUT CAUSES ORPHANED THREADS")
            print ("** possibly causes missed stdout?")
            pool = multiprocessing.pool.ThreadPool(processes=1)
            async_result = pool.apply_async(item, args, kwargs)
            # raises a TimeoutError if execution exceeds max_timeout
            return async_result.get(max_timeout)
        return func_wrapper
    return timeout_decorator

#causes orphaned threads#  @timeout1(30)
#@timeout1(5)
def buffer_patch_timeout(stdout):
    #1v1# Not exiting
    #line = stdout.readline() #**error on buffer blocking
    line = stdout.readline().decode('utf-8') #?py3 does bytes-like object? -- will hang if full??
    return line

def enqueue_output(out, queue):
#    for line in fp.readline():
#        print ("YES: "+str(line))
#        queue.put(line)
#    fp.close()
    if out is not None:
        for line in iter(out.readline, b''):
            queue.put(line)
        out.close()


class Execute_Command(object):
    def __init__(self):
#        self.Windows=Windows_Computer()
        return

    def get_workon_directory(self,workon):
        workon_dir='C:/Users/jon/Envs/'+workon+'/Scripts'
        if not os.path.exists(workon_dir):a=missing_workon
        return workon_dir
    
    def run_windows_background(self,cmd,cwd,workon='',visible=False,terminate_on_complete=True):
        ## 1v0   Visible output always??

        #Options:
        #- spawn=True   # won't wait for exit
        
        
        #If using workon, clear PYTHONPATH before running ENV or it consumes it too
        
        #PERFORMANCE:
        #- for python:
        #  - use pythonw over python.exe
        
        #OPTIONS:
        #cmd /k:  Is used if not calling python directly

        #CMD /C    Run Command and then terminate
        #CMD /K    Run Command and then return to the CMD prompt.
          
        cwd=cwd
        org_cwd=os.getcwd()
        cmd_title='Running: '+cmd
        
        if not os.path.exists(cwd):a=missing_cwd

        command=''
        command+='START '

        if not visible:
            command+='/B ' #not background...just don't show

        command+='"'+cmd_title+'" '
        if terminate_on_complete:
            command+='cmd /c "' #run command  then terminate
        else:
            command+='cmd /k "' #run command  then return to cmd prompt

        if workon:
            workon_dir=self.get_workon_directory(workon)
            command+='set PYTHONPATH= & ' #Clear PYTHONPATH ** FOR workon to initialize
            command+='cd /d '+workon_dir+' & activate &'  #start workon
        command+='cd /d '+cwd+' & '
        command+=cmd
        
        print ("<run>: "+command)
        os.system(command)
        os.chdir(org_cwd)
        return

    def lines2lines(self,lines):
        #py3
        liness=[]
        for line in lines:
            try:
                liness+=[line.decode('utf-8')]
            except:
                try:
                    liness+=[str(line)]
                except:
                    liness+=[line]
        return liness

    def run_command_iter(self,cmd,echo=False,python_path='',cwd='',background=False,spawn=False,workon='',verbose=False,branch_run_fast=False):
        global PY3
        #>  branch_run_fast:  if fails too soon may miss output!

        ## BUG:  JC  Jan 10, 2020  Not always grabbing ALL output?
        ## BUG:  JC  Apr  2, 2020  Correct see test_execute
        
        #Affects py3 and py2
        
        #maybe fix:  
        #https://www.saltycrane.com/blog/2009/10/how-capture-stdout-in-real-time-python/
        #https://zaiste.net/realtime_output_from_shell_command_in_python/
        #https://www.endpoint.com/blog/2015/01/28/getting-realtime-output-using-python
        #https://stackoverflow.com/questions/803265/getting-realtime-output-using-subprocess
        
        
        

        """
           Standard subprocess that outputs stdout as iterator
           
           when?:
           out, err = process.communicate()  # The output and error streams. 
           
           BACKGROUND OPTIONS:
           a) run in background but don't detache: close_fds
           b) run in background and detache process:
           
           "spawn"== run as own process AND PERSIST
        """
        #p = os.popen4(command,"r")

#?        print ("[] add trial buffer mod")

        if echo:
            if cwd:
                print ("cd> "+cwd)
            print ("Running> "+str(cmd))
            if background:
                print ("Running in background. Same process, output below:")
            if spawn:
                print ("Running in background. Separate process")
            else:
                print ("stdout below:")
        
        if spawn:
            self.run_windows_background(cmd,cwd)
        else:
            if background:
                shell=False
                close_fds=True
                sub_pipe=None
                if detach_process:
                    creationflags=0x00000008
            else:
                shell=True
                close_fds=False
                sub_pipe=sub.PIPE
                creationflags=0
            if not cwd:cwd=None
                
            if python_path:
                env = os.environ.copy()
                env["PYTHONPATH"] = python_path+" "+env["PATH"]
            else:
                env=None
    
            if workon:
                workon_dir=self.get_workon_directory(workon)
                #env = os.environ.copy()
                #env["PYTHONPATH"] = python_path+" "+env["PATH"]
                command=''
                command+='set PYTHONPATH=c:\jon & ' #Clear PYTHONPATH ** FOR workon to initialize
                                                    #Also allow for supposedly pythonpath friendly workon items ie/ truthkit
                command+='cd /d '+workon_dir+' & activate & '  #start workon
                if cwd:
                    command+='cd /d '+cwd+' & '
                #Add direct link to python if python path not set
                #ok no #cmd=re.sub(r'python ',workon_dir+"/python ",cmd,flags=re.I)
                command=command+cmd
            else:
                command=''
                command=command+cmd

#D            if True: print ("[debug] FINAL CMD: "+str(command))


            #A closer inspection of the subprocess.Popen docs revealed a warning "Note: The data read is buffered in memory, so do not use this method if the data size is large or unlimited."
            #Apparently, that warning actually means "Note: if there's any chance that the data read will be more than a couple pages, this will deadlock your code." What was happening was that the memory buffer was a fixed size. When it filled up, it simply stopped letting the child process write to it. The child would then sit and patiently wait to be able to write the rest of its output.
            #Instead of setting stdout and stderr to PIPE, they need to be given proper file (or unix pipe) objects that will accept a reasonable amount of data. (A further hint for anyone who found this page because they encountered the same problem and are looking for a fix: Popen() needs real file objects with fileno() support so StringIO-type fake file objects won't work; [tempfile.TemporaryFile] is your friend).

            #https://stackoverflow.com/questions/38374063/python-can-we-use-tempfile-with-subprocess-to-get-non-buffering-live-output-in-p
            # the temp file will be automatically cleaned up using context manager

            #NO EFFECT  shell=False
            if verbose:
                print ("[d5]  Yes, using temp file...")

            with TemporaryFile(mode='w+',encoding='utf-8') if PY3 else TemporaryFile() as output: #bufsize=xxx sub_pipe=tempfile.NamedTemporaryFile(mode='w+b') #<-- open file
                
                if branch_run_fast:
                    USE_OUTPUT_MISSES_FAST=True
                else:
                    USE_OUTPUT_MISSES_FAST=False

                    #ok# suby = Popen(command, stdout=output, stderr=STDOUT, shell=True)
                    #suby = Popen(command, stdout=output, stderr=output, shell=shell,env=env,cwd=cwd,close_fds=close_fds,creationflags=creationflags)
                
                lines=[]
                last_read_where=0
                start_time=time.time()

                if USE_OUTPUT_MISSES_FAST:
                    suby = Popen(command, stdout=output, stderr=output, shell=shell,env=env,cwd=cwd,close_fds=close_fds,creationflags=creationflags)
                                    #JON NOTE:
                    #- misses some of the first few lines sometimes

                    # sub.poll returns None until the subprocess ends,
                    # it will then return the exit code, hopefully 0 ;)
                    while suby.poll() is None:
                        lines = output.read(last_read_where)
                        last_read_where = output.tell()
                        if not lines:
                            # Adjust the sleep interval to your needs
                            sleep(0.1)
                            # make sure pointing to the last place we read
                            #output.seek(last_read_where)
                        else:
                            start_time=time.time()
    #                        lines=self.lines2lines(lines)
                            for line in re.split(r'\n',lines):
                                yield line
                            lines=[]
                            if echo:
                                sys.__stdout__.write(lines)
                            sys.__stdout__.flush()
    
                    output.seek(last_read_where) #<-- even this misses some
                    #output.seek(last_read_where)
                    # A last write needed after subprocess ends
                    lines = output.read()
                    last_read_where = output.tell()
    
                    if echo:
                        sys.__stdout__.write(lines)


                    sys.__stdout__.flush()
    
    #                lines=self.lines2lines(lines)
                    for line in re.split(r'\n',lines):
                        yield line
                    
                    output.seek(last_read_where) #<-- even this misses some
                    lines = output.read()
                    last_read_where = output.tell()
    
                    #0v9#
    #                lines=self.lines2lines(lines)
                    for line in re.split(r'\n',lines):
                        yield line


                else:
                    ## OPTION:  From last _org
                    ## > good but looks terrible
                    #REF OPTIONS
                    #https://stackoverflow.com/questions/2804543/read-subprocess-stdout-line-by-line o
                    if verbose:
                        print ("[cwd]: "+str(cwd))
                    
                    sub_pipe=sub.PIPE
                    p = Popen(command,stdout=sub_pipe,stderr=sub_pipe, shell=shell,env=env,cwd=cwd,close_fds=close_fds,creationflags=creationflags)
                    found_line=False
                    
                    while p.poll() is None:
                        try:
                            line=buffer_patch_timeout(p.stdout)  #Freezes
    #                        line = p.stdout.readline() #**error on buffer blocking
    #err                            line = nbsr.readline(0.1)
                            if not line: break
                            found_line=True
                            line=re.sub(r'\n','',line) 
                            if echo: print (line)
                            yield line
                        except Exception as e:
                            print ("Caught exception: "+str(e))
                            print ("1/ " +str(traceback.print_exc()))
                            exc_info = sys.exc_info()
                            print ("2/ " +str(traceback.print_exception(*exc_info)))
                            break
    
                    while p.poll() is None:
                        try:
                            #line = p.stderr.readline()
                            line=buffer_patch_timeout(p.stdout)
                            found_line=True
                            if not line: break
                            line=re.sub(r'\n','',line) 
                            if echo: print (line)
                            yield line
                        except Exception as e:
                            print ("Caught exception: "+str(e))
                            print ("1/" +str(traceback.print_exc()))
                            exc_info = sys.exc_info()
                            print ("2/" +str(traceback.print_exception(*exc_info)))
                            break
                        

                    #WAIT opt 1#  text = p.communicate()[0]
                    #WAIT FOR END:   p.stdout.close()
                    
#py3                    for line in io.TextIOWrapper(suby.stdout, encoding="utf-8"):  # or another encoding
#py3                        # do something with line
#py3                        yield line
    
#                    #OPTION/ 
#                    while suby.poll() is None:
#                        lines = output.read(last_read_where)
#                        last_read_where = output.tell()
#                        if not lines:
#                            # Adjust the sleep interval to your needs
                    
                    
#err       


            if False:
                #*** this approach still freezes cause sub_pipe can buffer fill and hang background process.
                p = sub.Popen(command,stdout=sub_pipe,stderr=sub_pipe, shell=shell,env=env,cwd=cwd,close_fds=close_fds,creationflags=creationflags)
    
                q = Queue()
                t = Thread(target=enqueue_output, args=(p.stdout, q,sub_pipe))
                t.daemon = True # thread dies with the program
                t.start()
                
                # ... do other things here
                sleep_time=0.1
                max_wait_no_update=30
                c=0
                while 1:
                    c+=1
                    # read line without blocking
                    #paused#?  try:  line = q.get_nowait() # or q.get(timeout=.1)
                    yielded=False
                    try:
                        line = q.get(timeout=.1)
                    except Empty:
                        pass
                    else: # got line
                        # ... do something with line
                        c=0
                        yielded=True
                        yield line.strip()
                    if not p.poll() is None:
                        break
    
                    if not yielded:
                        time.sleep(sleep_time)
    
                    if c>int(max_wait_no_update/sleep_time):
                        print ("Break no update to screen (possibly [ ] finishes in background.")
                        break


#D        print ("Done iter")
        return

    def run_command_iter_org(self,cmd,echo=False,python_path='',cwd='',background=False,spawn=False,workon=''):
        """
           Standard subprocess that outputs stdout as iterator
           
           when?:
           out, err = process.communicate()  # The output and error streams. 
           
           BACKGROUND OPTIONS:
           a) run in background but don't detache: close_fds
           b) run in background and detache process:
           
           "spawn"== run as own process AND PERSIST
        """
        #p = os.popen4(command,"r")

        print ("[] add trial buffer mod")

        if echo:
            if cwd:
                print ("cd> "+cwd)
            print ("Running> "+str(cmd))
            if background:
                print ("Running in background. Same process, output below:")
            if spawn:
                print ("Running in background. Separate process")
            else:
                print ("stdout below:")
        
        if spawn:
            a=validate_new_spawn
            self.run_windows_background_spawn(cmd,cwd)
        else:
            if background:
                shell=False
                close_fds=True
                sub_pipe=None
                if detach_process:
                    creationflags=0x00000008
            else:
                shell=True
                close_fds=False
                sub_pipe=sub.PIPE
                creationflags=0
            if not cwd:cwd=None
                
            if python_path:
                env = os.environ.copy()
                env["PYTHONPATH"] = python_path+" "+env["PATH"]
            else:
                env=None
    
            if workon:
                workon_dir=self.get_workon_directory(workon)
                #env = os.environ.copy()
                #env["PYTHONPATH"] = python_path+" "+env["PATH"]
                command=''
                command+='set PYTHONPATH=c:\jon & ' #Clear PYTHONPATH ** FOR workon to initialize
                                                    #Also allow for supposedly pythonpath friendly workon items ie/ truthkit
                command+='cd /d '+workon_dir+' & activate & '  #start workon
                if cwd:
                    command+='cd /d '+cwd+' & '
                #Add direct link to python if python path not set
                #ok no #cmd=re.sub(r'python ',workon_dir+"/python ",cmd,flags=re.I)
                command=command+cmd
            else:
                command=''
                command=command+cmd

            if True:
                print ("[debug] FINAL CMD: "+str(command))
            
            p = sub.Popen(command,stdout=sub_pipe,stderr=sub_pipe, shell=shell,env=env,cwd=cwd,close_fds=close_fds,creationflags=creationflags)
#err            nbsr = NBSR(p.stdout)
    
            if not background:
                while 1:
                    try:
                        line=buffer_patch_timeout(p.stdout)
#                        line = p.stdout.readline() #**error on buffer blocking
#err                            line = nbsr.readline(0.1)
                        if not line: break
                        line=re.sub(r'\n','',line) 
                        if echo: print (line)
                        yield line
                    except Exception as e:
                        print ("Caught exception: "+str(e))
                        print ("1/ " +str(traceback.print_exc()))
                        exc_info = sys.exc_info()
                        print ("2/ " +str(traceback.print_exception(*exc_info)))
                        break

                while 1:
                    try:
                        #line = p.stderr.readline()
                        line=buffer_patch_timeout(p.stdout)
                        if not line: break
                        line=re.sub(r'\n','',line) 
                        if echo: print (line)
                        yield line
                    except Exception as e:
                        print ("Caught exception: "+str(e))
                        print ("1/" +str(traceback.print_exc()))
                        exc_info = sys.exc_info()
                        print ("2/" +str(traceback.print_exception(*exc_info)))
                        break

            #  If you want to be sure that it has completed, run p.wait().
        return
    
    def run_python_iter(self,cmd,echo=False,cwd='.',python_version=2,allow_multiple_instances=False,background=False,kill_if_running=False,spawn=False):
        if background==False and spawn==True:
            
            print ("[debug] forcing background since spawn=True")
            background=True

#py3        config_python3_path=self._convert_to_safe_filename("C:\Users\jon\AppData\Local\Programs\Python\Python36-32")

        cwd=self._convert_to_safe_filename(cwd)
        cwd=re.sub(r'^\.',self._convert_to_safe_filename(LOCAL_DIR)+r"//\.",cwd)
        cmds=re.split(r'[ ]+',cmd)
        script_py=cmds[0]
        script_args=cmds[1:]

        if python_version==3:
            python_path=config_python3_path
            python_exe="python3"
            if not os.path.exists(python_path):a=bad_python3_path
        else:
            python_path=''
            python_exe="python"
        
        ok_to_run=True
        
        ######## VALIDATORS
        if not allow_multiple_instances or kill_if_running:
            if self.is_running(script_py,kill_if_running=kill_if_running):
                if not allow_multiple_instances:
                    ok_to_run=False
                    print ("[debug] already running!")
            else:
                print ("[debug] is NOT running (anymore): "+script_py)
        if not os.path.exists(cwd+"/"+script_py):
            ok_to_run=False
            print ("Bad path: "+str(cwd+"/"+script_py))
            a=bad_path
        
        if ok_to_run:
            if python_version==3: #check if 3 is valid
                python_valid=False
                #Check python 3 path
                cmd=python_exe+""" -c "print ('True')" """
                for line in self.run_command_iter(cmd, echo=False,python_path=python_path):
                    if re.search(r'^True',line):python_valid=True
            else:
                python_valid=True
            
            if not python_valid:a=python_setup_invalid
            else:
                cmd=python_exe+" "+script_py+" "+" ".join(script_args)
                for line in self.run_command_iter(cmd, echo=echo,python_path=python_path,cwd=cwd,background=background,spawn=spawn):
                    yield line
        return

    def is_running_windows(self,cmdline_regex,verbose=False):
        #cmd="wmic path win32_process get name, commandline | FINDSTR python | FINDSTR .py"
        cmd="wmic path win32_process get name, commandline"
#D#        print ("CHECK PROCESSES: "+cmd)
        is_running=False
        c=0
        for line in self.run_command_iter(cmd):
            c+=1
            if verbose:
                temp=line.strip()
                if temp:
                    #temp=re.sub(r"^[ \s]+","",temp)
                    #temp=re.sub(r"[ \s]+$","",temp)
                    temp=re.sub(r'[ \s]+',' ',temp)
#D#                    print (">> "+str(temp))
            if re.search(cmdline_regex,line.strip()):
                is_running=True
                break
#        print ("Line count: "+str(c))
        if verbose:
            print ("[verbose process running]: "+str(is_running)+" at: "+str(cmdline_regex))
        return is_running

    def is_running(self,cmdline_regex,kill_if_running=False,echo=False,verbose=False):
        global ON_WINDOWS
        """
            Note:  slow to get process list -- so consider processing list
        """

        if ON_WINDOWS: #**watch this stuff!  works now
            try:
                is_running=self.is_running_windows(cmdline_regex,verbose=verbose)
                if not is_running:
                    return is_running
                if not kill_if_running:
                    return is_running
            except Exception as e:
                print ("[warning] fast is_running failed but will try other ie/ "+str(e))

        #Auto patch as may be loaded in notepad
        if re.search(r'\.py',cmdline_regex,flags=re.I) and not re.search(r'python',cmdline_regex,flags=re.I):
            cmdline_regex="python.*"+cmdline_regex

        cmdline_regex_list=[cmdline_regex]
        for pid,pname,dicta in self._iter_processes():
            cmdline=" ".join(dicta['cmdline'])
            if echo and re.search(r'\.py',cmdline,flags=re.I):
                print ("> "+str(cmdline))
            for other in cmdline_regex_list:
                if re.search(other,cmdline,flags=re.I):
                    if kill_if_running:
                        try: p=psutil.Process(pid)
                        except: p=False
                        if p:
                            print ("[debug] killing: "+cmdline+" pid: "+str(pid))
                            try: p.kill()
                            except:pass #quiet
                    else:
                        print ("active> "+str(pname)+" "+cmdline)
                        cmdline_regex_list.remove(other)
                    
        if not cmdline_regex_list:
            return True
        else:
            return False
    
    def get_processes_not_running(self,pnames=[]):
        #Note: does *.search*
        for pid,pname,dicta in self._iter_processes():
            cmdline=" ".join(dicta['cmdline'])
            for other in pnames:
                if re.search(other,cmdline,flags=re.I):
                    print ("active> "+str(pname)+" "+cmdline)
                    pnames.remove(other)
        #returns pnames not running
        return pnames
    
    
    def _iter_processes(self):
        #0v2# via performance.py
        for item in psutil.process_iter():
            try: p=psutil.Process(item.pid)
            except: p=False
    
            if p:
                try: name=str(p.name()).lower() #win
                except: name=str(p.name).lower()
                
                dicta={}
                try:
                    dicta['cmdline']=p.cmdline()
                except:
                    dicta['cmdline']='' #smss accessdenied
                yield item.pid,name,dicta
                
                if False:#stats from below
                    try:
                        ddict=str(p.as_dict())
                        exe=str(p.exe()).lower()
                        create_time=p.create_time()
                        io_counters=p.io_counters()
                    except:
                        ddict=''
                        exe=''
                        create_time=''
                        io_counters=''
                    try: parent=str(p.parent().name())
                    except: parent=''
                    #mem=p.get_memory_info().rss
                    try: mem=p.get_memory_info().rss
                    except:
                    #print ("could not get_memory_info()")
                        mem=0
                    cpu=p.cpu_percent(interval=0.1)
                    try: cpu=p.cpu_percent(interval=0.1)
                    except: cpu=0
                    #liner=str(item.pid)+","+str(name)+","+str(parent)+","+str(mem)+","+str(cpu)+","+str(exe)+","+str(io_counters)
                    liner=str(item.pid)+",name:"+str(name)+","+str(parent)+",mem:"+str(mem)+",cpu:"+str(cpu)+",exe:"+str(exe)+",io:"+str(io_counters)
        return

    def _convert_to_safe_filename(self,wd):
        wd="%r"%wd
        wd=re.sub(r"'",'',wd)
        filename=str(re.sub(r'[\\]+',r'/',wd))
        return filename
    
    def make_always_on(self,pp):
        regex=pp['regex']
        if not self.is_running_regex(regex):
            print ("NOT ON: "+pp['cmd'])
            #Admin.Win.spawn_background(pp['cmd'],pp['directory'])
            a=validate_always_on
            self.run_windows_background_spawn(pp['cmd'],pp['directory'])
        return
        
    def is_running_regex(self,regex):
        is_it_on=False
        for pid,pname,cmdline in self.Win.iter_processes_regex(regexes=[regex]):
            is_it_on=True
        return is_it_on
    
    
    

def test():
    script_py="./net_abstract/ncpoc_master/tk_pool.py"
    if False:
        Exe=Execute_Command()
        Exe.run_script(script_py, only_one=True)

    Execute_Command(script_py=script_py)
    return
    
def convert_to_safe_filename(wd):
    wd="%r"%wd
    wd=re.sub(r"'",'',wd)
    filename=str(re.sub(r'[\\]+',r'/',wd))
    return filename
    
def run_python_test():
    Exe=Execute_Command()

    wd="C:\jon\tk\tk_fetch\-- sources\patreon\PatreonArchiver-master"
    script_py="run_dev.py"
    python_version=3
    
    if False:
        is_running=Exe.is_running(script_py)
        print ("Is it running; "+str(is_running))

    script_args=[]
    for line in Exe.run_python_iter(script_py,echo=True,cwd=wd,python_version=python_version,allow_multiple_instances=False,kill_if_running=True,background=True):
        pass

    print ("---------------")
    print ("Done run_python")
    return

def test_background():
    Exe=Execute_Command()

    wd="./bot_utilities"
    script_py="bot_sleep.py"
    for line in Exe.run_python_iter(script_py,cwd=wd,allow_multiple_instances=False,kill_if_running=True,background=True,spawn=True):
        pass
    return

def test_always_on_or_spawn():
    #via always_on.py
    dd=[]
    pp={}
    pp['directory']='C:/c/utils/private_internet_access'
    pp['cmd']='python fix_pia.py'
    pp['regex']='fix_pia'
    dd+=[pp]
    need_case=ok
    return
    
         
def test_set_validated():
    Exe=Execute_Command()
    Exe.run_windows_background('echo Hello World flash then close','.',workon='python3',visible=True)
    
    print ("[] add test python scripts o.open etc.")

    print ("Done tests")
    return
    

if __name__=='__main__':
    branches=['test']
    branches=['run_python_test']
    branches=['test_always_on_or_spawn']
    branches=['test_background']
    
    branches=['test_set_validated']


    for b in branches:
        globals()[b]()






#background option:

#1/  start program

#2/
# cwd = os.getcwd()
#    os.chdir("../pjsua")
#    os.system("python runall.py --list > list")
    
#3/
#You could run it silently using a Windows Script file instead. The Run Method allows you running a script in invisible mode. Create a .vbs file like this one
#Dim WinScriptHost
#Set WinScriptHost = CreateObject("WScript.Shell")
#WinScriptHost.Run Chr(34) & "C:\Scheduled Jobs\mybat.bat" & Chr(34), 0
#Set WinScriptHost = Nothing
#and schedule it. The second argument in this example sets the window style. 0 means "hide the window."












