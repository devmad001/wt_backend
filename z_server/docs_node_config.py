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



#0v1# JC  Nov 20, 2023  Init



"""
    NODE
    - setup and install on ubuntu for wt_dash etc.
"""


def dev1():
    """
    curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.1/install.sh | bash
    source ~/.bashrc
    nvm --version
    nvm install 18.16.0

    node --version v18.16.0   *on laptop
    
    #NO#sudo apt-get -y install npm
    #NO# sudo apt-get -y install vite
    npm install vite

    npm run dev
    
    ** but if looking for outside localhost with dev: package.json -> 127.0.0.1 -> 0.0.0.0
    http://127.0.0.1:5173/
    http://3.20.195.157:5173/

    http://3.20.195.157:5173/case/case_atm_location/run
    


    npm install yarn
    yarn install
    yarn build
    yarn start



    """
    return


if __name__=='__main__':
    branches=['dev1']
    for b in branches:
        globals()[b]()



