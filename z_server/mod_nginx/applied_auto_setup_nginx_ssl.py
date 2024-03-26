import os
import sys
import re


from auto_nginx import Auto_Server_Setup
from mod_execute.mod_execute import The_Execute_Command


LOCAL_PATH=os.path.join(os.path.dirname(__file__), "./")

#021# ** THIS can mostly be ignored
#021# JC Jan 19, 2023  Use with chats kit new server
#0v1# JC Apr  1, 2021  Basic ssl/https setup


##NOTES:
#- see auto_nginx.py
#- see mod_ssl directory


###################################
#  APPLIED Auto_Server_Setup  NOTES
###################################
#
## GRETNET landingpage
# A Record, @, 185.199.108.153
# A Record, @, 185.199.109.153
# A Record, @, 185.199.110.153
# A Record, @, 185.199.111.153
# CNAME,  www, panamantis.github.io.
#52.71.179.158

OPTIONS=[]
OPTIONS=['test_base_commands']
OPTIONS=['install_python_env']
OPTIONS=['test_base_commands']

#OPTIONS=['install_ssl_libraries']
OPTIONS=['install_python_virtual_env_and_libs']  #** required for server share so may as well do early


CONFIG={}
CONFIG['target_project_directory']='~/myproject'
CONFIG['workon']='gretnet'                    # virtual env name
CONFIG['python_location']='/usr/bin/python3'  # virtual env name
CONFIG['domains']=['gretnet.com']     # may have system domains too to manage?
CONFIG['user']='ubuntu'
CONFIG['full_project_directory']="/home/"+CONFIG['user']+re.sub(r'\~','',CONFIG['target_project_directory']) #/home/buntu/myproject


def do_complete():
    global OPTIONS
#    print ("Setup virtual env first?  0icmds+=['cd ~/myproject && python3 -m venv myprojectenv']

    
    b=[]
    b=['step_point_namecheap_to_ip']
    b=['step_copy_mod_nginx']

    b+=OPTIONS

    if 'step_point_namecheap_to_ip' in b:
        #0v1# A_RECORD
        print ("1)  Point namecheap to ip address")
        print (" >  Create A Record to point all ie @ to IP")
        print (" >  optional Create A www to IP")
        print (" >  optional Create A point subdomain to IP")
        
        print ("2)  On server python3 -m pip install certbot")
        print ("(NO) sudo certbot -d gretnet.com -d www.gretnet.com")

    if 'step_copy_mod_nginx' in b:
        print ("1)  copy folder and run it")

    Auto=Auto_Server_Setup()
    if 'test_base_commands' in b:
        Auto.test()

    if 'install_python_virtual_env_and_libs' in b:
        Auto.auto_setup_env(CONFIG)



    return

if __name__=='__main__':
    branches=['review_theory']
    branches=['do_complete']

    for b in branches:
        globals()[b]()

"""
#def review_theory():
#    ## ? nginx and flask options
#    #a)  Flask can handle pem/ppk files directly (see flask_scalable.py)
#    #b)  But, nginx is ultimately more flexible.
#    
#    ## nginx
#    #- acts as front router on server and can handle multiple domain front-ends to one machine
#    
#    ## Ideally, run auto_nginx
#    
#    return

"""










