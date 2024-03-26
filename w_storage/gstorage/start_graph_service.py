import re
import sys,os
import json
import uuid
import datetime
import copy

LOCAL_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '.'))+"/"
sys.path.insert(0,LOCAL_PATH)

from gneo4j import Neo4j_Interface

sys.path.insert(0,LOCAL_PATH+'../../')
from get_logger import setup_logging
logger = setup_logging()


#0v1# JC  Sep  5, 2023  


def NOTES_start_neo4j_db():
    print ("1.  recall, vmware gretnet")
    print ("2.  vmx at: R:\from_Windows7_OS\vms\gretnet_MAR30_2021_neo4j_vm_OK1\neo4j_vm_OK1")
    print ("3.  login: bitnami/4gretnet!")
    print ("4.  get ip:  sudo ifconfig  (ideally on local wifi network)")
    print ("5.  neo4j status.  if not running, start:  sudo neo4j start")
    print ("6.  w_settings.ini has neo4j_address (also local option)")
    print ("    - remove option requires routing to .41 address on router")

    return

def dev_notes_on_starting():

    """
    NOTES:
    newer?
    C:\ccm\gretnet\grant4web\GRETNET_GITHUB\gretcode

    Put into w_settings
    neo4j_service use SERVER_IP is neo4j_local

    z800
    R:\from_Windows7_OS\vms\gretnet_MAR30_2021_neo4j_vm_OK1\neo4j_vm_OK1
    vmx.
    bitnami login worked:
    bitnami
    4gretnet!

    print ("- neo4j_service.py")
    print ("- vmware workstation 16 player")
    print ("neo4j libraries was 4.1.1 now 5.12.0")

    """

    return

def dev1():
    return

def get_neo():
    logger.info("Connecting to Neo4j...")
    Neo=Neo4j_Interface()
    Neo.connect()
    return Neo

def test_cypher_query():
    Neo=get_neo()

    stmt='MATCH (n) RETURN COUNT(n) as TotalNodes;'
    logger.info("stmt: "+str(stmt))
    for dd in Neo.iter_stmt(stmt):
        print ("> "+str(dd))

    return

def install_apoc_for_admin_stuff():
    """
    *** See install_neo4j.py
    There is no procedure with the name apoc.meta.data registered for this database instance" indicates that the APOC (Awesome Procedures On Cypher) library is either not installed or not properly configured in your Neo4j database instance.


    // neo4j.conf and activate:
    dbms.security.procedures.unrestricted=apoc.*

    """

    return

if __name__=='__main__':
    branches=['dev1']
    branches=['dev_notes_on_starting']
    branches=['test_cypher_query']

    for b in branches:
        globals()[b]()
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
