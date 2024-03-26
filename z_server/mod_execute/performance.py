from __future__ import division
import re
import psutil
import subprocess as sub
import os
import sys
import pickle
import time

import psutil

#0v9# JC Dec 14, 2019  Use in WT
#0v8# JC Aug  2, 2019  Get parent of orphaned firefoxes
#0v7# JC Apr 16, 2019  Break at first kill option
#0v6# JC Feb 12, 2019  Use in TT
#0v5# JC Sep 12, 2017  Integrate into TK
#0v4# JC Apr 10, 2017  Use in TK chapter 1
#0v3# JC Feb 15, 2017  Use in labxi
#0v2# JC Jan 28, 2017  Validate on liinux
#0v1# JC Jan 28, 2017  Use in contacts project

#$ sudo pip uninstall psutil
#Uninstalling psutil:
#  /usr/local/lib/python2.7/dist-packages/_psutil_linux.so
#  /usr/local/lib/python2.7/dist-packages/_psutil_posix.so
#  /usr/local/lib/python2.7/dist-packages/psutil
#  /usr/local/lib/python2.7/dist-packages/psutil-2.2.1.egg-info
#Proceed (y/n)? y
#  Successfully uninstalled psutil
#$ sudo apt-get remove --purge python-psutil
#Reading package lists... Done
#Building dependency tree       
#Reading state information... Done
#The following packages will be REMOVED:
#  python-psutil*
#0 upgraded, 0 newly installed, 1 to remove and 294 not upgraded.
#After this operation, 215 kB disk space will be freed.
#Do you want to continue [Y/n]? Y
#(Reading database ... 183978 files and directories currently installed.)
#Removing python-psutil ...
#Processing triggers for python-support ...
#$ sudo pip install 'psutil==2.2.1'


#DEV NOTES:
#full path:
#http://stackoverflow.com/questions/30909457/find-the-path-of-every-running-process-in-python


class Performance_Tracker(object):
    #Generic performance tracker
    def __init__(self):
        self.estart=0
        self.eend=0
        self.etime=0

        self.most_mem_line=""
        self.most_mem=0
        
        self.is_windows = sys.platform.startswith('win')
        try: self.cpu_nums = psutil.NUM_CPUS
        except:self.cpu_nums=-1
        try: self.max_mem = psutil.TOTAL_PHYMEM
        except:-1
        
        self.mtimer={}
        return
    
    def iter_processes(self):
        for item in psutil.process_iter():
            try: p=psutil.Process(item.pid)
            except: p=False
    
            if p:
                try: name=str(p.name()).lower() #win
                except: name=str(p.name).lower()
                
                dicta={}
                try:
                    dicta['cmdline']=p.cmdline()
                except Exception as e:
                    dicta['cmdline']=''
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
                    #print "could not get_memory_info()"
                        mem=0
                    cpu=p.cpu_percent(interval=0.1)
                    try: cpu=p.cpu_percent(interval=0.1)
                    except: cpu=0
                    #liner=str(item.pid)+","+str(name)+","+str(parent)+","+str(mem)+","+str(cpu)+","+str(exe)+","+str(io_counters)
                    liner=str(item.pid)+",name:"+str(name)+","+str(parent)+",mem:"+str(mem)+",cpu:"+str(cpu)+",exe:"+str(exe)+",io:"+str(io_counters)
        return

    def profile_object_memory(self,obj):
        #for attr, value in k.__dict__.iteritems():
        oa=[]
        total=sys.getsizeof(pickle.dumps(obj))
        rem=total
        oa.append("Total: "+str(total))
        members = [attr for attr in dir(self) if not callable(attr) and not attr.startswith("__")]
        for member in members:
            try:
                t=sys.getsizeof(pickle.dumps(getattr(self,member)))
            except: t=0
            oa.append(member+": "+str(t))
            rem-=t
        oa.append("Unprofiled size: "+str(rem))
        return oa,total,rem

    def get_size_of_object(self,obj):
        return sys.getsizeof(pickle.dumps(obj))
    
    def start(self,id=''):
        if not id:
            self.estart=time.time()
        else:
            self.mtimer[id]=time.time()
        return
    
    def end(self,id=''):
        if not id:
            self.eend=time.time()
            self.etime=self.eend-self.estart
            r=self.etime
        else:
            r=time.time()-self.mtimer[id]
        return r
    
    def end_print(self):
        self.eend=time.time()
        self.etime=self.eend-self.estart
        print ("Execution time: "+str(self.etime))
        return self.etime
    
    
    def server_profile(self,names=['httpd','java','python']):
        self.most_mem_line=""
        self.most_mem=0
        for item in psutil.process_iter():
            try: p=psutil.Process(item.pid)
            except: p=False
    
            if p:
                try: name=str(p.name()).lower() #win
                except: name=str(p.name).lower()

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
                    #print "could not get_memory_info()"
                    mem=0
                cpu=p.cpu_percent(interval=0.1)
                try: cpu=p.cpu_percent(interval=0.1)
                except: cpu=0
                #liner=str(item.pid)+","+str(name)+","+str(parent)+","+str(mem)+","+str(cpu)+","+str(exe)+","+str(io_counters)
                liner=str(item.pid)+",name:"+str(name)+","+str(parent)+",mem:"+str(mem)+",cpu:"+str(cpu)+",exe:"+str(exe)+",io:"+str(io_counters)
                for n in names:
                    if re.search(r''+n,name):
                        print (liner)
                        if mem>self.most_mem:
                            self.most_mem=mem
                            self.most_mem_line=liner
                        break
        print ("Most mem: "+str(self.most_mem_line))
        return

    def get_most_mem(self,refresh=False):
        if not self.most_mem or refresh: self.server_profile()
        return self.most_mem

    def run_command(self,command):
        # p = sub.Popen(command,stdout=sub.PIPE,stderr=sub.PIPE)
        # output, errors = p.communicate()
        print ("[] consider using executor.py")
        p = os.popen(command,"r")
        while 1:
            line = p.readline()
            if not line: break
            line=re.sub(r'\n','',line) 
            yield line
        return
    def spawn_background_process(self,cmd,visible=False,cwd=''):
        cmd_array=re.split(r' ',cmd)
            
        if not cwd:
            process=sub.Popen(cmd_array, shell=True, stdout=sub.PIPE, stderr=sub.PIPE)
        else:
            print ("[debug] changing to: "+cwd+" running: "+str(cmd_array))
            process=sub.Popen(cmd_array, shell=True, stdout=sub.PIPE, stderr=sub.PIPE,cwd=cwd)

        
        if visible:
            print ("Waiting for process to end: "+str(cmd)+"...")
            out, err = process.communicate()  # The output and error streams. 
            print ("OUTPUT 1: "+str(out))
            print ("OUTPUT 2 err: "+str(err))
        return
    
    def dump_processes(self):
        cmdlines=[]
        for pid,pname,dicta in self.iter_processes():
            cmdline=" ".join(dicta['cmdline'])
            cmdlines+=[cmdline]
        return cmdlines
    
    def check_processes(self,pnames=[]):
        for pid,pname,dicta in self.iter_processes():
            cmdline=" ".join(dicta['cmdline'])
#            if re.search(r'python',cmdline,flags=re.I):
#                print "> "+str(pname)+" "+cmdline
            for other in pnames:
                if re.search(other,cmdline,flags=re.I):
                    print ("active> "+str(pname)+" "+cmdline)
                    pnames.remove(other)
        #returns pnames not running
        return pnames
    
    def kill_process(self,pname_given='',pid_given='',break_at_first=False):
        found=False
        for pid,pname,dicta in self.iter_processes():
            cmdline=" ".join(dicta['cmdline'])
            if re.search(pname_given,cmdline,flags=re.I) or pid==pid_given:
                try: p=psutil.Process(pid)
                except: p=False
                if p:
                    found=True
                    print ("[debug] killing: "+pname_given+" pid: "+str(pid))
                    p.kill()
                    if break_at_first:break
        if not found:
            print ("warning:  Could not kill/find: "+pname_given)
        return
    
    def linux_ram_list(self,filter="flow_run"):
        cmd="ps -e -orss=,args= | sort -b -k1,1n | pr -TW$COLUMNS | grep 'httpd'"
        cmd="ps -e -orss=,args= | sort -b -k1,1n | grep 'httpd'"
        cmd="ps -e -orss=,args= | sort -b -k1,1n | grep '"+filter+"'"
#D#        print "Running: "+str(cmd)
        tot_ram=0
        for line in self.run_command(cmd):
#D            print "YO: "+str(line)
            if re.search(r''+filter,line):
                ss=line.split(r' ')
                try:
                    tot_ram+=int(ss[0])
                except:pass
        return tot_ram

    def linux_cpu_count(self,filter='flow_run',threshold=5):
        cmd="ps -e -o pcpu,nice,state,cputime,args --sort -pcpu | head -10"
#D#        print "Running: "+str(cmd)
        tot_cpu=0
        cpu_count=0
        for line in self.run_command(cmd):
            if re.search(r''+filter,line):
                ss=line.split(r' ')
#D#                print "CPU string: "+str(ss)
                this_cpu=0
                try: this_cpu=float(ss[1])
                except: this_cpu=float(ss[0])
                if this_cpu>threshold:
                    tot_cpu+=this_cpu
                    cpu_count+=1
        
#D#            print "YO: "+str(line)
        return tot_cpu,cpu_count

    def linux_cpu_list(self,filter='flow_run'):
        cmd="ps -e -o pcpu,nice,state,cputime,args --sort -pcpu | head -10"
#D#        print "Running: "+str(cmd)
        tot_cpu=0
        for line in self.run_command(cmd):
            if re.search(r''+filter,line):
                ss=line.split(r' ')
#D#                print "CPU string: "+str(ss)
                try: tot_cpu+=float(ss[1])
                except: tot_cpu+=float(ss[0])
        
#D#            print "YO: "+str(line)
        return tot_cpu

    def linux_free_space(self,mount='vda1'):
        cmd="df"
        tot=0
        for line in self.run_command(cmd):
            if re.search(r''+mount,line):
                ss=line.split()
                try: tot=int(ss[3])
                except: pass
        return tot

    def linux_free_mem(self):
        cmd="cat /proc/meminfo"
        tot=0
        for line in self.run_command(cmd):
#ok            print ("[debug meminfo]: "+str(line))
#NONCOMMIT#            if re.search(r'MemFree',line):
            if re.search(r'MemAvailable',line):
                ss=line.split()
#                print "YO: "+str(ss)
                try: tot=int(ss[1])
                except: pass
        return tot
    
    def windows_process_memory(self,the_type=''):
        #via performance jon_clean
        this_id=os.getpid()
        try: p=psutil.Process(this_id)
        except: p=False
        
        stats={}
        stats['mem']=p.get_memory_info().rss
#         stats['cpu']=p.cpu_percent(interval=0.1)
        stats['create_time']=p.create_time()
        stats['io_counters']=p.io_counters()

        print ("mem: "+str(stats['mem']))
        
        
        if False:
            process='python'
            print ("Checking process memory...")
            plist=psutil.get_process_list()
            print ("Got process list...")
            for item in plist:
                print ("For: "+str(item))
                try: p=psutil.Process(item.pid)
                except: p=False
        
                if p:
                    try:
                        ddict=str(p.as_dict())
                        name=str(p.name()).lower()
                        exe=str(p.exe()).lower()
                        create_time=p.create_time()
                        io_counters=p.io_counters()
                    except:
                        ddict=''
                        name=''
                        exe=''
                        create_time=''
                        io_counters=''
                    try: parent=str(p.parent().name())
                    except: parent=''
                    
                    if re.search(r''+process,name):
                        mem=p.get_memory_info().rss
                        cpu=p.cpu_percent(interval=0.1)
                        liner=str(item.pid)+","+str(name)+","+str(parent)+","+str(mem)+","+str(cpu)+","+str(exe)+","+str(io_counters)
                        print (liner)
        return stats
    
    #https://gist.github.com/meganehouser/1752014
    def get_ram_used(self):
        percent_used=100
        if self.is_windows:
            #print psutil.cpu_percent(interval=0.1)
            #print(psutil.phymem_usage())#svmem(total=17057431552L, available=1096183808L, percent=93.6, used=15961247744L, free=1096183808L)
            #print(psutil.virtual_memory())
            #ram=psutil.virtual_memory()
            #percent_used=float(ram[2])

            try:
                percent_used = float(psutil.used_phymem()) / self.max_mem * 100
            except Exception as e:
                print ("[psutil] error on windows or version: "+str(e))
                mem=psutil.virtual_memory()
                percent_used=mem.percent

        else:
            mem=psutil.virtual_memory()
            #svmem(total=10367352832, available=6472179712, percent=37.6, used=8186245120, free=2181107712, active=4748992512, inactive=2758115328, buffers=790724608, cached=3500347392, shared=787554304)
            percent_used=mem.percent
            
        return percent_used

    def get_cpu_used(self,interval=0.2):
        # 0.0 is instannt so will be off
        percent_used=100
        if self.is_windows:
            percent_used = psutil.cpu_percent(interval=interval, percpu=False)
        else:
            percent_used = psutil.cpu_percent(interval=interval, percpu=False)
        return percent_used
    
    def get_obj_size(self,the_object):
        return sys.getsizeof(the_object)
            
def profile_linux():    
    Perf=Performance_Tracker()
#    Perf.start()
#    Perf.server_profile()
#    Perf.end_print()

    if False:
        cpu=Perf.linux_cpu_list()
        ram=Perf.linux_ram_list()
        space=Perf.linux_free_space()
        free_ram=Perf.linux_free_mem()
        print ("Total apache ram free: "+str(free_ram))
        print ("Total apache ram used: "+str(ram))
        print ("Total apache cpu used: "+str(cpu))
        print ("Total apache space left: "+str(space))


    print ("Ram: "+str(Perf.get_ram_used()))
    print ("CPU: "+str(Perf.get_cpu_used()))
    return
    
def main():
    Perf=Performance_Tracker()
    if Perf.is_windows:
        print ("Windows profile:")
        #Perf.windows_process_memory()
        print ("Ram: "+str(Perf.get_ram_used()))
        print ("CPU: "+str(Perf.get_cpu_used()))
    else:
        print ("Ram: "+str(Perf.get_ram_used()))
        print ("CPU: "+str(Perf.get_cpu_used()))
    return

def dev_orphans():
    pid_firefox='32185'
    pid_firefox='1999'

    #p=psutil.Process(item.pid)
    p=psutil.Process(int(pid_firefox))
    print ("FOR: "+str(p.name()))
    print ("FOR: "+str(p.cmdline()))

    print ("FOR: "+str(p.create_time()))
    import time
    ddd=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(p.create_time()))
    print ("OK: "+str(ddd))

    print ("FOR: "+str(p.parent().name()))

#j1293678383.0799999
#>>> time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(p.create_time()))
#'2010-12-30 04:06:23'

    parent=p.parent()
    pp=parent.parent()
    if pp:
        print ("FOR parent parent : "+str(pp.name()))
        print ("FOR parent parent : "+str(pp.cmdline()))
    return


"""
                try: name=str(p.name()).lower() #win
                except: name=str(p.name).lower()
                    dicta['cmdline']=p.cmdline()
                except Exception as e:
                        ddict=str(p.as_dict())
                        exe=str(p.exe()).lower()
                        create_time=p.create_time()
                        io_counters=p.io_counters()
                    try: parent=str(p.parent().name())
                    except: parent=''
                    try: mem=p.get_memory_info().rss
                    except:
                    try: cpu=p.cpu_percent(interval=0.1)
"""


if __name__ == '__main__':            
    profile_linux()
#    dev_orphans()
#    main()
    



