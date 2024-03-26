import sys,os
import requests

try: import ConfigParser
except: import configparser as ConfigParser

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"



#0v4# JC  Sep  5, 2023  Evolve from gret

## NOTES ON VM staic
#i) sudo ifconfig {note name of interface: ens160}
#> inet 192.168.0.23 netwask 255.255.255.0 broadcast 192.168.0.255
#ii) get current default gateway:
#> ip r | grep ^def   --> 192.168.0.1
#iii)  get current dns
#> systemd-resolve --status --> 192.168.0.1
#iv)  edit  /etc/network/interfaces.: https://www.ibm.com/support/pages/how-set-linux-vmware-workstation-static-ip-ipv4: https://www.ibm.com/support/pages/how-set-linux-vmware-workstation-static-ip-ipv4
#???
#v)   sudo service networking restart
#^^above still changed?!
#- do again https://www.howtoforge.com/debian-static-ip-address


Config = ConfigParser.ConfigParser()
Config.read(LOCAL_PATH+"neo4j_settings.ini")

SERVER_USERNAME=Config.get('neo4j_local','username')
SERVER_PASSWORD=Config.get('neo4j_local','password')

MainConfig = ConfigParser.ConfigParser()
MainConfig.read(LOCAL_PATH+"../../w_settings.ini")

SERVER_IP=MainConfig.get('neo4j','neo4j_address')
SERVER_PORT=MainConfig.get('neo4j','neo4j_port')
SERVER_PROTOCOL=MainConfig.get('neo4j','neo4j_protocol') #http

#SERVER_IP=Config.get('neo4j','neo4j_address_local')


GLOBAL_AUTO_FIND_IP=True


class Manage_Neo4j_Service(object):

    def __init__(self):
        global SERVER_IP, SERVER_PORT, SERVER_PROTOCOL

        self.server_port=SERVER_PORT #7474 #/browser/
        self.server_ip=SERVER_IP
        self.server_protocol=SERVER_PROTOCOL
        self.server_endpoint=self.server_protocol+'://'+self.server_ip+":"+str(self.server_port)
        return
    
    def connect(self,username='',password='',ip=''):
        global SERVER_USERNAME,SERVER_PASSWORD,SERVER_IP
        if not username: username=SERVER_USERNAME
        if not password: password=SERVER_PASSWORD
        if not ip: ip=SERVER_IP
        return
    
    def auto_install_service(self):
        return
    def auto_maintenance(self):
        return
    def auto_migration(self):
        #  <option to move data>
        return
    
    def start_service(self,method='vmrun'):
        if not self.check_service():
            print ("[warning] could not start neo4j -- check virtual machine")

            if False:
                moved_auto=start_changed
                #OVERVIEW:
                #i)   via vmrun
                #ii)  via vmplayer
                #vmrun -T ws start "F:\VMWare-VMs\S1.vmx"
                #vmrun start "C:\VMs\D10AMP\D10AMP.vmx" nogui
                # use task scheduler if requires admin disks
                
                #OPTION 2;  background service
                #https://www.coretechnologies.com/products/AlwaysUp/Apps/RunVMwarePlayerAsAService.html
                
                #For example (Target): "C:\Program Files (x86)\VMWare Player\vmplayer.exe" "C:\Virtual Machines\Serve\Serve.vmx"
                
                if method=='vmrun':
                    options=" nogui"
                    options=""
    
                    vmrun_exe="C:/Program Files (x86)/VMware/VMware Workstation/vmrun.exe"
                    vmx_path="F:/vms/neo4j/neo4j_vm_OK1/bitnami-neo4j-4.1.3-0-linux-debian-10-x86_64-nami.vmx"
    
                    vm_cmd='" "'+vmrun_exe+'" start "'+vmx_path+'" "' #** double quote the double quoted
                    print ("[starting neo4j vm]: "+vm_cmd)
                    os.system(vm_cmd)
        return
    
    def check_service(self):
        is_ok=False
        # Check if process running
        #7474 service as bolt  no request
        
        endpoint=self.server_protocol+"://"+self.server_ip+":"+str(self.server_port)
        try: r=requests.get(endpoint,timeout=3)
        except: r=None
        if r and r.status_code==200:
            is_ok=True
        else:
            print ("[warning] could not locate neo4j service at: "+str(endpoint))
        return is_ok



def start_neo4j_background_service():
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

def debug_server():
    print ("> neo4j status")
    print ("  <if not running?>  but is?")
    print ("vi /opt/bitnami/neo4j/logs/neo4j.log")
    return

def check_server():
    Neo=Manage_Neo4j_Service()
    is_ok=Neo.check_service()
    print ("IS OK: "+str(is_ok))
    return

if __name__=='__main__':
    branches=['start_neo4j_background_service']
    branches=['debug_server']
    branches=['check_server']

    for b in branches:
        globals()[b]()
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
