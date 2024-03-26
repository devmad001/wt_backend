import os
import sys
import re

import subprocess
import datetime


#from auto_nginx import Auto_Server_Setup
#from mod_execute.mod_execute import The_Execute_Command


LOCAL_PATH=os.path.join(os.path.dirname(__file__), "./")



#0v1# JC Jan 25, 2024  Create

#- see auto_nginx.py
#- see mod_ssl directory


###################################
#  APPLIED Steps on auto letsencrypt cert renewal
###################################
#


def is_sudo():
    # Get the effective user ID
    if os.geteuid() == 0:
        return 1
    else:
        print("Not running with root privileges. Please run the script with 'sudo'.")
        return 0

def check_cert_expiry(domain, days_before_expiry=30):
    # Path to the certificate
    cert_path = f'/etc/letsencrypt/live/{domain}/cert.pem'

    # Command to get the expiry date
    command = f'openssl x509 -enddate -noout -in {cert_path}'

    # Execute the command
    result = subprocess.run(command.split(), capture_output=True, text=True)
    expiry_date_str = result.stdout.strip().split('=')[1]

    # Convert expiry date to a datetime object
    expiry_date = datetime.datetime.strptime(expiry_date_str, '%b %d %H:%M:%S %Y %Z')

    # Calculate days until expiry
    days_until_expiry = (expiry_date - datetime.datetime.now()).days

    # Check if expiry is within the specified threshold
    if days_until_expiry <= days_before_expiry:
        print(f'Certificate for {domain} expires in {days_until_expiry} days on: {expiry_date}')
    else:
        print(f'Certificate for {domain} expires in {days_until_expiry} days on: {expiry_date}')



def steps_auto_renew_domains():
    domains=[]
    domains+=['ws.epventures.co']
    domains+=['core.epventures.co']

    if is_sudo():
        for domain in domains:
#D1#            print ("CHECK RENEW: "+str(domain))
            check_cert_expiry(domain)

    return

if __name__=='__main__':
    branches=['steps_auto_renew_domains']
    for b in branches:
        globals()[b]()


"""
"""










