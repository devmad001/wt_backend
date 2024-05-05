import os
import sys
import codecs
import json
import re
import time
import requests

import configparser as ConfigParser


LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")

from get_logger import setup_logging
logging=setup_logging()



#0v1# JC  Feb 26, 2023  Auto audit


"""
    AUTO AUDIT
    - validate system outputs against schema targets
    - validate system outputs against plugin expandible rules
    - hook audit into pipeline touchpoints
    - route processing as required (ie: done, rerun @extended, etc.)

"""


class AutoAuditor:
    def __init__(self):
        self.schema_type=None
        return
    
    def touch_plugins():
        return
    
    def get_schema(self,schema_type):
        self.schema_type=schema_type
        schema={}
        if self.schema_type=='dev1':
            pass
            #schema=self.get_schema_dev1()
        return schema
    
    def prepare_outputs(self,outputs,schema):
        ## Pre-calculations etc.
        #[ ] optionally move to function
        data=outputs

        return data
    
    def log_audit_results(self,audit_results):
        return


class AuditStorage:
    """
        Keep stand-alone db interface (ie/ resolved incidents may not restart main Auditor state)
    """
    def __init__(self):
        return
    """
        (Collect notes for design)
        - store audit incidents
        - store audit routes
        - store audit system outputs
        - store audit system meta
    """

class AbstractSystemOutputs:
    def __init__(self):
        return
    
    def dump(self):
        """
            Raw data outputs
            System status (ie/ upstream functions used, versions, rerun, etc.?)
        """
        outputs={}
        system_state={}
        return outputs
    

class A_Resolver:
    def __init__(self):
        return
    """
        (Collect notes for design)
        - is resolver exists?
        - can be a specific routing goal
        - 
    """

class An_Incident:
    def __init__(self):
        self.id=os.urandom(16).hex()
        return
    """
        (Collect incident design notes)
        - incident has: suggested resolver (route,direct,etc)
        - estimate metric ie/ ocr quality issue %
        - human reason
        - is resolved or requires action or requires review (db)?
        - idenfiy specific data formats or field requiring update (ie/ "date" fixer is generic resolver)
    """
    

"""
    **sample
    ## ACTION SPACE  (set of routes)
    #[A] route to rerun entire document at higher quality?
    #[B] route to rerun specific OCR elements?  (page-level etc)
    #[C] route to done
    #[D] route to done with warnings

"""

def audit_evaluator(data, system_meta, schema):

    # Combine evaluation, decision-making, and routing processes.
    ## DESIGN NOTES:
    #-> 
    
    report = []     # Human-readable summary of audit findings.
    tbd_db = []     # Data points flagged for potential storage or further analysis.
    incidents = {}  # Detailed records of each audit incident.
                    # Each incident includes a suggested action or resolver.

    ####################################
    # Schema-specific Evaluations
    # - Perform validations based on schema definitions to ensure data integrity.
    # - Examples include checking for valid currency formats in transaction amounts
    #   and verifying the presence and correctness of document dates.

    # Evaluate 'transaction_amounts' to ensure each is a valid currency amount.
    for transaction_amount in data.get('transaction_amounts', []):
        # Identify poor quality OCR by looking for multiple commas.
        if re.search(r'\,.*\,', transaction_amount):
            inc = An_Incident()  # Create a new incident instance for tracking.
            incidents[inc.id] = inc  # Log the incident by its unique ID.
    

    ####################################
    #   Plug-in Evaluations
    # - Apply additional, more complex rules that may be context-specific
    #   or require deeper analysis beyond basic schema validations.
    # - These can include checks like reconciling bank statement balances
    #   with transaction records or identifying discrepancies in summary entries.

    ## Sample rule addons (depending on scope)
    #[ ] summary entries are not transactions
    #[ ] date fields are correctly mapped and within a valid range

    return report, incidents



"""
    FUTURE NOTES:
    - 
"""
def dev_simulate_audit_flow():
    
    outputs=AbstractSystemOutputs().dump()
    system_meta='what was run already. rerun already. etc'

    schema_type='dev1' #[ ] possibly include audit_area (page2t, final, ocr, etc)

    Auditor=AutoAuditor()

    Auditor.activate_schema(schema_type)
    
    schema=Auditor.get_schema()
    
    ## Prepare audit values
    #- top level normalize to ie/ 1-dim key-value
    #- tbd on whether needed but data_meta would describe how to handle data
    data,data_meta=Auditor.prepare_outputs(outputs,schema)
    
    ## Evaluator
    report,incidents=audit_evaluator(data,system_meta,schema)
    
    ## Log results or db push for ie/ future review if successfull
    Auditor.log_audit_results(report,incidents)
    
    #################################
    ## RESOLVER   (fancy but put pattern here for now)
    #> route to rerun entire document at higher quality?
    #> route to rerun specific OCR elements?  (page-level etc)
    #> route to resolve specific field  (easy currency fix)
    
    route_decisions=[]

    return


def dev1():
    print ("> setup environments")

    print ("i)  adding audit hook into run_pipeline.py -> run_pipeline")
    print ("@:  out_normalize=do_normalize(mega,run=run,job=job)  #<-- prepare epages etc.")
    
    print ("ii)  call pipeline via test for TD. So, register page test (local file or remote or sync or..)")
    print (">> gold test should source given pdf to local file if can't find it online")

    return



if __name__=='__main__':
    branches=['dev1']
    for b in branches:
        globals()[b]()





