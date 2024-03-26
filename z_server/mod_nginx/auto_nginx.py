import os
import sys


from mod_execute.mod_execute import The_Execute_Command


LOCAL_PATH=os.path.join(os.path.dirname(__file__), "./")


#0v6# JC Sep 27, 2023  Setup w WT
#0v5# JC Jan 19, 2023  Setup w chatskit
#0v4# JC Apr  1, 2021  Setup w gretnet
#0v3# JC Jul  9, 2020  Rev for saleor on tk & americakit.com
#0v2# JC May  5, 2020  How to know if running?
#0v1# JC Apr 15, 2020  Auto server setup


#NOTES:
#===  Eclipse Remote System Explorer
#- Window > Open Perspective > Other... and choose Remote System Explorer f
#- new connection ssh, hostname
#- ssh keys:  prefs -> ssh2 -> add private key
#- sftp -> right click -> create remote project


#===  Recall:  auto server in truthkit for library install
if False:
    print ("******* BIG LESSON LEARNED:  could be other nginx defaults in dir")
    print ("1)  JUST RUN:  sudo certbot --nginx -d americakit.com -d www.americakit.com")
    print ("2)  /etc/nginx/sites-enable/add_new_site *** MAY ALREADY BE IN DEFAULT SO JUST SET LOCATION VARIABLE ")
    print ("3)  sudo systemctl restart nginx")


def test_stack():
    ASS=Auto_Server_Setup()
    for liner in ASS.Exe.run_command_iter('dir'):
        print ("dir> "+str(liner))
    return

class Auto_Server_Setup(object):
    def __init__(self):
        self.Exe=The_Execute_Command()
        return

    def test(self):
        is_ok=False
        for liner in self.Exe.run_command_iter('dir'):
            #print ("dir> "+str(liner))
            is_ok=True
        return is_ok
    
    def setup_new_server_libs(self,branch=''):
        cmds,apts,pips=self.get_std_cmds()
        
        for cmd in cmds:
            for liner in self.Exe.run_command_iter(cmd):
                print ("["+str(cmd)+"]: "+str(liner))
        for cmd in apts:
            cmd="apt-get -y install "+cmd
            for liner in self.Exe.run_command_iter(cmd):
                print ("["+str(cmd)+"]: "+str(liner))
        for cmd in pips:
            #? pip3 , envs or python -m
            cmd="pip install "+cmd
            for liner in self.Exe.run_command_iter(cmd):
                print ("["+str(cmd)+"]: "+str(liner))
        return
    
    def get_std_cmds(self):
        #branch
        cmds=[]
        cmds+=['apt update']
        cmds+=['apt-get -y update']
        cmds+=['add-apt-repository --yes universe']
        cmds+=['add-apt-repository --yes ppa:certbot/certbot']
        cmds+=['apt-get -y update']

        apts=[]
        apts+=['software-properties-common']
        apts+=['nginx']
        apts+=['htop']
        apts+=['certbot']
        apts+=['nginx gunicorn']
        apts+=['python-certbot-nginx']
        apts+=['python3-venv']

        ## Python
        apts+=['python python3-pip python3-dev build-essential libssl-dev libffi-dev python3-setuptools']
        apts+=['python-pip']

        ## Pip
        pips=[]
        pips+=['--upgrade pip']
        pips+=['wheel']

        ## Pip standard
        pips+=['flask flask-cors']
        
        return cmds,apts,pips

    def auto_setup_env(self,CONFIG):
        print ("Assumes service registered as 'myproject'") #don't confuse with myproject directories
        
        cmds=[]
    
        #===  Create virtual env
        cmds+=['mkdir '+CONFIG['target_project_directory']]  #~/myproject']
        cmds+=['sudo chown '+CONFIG['user']+":"+CONFIG['user']+" "+CONFIG['target_project_directory']]   # cmds+=['sudo chown ubuntu:ubuntu ~/myproject']
        cmds+=['cd '+CONFIG['target_project_directory']+' && '+CONFIG['python_location']+' -m venv '+CONFIG['workon']]
    
        cmds+=['source '+CONFIG['target_project_directory']+'/'+CONFIG['workon']+'/bin/activate'] # cmds+=['source ~/myproject/myprojectenv/bin/activate']
        activate='source '+CONFIG['target_project_directory']+'/'+CONFIG['workon']+'/bin/activate && '
        
        
        #===  Add default libs
        cmds+=[activate+'pip install --upgrade pip']
        cmds+=[activate+'pip install wheel']
        cmds+=[activate+'pip install gunicorn flask']
        print ("Warning gunicorn flask not installing on activate")
    
        #===  Demo flask
        cmds+=["cp "+LOCAL_PATH+"myproject/myproject.py "+CONFIG['target_project_directory']+"/myproject.py"]
        cmds+=["cp "+LOCAL_PATH+"myproject/wsgi.py "+CONFIG['target_project_directory']+"/wsgi.py"]
    
        #===  Register service
        service_filename=self.dump_service(CONFIG['full_project_directory'],CONFIG['workon'])
        cmds+=["cp "+service_filename+" /etc/systemd/system/myproject.service"]
        cmds+=["systemctl start myproject"]
        cmds+=["systemctl enable myproject"]
        cmds+=["systemctl status myproject"]
        
    
        cmds=[] ###############################
        
        #===  nginx
        cmds+=["apt install -y nginx"]
        #has ssl# cmds+=["cp "+LOCAL_PATH+"myproject/myproject_sites-available /etc/nginx/sites-enabled/myproject"]

        template_filename=self.dump_template(CONFIG['domains'],CONFIG['workon'])
        cmds+=["cp "+template_filename+" /etc/nginx/sites-enabled/myproject"]
        print ("Recall nginx will have ssl added by certbox not before")
        
        cmds+=['sudo ln -s /etc/nginx/sites-available/myproject /etc/nginx/sites-enabled']
        cmds+=['sudo nginx -t']  #test
        cmds+=['sudo systemctl restart nginx']
    
        #===  ssl certbot
        #** fragile install
        #apt --reinstall install -y certbot
        if True:
            #just do new python??
            #            apt-get install python3.4-dev python3.4-venv
            #And then create your virtualenv
            #python3.4 -m venv myVenv
            print ("./venv/bin/certbot   << was installed using python3.8 thingy")
            print ("*****FOLLOW: https://certbot.eff.org/lets-encrypt/pip-other.html")
            print ("1)  sudo apt-get remove certbot")
            print ("sudo /opt/certbot/bin/pip install certbot")
            print ("2)  create link and ensure can run ie /opt/certbot/bin/certbot  or ln -s /opt/certbot/bin/certbot /usr/bin/certbot")
            print ("./venv/bin/certbot --nginx -d gretnet.com") 
#            cmds+=['add-apt-repository --yes ppa:certbot/certbot']
#            cmds+=['apt install -y python-certbot-nginx']
            #?cmds+=['apt install -y python3-certbot-nginx'] #
        else:
           #Do manually
           #cmds+=['curl -o- https://raw.githubusercontent.com/vinyll/certbot-install/master/install.sh | bash']
           stopp=kkk

        domain_str=''
        for domain in CONFIG['domains']:
            domain_str+="-d "+domain+" "

        cmds+=["sudo certbot --nginx "+domain_str]
        #sudo certbot --nginx -d sciencemapped.com -d www.sciencemapped.com
        cmds+=['sudo systemctl restart nginx']
        
        #cmds+=['sudo ufw allow 'Nginx Full'
    
        for cmd in cmds:
            print ("RUNNING: "+cmd)
            info=''
            if 'sudo certbot' in cmd:
                info='**must press c to accept'
                
            input("? run: "+str(cmd))
            for liner in self.Exe.run_command_iter(cmd):
                print (info+" ["+cmd+"]: "+str(liner))
        return

    def dump_template(self,domains,workon):
        if len(domains)>1:
            print ("DOMAINS: "+str(domains))
            topp=check_multiple
        domain_str=""
        for domain in domains:
            domain_str+=domain+' www.'+domain+';'

        #   server_workon sciencemapped.com www.sciencemapped.com;
        content="""server {
            listen 80;
            server_name """+domain_str+"""
            location / {
                include proxy_params;
                proxy_pass http://unix:/home/ubuntu/myproject/myproject.sock;
            }
        }
        """
        template_filename=LOCAL_PATH+"myproject/myproject_sites-available-template-"+workon
        fp=open(template_filename,'w')
        fp.write(content)
        fp.close()

        return template_filename

    def dump_service(self,project_dir,workon):
        env=project_dir+'/'+workon+'/bin'  #   # ExecStart=/home/ubuntu/myproject/myprojectenv/bin/gunicorn --workers 3 --bind unix:myproject.sock -m 007 wsgi:app

        #see service file
        content="""
            [Unit]
            Description=Gunicorn instance to serve myproject
            After=network.target
            [Service]
            User=ubuntu
            Group=www-data
            WorkingDirectory="""+project_dir+"""
            Environment='PATH="""+env+"""'
            #  bind to unix socket file myproject.sock, umask value 007 (socket file permissions to owner only)
            ExecStart="""+env+"""/gunicorn --workers 3 --bind unix:myproject.sock -m 007 wsgi:app
            [Install]
            #  where to link at boot up ie/ start when regular multi-user system is up
            WantedBy=multi-user.target
            """

        filename=LOCAL_PATH+"myproject/myproject.service-"+workon
        fp=open(filename,'w')
        fp.write(content)
        fp.close()

        return filename


def auto_server_setup():
    ASS=Auto_Server_Setup()
    
    print ("> do system setup: nginx, gunicorn, flask, test.")
    print ("> do env setups: virtual envs etc.")

    return

def nginx2flask():
    #See mod_ssl requirements.txt
    return

def auto_application():
    print ("See mod_ec2 and auto_application")
    print ("Including auto connect to remote server from demo_deploy.mod_auto_deploy import High_Automation")

    ASS=Auto_Server_Setup()
    
    b=['step1']
    
    if 'step1' in b:
        ASS.setup_new_server_libs()
        
    return

def auto_ssl():
    #*also see ?https.sh
    #sudo add-apt-repository ppa:certbot/certbot
    #sudo apt install -y python-certbot-nginx
    #sudo certbot --nginx -d sciencemapped.com -d www.sciencemapped.com
    return

def auto_nginx():
    #  TUTORIAL REF:
    #  https://www.digitalocean.com/community/tutorials/how-to-serve-flask-applications-with-gunicorn-and-nginx-on-ubuntu-18-04
    #  org was requirements.txt
    domains='-d sciencemapped.com -d www.sciencemapped.com'

    ASS=Auto_Server_Setup()
    #**must match with nginx service setup -- or possibly auto

    print ("Assume setup for ubuntu user")
    
    cmds=[]

    #===  Create virtual env
    cmds+=['mkdir ~/myproject']
    cmds+=['sudo chown ubuntu:ubuntu ~/myproject']
    cmds+=['cd ~/myproject && python3 -m venv myprojectenv']

    cmds+=['source ~/myproject/myprojectenv/bin/activate']
    activate='source ~/myproject/myprojectenv/bin/activate && '
    
    
    #===  Add default libs
    cmds+=[activate+'pip install --upgrade pip']
    cmds+=[activate+'pip install wheel']
    cmds+=[activate+'pip install gunicorn flask']
    print ("Warning gunicorn flask not installing on activate")

    #===  Demo flask
    cmds+=["cp "+LOCAL_PATH+"myproject/myproject.py ~/myproject/myproject.py"]
    cmds+=["cp "+LOCAL_PATH+"myproject/wsgi.py ~/myproject/wsgi.py"]

    #===  Register service
    cmds+=["cp "+LOCAL_PATH+"myproject/myproject.service /etc/systemd/system/myproject.service"]
    cmds+=["systemctl start myproject"]
    cmds+=["systemctl enable myproject"]
    cmds+=["systemctl status myproject"]
    

    cmds=[] ###############################
    
    #===  nginx
    cmds+=["apt install -y nginx"]
    #has ssl# cmds+=["cp "+LOCAL_PATH+"myproject/myproject_sites-available /etc/nginx/sites-enabled/myproject"]
    cmds+=["cp "+LOCAL_PATH+"myproject/myproject_sites-available-template /etc/nginx/sites-enabled/myproject"]
    print ("Recall nginx will have ssl added by certbox not before")
    
    cmds+=['sudo ln -s /etc/nginx/sites-available/myproject /etc/nginx/sites-enabled']
    cmds+=['sudo nginx -t']
    cmds+=['sudo systemctl restart nginx']

    #===  ssl certbot
    cmds+=['add-apt-repository --yes ppa:certbot/certbot']
    cmds+=['apt install -y python-certbot-nginx']
    cmds+=["sudo certbot --nginx "+domains]
    #sudo certbot --nginx -d sciencemapped.com -d www.sciencemapped.com
    cmds+=['sudo systemctl restart nginx']
    
    #cmds+=['sudo ufw allow 'Nginx Full'

    for cmd in cmds:
        print ("RUNNING: "+cmd)
        info=''
        if 'sudo certbot' in cmd:
            info='**must press c to accept'
            
        for liner in ASS.Exe.run_command_iter(cmd):
            print (info+" ["+cmd+"]: "+str(liner))
    
    return

def auto_ssl():
    ASS=Auto_Server_Setup()
    print ("**must provide email")
    print ("Just add new domain...")
    domains=['hello.aipages.com']
    cmds=[]
    for domain in domains:
        cmds+=["sudo certbot --nginx -d "+domain]

    for cmd in cmds:
        print ("RUNNING: "+cmd)
        for liner in ASS.Exe.run_command_iter(cmd):
            print ("["+cmd+"]: "+str(liner))
    return

def auto_flask_template():
    print ("> Create flask service or run stand-alone")
    print ("> nginx point subdomain to flask")
    
    print ("vi /etc/nginx/sites-enabled/myproject")
    ## What edits to make to nginx?
    # vi 
    #server {
    #    listen 80;
    #    server_name user.domain.com;
    #    location / {
    #        proxy_set_header Host $host;
    #        proxy_pass http://127.0.0.1:3435;
    #        proxy_redirect off;
    #    }
    #}
    print ("sudo systemctl restart nginx")
    return

def is_it_up_though():
    print ("See c:...mod_ssl...requirements.txt")
    print ("- check logs etc")
    return


if __name__=='__main__':
#    branches=['auto_server_setup']
    branches=['nginx2flask']
    branches=['test_stack']
    branches=['auto_application']
    branches=['auto_nginx']
    branches=['auto_ssl']
    branches=['auto_flask_template']
    branches=['is_it_up_though']
    
    for b in branches:
        globals()[b]()

        

"""
"""










