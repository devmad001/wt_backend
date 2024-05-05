import os
import sys
import inspect
import codecs
import json
import re
import time
import datetime


LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")


from z_apiengine.database_models import AutoAudit
from z_apiengine.database import SessionLocal

#from get_logger import setup_logging
#logging=setup_logging()



#0v1# JC  Feb 29, 2023  Auto audit


"""
    AUTO AUDITOR
    - see dev_autoaudit for initial details, see apply_auto_audit.py for sample
    OVERVIEW:
    - An Incident is created if a audit test fails.
    - Tests are either schema based (like variable formats) or, expandible plugins

    - For simplest audit place Auditor around a function call.
    - For advanced audit, use the results of the Audit to route/loop/rerun the function with new parameters!
    
    DESIGN NOTES:
    - Try to avoid steering actions, routes and enforcing results.  But log where possible.

"""

## NOTES:
#> 

def register_plugin(scopes):
    def decorator(func):
        AutoAuditor.register_plugin(func.__name__, func, scopes)
        return func
    return decorator


class An_Incident:
    def __init__(self,phrase,scope=''):
        self.id=os.urandom(16).hex()
        self.phrase=phrase
        self.type=phrase  #Future have set of known incident types
        self.scope=scope
        self.suggested_actions=[]
        return
    
    def __str__(self):
        return self.phrase
    
    def suggest_action(self,action):
        if action:
            self.suggested_actions+=[action]
        return
    
    def dump(self):
        """ For serialization (storage) """
        return self.__dict__
    
    ## suggestion action?
    ## suggest what a good result looks like?



class AutoAuditor:
    plugins = {}  # Class-level plugin registry
    
    def __init__(self):
        self.counter=0
        self.all_incidents=[]
        self.all_reports=[]
        return
    
    def is_active(self):
        self.counter+=1
        return True
    
    def add_incident(self,incident_phrase):
        # Manual add (ie/ if just curious on logging)
        incident=An_Incident(incident_phrase)
        incidents=[incident]
        self.all_incidents+=[incidents] #double cause can have multiple run attempts
        self.all_reports+=[{}]
        return
    
    @classmethod
    def register_plugin(cls, name, plugin_func, scopes):
        for scope in scopes:
            if scope not in cls.plugins:
                cls.plugins[scope] = {}
            cls.plugins[scope][name] = plugin_func

    def run_audit_pipeline(self, scopes=[], schema={}, state={}):
        incidents, report = run_audit_evaluator(schema, state)

        # Iterate over each scope in the scopes list
        for scope in scopes:
            if scope in self.plugins:
                for plugin_name, plugin_func in self.plugins[scope].items():
                    try:
                        plugin_incidents, plugin_report = plugin_func(scope, schema, state)  # Pass scope to plugin
                        incidents.extend(plugin_incidents)
                        report.update(plugin_report)
                    except Exception as e:
                        print(f"Error in plugin {plugin_name}: {e}")
                        # Handle or log the error appropriately

        self.all_incidents += [incidents]  # Fixed: use += to extend the list
        self.all_reports += [report]  # Fixed: use += to extend the list
        return incidents, report

    def get_all_incidents(self):
        return self.all_incidents
    
    def dump_all_incidents(self):
        # .dump() for lists of lists (all_incidents and incidents are lists)
        return [incident.dump() for incidents in self.all_incidents for incident in incidents]
    
    def log_audit_results(self, case_id='', route=[], runtime=0, scopes=[], state={},results=[],suggested_actions=[]):
        #[] Validate required meta_system items
        
        ## Auto store the code point (caller info)
        caller_frame = inspect.stack()[1]
        state['caller_info'] = {
            'filename': caller_frame.filename,
            'line_number': caller_frame.lineno,
            'function_name': caller_frame.function
        }

    
        ## Build the audit record
        audit_record = {
            'id': os.urandom(16).hex(),
            'incidents': self.dump_all_incidents(),
            'report': self.all_reports,
            'the_date': datetime.datetime.now(),
            'case_id': case_id,
            'route': route,
            'runtime': runtime,
            'scopes': scopes,
            'state': state,
            'results': results,
            'suggested_actions': suggested_actions
        }
    
        # Extract and store incident types for easier querying
        incident_types = {incident.type for incidents in self.all_incidents for incident in incidents}
        audit_record['incident_types'] = list(incident_types)
    
        # Store the audit record in the database
        self._store_audit_results(audit_record)
        self._echo(audit_record)
    
    def _store_audit_results(self, audit_record):
        # Ensure all required fields are present and properly formatted
        required_fields = ['id', 'incidents', 'report', 'the_date', 'incident_types']
        for field in required_fields:
            if field not in audit_record:
                print(f"Missing required audit record field: {field}")
                return  # Consider handling this case more appropriately
    
        # Convert lists to strings for 'route' and 'scopes' if they are not already strings
        audit_record['route'] = ",".join(audit_record['route']) if isinstance(audit_record['route'], list) else str(audit_record['route'])
        audit_record['scopes'] = ",".join(audit_record['scopes']) if isinstance(audit_record['scopes'], list) else str(audit_record['scopes'])
        audit_record['results'] = ",".join(audit_record['results']) if isinstance(audit_record['results'], list) else str(audit_record['results'])
        
        #Make suggested_actions unique
        if audit_record.get('suggested_actions',[]):
            audit_record['suggested_actions'] = list(set(audit_record['suggested_actions']))
            audit_record['suggested_actions'] = ",".join(audit_record['suggested_actions']) if isinstance(audit_record['suggested_actions'], list) else str(audit_record['suggested_actions'])
        if not audit_record.get('suggested_actions'):
            audit_record['suggested_actions'] = ""
    
        # Insert the audit record into the database
        with SessionLocal() as db:
            db.add(AutoAudit(**audit_record))
            try: db.commit()
            except Exception as e:
                print ("[warning] db error on insert likely out of sync: "+str(e))

            print("[debug] Saved audit record to db")
    

    def _echo(self,dd):
        print ("=== AUDIT RAW RESULTS:")
        ## MUST MANUALLY SERIALIZE!!
        ddcopy=dd.copy()
        ddcopy['the_date']=str(ddcopy['the_date'])

        print (json.dumps(ddcopy,indent=4))
        return
    
    def stop_audit(self):
        return
    

############################################
#  SCHEMA AUDITOR
############################################
def run_audit_evaluator(schema,state):
    ## First-pass is general schema
    #- Consider logging incident with id of record!
    #- ( plugin or Second-pass is plugin-specific )

    incidents=[]
    report={}

    ## Run general schema
    for data in state.get('data',[]):
        for schema_key in schema:
            if not schema_key in data: continue
            
            ## Check data type
            if 'type' in schema[schema_key]:
                if not type(data[schema_key])==schema[schema_key]['type']:
                    incidents+=[An_Incident('Type mismatch: '+schema_key)]
    
            ## Check data format
    
            ## Check data values
            if 'min' in schema[schema_key]:
                if data[schema_key]<schema[schema_key]['min']:
                    #incidents+=[An_Incident('Bad min value: '+schema_key+" "+str(data[schema_key]))]
                    incidents+=[An_Incident('Bad min value: '+schema_key)]
            if 'max' in schema[schema_key]:
                if data[schema_key]>schema[schema_key]['max']:
                    incidents+=[An_Incident('Bad max value: '+schema_key)]
    
    return incidents,report


############################################
#   SAMPLE PLUGINS
############################################
#- use the decorator to register the plugin under what scope

@register_plugin(['dummy_check'])
def sample_plugin(scope, schema, state):
    incidents=[]
    report={}
    return incidents,report

@register_plugin(['dummy_check','set_of_plugins_B'])
def another_plugin(scope, schema, state):
    incidents=[]
    report={}
    return incidents,report


if __name__=='__main__':
    branches=['dev1']
    for b in branches:
        globals()[b]()





