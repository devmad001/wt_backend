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



#0v1# JC  Feb 14, 2024  Init



"""
    FRESH INSTALL OF THE wt_finaware library
    - version 0.1.0  (ie/ still not formal but closer)
"""


def install_steps():
    """
    [1]
        Not sure on requirements file so check active server
        (3.137.103.23 finaware dev)
        pip freeze
        >> Jon use freeze as reference for fresh install.
        
        python 3.10?? org
        python 3.11.5 trying now


        ## apt updates (ubuntu)
        #- ie/ to support pytest
    
        sudo apt-get update
        apt-get install python3-apt
        
        #- gcc may not be required but possibly for 'traits' or similar libs
        #     (can skip until needed)
        apt install gcc


    [2]  python -m pip install -r requirements.txt
        - sourced from frozen ubuntu version so may need adjustments
        Errors?
        i)   First try removing hard version and allow latest version to install
        ii)  Possibly can remove library if won't install but make a note and check with Jon 

    [3]  Config files
        Here are the list of config files to source from remote server
        THESE MUST BE MANUALLY MOVED TO SERVER (non git)
    
        w_settings.ini
        w_storage/gstorage/neo4j_settings.ini
        z_apiengine/db_config.ini
        w_admin/openai.ini
        z_server/aws/watchtower_webservices_user_accessKeys.ini
        
        
        ## UNUSED:
        w_app_settings.ini
        chatskit_ui/config_chatgpt.ini   
    


    """
        


    return


def special_libraries():

    """
        Failed building wheel for PyMuPDF



    """

    """
    ocrmypdf
    ** requires latest version but also latest tesseract data files!
    
    #    sudo apt-get update
    #    sudo apt-get -y install ocrmypdf python3-pip
    #    pip install --user --upgrade ocrmypdf
    #    """
    #
    #    ## WINDOWS:
    #    """
    #    powershell.exe   *may have already
    #    choco to test
    #    https://chocolatey.org/install
    #
    #    from powershell admin:
    #    choco install python3
    #    choco install --pre tesseract
    #    choco install ghostscript
    #    choco install pngquant (optional)
    """

    return

if __name__=='__main__':
    branches=['install_steps']
    for b in branches:
        globals()[b]()



