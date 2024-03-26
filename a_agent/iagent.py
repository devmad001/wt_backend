import os
import sys
import codecs
import json
import re
import time
import threading

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")

from w_storage.ystorage.ystorage_handler import Storage_Helper

from get_logger import setup_logging
logging=setup_logging()

Storage=Storage_Helper(storage_dir=LOCAL_PATH+"../w_datasets/pipeline")
Storage.init_db('jobs')
Storage.init_db('job_logs')

from algs_iagent import alg_get_case_files


#0v5# JC  Jan 17, 2024  Adjust case2job. Also, main_pipeline_finished
#0v4# JC  Nov 24, 2023  MIgrate to more formal c_jobs_manager (db, queue, classes, etc.)
#0v3# JC  Sep 22, 2023  Job logs
#0v2# JC  Sep 12, 2023  Integrate job scheduling
#0v1# JC  Sep  6, 2023  Init



"""
    SMART AGENT
    - various
    - clean abstract to undefined or specific api

    - job scheduling  (possible to migrate to another routine or rename this)

"""


STATES=[]
STATES+=['create_run_job','ocr_conversion']
STATES+=['start_main_processing_pipeline','end_main_processing_pipeline']
STATES+=['running_KBAI_processing_pipeline'] #<-- called from within pipeline (so can see status)
STATES+=['start_KBAI_processing_pipeline','end_KBAI_processing_pipeline']
STATES+=['wt_main_pipeline_finished']

class Smart_Agent():
    def __init__(self):
        self.lock = threading.Lock()
        return
    
    def dev_has_case_finished_ever(self,case_id):
        # ** beware will trigger a state change from PROCESSING -> DONE in case_pipeline.py
        ## Jan 17, 2024  Quick check of case job to see if its' ever finished
        #[ ] needs tests cause some exceptions like odd case2job lookup 
        finished_ever_dev=False
        job1=self.case2job(case_id)

        logging.info ("[debug] job ever finished?: "+str(job1))
        if 'case_id' in job1 and not case_id==job1['case_id']:
            #** was bug but keep this for now
            logging.error("[cases] don't match!")
            print ("WANTED CASE: "+str(case_id))
            print ("GOT    CASE: "+str(job1['case']))

        else:
            #wt_main_pipeline_finished': {'time': 1705524373},
            if 'wt_main_pipeline_finished' in job1.get('state',''):
                if 'time' in job1['state']['wt_main_pipeline_finished']:
                    finished_ever_dev=True
        
#        if 'end_KBAI_processing_pipeline' in job1.get('state',''):
#            finished_ever_dev=True
#        if 'end_main_processing_pipeline' in job1.get('state',''):
#            finished_ever_dev=True
        
        #strr=str(job1.get('state',''))
        ### Raw check?
        #if 'end_KBAI_processing_pipeline'
        return finished_ever_dev
    
    def get_case_jobs_newest_states(self,case_id):
        ## Sort by age so newest first
        states={}
        min_age_key=''
        min_age_value=-1
        
        ## 1/  Iterate over all jobs!
        jobs=[]
        for job in self.iter_all_jobs():
            if case_id==job.get('case_id',''):
                jobs+=[job]
                
        if jobs:
            ## 2/  Sort given
            sorted_jobs = sorted(jobs, key=lambda x: x.get('last_active', 0), reverse=True)
            
            newest_job=sorted_jobs[0]
            
            ## 3/  Get states of newest job
            states=self.get_case_states(case_id,job=newest_job)

        if states:
            min_age_key = min(states, key=lambda k: states[k]['age'])
            min_age_value=states[min_age_key]['age']
        return states,min_age_key,min_age_value
    
    def iter_all_jobs(self):
        for jkey in Storage.iter_database('jobs'):
            job=Storage.db_get(jkey,'jobs',name='jobs')
            yield job
        return
    def get_all_jobs_sorted(self):
        jobs=[]
        for job in self.iter_all_jobs():
            jobs+=[job]
        sorted_jobs = sorted(jobs, key=lambda x: x.get('last_active', 0), reverse=True)
        return sorted_jobs

    def get_next_job(self):
        global Storage
        ## ORG
        #dd={}
        #dd['case_id']='case_1'
        dd={}

        for job_id in Storage.iter_database('jobs'):
            job=Storage.db_get(job_id,'jobs',name='jobs')
            if job['state']=='requested':
                dd=job
                break
        return dd

    def get_case_states(self,case_id,job={}):
        # org sim_wt
        all_states={}
        if not job:
            job,is_created=self.create_job_request_dict(case_id=case_id)

        for state_name in job.get('state',[]):
            if not isinstance(job['state'],dict): continue
#            print ("[get_case_status] AT: "+str(job['state']))
            status_time=job['state'][state_name]
            #Patch
            if isinstance(status_time,dict):
                status_time=status_time.get('time',0)

            age=int(time.time())-status_time
            all_states[state_name]={}
            all_states[state_name]['age']=age
        return all_states

    def get_state_status(self,job_id,state): 
        #[ ] tbd test but not used
        age_hours=0
        status={}
        job=Storage.db_get(job_id,'jobs',name='jobs')
        if job:
            status=job.get('state',{}).get(state,{})
            if status:
                if isinstance(status,dict):
                    age=int(time.time())-status.get('time',0)
                else:
                    #assume time
                    age=int(time.time())-status
                age_hours=age/60/60

        return status,age_hours
    
    def case2job(self,case_id):
        ## newest job
        newest_case_job={}
        jobs=self.get_all_jobs_sorted() #** watch 
        if jobs:
            for job in jobs:
                if job['case_id']==case_id:
                    newest_case_job=job   #Bug
#D1#                    print ("case2job match at: "+str(case_id))
        return newest_case_job

    def note_job_status(self,job,state,the_value='',meta={}):
        global STATES
        if not state in STATES:
            raise Exception("[note_job_status] unknown state: "+str(state))
        if not job:
            raise Exception("[note_job_status] job required")

        ## For tracking inner states of job execution
        # See:  sim_wt:  create_run_job, upload_files, ocr_conversion,....
        job_id=job['job_id']
        time_now=int(time.time())

        ## LOAD AND UPDATE JOB
        with self.lock:  # acquire the lock
            job_stored=Storage.db_get(job_id,'jobs',name='jobs')
            if not job_stored: raise Exception("[note_job_status] job not found: "+str(job_id))
            job_stored.update(job)
    
            ## SET JOB STATUS AND RESAVE
            if not 'state' in job_stored or isinstance(job_stored['state'],str):
                job_stored['state']={}
            if not state in job_stored['state']:
                job_stored['state'][state]={}
    
            ## Store state variable:  it's value and extra meta and TIME!
            #- overwrite to latest value
            #- assume status happens at end of event
            if meta:
                job_stored['state'][state]['meta']=meta
            if the_value:
                job_stored['state'][state]['value']=the_value
            job_stored['state'][state]['time']=time_now
            
            ## Default last_active
            job['last_active']=time_now
    
            Storage.db_put(job_id,'jobs',job_stored,name='jobs')
            job=job_stored
        return job

    def TODO_listener_enqueues_request(self,job_request):
        return
    
    def TODO_auto_start_main_pipeline(self):
        #. cron, on request, etc.
        return

    def dump_job_status(self,case_id):
        stats={}
        stats['case_id']=case_id
        stats['status']='running'
        stats['job_id']='?'
        stats['started_on']=''
        stats['completed_on']=''
        stats['runtime']=''
        stats['excel_dump_filename']=''

        #versions?

        # State of extraction
        stats['transactions_count']=0
        stats['nodes_count']=0

        # Logs, errors, warnings

        return

    def store_job_request(self,job_request):
        global Storage
        stopp=multi_states

        ## Create record, update
        job_record=self.load_job(job_id=job_request['job_id'])

        if not job_record:
            ## CREATE new job (requested)
            job_state='requested'
            
            if not 'state' in job_request:
                job_request['state']={}
            job_request['state'][job_state]=time.time()

            Storage.db_put(job_request['job_id'],'jobs',job_request,name='jobs')

            logging.info("[JOB CREATED] : "+str(job_request['job_id']))

        else:
            pass # CHECK/update
            logging.info("[JOB REQUESTED note: EXISTS] : "+str(job_request['job_id']))
        return

    def load_job(self,job_id='',case_id=''):
        global Storage
        ## Ideally load via job
        #- alt will search ALL jobs for first case_id match

        job={}
        if job_id:
            job=Storage.db_get(job_id,'jobs',name='jobs')
        elif case_id:
            ## Reverse index or, for now, just iterate
            for id in Storage.iter_database('jobs'):
                job=Storage.db_get(id,'jobs',name='jobs')
                if job['case_id']==case_id:
                    break
                else:
                    job={}
        else:
            pass
        return job

    def create_job_request_dict(self,case_id=''):
        #Load or create!
        #* does not store
        is_created=False
        if not case_id: raise Exception("[create_job_request] case_id required")

        job=self.load_job(case_id=case_id)
        if not job:
            ## Create job request
            is_created=True

            ## Check source files
            case_path_filenames,case_filenames,base_dir=alg_get_case_files(case_id)
            dd={}
            dd['case_id']=case_id
            dd['state']={}
            dd['state']['requested']=int(time.time())
            dd['base_dir']=base_dir
            dd['filenames']=case_filenames
            dd['path_filenames']=case_path_filenames
            job=job_template(**dd)

            ## Store new job
            Storage.db_put(job['job_id'],'jobs',job,name='jobs')

        else:
            ## Hard code update to base dir
            case_path_filenames,case_filenames,base_dir=alg_get_case_files(case_id)
            job['base_dir']=base_dir
#D#            print ("BASE: "+str(base_dir))
        
        ## BASE JOB REFRESH INITIALS
        #i)  possible for case files to be added after job begins
        job=self._refresh_case_files(job)

        ## Validate job status?
        return job,is_created

    def _refresh_case_files(self,job):
        ## Possibly updated
        #[ ] deleting won't be used
        case_path_filenames,case_filenames,base_dir=alg_get_case_files(job['case_id'])

        ## Don't overwrite with nothing!
        if case_path_filenames:
            job['filenames']=case_filenames
            job['path_filenames']=case_path_filenames

            if not job['path_filenames']==case_path_filenames:
                logging.info("[info] UPDATED case files for: "+str(job['case_id']))

                ## Dummy check exists
                dd=Storage.db_get(job['job_id'],'jobs',name='jobs')
                if not dd:
                    raise Exception("[_refresh_case_files] job not found: "+str(job['job_id']))
                
                # Store
                Storage.db_put(job['job_id'],'jobs',job,name='jobs')
            else:
                pass #Same
        else:
            print ("[warning] no case files at: "+str(base_dir))
        return job

    def save_job_log(self,job_id,text='',the_type='info',log_entry=()):
        # types: info, error, etc
        data={}
        if log_entry:
            text=log_entry[0]
            data=log_entry[1]
        if the_type:
            data['the_type']=the_type

        if not text and log_entry: text=log_entry[1]
        data=lo

        dd={}
        dd['id']=job_id
        dd['itime']=int(time.time()) #in
        dd['text']=text
        dd['data']=data

        ## Append!
        logs=Storage.db_get(job_id,'job_logs',name='job_logs')

        id=job_id
        return
    
    def set_job_field(self,job,field,vvalue):
        #pages_count
        if not field in ['pages_count','page_active']:
            raise Exception("[set_job_field] unknown field: "+str(field))
        job_id=job['job_id']
        job_stored=Storage.db_get(job_id,'jobs',name='jobs')
        job_stored.update(job)
        job_stored[field]=vvalue
        Storage.db_put(job_id,'jobs',job_stored,name='jobs')
        return job_stored
    

def job_template(case_id='',state='created',base_dir='',filenames=[],path_filenames=[]):
    ## Formal mapping
    job={}
    job['case_id']=case_id

    job['version']=1
    job['job_id']=job['case_id']+"-"+str(job['version'])  #1:1 for now

    job['base_dir']=base_dir
    job['filenames']=filenames #Just file name
    job['path_filenames']=path_filenames
    job['state']=state
    job['next_actions']=[]
    return job


def dev_sample_pipeline():
    Agent=Smart_Agent()
    job=Agent.get_next_job()
    print ("[debug] next job: "+str(job))

    return

def dev1():
    ## Check request queue + status etc.
    #- built in memory

    print ("Smart Agent")
    print ("Check job state, enqueue or update")

    Agent=Smart_Agent()

    ## Process job request
    job={}
    job['case_id']='case_1'

    job['version']=1
    job['job_id']=job['case_id']+"-"+str(job['version'])  #1:1 for now

    job['base_dir']=''
    job['filenames']=[]   #Relative paths
    job['state']='requested'
    job['next_actions']=[]

    job_state=Agent.check_job_status(job['job_id'])

    print ("Job state for: "+str(job['job_id'])+":")
    print (str(job_state))

    b=[]
    b=['hardcode_case_1_demo_job']
    b=['handle_request_from_front_end']

    if 'hardcode_case_1_demo_job' in b:
        ## Build job local
        print ("[ ] a_normalize hardcoded files")

        ## INPUTS
        ddir=LOCAL_PATH+"../w_datasets/Bank Statements - for Beta Testing/"
        filename="07A210E6-B60D-46B6-9D40-9B3239237F05-list.pdf"
        path_filename=ddir+"07A210E6-B60D-46B6-9D40-9B3239237F05-list.pdf"
        case_id='case_1'

        ## MAP
        job['case_id']=case_id
        job['job_id']=job['case_id']+"-"+str(job['version'])  #1:1 for now

        ## Map
        job['base_dir']=ddir
        job['filenames']=[]   #Relative paths
        job['path_filenames']=[]   #Relative paths

        job['filenames']+=[filename]
        for filename in job['filenames']:
            job['path_filenames']+= [(ddir+filename,filename)] #Both

    if 'handle_request_from_front_end' in b:
        ## Build job local
        case_id='SGM BOA'

        case_path_filenames,case_filenames,base_dir=alg_get_case_files(case_id)

        job['case_id']=case_id
        job['job_id']=job['case_id']+"-"+str(job['version'])  #1:1 for now

        ## Map
        job['base_dir']=base_dir
        job['filenames']=case_filenames
        job['path_filenames']=case_path_filenames

        print ("[job request] : "+str(job))

    else:
        stopp=checkk

    ## Process job request
    Agent.process_job_request(job)

    logging.info("[info] done smart agent job request")
    return


def dev_job_logger():
    # Separate db for logging ongoing status/state

    case_id='case_schoolkids'

    Agent=Smart_Agent()
    job,is_created=Agent.create_job_request_dict(case_id=case_id)

    job_id=job['job_id']

    log_entry=('text',{})

    Agent.save_job_log(job_id,text='',the_type='info',log_entry=())

    print (" SAVED: "+str(log_entry))

    return


if __name__=='__main__':
    branches=['dev_sample_pipeline']
    branches=['dev1']
    branches=['dev_job_logger']
    for b in branches:
        globals()[b]()


"""
"""
