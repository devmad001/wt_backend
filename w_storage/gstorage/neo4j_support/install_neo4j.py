import sys,os
import requests

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"

#0v4# JC  Sep 11, 2023  Setup

def notes_add_user():
    """
        1)  web browser http://3.20.195.157:7474/browser/  (possible via cypher too)
        2)  :use system
        3)  CREATE USER wt_hub SET PASSWORD 'Watchtower2024!' CHANGE NOT REQUIRED;
        4)  GRANT ROLE 
    """
    return

def dev_install_notes():
    #1)  github
    #2)  ec2 gp3 ssd, 200gb, t3 small (4gb ram), ubuntu 22

    ## DigitalOcean setup new sever options
    # https://www.digitalocean.com/community/tutorials/initial-server-setup-with-ubuntu-22-04

    """
        ufw firewall management?!
        sudo ufw status
    """

    """
    When the upgrade is finished, reboot if necessary.

    Once the upgrade is completed, install the Neo4j dependencies with the command:

    sudo apt-get update && sudo apt-get upgrade -y
    sudo apt-get install wget curl nano software-properties-common dirmngr apt-transport-https gnupg gnupg2 ca-certificates lsb-release ubuntu-keyring unzip -y
    """
    cmds=[]
    cmds+=['sudo apt-get update && sudo apt-get upgrade -y']
    cmds+=['sudo apt-get install wget curl nano software-properties-common dirmngr apt-transport-https gnupg gnupg2 ca-certificates lsb-release ubuntu-keyring unzip -y']

    ## DigitalOcean neo4j install
    #https://www.digitalocean.com/community/tutorials/how-to-install-and-configure-neo4j-on-ubuntu-22-04

    ## Keys + repository pointer
    cmds+=['curl -fsSL https://debian.neo4j.com/neotechnology.gpg.key |sudo gpg --dearmor -o /usr/share/keyrings/neo4j.gpg']
    cmds+=['echo "deb [signed-by=/usr/share/keyrings/neo4j.gpg] https://debian.neo4j.com stable 4.1" | sudo tee -a /etc/apt/sources.list.d/neo4j.list']

    cmds+=['sudo apt update'] #again?

    cmds+=['sudo apt install -y neo4j']

    ## As a service

    cmds+=['sudo systemctl enable neo4j.service']
    cmds+=['sudo systemctl start neo4j.service']
    cmds+=['sudo systemctl status neo4j.service']

    ## Login and pw

    cmds+=['cypher-shell']
    cmds+=['neo4j/neo4j']

    #wt password:  see ref aws

    ### Remote access
    cmds+=['sudo vi /etc/neo4j/neo4j.conf']
    # uncomment listen to all:
    cmds+=['dbms.default_listen_address=0.0.0.0']
    cmds+=['dbms.connector.bolt.listen_address=:7687']
    cmds+=['dbms.connector.http.listen_address=:7474']
    cmds+=['dbms.security.procedures.unrestricted=apoc.*'] #apoc but must be installed

    print ("*********SEE APOC install instructions below")

    ### Firewall
    cmds+=['sudo ufw enable']
    cmds+=['sudo ufw status']

    """
    sudo ufw allow 22
    sudo ufw allow 22
    sudo ufw allow 22
    sudo ufw allow 22

    BEWARE:
    sudo ufw default allow incoming

    BOLT user access:
    #sudo ufw allow from 203.0.113.1 to any port 7687 proto tcp
    sudo ufw allow 7687
    sudo systemctl restart neo4j

    """

    #CHECK for external access!!
    #- may take a bit from another server if server was down!

    #? cypher-shell -a 'neo4j://3.20.195.157:7687'

    ## This library see gneo4j.py -> w_settings.ini -> neo4j_*

    return

def test_remote_access():
    ip=''
    username='neo4j'
    password=''
    return


def REF_OLD_start_neo4j_background_service():
    Neo=Manage_Neo4j_Service()
    
    Neo.start_service()

    print ("LOGIN:  bitnami/4gretnet!")
    print ("IP:  sudo ifconfig")
    print ("CHECK:  neo4j_settings.ini")
    print ("[1]  check if connected to normal meow_pwr_5")
    print ("VMWARE org specific VMnet4 custom virtual network")
    print ("virtual network editor shows bridged to wireless...")
    print ("[2] jc after trying to change ip address then boot then ok")
    print ("ifconfig ens160 192.168.0.28 netmask 255.255.255.0")
    
    #ifconfig enp0s3 192.168.178.32 netmask 255.255.255.0
    #static options: https://devconnected.com/how-to-change-ip-address-on-linux/
    #>> 
    return

def apoc_activation():
    """

    WORK!  COMMENTS:
    - my 4.1.13 version matches to apoc 4.1.0.2
    - if you don't match, neo4j will keep restarting
    - no logs produced so must use journalctl system level
    - once works, ok

    my neo4j is 4.1.13
    https://neo4j.com/labs/apoc/4.1/installation/
    4.1.0.0 4.1.0 (4.1.x)
    suggests:
    Neo4j: 4.1.13
    Neo4j-Apoc: 4.1.0.2


    *** See install_neo4j.py
    There is no procedure with the name apoc.meta.data registered for this database instance" indicates that the APOC (Awesome Procedures On Cypher) library is either not installed or not properly configured in your Neo4j database instance.


    // neo4j.conf and activate:
    dbms.security.procedures.unrestricted=apoc.*

    cmds+=['sudo vi /etc/neo4j/neo4j.conf']
    sudo systemctl restart neo4j

    ## INSTALL STEPS:
    sudo wget https://github.com/neo4j-contrib/neo4j-apoc-procedures/releases/download/4.1.0.2/apoc-4.1.0.2-all.jar


?or ubuntu or 777
sudo chown -R neo4j:neo4j /var/lib/neo4j/plugins/


    """

    return

def debug_no_neo4j():
    """
    you restarted and can't connect?
     sudo systemctl restart neo4j
     sudo systemctl start neo4j
     sudo systemctl status neo4j

     SYSTEM LOGS:
     sudo journalctl -u neo4j -e


     MISSING:
     sudo cat /var/log/neo4j/neo4j.log
     sudo tail -f /var/log/neo4j/neo4j.log

    """
    return


if __name__=='__main__':
    branches=[]

    for b in branches:
        globals()[b]()
        
        
"""
install python 3.10 on ubuntu

open port 80 for ubuntu user
sudo apt install authbind

sudo touch /etc/authbind/byport/80
sudo chmod 777 /etc/authbind/byport/80

authbind python3 your_flask_app.py




### github username etc.
sudo apt-get install libsecret-1-0 libsecret-1-dev
sudo apt-get install git-credential-libsecret
git config --global credential.helper libsecret


"""
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
