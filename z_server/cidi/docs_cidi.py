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



#0v1# JC  Feb  5, 2023  Init


"""
    SERVER SERVICE REGISTRATION
    - continuous integration stuff

"""



def dev1():

    print ("1)  Register python scripts as service")
    print ("2)  Optionally integrate with git auto deploy")

    ## CI / CI notes:
    #> github actions  (workflow/main.yml)
    #> github actions (ssh-action) for ssh and doing deployment commands.
    #- regularily review logs
    
    ## SCRIPT SERVICES
    #- systemd
    #[ ] how to ensure all workers are still live?

    ## CURRENT SCRIPTS:
    #ws)  'cd '+LOCAL_PATH+"../z_apiengine && python fast_ws_v1.py" 
    #main) 'cd '+LOCAL_PATH+"../z_apiengine && python -m uvicorn fast_main:app --port 8008 --workers 3" 
    #job runner): ENTRYPOINT_mega_job.py
    
    return


def applied_script_registration_as_a_service_notes():
    """

              #job runner): ENTRYPOINT_mega_job.p 
              * permissions.
              
              ### [permissions])
              chown ubuntu:ubuntu /home/ubuntu/WT_LOGS/wt_main
              chown ubuntu:ubuntu /home/ubuntu/WT_LOGS/wt_queue
              chown ubuntu:ubuntu /home/ubuntu/WT_LOGS/wt_ws
              
              ### [create service config]  
              vi /etc/systemd/system/wt_job_queue.service
              - 

              #job runner): ENTRYPOINT_mega_job.py
              -

    """

    return


def systemd_stuff():
    #GITHUB actions workflow (to reload service)
    
    """
        CURRENT ENTRYPOINTS:
        
        ## CURRENT SCRIPTS:
        #ws)  'cd '+LOCAL_PATH+"../z_apiengine && python fast_ws_v1.py" 
        #main) 'cd '+LOCAL_PATH+"../z_apiengine && python -m uvicorn fast_main:app --port 8008 --workers 3" 
        #job runner): ENTRYPOINT_mega_job.py
        /etc/systemd/system/wt_job_queue.service
    
    """
    

    """
        RAW NOTES:
            
        sudo systemctl restart your-service.service: This will stop and then start the service, which is useful if you need to completely restart the service to apply new changes.

        sudo systemctl reload your-service.service: This will reload the service's configuration without interrupting its current operations. This is useful for services that support reloading, but your Python script needs to be designed to handle this kind of reloading.

        sudo systemctl daemon-reload: This is sometimes necessary if you've made changes to the systemd service file itself. It reloads systemd's configuration files but doesn't restart your services. Typically, you'd follow this with a restart or reload of your specific service.
    """


    """
    SAMPLE FOR GITHUB ACTIONS AUTO SSH AND DEPLOY
        - name: Deploy
      uses: appleboy/ssh-action@master
      with:
        host: ${{ secrets.HOST }}
        username: ${{ secrets.USERNAME }}
        key: ${{ secrets.SSH_KEY }}
        script: |
          cd /path/to/your/project
          git pull origin master
          # Reload or restart your systemd service
          sudo systemctl restart your-service.service
          # Or if your service supports it, you might prefer:
          # sudo systemctl reload your-service.service

    """


    return

def systemd_setup_notes():
    """
        1)  Log files:  ~/WT_LOGS/   wt_main, wt_ws, wt_queue
        PLUS PERMISSION:
        mkdir -p /home/ubuntu/WT_LOGS/ws
        chown ubuntu:ubuntu /home/ubuntu/WT_LOGS/ws

        2)  Create a service file
        sudo vi /etc/systemd/system/wt_job_queue.service
        **see sample contents
        NOTES:
        - After=network.target ** but may want mysql up too

        3)  
        sudo systemctl status wt_job_queue.service     
        sudo systemctl daemon-reload
        sudo systemctl enable my_python_script.service
        sudo systemctl start my_python_script.service
        sudo systemctl status wt_job_queue.service     
        tail -f /home/ubuntu/WT_LOGS/wt_queue/service_log.log
        

//////////////////////////////////////////
[Unit]
Description=My Python Script Service
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/wt/z_apiengine
ExecStart=/usr/bin/python3 /home/ubuntu/wt/z_apiengine/fast_ws_v1.py
StandardOutput=append:/home/ubuntu/WT_LOGS/ws/service_log.log
StandardError=append:/home/ubuntu/WT_LOGS/ws/service_error.log
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target

        4)  START
        sudo systemctl daemon-reload
        sudo systemctl enable my_python_script.service
        sudo systemctl start my_python_script.service
        
        5)  ADMIN
        sudo systemctl status my_python_script.service
        sudo systemctl stop my_python_script.service
        sudo systemctl restart my_python_script.service
        sudo systemctl reload my_python_script.service
        sudo systemctl disable my_python_script.service
        
        tail -f /home/<your-username>/WT_LOGS/ws/service_log.log
        
    """
    
    """
    ROTATING LOG FILE NAMES **SEPARATE SERVICE>
    To implement rotating log filenames for your systemd service, you would typically use an external utility like logrotate, which is designed for managing log files in Linux. logrotate can compress, remove, and rotate log files based on size, age, or a combination of both.

Setting Up logrotate for Your Service
Create a logrotate Configuration File: You will need to create a new configuration file for your service in the /etc/logrotate.d/ directory. This directory is scanned by logrotate for custom configurations.

bash
Copy code
sudo nano /etc/logrotate.d/my_python_script
Configure Log Rotation: In the editor, add the following content, adjusting paths and settings to your requirements:

apache
Copy code
/home/<your-username>/WT_LOGS/ws/service_log.log /home/<your-username>/WT_LOGS/ws/service_error.log {
    rotate 7
    daily
    missingok
    notifempty
    compress
    delaycompress
    create 640 <your-username> <your-username>
    postrotate
        systemctl restart my_python_script.service > /dev/null
    endscript
}
Replace <your-username> with your actual username.
rotate 7 means that logrotate will keep 7 rotated log files.
daily specifies that the rotation should occur daily. You can also use weekly, monthly, or size (e.g., size 10M for rotating when the file exceeds 10MB).
The postrotate/endscript section is used to restart your service after logs are rotated. This ensures that your service will start writing to the new log files. Note: Depending on how your script handles files, you might not need to restart the service and could use less disruptive commands like kill -HUP to re-open log files.
Save and Close: After configuring the settings, save and close the file.

Testing logrotate Configuration
You can test your logrotate configuration to ensure it works as expected without actually waiting for the scheduled time:

bash
Copy code
sudo logrotate -dv /etc/logrotate.d/my_python_script
The -d option tells logrotate to run in debug mode (it shows what would be done but doesn't actually perform the rotations), and -v enables verbose output.

Automating logrotate
logrotate is typically run automatically by a cron job on a daily basis. You can check the cron jobs in /etc/cron.daily/ to see if logrotate is set up to run automatically. If it's not there, you can set it up by adding a symlink or script that calls logrotate.

Note on Systemd and Log Rotation
Since you're using systemctl restart in the postrotate script, make sure that restarting your service doesn't negatively impact your application. If it's critical that your service remains running, you might need to find a way for your application to close and reopen its log files when receiving a signal, allowing you to use a less disruptive signal instead of restarting the service.

With this setup, logrotate will manage your log files, ensuring they're rotated, compressed, and removed according to the rules you've specified, keeping your log directory manageable and preventing disk space issues.
    """
    
    return



if __name__=='__main__':
    branches=['dev1']
    for b in branches:
        globals()[b]()
