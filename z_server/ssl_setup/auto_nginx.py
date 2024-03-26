
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

