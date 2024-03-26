import os
import sys
import codecs
import json
import re
import time

#import threading
#import psutil

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")


#from w_storage.ystorage.ystorage_handler import Storage_Helper

from get_logger import setup_logging
logging=setup_logging()

from job_analytics import ALG_machine_has_resources

from jobs_manager import JobsManager
from jobs_model import JobModel

from a_agent.interface_manager import Manager_Interface #iagent -> Smart_Agent
from c_case_manager.case_analytics import interface_get_BE_cases_statuses

from w_utils import am_i_on_server
from z_server.mod_execute.performance import Performance_Tracker


ON_SERVER=am_i_on_server()

#  self.states = ["RUNNING", "PENDING", "DONE", "ERROR","REQUESTED"]


#0v3# JC  Jan 13, 2024  Basic test at test_job_case_queues.py
#0v2# JC  Dec 13, 2023  Track machine performance prior to spawn
#0v1# JC  Dec 10, 2023  To-the-point runner

"""
    MEGA JOB
    - Runs job "case processing" in the background
    - checks if resources available
    - pulls next job from FE c_case_manager
    [ ] document + test TODO
    [ ] test cases + ideally simplify where possible

NOTES:
> spawn option via c_execution/EXECUTE_JOB_SERVICE.py

"""



## ARCHITECTURE RECALL:
#- sqlite has job details for running
#- raw .py logs to case that ran
#- Job models, Case (uesr facing) models
#- Keep this entrypoint obvious + clean from start then expend in background if needed
#- Keep ledger of requests, status etc. (not in DB) so quick & easy view/history/audit/debug (esp if Jobs can memory fail and multi-process)


## Job LOGFILE
JOB_LOGFILE=LOCAL_PATH+"../w_datasets/jobs_log"
if not os.path.exists(JOB_LOGFILE):
    os.makedirs(JOB_LOGFILE)
JOB_LOGFILE=LOCAL_PATH+"../w_datasets/jobs_log/jobs_log.jsonl"


def log_dict_to_jobs_log(ddict):
    ddict['time']=time.time()
    ## Direct append dict to file
    with codecs.open(JOB_LOGFILE,'a','utf-8') as f:
        try: f.write(json.dumps(ddict)+"\n")
        except:
            f.write(str(ddict)+"\n") #** this is a hack to get around unicode errors
    return



def interface_get_verbose_job_status(case_id,MG=None):
    # "job" is separate from "case" status
    ## Use in FE_user.py for FE estimated view
    if not MG: MG=Mega_Jobber()
    vv={}
    try:
        vv=MG.get_verbose_state_of_case(case_id)
    except Exception as e:
        logging.info("[no job status - case unknown or not started?]: "+str(case_id)+": "+str(e))
        ## Default?

    return vv,MG


class Mega_Jobber:
    ## Use singletons to ensure distributed support

    def __init__(self):
        self.Manager=JobsManager() #< Jobs DB
        self.MInterface=Manager_Interface()  #<-- Smart_Agent + view into job + machine stats
        return
    
    def start_long_running_job_process_in_background(self,case_id):
        ## Assume all checks down
        
        #0) Get job object
        job_instance=self.Manager.query_jobs(query={'case_id':case_id})[0] #many?
        
        #[ ] final check multiple, check state, etc.
        
        if not job_instance.status=='RUNNING':
            #1)  run
            self.MInterface.start_long_running_job_process_in_background(case_id)

            #2)  update job queue status
            self.Manager.update_job_status(job_instance.id,status='RUNNING')
            
            ## Local validate state
            job_instance=self.Manager.query_jobs(query={'case_id':case_id})[0] #many?
            if not job_instance.status=='RUNNING':
                raise Exception("Job not running after start for case_id: "+str(case_id)+" job dict: "+str(job_instance.to_dict()))

        return

    def get_verbose_state_of_case(self,case_id):
        #is_done_processing, percent_complete (int) seconds_since_started, estimated_runtime
        #[ ] ideally detailed stage but tbd
        # ** use in FE_user.py for passing to front-end
        return self.MInterface.get_verbose_state_of_case(case_id)
    
    def has_case_been_processed_ever(self,case_id,verbose=False):
        return self.MInterface.has_case_been_processed_ever(case_id,verbose=verbose)

    def is_background_case_processor_running(self):
        return self.MInterface.is_background_case_processor_running()
    
    def iter_jobs(self,filter=None):
        for Job in self.Manager.query_jobs(query={}):
            yield Job
        return
    
    def get_next_priority_case_id_to_run(self):
        ## Case would have been previously REQUESTED
        #> check if previously failed etc

        case_id=''

        counts={}
        for Job in self.iter_jobs():
            try: counts[Job.status]+=1
            except: counts[Job.status]=1

            if Job.status=='REQUESTED':
                job_dict=Job.to_dict()
                logging.info("[NEXT JOB TO RUN]: "+str(job_dict))
                case_id=Job.case_id
                break

        if not case_id:
            print ("[debug] beware no next cases ready assume Job.status=REQUESTED")
            print ("[debug] case state counts: "+str(counts))
            #  case state counts: {'DONE': 131, 'ERROR': 41}

        return case_id
    
    def add_case_id_run_request_to_job_queue(self,case_id):
        ## Always log
        is_added=False
        reasons=[]

        job_log={}
        job_log['action']='requested_add_case_id_to_job_queue'
        job_log['case_id']=case_id
        log_dict_to_jobs_log(job_log)
        #self.Manager.count_all_job_records() #ready if want to log changes after
        
        ## Review Job state before adding?
        ## case_id already running or in queue?
        
        ## Get related Job(s) for case
        
        ## Set Job request
        
        jobs=self.Manager.query_jobs(query={'case_id':case_id})
        
        flag_add_new_job=False

        ## BASIC LOGIC!!
        
        if len(jobs)==0:
            logging.info("[MEGA] adding job to queue at request of case_id: "+str(case_id))
            flag_add_new_job=True
            job_instance=self.create_job(case_id,status='REQUESTED')
            self.Manager.add_job(job_instance)
            
            is_added=True

        else:
            if len(jobs)==1:
                print ("[debug] job detail: "+str(jobs[0].__dict__))

            is_added=False
            logging.info("[MEGA] NOT adding job to queue because (Job for case) already exists: "+str(case_id))
            print ("[debug]  [MEGA] NOT adding job to queue because (Job for case) already exists: "+str(case_id))
            flag_add_new_job=False

            #raise Exception("Case already exists")
            
            for job in jobs:
                logging.info("[MEGA] Job exists: "+str(job.to_dict()))

        return is_added
    
    def create_job(self,case_id,status=''):
        if not status:
            raise Exception("Must provide status")
        job_instance=JobModel(case_id=case_id,status=status)
        return job_instance
    

    def close(self):
        return



def practical_receive_run_request_put_to_job_queue(case_id):
    #> request comes from FE.  Create case -> upload file -> request run
    is_added=False
    MJ=Mega_Jobber()
    is_added=MJ.add_case_id_run_request_to_job_queue(case_id)
    MJ.close()
    return is_added


### SEPARATE ACTIONS FROM CODE SO CLEAR
def ACTION_start_background_case(MJ,next_case_id_to_run):
    MJ.start_long_running_job_process_in_background(next_case_id_to_run)
    return



###############################################
#  MAIN ENTRYPOINT FOR JOB CYCLE
###############################################
def interface_run_one_job_cycle(commit=True):
    """
    Executes one job cycle within the system. This function is a part of 
    the job execution interface and acts as a wrapper for the 'handle_one_job_cycle' function.

    The job cycle execution involves checking the job queue and preparing the job for 
    execution. If the 'commit' parameter is set to True (default), the job will be 
    processed and executed. If 'commit' is set to False, the function will only 
    check the job queue and prepare the job but will not actually process or execute it.

    This functionality allows for a dry-run scenario where the effects of a job cycle 
    can be tested without making any actual changes.

    Parameters:
    commit (bool): If True, the job cycle will be processed and executed.
                   If False, the job cycle will only be prepared, not executed.

    Returns:
    None
    """
    #> via c_exeuction/EXECUTE_JOB_SERVICE.py
    handle_one_job_cycle(commit=commit)
    return


def is_resources_ready_pull_new_job_request(MJ):
    print ("[ ] pull yes, but what about executing?")

    ## Logic
    is_resources_ready=False

    branch=['logic branch on only run if no other cases running']
    branch=['if machine cpu and ram look good then run a case'] #Or no run a case even if non running

    if 'logic branch on only run if no other cases running' in branch:
        #[1] If no background jobs, consider pulling new
        if not MJ.is_background_case_processor_running():
            is_resources_ready=True
    else:
        branch=['if machine cpu and ram look good then run a case'] #Or no run a case even if non running
        is_resources_ready=ALG_machine_has_resources()

    return is_resources_ready


def handle_one_job_cycle(commit=True):
    
    meta={}
    
    logging.info("="*40)
    logging.info("[handle_one_job_cycle] commit: "+str(commit))

    MJ=Mega_Jobber()
    
    cycle_action=''
    info={}
    info['actions']=[]
    
    ###############################################
    ## REFRESH RUNNING JOB STATUSES
    #
    actions_sub=practically_refresh_all_running_job_status()
    info['actions']+=actions_sub


    ###############################################
    ## Run a Case if "possible"
    #- ASSUMPTIONS:
    flag_started_a_case_in_background,info_sub=practically_run_a_case_if_possible(commit=commit)
    sub_actions=info_sub.pop('actions',[])
    info['actions']+=sub_actions
    info.update(info_sub) #Other
    
    ###############################################
    ## Pull a next case to run from FE
    #- if resources ready to run a case, do it
    if is_resources_ready_pull_new_job_request(MJ):
        if commit:
            actions_sub=practical_fetch_next_case_from_FE_if_never_ran_before(commit=commit)
            info['actions']+=actions_sub
        else:
            info['actions']+=['[commit False]  Resources ready to run queue item (could pull from FE)']
        
    logging.info("B  [Mega_Jobber cycle state info]: "+str(info))
    
    if info['actions']:
        print ("="*40)
        print ("[ONE CYCLE ACTIONS]:")
        for a in info['actions']:
            print ("[ACTION]: "+str(a))
            
    ## General info
    meta['actions']=info['actions']
    return meta


def practically_run_a_case_if_possible(commit=True):
    ## Called from main job cycler
    #- will spawn a background job (process case) if (logic ie: has resources)
    print ("[debug] practically run a case if possible (mega_job)...")

    flag_started_a_case_in_background=False
    MJ=Mega_Jobber()

    info={}
    info['actions']=[]
    info['flag_is_there_a_case_already_running']=MJ.is_background_case_processor_running()


    START_NEXT_CASE=True
    ASSUME_requested_case_has_local_files=True

    logging.info("A  [Mega_Jobber cycle state info]: "+str(info))

    ## LOGIC 1:    If system resources ready then attempt to start next case (assuming there's one in queue)
    resources_ready=ALG_machine_has_resources()

    logging.info("B  [Resources ready]: "+str(resources_ready))
    print       ("B  [Resources ready]: "+str(resources_ready))


    ## APPLY ABOVE LOGIC
    if resources_ready:
        START_NEXT_CASE=True
    else:
        START_NEXT_CASE=False

    
    ## Is there a requested case to run?
    if START_NEXT_CASE:
        next_case_id_to_run=MJ.get_next_priority_case_id_to_run()
        
        if next_case_id_to_run:
            logging.info("C  [Ready to run case id: "+str(next_case_id_to_run))
                    
            if commit:
                #*watch for immediate fail or check running
                print ("[debug] spawning in background: "+str(next_case_id_to_run))
                ACTION_start_background_case(MJ,next_case_id_to_run)
                info['actions']+=['Started case: '+str(next_case_id_to_run)]
                flag_started_a_case_in_background=True

            else:
                info['actions']+=['[commit False]  Otherwise would spawn this background  case: '+str(next_case_id_to_run)]
        else:
            logging.info("C  [ NO CASES READY ]")
            info['actions']+=['C NO CASES READY']
        
    return flag_started_a_case_in_background,info


def refresh_single_running_job_status(case_id,job_dict=None,is_a_case_running=False):
    MJ=Mega_Jobber()
    #** job background processes may fail and not update status
    
    ## INPUT STATES:   RUNNING
    ## OUTPUT STATUS:  DONE/ERROR
    NEW_STATE=job_dict['status']

    logging.info("[refreshing RUNNING] job state: "+str(case_id)+" "+str(job_dict))
    
    flag_has_case_ever_finished=False
    flag_is_case_still_running=False
    

    ## [1] Ever finished processing?
    flag_has_case_ever_finished=MJ.MInterface.has_case_been_processed_ever(case_id)
    
    ## [2]  Still running?
    ## ACTUALLY STILL RUNNING?
    
    if ON_SERVER:
        active_cases=MJ.MInterface.which_cases_are_running()
        logging.info("[refreshing RUNNING] active cases: "+str(active_cases))
        
        print ("[ ] watch: active_casess only works on server (not windows process)")
        if case_id in active_cases:
            flag_is_case_still_running=True
    else:
        print ("[-----] On local computer so assume case still running if ANY are")
        if is_a_case_running:
            flag_is_case_still_running=True
        
    if not flag_is_case_still_running:
        if flag_has_case_ever_finished:
            ## Update status
            logging.info("[refreshing RUNNING] case finished: "+str(case_id))
            MJ.Manager.update_job_status(job_dict['id'],status='DONE')
            NEW_STATE='DONE'
        else:
            logging.warning("[refreshing RUNNING] case never finished (and is not running): "+str(case_id))
            really_never_finished=MJ.has_case_been_processed_ever(case_id,verbose=True)
            print ("[debug] really?: "+str(really_never_finished))

            MJ.Manager.update_job_status(job_dict['id'],status='ERROR')
            NEW_STATE='ERROR'
    
    return NEW_STATE
    

def practically_refresh_all_running_job_status(verbose=True):
    MJ=Mega_Jobber()
    
    actions=[]

    case_id='6578e48c20668da6f77cd052' #" done" per ask 
#    refresh_single_running_job_status(case_id)
    
    print ("Precheck if any cases running..")
    flag_is_there_a_case_already_running=MJ.is_background_case_processor_running()


    for Job in MJ.iter_jobs():

        job_dict=Job.to_dict()
        if job_dict.get('status','')=='RUNNING':
            logging.info("[debug] JOB STATE RUNNING: "+str(job_dict))

            NEW_STATE=refresh_single_running_job_status(job_dict['case_id'],job_dict=job_dict,is_a_case_running=flag_is_there_a_case_already_running)
            
            if not NEW_STATE=='RUNNING':
                logging.info("[CASE STATE UPDATED] TO: "+str(NEW_STATE))
                actions+=['Updated job state for: '+str(case_id)+' from RUNNING to: '+str(NEW_STATE)]
                
        ## IGNORE If DONE
        elif job_dict.get('status','')=='DONE':
            pass

        else:
            if verbose:
                pass
#                logging.info("[debug] job status not running: "+str(job_dict))

    return actions



##########################
# FE "queue" -> job queue
##########################
def practical_fetch_next_case_from_FE_if_never_ran_before(commit=True,verbose=False):

    logging.info("="*60)
    logging.info("=  PULLING NEXT CASE FROM FE IF NEVER RAN BEFORE (commit: "+str(commit)+")")
    logging.info("="*60)

    #>> recall, LOCAL_add_case_request_to_job_queue
    #>> but from FE
    
    ### ASSUMPTIONS:

    
    MJ=Mega_Jobber()
    
    actions=[]
    count_jobs_already_processed=0


    ## ENTER AT PUSH OR PULL JOB
    #**watch imports
    branch=['poll_pull_job_requests']
    

    if 'poll_pull_job_requests' in branch:

        logging.info("PULL JOB REQUESTS...")
        logging.info("LOGIC: if case in FE system, (and not in job queue) enqueue in job queue")
        
        case_options=[]

        ## Pull all FE case options (all users)
#ORG        for case_id,processing_status,case_state,case_meta in interface_list_cases_states(all_states=True):
        for cdict in interface_get_BE_cases_statuses(limit=1000):
            if verbose:
                logging.info("[consider case for FE->Job]: "+str(cdict))

            ## Direct map at start for obvious
            case_id=cdict['case_id']
            state=cdict['state']
            case_meta=cdict['case_meta']
            case_state=cdict['case_state']

            is_option=True
            
            ## SELECT LOGIC 1:
            if not case_meta:
                if verbose:
                    logging.info("[no case meta] case: "+str(case_id))
                continue #No posted details
            
            ## SELECT LOGIC 2:
            flag_has_files=False
            file_urls=case_meta.get('file_urls',[])

            if file_urls and '//' in str(file_urls): #'STRING' bad
                flag_has_files=True
            else:
                flag_has_files=False
                is_option=False
                if verbose:
                    logging.info("[no files] case: "+str(case_id))

            ## maybe stats
#            last_updated_unix_time=case_state.get('last_updated',0)
#            age_hours=(time.time()-last_updated_unix_time)/3600.0

            ## CASE ok.  Enqueue from FE to Job
            if is_option:

                print ("-"*30+" BELOW IS CASE OPTION FOR RUNNING age: xxx") #"+str(int(age_hours))+" hrs")

#                print ("CASE OPTION A: "+str(case_id)+" --> "+str(processing_status))
                print ("[debug] CASE STATE: ["+str(case_id)+"] State: "+str(state)+" case_state: "+str(case_state))
                print ("[debug] CASE META: "+str(case_id)+" --> "+str(case_meta))
                
                ## Already seen or in queue?

                #-> case_state last_updated
                #-> case_meta case_creation_date
                case_options.append(case_id)




        ## Ignoring FE states, check if should be in queue or seen or status
        #[ ] watch if previous errors etc.
        #[ ] prioritize by case creation (latest gets priority)
        print ("[debug] considering "+str(len(case_options))+" case options..")
        if case_options:
            #Reverse
            case_options=case_options[::-1]

            for case_id in case_options:
                is_added=False

                ## FINAL LOGIC CHECK (can add case to job from here but ensure never finished)
                flag_has_case_ever_finished=MJ.has_case_been_processed_ever(case_id)
                
                if flag_has_case_ever_finished:
                    #D1# print ("CASE (add to job queue) OPTION: "+str(case_id)+" already processed")
                    count_jobs_already_processed+=1
                    continue
                else:
                    print ("[case has never been processed] CASE OPTION: "+str(case_id))
                    
                    if commit:
                        is_added=practical_receive_run_request_put_to_job_queue(case_id)
                        print ("CASE ADDED to job queue? "+str(case_id)+" --> "+str(is_added))
                    else:
                        print ("[DEBUG MODE (no commit)] not actually selecting... CASE OPTION: "+str(case_id)+" --> "+str(is_added))
                        break

                
                if is_added:
                    print ("debug added case: "+str(case_id))
                    actions+=['[PULL] Added case to queue: '+str(case_id)]
                    break
                
    ## Basic counts
    print ("[info] count of jobs reviewed but already processed: "+str(count_jobs_already_processed))
    return actions


def ADMIN_remove_jobs_from_queue():
    a=okkk
    jobs=[]
    jobs+=['657904fc20668da6f77cd64a']
    jobs+=['657904d420668da6f77cd640']
    
    MJ=Mega_Jobber()
    for case_id in jobs:
        query={'case_id':case_id}
        print ("ADMIN REMOVE JOB FROM QUEUE: "+str(query))
        MJ.Manager.delete_job(query=query)

    return


## Using local job if ERROR set to REQUESTED
def practical_requeue_error_runs():
    actions=[]
    max_requeue=1
    MJ=Mega_Jobber()
    for Job in MJ.iter_jobs():
        job_dict=Job.to_dict()
        if job_dict.get('status','')=='ERROR':
            logging.info("[requeueing ERROR] job state: "+str(job_dict))
            MJ.Manager.update_job_status(job_dict['id'],status='REQUESTED')
            actions+=['Requeued job: '+str(job_dict['case_id'])]
            max_requeue-=1
        if not max_requeue: break
    return actions



def dev_state_and_resources():
    MJ=Mega_Jobber()
    if False:
        #print ("BACKGROUND: "+str(MJ.is_background_case_processor_running()))
        case_id='6579c0370c64027a3b9f2d46' #SHould have finished but marked as error cause not ran??
        print ("EVER DONE: "+str(MJ.has_case_been_processed_ever(case_id)))
        print ("ACTIVE CASES: "+str(MJ.MInterface.which_cases_are_running(verbose=True)))
    Perf=Performance_Tracker()
    cpu=Perf.get_cpu_used(interval=3)
    ram=Perf.get_ram_used()

    print ("CPU: "+str(cpu)+" ram: "+str(ram))

    print ("MACHINE HAS RESOURCES?: "+str(ALG_machine_has_resources()))

    return


def dev1():
    MJ=Mega_Jobber()

    b=['local_try_one_job_cycle']

    b=['local_check_job_queue_statuses']

    if 'local_try_one_job_cycle' in b:
        handle_one_job_cycle()

        
    if 'local_check_job_queue_statuses' in b:
    
        print ("JOB STATUSES  ===============")
        # JOB: {'name': None, 'case_id': 'simulated_case_request_case_1', 'data': None, 'status': 'REQUESTED', 'id': 1}
        print ("Jobs in queue: "+str(MJ.Manager.count_all_job_records()))
        for Job in MJ.iter_jobs():
            print ("JOB: "+str(Job.to_dict()))
            
#    #[x] moved to ADMIN_mega_job
#    if 'ADMIN_things' in b:
#        #case_id='simulated_case_request_case_1'
#        #ADMIN_remove_job_from_queue(case_id=case_id)
#
#        case_id='65713fc888061612aa2fc3c6'
#        LOCAL_add_case_request_to_job_queue(case_id)

    #flag_is_case_already_queued=False
    #flag_does_system_have_resources_to_start=False

    return

def local_echo_job_queue_status():
    print ("> local echo job queue status")

    #(elsewhere but this for simplicity)
    MJ=Mega_Jobber()
    for Job in MJ.iter_jobs():
        print ("JOB: "+str(Job.to_dict()))
    
    return
 

if __name__=='__main__':

    branches=['dev1']
    branches=['check_job_running_status']
    branches=['practically_refresh_all_running_job_status']

    branches=['ADMIN_remove_jobs_from_queue']

    branches=['practical_fetch_next_case_from_FE_if_never_ran_before']

    branches=['practical_requeue_error_runs']

    branches=['dev_jon13']

    
    branches=['local_echo_job_queue_status']

    branches=['interface_run_one_job_cycle']
    

    for b in branches:
        globals()[b]()



print ("**see entry_workflows_jobs because connects to agent")


"""

"""
