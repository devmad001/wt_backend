import os
import sys
import json
import re
import time
import random

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)

from auto_auditor import AutoAuditor
from auto_auditor import register_plugin
from auto_auditor import An_Incident



#0v1# JC  Feb 29, 2023  Auto audit


"""
    SKELETON FOR AUTO AUDITOR

"""


def dummy_resolver_A_bad(env_state):
    ## Do something
    env_state['temperature']=-300
    return env_state

def dummy_resolver_B_good(env_state):
    ## Do something
    env_state['temperature']=25
    return env_state



def sample_main_pipeline(TEST_SELF_active=False):
    ## Easy test setting
    TEST_SETTING_force_first_run_fails=TEST_SELF_active
    
    ## Route tracking object (list for simplicity)
    route=[]
    route+=['start']
    
    env_state={}

    ##########################################
    #  AUDIT CELL
    ##########################################
    #
    
    ## Sample schema:
    schema={}
    schema['temperature']={'type':int,'min':-100,'max':100}
    scopes=['dummy_check']

    Auditor=AutoAuditor()
    start_time=time.time()  #Optional 
    while Auditor.is_active():

        if random.choice([True,False]):
            route+=['dummy_resolver_A_bad']
            env_state=dummy_resolver_A_bad(env_state)
        else:
            env_state=dummy_resolver_B_good(env_state)
            route+=['dummy_resolver_B_good']
            
        ## PREPARE AND RUN AUDIT
        # schemas: are data/format standard related vs 'scope' which applies plugins
        incidents,report=Auditor.run_audit_pipeline(scopes=scopes,schema=schema,state=env_state)

        if not incidents:
            print ("[debug] no incidents at loop #" + str(Auditor.counter))
            break
        else:
            ## ADDRESS INCIDENTS BY ROUTING TO RESOLVERS 
            #** THIS LOGIC MAPS FROM SPECIFIC INDICENT TO RESOLVER
            #[ ] local logic for now:  if any incident just rerun max 1 time
            if Auditor.counter>1:
                break

    ## Finalize audit (assume not auto-save)
    case_id='1'
    runtime=time.time()-start_time
    
    
    #####################
    # MANUALLY ADD AN AUDIT INCIDENT
    #####################
    Auditor.add_incident('manual incident phrase')

    Auditor.log_audit_results(case_id=case_id,route=route,runtime=runtime,scopes=scopes,state=env_state)
    Auditor.stop_audit()
    #
    ##########################################


    ## SUMMARY
    print ("SUMMARY:")
    print('Route:',route)
    print ("REPORT: "+str(report))
    print ("env state: "+str(env_state))

    all_incidents=Auditor.get_all_incidents()
    
    for incidents in all_incidents:
        for incident in incidents:
            print ("INCIDENT: "+str(incident))
    
    ## Return 'meta' style results
    results={}
    results['route']=route
    results['all_incidents']=all_incidents

    return results



@register_plugin(['odd_content_not_3.5'])
def challenging_content(scope, schema, state):
    #** hard to enforce schema stuff while remaining flexible so have loosely bound but modular

    suggestive_actions=[]
    suggest_good_results=[]

    incidents=[]
    report={}
    
    ## Check state assuming
    if 'content' in state:
        
        # A)  recall if >250 numbers then yes challenging  (move this from codebase to here)
        if len(re.findall(r'[\d\.\,]+', state['content']))>250:
            Incident=An_Incident('content has over 250 numbers',scope='odd_content_not_3.5')
            Incident.suggest_action("use_gpt_4")
            incidents.append(Incident)
            
        # B)  if summary in text then do blanket gpt-4 suggestive action
        if re.search(r'summary',state['content'],re.IGNORECASE):
            ## Assume state 'models' would have '4' in it
            if '4' in str(state.get('models',[])):
                print ("[debug] ignore if it thinks gpt-4 already used")
            else:
                Incident=An_Incident('content has SUMMARY => no 3.5',scope='odd_content_not_3.5')
                Incident.suggest_action("use_gpt_4")
                incidents.append(Incident)
    
    return incidents,report


def test_minimalistic_audit():
    print ("Do custom test then log suggestion and log action and log final results")
    
    print ("[if current approach is weak model and see potential issue then route to bigger]")
    
    ## Implied logic:
    #i)  model used route has 3.5 but not 4 then check for low challenges
    #ii)  If 'SUMMARY' in blob  => require min 4
    blob='Does this contain CHECK SUMMARY word su mmary?'
    Auditor=AutoAuditor()
    
    env_state={}
    env_state['content']=blob
    env_state['models']=['gpt3.5']
    env_state['function_name']=''  #lineno etc.
    
    scopes=['odd_content_not_3.5'] # pre-check OR post check depending what comes out?

    schema={}
    incidents,report=Auditor.run_audit_pipeline(scopes=scopes,state=env_state)
    
    suggested_actions=[]
    for incident in incidents:
        print ("INCIDENT: "+str(incident))
        suggested_actions+=incident.suggested_actions
        
    ##Log or mark resolved or mark actions taken?
#    actions_taken=[]
#    route=actions_taken

    Auditor.log_audit_results(scopes=scopes,suggested_actions=suggested_actions,state=env_state)

    return



def test_auto_audit_pipeline():
    #** note a real test but you get the idea
    
    results=sample_main_pipeline(TEST_SELF_active=True)
    
    ## Check route where test forces first fail so should have both dummy functions
    #if 'dummy_resolver_A_bad' in results['route'] and 'dummy_resolver_B_good' in results['route']:
    
    print ("LEN: "+str(len(results['all_incidents'])))
    
    ## Keep functional style for now.  If incidents then should have more then 1 dummy function
    if len(results['all_incidents'])>1:
        count_dummies=0
        for route in results['route']:
            if 'dummy' in route:
                count_dummies+=1
        if count_dummies>1:
            print ("[test] test_auto_audit_pipeline:  PASS")
            return
        else:
            print ("[test] test_auto_audit_pipeline:  FAIL at route: "+str(results['route']))
            return
    
    return




if __name__=='__main__':
    branches=['sample_main_pipeline']
    branches=['test_auto_audit_pipeline']
    branches=['test_minimalistic_audit']

    for b in branches:
        globals()[b]()





"""


"""
