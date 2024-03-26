import os
import sys
import re
import time
import uuid
import codecs
import datetime

#import urllib2

import traceback

from multiprocessing import Pool
try: from Queue import Queue
except: from queue import Queue  #py3
from threading import Thread
from concurrent import futures # pip install futures
from concurrent.futures import ThreadPoolExecutor


try:
    from performance import Performance_Tracker #optional
    PERFORMANCE=True
except:
    PERFORMANCE=False

import sys


        
PERFORMANCE=False

if not PERFORMANCE:
    print ("[] multi not tracking performance stats (pip install psutil)")

##############################################################
# Support library **not officially released
##############################################################

    #2v1# JC Dec 16, 2023 Verbose logs for stuck threads
    #2v0# JC Sep 26, 2023 Use in WT
    #1v9# JC Apr  6, 2023 Add run wait sleep time while processes full
    #1v8# JC Dec  2, 2022 Use in logg
    #1v7# JC Dec  2, 2020 Capture exceptions in file
    #1v6# JC Nov 27, 2020 Use in gret
    #1v5# JC Nov  6, 2020 py3 ok
    #1v4# JC Nov  6, 2020 Use in snapshot service
    #1v3# JC Sep 12, 2020 Use in voyager
    #1v2# JC Aug 13, 2020 Missed stats quiting
    #1v1# JC Aug  5, 2020 Threads stalling.  Add meta to future object: .id .start_time and track status ([] consider max time allowed)
    #1v0# JC Dec 30, 2019 Use in angelco mega map
    #0v9# JC Apr 30, 2019 Use in angelco
    #0v8# JC Jul 19, 2018 Use in gmail extractor

    #0v7# JC Jun 20, 2017 Use in db insert
    #0v6# JC Feb 20, 2017 For labX
    #0v5# JC Jan 31, 2017 (from academia)
    #0v4# JC Jan 29, 2017 (from upwork)
    #0v3# JC Jan 20, 2017
    #0v2# JC June 20, 2016


def beep():
    try:
        import winsound
        winsound.Beep(300,2000)
    except:pass
    return

def progress(count, total, status=''):
    bar_len = 60
    filled_len = int(round(bar_len * count / float(total)))

    percents = round(100.0 * count / float(total), 1)
    bar = '=' * filled_len + '-' * (bar_len - filled_len)

    sys.stdout.write('[%s] %s%s ...%s\r' % (bar, percents, '%', status))
    sys.stdout.flush()  # As suggested by Rom Ruben (see: http://stackoverflow.com/questions/3173320/text-progress-bar-in-the-console/27871113#comment50529068_27871113)
    

## To get thread exceptions use this:
#- otherwise futures swallows exception
class ThreadPoolExecutorStackTraced(ThreadPoolExecutor):
    #https://stackoverflow.com/questions/19309514/getting-original-line-number-for-exception-in-concurrent-futures
    #So, to avoid losing the traceback, you have to save it somewhere. My workaround is to wrap the function to submit into a wrapper whose only task is to catch every kind of exception and to raise an exception of the same type whose message is the traceback. By doing this, when an exception is raised it is captured and reraised by the wrapper, then when sys.exc_info()[1] is assigned to the exception of the Future object, the traceback is not lost.

    def submit(self, fn, *args, **kwargs):
        """Submits the wrapped function instead of `fn`"""

        return super(ThreadPoolExecutorStackTraced, self).submit(
            self._function_wrapper, fn, *args, **kwargs)

    def _function_wrapper(self, fn, *args, **kwargs):
        """Wraps `fn` in order to preserve the traceback of any kind of
        raised exception
        
        [ ] So I suppose error here is really error in function.  How to show?

        """
        try:
            return fn(*args, **kwargs)
        except Exception:
            print ("[debug] multi.py -> _function_wrapper args: "+str(args)+" kwargs: "+str(kwargs)+" fn: "+str(fn))
            raise sys.exc_info()[0](traceback.format_exc())  # Creates an  **ERROR maybe py version related:  __init__() takes at least 4 arguments (2 given)
                                                             # exception of the
                                                             # same type with the
                                                             # traceback as
                                                             # message

class Multi_Wrap(object):

    #Generic  multi-threaded etl
    #**support for multi thread (if io bound), or multiprocess
    #def __init__(self,multi='process',max_workers=20,verbose=False):
    def __init__(self,multi='thread',max_workers=20,verbose=False,mode='normal',exception_log=''):
        #stopp=threadingg #causing sqlite error on non threaded maybe
        
        ## Option to track and log exceptions
        self.exception_log=exception_log
        self.exceptions=[]

        self.mode=mode #normal or db for starting connections
        self.verbose=verbose
        self.max_workers=max_workers
        self.cycles=0
        self.pending=0
        self.threads=0
        
        self.print_status_every=40 #cycles
        self.target_pending=self.max_workers*2
        self.multi=multi
        self.log_runtimes={}

        self.run_wait_sleep_time=3  #Can set_run_wait_sleep_time

        if PERFORMANCE:
            self.Perf=Performance_Tracker()
        
        self.max_ram=93
        
        if self.multi=='process':
            self.poolx = futures.ProcessPoolExecutor(self.max_workers)
        else:
#            self.poolx = futures.ThreadPoolExecutor(self.max_workers)
            self.poolx = ThreadPoolExecutorStackTraced(self.max_workers)
        self.running_futures=[]
        self.db_connections=[]
        return
    
    def init_db_connections(self,DB):
        self.db_connections.append(DB)
        return
    
    def count_active(self):
        return len(self.running_futures)
    
    def count_available(self):
        return self.max_workers-self.count_active()
    
    def set_max_targets(self,max_ram=93,max_workers=0):
        #**do only at initial
        self.max_ram=max_ram
        if max_workers:
            self.max_workers=max_workers #also defined org

        if self.multi=='process':
            self.poolx = futures.ProcessPoolExecutor(self.max_workers)
        else:
            self.poolx = futures.ThreadPoolExecutor(self.max_workers)
        return
    
    def status(self):
        liner=''
        liner="\n-- At cycle: "+str(self.cycles)+" pending "+str(self.pending)+" threads "+str(self.threads)
        if not self.cycles%self.print_status_every:
            self.refresh_stats()
            print (liner)
        return liner
    
    def refresh_stats(self):
        self.pending=self.poolx._work_queue.qsize()
            #Do pending calc for process. which means??
        self.threads=len(self.poolx._threads)
        
        return
    
    def refresh_process_stats(self):
        self.get_completed() #not returning anything
        self.processes=len(self.running_futures)
        print ("\n-- At cycle: "+str(self.cycles)+" active processes "+str(self.processes)+" of "+str(self.max_workers))
        return

    def process_run(self,function_name,*args,**kwargs):
        added=False
        self.cycles+=1 #Raw counter
        self.refresh_process_stats()

        #Special logic if GLOBAL_WAIT
        waiting=False
        if hasattr(self,'GLOBAL_WAIT'):
            if self.GLOBAL_WAIT>20: waiting=True
            
        #RAM LIMIT
        if PERFORMANCE and self.Perf.get_ram_used()>self.max_ram:
            if self.verbose: print ("Sleeping as [RAM LIMIT] at : "+str(self.Perf.get_ram_used())+" > "+str(self.max_ram))
            time.sleep(5)
        elif self.processes>=self.max_workers or waiting:
            if self.verbose: print ("Sleeping as "+str(self.processes)+" of "+str(self.max_workers)+" already running...")
            if waiting:
                if self.verbose: print ("Not creating more processes as urlfetch waiting on: "+str(self.GLOBAL_WAIT))
            time.sleep(3)
        else:
            added=True
            future=self.poolx.submit(function_name,*args,**kwargs)
            future.id=str(uuid.uuid1())
            future.start_time=time.time()
            self.running_futures.append(future)
        return added

    def set_run_wait_sleep_time(self,sleep_time):
        self.run_wait_sleep_time=sleep_time
        return
   
    def threaded_run(self,function_name,*args,**kwargs):

        added=False
        self.cycles+=1 #Raw counter
        self.refresh_stats()

        #Special logic if GLOBAL_WAIT
        waiting=False
        if hasattr(self,'GLOBAL_WAIT'):
            if self.GLOBAL_WAIT>20: waiting=True
        
        if self.pending>self.target_pending or waiting:
            time.sleep(self.run_wait_sleep_time)
            if self.verbose: print ("Sleeping "+str(self.run_wait_sleep_time)+" as "+str(self.pending)+" pending...")
            if waiting:
                if self.verbose: print ("Not creating more processes as urlfetch waiting on: "+str(self.GLOBAL_WAIT))
        else:
            added=True
            future=self.poolx.submit(function_name,*args,**kwargs)
            future.id=str(uuid.uuid1())
            future.start_time=time.time()
            self.running_futures.append(future)
#            self.log_runtimes[]
        return added

    def enqueue_init(self):
        self.enqueued={}
        self.enqueued_out={}
        return
    def enqueue_run_key(self,the_key,function_name,*args,**kwargs):
        ## GIVEN key -- expect results into dict
        self.enqueued[the_key]=(function_name,args,kwargs)
        return
    def enqueue_wait_all(self,verbose=True):
        ## .threaded_run()

        self.cycles+=1 #Raw counter
        self.refresh_stats()
        
        ## ENQUEUE ALL
        enqueued_targets=self.enqueued.keys()
        while enqueued_targets:
            if self.pending>self.target_pending:
                time.sleep(2)
                if self.verbose: print ("Sleeping as "+str(self.pending)+" pending...")
                if waiting:
                    if self.verbose: print ("Not creating more processes as urlfetch waiting on: "+str(self.GLOBAL_WAIT))
            else:
                the_key=enqueued_targets.pop()
                #future=self.poolx.submit(function_name,*args,**kwargs)
                future=self.poolx.submit(self.enqueued[the_key][0], *self.enqueued[the_key][1], **self.enqueued[the_key][2])
                future.the_key=the_key
                self.running_futures.append(future)

        print ("[debug] waiting for finishes...")
        
        ## .get_completed()
        total_expected=len(self.enqueued)
        total_found=len(self.enqueued_out)
        while not total_expected==total_found:
            total_expected=len(self.enqueued)
            total_found=len(self.enqueued_out)

            for future in list(self.running_futures): #loop copy
                total_expected=len(self.enqueued)
                total_found=len(self.enqueued_out)

                if future.done():
                    try:
                        result=future.result()
                    except Exception as e:
                        print ("BAD: "+str(e))
                        beep()
                        result=future.result()
                    self.enqueued_out[future.the_key]=result

                    self.running_futures.remove(future)
                    #print ("Waiting for: "+str(len(self.running_futures))+"...")
                
                time.sleep(0.1)
                
                if verbose:
                    progress(total_found, total_expected, status='')
                    
                ## Log if near error
                if (total_found/total_expected)>0.98:
                    self.future_status()
            ## Log if near error
            if (total_found/total_expected)>0.98:
                print ("Debug future length: "+str(len(self.running_futures)))
                

        return self.enqueued_out
    
    
    def db_run(self,sql,verbose=False):
        #Similar to threaded run -- though maintains db connections
        added=False
        self.cycles+=1 #Raw counter
        self.refresh_stats()

        #Special logic if GLOBAL_WAIT
        waiting=False
        if hasattr(self,'GLOBAL_WAIT'):
            if self.GLOBAL_WAIT>20: waiting=True
        
        if self.pending>self.target_pending or waiting:
            time.sleep(3)
            if self.verbose: print ("Sleeping as "+str(self.pending)+" pending...")
            if waiting:
                if self.verbose: print ("Not creating more processes as urlfetch waiting on: "+str(self.GLOBAL_WAIT))
        else:
            DB=self.get_active_connection()
            if DB:
                added=True
                if verbose:
                    print ("Adding sql to id: "+str(DB.id))
                future=self.poolx.submit(DB.insert_bulk_insert,sql)
                self.running_futures.append(future)
            else:
                #Assume external wait as well
                wtime=0.2
                if verbose:
                    print ("No free db connections... {waiting "+str(wtime)+"}")
                time.sleep(wtime) #pause externally as well

        return added
    
    def get_active_connection(self,verbose=False):
        gotten_DB=''
        
        #Get any completed connections
        results=self.get_completed(verbose=False)
        if results:
            for DB in self.db_connections:
                for result in results:
                    if DB.id==result: #Only for db
                        if verbose:
                            print ("Database connection ready again at id: "+str(DB.id))
                        DB.set_state('ready')
        
        for DB in self.db_connections:
            if verbose:
                print ("Trying to get at id: "+str(DB.id)+" state: "+str(DB.state))
            if not DB.state=='running':
                if verbose:
                    print ("Got DB connection ready id: "+str(DB.id))
                DB.set_state('running')
                gotten_DB=DB
                break
        return gotten_DB
    
    def log_exception(self,exception,echo_exception=True):
        if self.exception_log:
            if not self.exceptions:
                fp=codecs.open(self.exception_log,'w',encoding='utf-8',errors='ignore')
            else:
                fp=codecs.open(self.exception_log,'a',encoding='utf-8',errors='ignore')
                
            fp.write("-- Exception #"+str(len(self.exceptions))+" at: "+str(datetime.datetime.now())+"-"*35+"\n")
            try:
                fp.write(str(exception))
            except Exception as e:
                fp.write("Could not log exception: "+str(e))
            fp.write("\n")
            self.exceptions+=[exception]
            fp.close()
        if echo_exception:
            print ("-- Exception #"+str(len(self.exceptions))+"-"*35)
            print (str(exception))
            print ("^"*50)
        return

    def get_completed(self, verbose=False, fail_on_error=True):
        # Updated Dec 19, 2023
        #https://docs.python.org/3.2/library/concurrent.futures.html#concurrent.futures.Future
        results = []
        if verbose:
            print("Current threads active: " + str(len(self.running_futures)))
    
        for future in list(self.running_futures):  # Loop copy
            if future.done():
                try:
                    result = future.result()
                except Exception as e:
                    self.log_exception(e)
                    beep()
    
                    if fail_on_error:
                        raise e  # Re-raise the exception to handle it outside
                    else:
                        result = None  # Proceed with None if not failing on error
    
                results.append(result)
                self.running_futures.remove(future)
    
        return results

#    def get_completed(self,verbose=False,fail_on_error=True):
#        #https://docs.python.org/3.2/library/concurrent.futures.html#concurrent.futures.Future
#        results=[]
#        if verbose:
#            print ("Current threads active: "+str(len(self.running_futures)))
#        for future in list(self.running_futures): #loop copy
#            if future.done():
#                try:
#                    result=future.result()
#                except Exception as e:
#                    self.log_exception(e)
#                    beep()
#                    
#                    if fail_on_error:
#                        result=future.result()
#                    else:
#                        result=None
#                    
#                results.append(result)
#                #hides!#  try:results.append(future.result())
#                #hides!#  except:results.append("BAD FORMAT")
#                self.running_futures.remove(future)
#        return results

    def future_status(self,future):
        #https://docs.python.org/3/library/concurrent.futures.html
        dd={}
        dd['id']=future.id
        try: dd['running']=future.running()
        except: dd['running']=future.running
        dd['done']=future.done()
        try: dd['ss']=str(future)
        except:
            dd['ss']=''
        dd['runtime']=time.time()-future.start_time #**custom added start time

        #none# dd['partial_result']=future._result  #base class: https://github.com/python/cpython/blob/master/Lib/concurrent/futures/_base.py

        #result(timeout=None)
        #t.cancel():
        try: print ("[future status]: "+str(dd)) 
        except: print ("[future status]: UNKNOWN")
        return
    
    def wait_for_finish(self,verbose=False, fail_on_error=True):
        ## GOAL:  still wait for ALL to be completed
        ##
        stats={}

        all_results=[]
        start_wait=time.time()
        while(len(self.running_futures)):

            ## COUNT ACTIVE
            stats['count_workers']=self.max_workers
            stats['count_done']=0
            stats['count_active']=0
            stats['count_total']=len(self.running_futures)
            stats['wait_time']= total_waited=(time.time()-start_wait)/(60*60)

            for future in list(self.running_futures): #loop copy
                if future.done(): stats['count_done']+=1
                if future.running(): stats['count_active']+=1

            if stats['count_total']:
                stats['thead_load']=stats['count_active']/stats['count_total']
            else:
                stats['thead_load']=0

            if verbose:
                if stats['wait_time']>1:
                    print ("[wait_for_finish] "+str(stats))

                for future in self.running_futures:
                    self.future_status(future)

            time.sleep(0.5)  #Basic wait between checks

            results=self.get_completed(fail_on_error=fail_on_error) #empty some
            all_results+=results
        return all_results


    def wait_for_all_results(self, delay=0.5, fail_on_error=False, verbose=False, update_interval=30,max_wait_time=0):
        """
        Waits for all futures (threads/tasks) to complete.
    
        :param delay: Time to wait (in seconds) before checking again.
        :param fail_on_error: If True, will fail on any error in the futures.
        :param verbose: If True, prints detailed logs.
        :param update_interval: Time interval (in seconds) for verbose updates.
        : max_wait_time: Max time to wait for all futures to complete. 0 means no limit.
        :return: List of results from all completed futures.
        """
        all_results = []
        start_time = time.time()
        last_update_time = start_time
        
        total_futures = len(self.running_futures)
    
        while len(self.running_futures):
            current_time = time.time()
            elapsed_time = current_time - start_time
            # Check if max_wait_time has been exceeded
            if max_wait_time and elapsed_time > max_wait_time:
                raise Exception(f"Max wait time of {max_wait_time} seconds exceeded. Exiting wait loop.")

            # Check for completed results
            results = self.get_completed(fail_on_error=fail_on_error)
            if results:
                all_results.extend(results)
    
            # Verbose logging
            if verbose:
                current_time = time.time()
                elapsed_time = current_time - start_time
                time_since_last_update = current_time - last_update_time
    
                if time_since_last_update >= update_interval:
                    remaining_futures = len(self.running_futures)
                    completed_futures = total_futures - remaining_futures
                    
                    print(f"Waiting for {remaining_futures}/{total_futures} threads to complete. Elapsed time: {elapsed_time:.2f} seconds. Update every {update_interval} seconds.")
      
                    last_update_time = current_time
    
            # Sleep before next check
            if len(self.running_futures):
                time.sleep(delay)
    
        return all_results


    def shutdown(self):
        self.poolx.shutdown(wait=False)
        return
    
    ##########Different ways to execute
    def execute(self,function_name,*args,**kwargs):
        self.GLOBAL_WAIT=kwargs.get('GLOBAL_WAIT',0)
        if 'GLOBAL_WAIT' in kwargs: kwargs.pop('GLOBAL_WAIT')
        execute_wait_time=kwargs.pop('execute_wait_time',0.1)

        #Guarantee add
        if self.multi=='process':
            while (not self.process_run(function_name,*args,**kwargs)):
                #if self.verbose: print "Waiting to add to queue..."
                time.sleep(execute_wait_time) #default
        else:
            while (not self.threaded_run(function_name,*args,**kwargs)):
                time.sleep(execute_wait_time) #default
        
        return

    def run(self,function_name,*args,**kwargs):
        #**runs same thing over and over
        #Self loop forever
        while(True):
            self.threaded_run(function_name,*args,**kwargs)
            
            #Get or process completed
            results=self.get_completed()
        self.shutdown()
        return
    

def main(args):
    ETL=ETL_Wrap()
    ETL.run(hello_extract,'')


def dummy_pause(sleep_time,throw_exception=False):
    print ("[info] stdout dummy_pause pausing at: "+str(sleep_time))
    time.sleep(sleep_time)
    if throw_exception:
        uncaughtt=exceptionn
    return

def test_threaded_exception():
    print ("[info] testing threaded exception...")

    exception_log='multi_exception.log'
    Multi=Multi_Wrap(max_workers=2,exception_log=exception_log)
    
    c=0
    while True:
        Multi.execute(dummy_pause,1,throw_exception=False)
        results=Multi.get_completed()   #verbose=True)
        c+=len(results)
        if results:
            print ("------------> "+str(c))
            
        ## Throw exception
        if c>3:
            print ("------------> THROWING EXCEPTION...")
            Multi.execute(dummy_pause,1,throw_exception=True)
            

    return


if __name__=='__main__':
    branches=['test_threaded_exception']

    for b in branches:
        globals()[b]()
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
