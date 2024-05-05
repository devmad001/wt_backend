import os
import sys
import codecs
import json
import re

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")


from get_logger import setup_logging
logging=setup_logging()



#0v1# JC  Sep 25, 2023  Init


"""
    NGINX

"""

## Activate Sept 27, 2023

#dashboard.epventures.co:5000 

subdomains=['dashboard']

#### *validated again oct 27,
### NOTES ON ADDING ONE MORE:

#1#  Which subdomain?:  - upload (then storage.)
#2#  Point subdomain from godaddy
#***don't configure any nginx in sites-enabled before certbot??

#3# Auto add certificates:
#     [ ] note expiration!
#     !!! DO NOT CREATE sites-enabled before running below!!!!
#     !!! DO NOT CREATE sites-enabled before running below!!!!
#     !!! DO NOT CREATE sites-enabled before running below!!!!
#     !!! DO NOT CREATE sites-enabled before running below!!!!
#     sudo certbot --nginx -d upload.epventures.co

#4# Config file
# cd /etc/nginx/sites-enabled/
# sudo cp square.epventures.co storage.epventures.co
# *edit to rename internal square to storage.  Note flask port (same in this case)

#??sudo ln -s /etc/nginx/sites-available/service1.epventures.co /etc/nginx/sites-enabled/

#5#  Reload config
# sudo nginx -t
# sudo systemctl reload nginx

#(recall, /z_server/define_dashboard.py does a lot of pointing to ports + services via .json config)


def log_cors_setup_notes():
    ## JON absolute CORS check:
    # Not modifying anything in nginx & having IPs in fast_main allows
    # get to button_handler ok.
    #> validated via local 5173 allowed but 5177 not allowed
    


    
    ## CORS with fast-api fine on local server but not on server
    """
    - so, it must be nginx
    /etc/nginx/sites-available/service1.epventures.co /etc/nginx/sites-enabled/
    
    sudo nginx -t
    sudo systemctl reload nginx


    """
    return


def log_wt_ssl_setup_notes():
    """
    1.  nginx.  but also need to setup nginx


    
    just follow Auto_Server_Setup and install libs
     
    THIS FIXED:: 
        apt-get install -y python3-certbot-nginx     
         
     2/  something on 90?     sudo lsof -i :80.....kill -9 ...

               sudo systemctl start nginx    *did have error on 80 in use but now:
               sudo systemctl status nginx ok
           sudo nginx -t    ok
tail both access and errro
sudo tail -f /var/log/nginx/error.log /var/log/nginx/access.log
           for log or see below ie/ sudo tail -n 20 /var/log/nginx/error.log
           


    3/  try lets encrypt again...
 sudo certbot --nginx -d service1.epventures.co
          
    Certificate is saved at: /etc/letsencrypt/live/service1.epventures.co/fullchain.pem
Key is saved at:         /etc/letsencrypt/live/service1.epventures.co/privkey.pem
This certificate expires on 2023-12-27.
These files will be updated when the certificate renews.


4/  use certificate via//
***JC:  use std flask but have nginx handle pem on front

5/  see service1   nginx...
b)  symbolic link:
sudo ln -s /etc/nginx/sites-available/service1.epventures.co /etc/nginx/sites-enabled/


6/  nginx user needs access to pem.  but who is user?
 ps -aux | grep nginx
ie/ worker process is www-data

b)  add this person to certificate owner:

sudo chown -R root:www-data /etc/letsencrypt/live
sudo chown -R root:www-data /etc/letsencrypt/archive
sudo chmod -R 750 /etc/letsencrypt/live
sudo chmod -R 750 /etc/letsencrypt/archive

==== DO FOR NEXT:

7/
recall ** dont want nginx site-enabled BEFORE running the dashboard
sudo certbot --nginx -d dashboard.epventures.co
create copy of service1.epventures.co
edit per update
sudo ln -s /etc/nginx/sites-available/dashboard.epventures.co /etc/nginx/sites-enabled/
^^^^sites-enabled is key ideally put into sites-avail and then link
sudo certbot --nginx -d dashboard.epventures.co
sudo nginx -t
sudo systemctl reload nginx



    """ 
    """
        FOLLOW CASE ETUPS COMPLETE SETUP + UPGRADE THEM 
        python 3.10.12
        sudo apt install -y nginx

        configs live here:
          /etc/nginx/sites-enabled/*templates*")

          sudo certbot --nginx -d americakit.com -d www.americakit.com"

          INSTALL CERTBOT
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
         
                
    """    
    
    
    return

def REF_():
    """
        print ("[B]  Check logs")
        sudo less /var/log/nginx/error.log: checks the Nginx error logs.
            > will show connection refuses
        sudo less /var/log/nginx/access.log: checks the Nginx access logs.

        sudo journalctl -u nginx: checks the Nginx process logs.
        sudo journalctl -u myproject: checks your Flask app’s Gunicorn logs.
    """
     
    return


if __name__=='__main__':
    branches=['dev1']
    for b in branches:
        globals()[b]()



"""
        
        gninx at
        /etc/nginx/sites-enabled
        chatskit...
        change port
        
        nginx -t
        
          # sudo nginx -t
    #sudo nginx -s reload

    #*** SEE chatgpt\devops\ CASE_STEPS_COMPLETE_SETUP.py
    

cert_filename=LOCAL_PATH+"pems/cert.pem"
key_filename=LOCAL_PATH+"pems/privkey.pem"

@app.route('/')
def hello_endpoint():
    dd={}
    dd['hello']='world'
#    return jsonify(dd)

    response = jsonify(dd)
    # Enable Access-Control-Allow-Origin  otherwise browser may block?
    #response.headers.add("Access-Control-Allow-Origin", "*")
    return response


if __name__ == '__main__':

#app.run(debug=True,port=PORT,host='0.0.0.0') #debug=false for auto reload
     
assl_context=(cert_filename,key_filename)

if os.name == 'nt': #windows
def else:
oooo#app.run(debug=True,port=9999,host='0.0.0.0')
app.run(debug=True,port=9999,host='0.0.0.0',ssl_context=ssl_context)



COMMON ERRORS:
    - 400 and bad request if not including ssl_context here (but don't NEED with gunicorn)

gunicorn --certfile ./pems/fullchain.pem --keyfile ./pems/privkey.pem -b 0.0.0.0:9999 flask_scalable:app

gunicorn --certfile /etc/letsencrypt/live/registryontario.com/fullchain.pem --keyfile /etc/letsencrypt/live/registryontario.com/privkey.pem -b 0.0.0.0:443 harp_endpoint:app

gunicorn -b 0.0.0.0:9999 harp_endpoint:app

???
possible via sockets?
https://github.com/miguelgrinberg/Flask-SocketIO/issues/1047



#cert_filename="/etc/letsencrypt/live/registryontario.com/cert.pem"
#key_filename="/etc/letsencrypt/live/registryontario.com/privkey.pem



"""
