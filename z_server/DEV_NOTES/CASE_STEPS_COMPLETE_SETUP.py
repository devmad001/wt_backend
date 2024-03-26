import os
import sys
import re


LOCAL_PATH=os.path.join(os.path.dirname(__file__), "./")

"""
FILE SHOULD LIVE AT:
/mods/mod_domain/mod_ngix 
  ^ extra scripts there too

"""


#0v3# JC Sep 27, 2023 (see nginx_config -- jon update this first but watch auto_nginx)
#0v2# JC Jan 19, 2023
#0v1# JC Jan 19, 2023  Use with chats kit new server


def entire_steps():
    print ("*** THIS IS NOT CORE INSTRUCTIONS BUT WHAT I ACTUALLY DID (so may be duplicate notes")

    print ("SEE:  auto_nginx.py")
    print ("SEE:  STEP_1_domain.py STEP_1_**")
    
    pritn ("GENERAL COMMENT:  All rather std but can get tricky if you install some libs with root vs ubuntu vs virtualenv")


    print ("Setup for chatskit.com")
    print ("[1] which of this libs to use?")
    print ("[2] domain on namecheap: chatskit.com")
    print ("  - didn't I have an auto ip pointer tool to rotate?")
    

    print ("> HAVE:  IP address of server (ec2 fixed): 54.243.123.7, domain: chatskit.com")
    print ("> GOAL:  Setup nginx")

    print ("> AVOID BUG:  use a virtual env for better version + gunicorn control")
    
    print ("python -m venv chatskit")
    """
    python -m pip install virtualenv
    whereis python3.9
    /usr/local/lib/python3.9
    virtualenv -p /usr/bin/python3.9 chatskit
    source chatskit/bin/activate
    """


    print ("================================================")
    print ("> NAMECHEAP A RECORD")
    #0v2# A_RECORD
    print ("1)  Point namecheap to ip address")
    print (" >  Create A Record to point all ie (HOST) @ to IP")
    print (" >  optional Create A (HOST) www to IP")
    print (" >  optional Create A point subdomain to IP ie/ buildingscience.chatskit.com")
    print (" >  * wild card for any subdomain forwarding")
    print ("================================================")
    
    print ("================================================")
    print ("> SERVER NGINX, SSL (https)")
    print ("*see auto_nginx.py")
    
    print ("1)  Installed required libraries")
    print ("    > apt install -y nginx")
    print ("    > python -m pip install certbot")
    print ("    > (plugin for certbot) pip install certbot-nginx") #or via apt at python-certbot-nginx

    print ("2)  Request certificates for domains")
    print ("    > sudo certbot --nginx -d chatskit.com -d www.chatskit.com -d buildingscience.chatskit.com")
    
    print ("3)  Did it work?  Restart nginx or check folders (recall that config file")
    print ("> see file has domain defs:  /etc/nginx/sites-enabled/myproject")
    print ("> test nginx setup:  sudo nginx -t")
    print ("> optional restart: sudo systemctl restart nginx")

    print ("================================================")
    print ("> YEAH BUT HOW TO VIEW FLASK AND PORT THINGY")
    print ("i)  flask-cors should be started with pem (certbot/https/ssl) reference")
    print ("ii)  nginx firewall permissions? internal ports? templates?")

    print ("1) Start demo flask_scalable.py with pem for trial")
    print ("KEYS AT:  /etc/letsencrypt/live/chatskit.com/*.pem")
    print ("create app copy> cp *.pem /home/ubuntu/chatskit/devops/pems")
    print ("run basic flask to test (gunicorn config option later): ~/chatskit/devops$ python flask_scalable.py")
    print ("   - port 9999 default")

    print ("3) nginx TEMPLATES Point nginx to this port")
    print ("i)  every website needs a template file (see sample below)")
    print ("ii)  steps are:  CREATE, LINK, TEST, RESTART")
    print ("CREATE>  use existing (see below)")
    print ("    /etc/nginx/sites-enabled/chatskit")
    print ("LINK> ???")
    print ("   > remove /etc/nginx/sites-enabled/default")
    print ("     ^^ otherwise, conflict error")
    
    print ("RESTART> sudo service nginx reload  ")
    
    print ("https://chatskit.com/ responds with 502 bad gateway but flask sees as bad request.  But it DOES see it")
    
    #?? require gunicorn??
    # gunicorn --certfile ./devops/pems/fullchain.pem --keyfile ./devops/pems/privkey.pem -b chatskit.com:443 flask_scalable:app
    # gunicorn --certfile ./pems/fullchain.pem --keyfile ./pems/privkey.pem -b chatskit.com:443 flask_scalable:app
    # gunicorn --certfile ./pems/fullchain.pem --keyfile ./pems/privkey.pem -b 0.0.0.0:9999 flask_scalable:app




    return

def extras():
    """
    FIREWALL?
    ufw enable
    ufw status
    ufw allow 80
    """
    
    """
    GUNICORN
    gunicorn --certfile /etc/letsencrypt/live/registryontario.com/fullchain.pem --keyfile /etc/letsencrypt/live/registryontario.com/privkey.pem -b registryontario.com:443 harp_endpoint:app
    """

    ## SAMPLE TEMPLATE for nginx point to internal port server
    """
    server {
    listen 443 ssl;
    server_name covid.fluidkit.com fluidkit.com www.fluidkit.com;

    location / {
        proxy_set_header Host $host;
        proxy_pass https://127.0.0.1:8080;
    }

    #OLD# ssl on;
    ssl_certificate /etc/letsencrypt/live/covid.fluidkit.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/covid.fluidkit.com/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;

    #    return 301 $scheme://covid.fluidkit.com:8080$request_uri;
    #    return 444;

    }
    """

    return

def notes_add_subdomain2flask():
    #(1)
    # flask at :8081
    # upload.chatskit.com/project/building1
    
    #(2)
    # nginx file: 
    # /etc/nginx/sites-enabled/chatskit
    
    #(3)
    # namecheap point wildcard to subdomain
    
    #(4)
    # but letsencrypt must still be updated for subdomain?!
    # **it will update the chatskit file nginx
    #sudo certbot --nginx -d upload.chatskit.com
    # sudo nginx -t
    #sudo nginx -s reload
    
    ###############
    # streamlit at 8082
    ###############
    # buildingscience.chatskit.com
    # no need to do certbot so just update:
    # /etc/nginx/sites-enabled/chatskit
    
    # sudo nginx -t
    #sudo nginx -s reload

    #*** SEE chatgpt\devops\ CASE_STEPS_COMPLETE_SETUP.py
    
    
    return

if __name__=='__main__':
    branches=['entire_steps']

    for b in branches:
        globals()[b]()

"""
"""










