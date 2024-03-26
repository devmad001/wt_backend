


#0v2# JC  Jan 12, 2024  via gret
#0v1# JC  Oct 26, 2023  via gret



"""
    MYSQL support

"""


def DEVEOPS_notes():
    """
    **beware, mysql workbench freezes mysql server!
    sudo systemctrl restart mysql
    sudo systemctrl status mysql

    """
    return

def new_user_credentials():
    """
        1// admin login
        2// 

        mysql> CREATE USER 'watchtower'@'%' IDENTIFIED BY 'XXX';
        mysql> GRANT ALL PRIVILEGES ON * .* TO 'watchtower'@'%';
        mysql> GRANT SELECT, INSERT, UPDATE, DELETE ON wtengine.* TO 'shankar'@'%'; 

    """

    return

def new_user_credentials():
    """
    This function outlines the steps to create a new MySQL user and grant them privileges.
    """

    # Step 1: Admin login not shown here; it's assumed to be handled by your database connection setup.
    # mysql -u root
    # mysql -u watchtower -p xxxx

    # Step 2: Create a new user
    create_user_sql = "CREATE USER 'watchtower'@'%' IDENTIFIED BY 'your_password_here';"

    # Step 3: Grant all privileges to the new user on all databases and tables
    #  GRANT ALL PRIVILEGES ON *.* TO 'wt_hub'@'%';
    grant_privileges_sql = "GRANT ALL PRIVILEGES ON *.* TO 'watchtower'@'%';"

    # Step 3 (alternative): Grant specific privileges on a specific database
    grant_specific_privileges_sql = "GRANT SELECT, INSERT, UPDATE, DELETE ON wtengine.* TO 'shankar'@'%';"

    # Step 4: Apply changes
    flush_privileges_sql = "FLUSH PRIVILEGES;"

    return
    
def install_notes():
    ## TO WATCH:
    #- administrator password!
    #- user password!
    #- root password!
    
    #- port 3306 open
    #- firewall
    #- remote access  (IP ranges)
    #- user access
    #- user access from remote

    
    #>. possibly have already

    #- sudo apt install mysql-server
    #- sudo apt install mysql-client
    #- sudo apt install libmysqlclient-dev
    #- sudo apt install python3-dev
    #- sudo apt install python3-pip
    #- sudo apt install python3-mysqldb
    #- sudo apt install python3-mysql.connector
    
    ## With SQLAlchemy support
    #- sudo apt install python3-sqlalchemy
    
    return

def actual_install_steps():
    """
    ** allow gpt suggestions
    
    sudo apt install mysql-server -y
    sudo mysql_secure_installation
    ^^ root must login locally

    ## LOGIN
    sudo mysql

        mysql> CREATE USER 'watchtower'@'%' IDENTIFIED BY 'XXX';
        mysql> GRANT ALL PRIVILEGES ON * .* TO 'watchtower'@'%';


Allow Remote Access:
Open the MySQL config file:

bash
Copy code
sudo nano /etc/mysql/mysql.conf.d/mysqld.cnf
Find the line that says bind-address and change its value to 0.0.0.0 (this allows connections from any IP address). Save and close the file.

Restart MySQL to apply changes:

bash
Copy code
sudo systemctl restart mysql.service
Open Ports on UFW (if you're using it):
Allow MySQL traffic:

bash
Copy code
sudo ufw allow 3306/tcp
Reload UFW:

bash
Copy code
sudo ufw reload
3. SQLAlchemy ORM Interface via Python:
Install necessary Python packages:

bash
Copy code
pip install sqlalchemy mysqlclient
Sample Python code to connect to your MySQL server using SQLAlchemy:

python
Copy code
from sqlalchemy import create_engine, MetaData

# Replace username, password, and dbname with your values
DATABASE_URL = "mysql+mysqldb://username:password@localhost/dbname"

engine = create_engine(DATABASE_URL)
metadata = MetaData()

# Now you can use this engine and metadata to define and interact with your tables.

CREATE DATABASE:
CREATE DATABASE dbname;

    

    """

    return

def dev_try_connect():
    from sqlalchemy import create_engine, MetaData

    # Replace username, password, and dbname with your values
    username='watchtower'
    password='xxx'
    ip='3.20.195.157'
    database='wtengine'

    DATABASE_URL = "mysql+mysqldb://"+username+":"+password+"@"+ip+"/"+database
    
    print ("FO: "+str(DATABASE_URL))
    engine = create_engine(DATABASE_URL)
    metadata = MetaData()
    
    # Now you can use this engine and metadata to define and interact with your tables.

    print ("Connected")
    return

def dev_try_connect_2():
    from sqlalchemy import create_engine, MetaData
    # Replace username, password, and dbname with your values
    username='shankar'
    password='xxx!'
    ip='3.20.195.157'
    database='wtengine'
    DATABASE_URL = "mysql+mysqldb://"+username+":"+password+"@"+ip+"/"+database
    print ("FO: "+str(DATABASE_URL))
    engine = create_engine(DATABASE_URL)
    metadata = MetaData()
    # Now you can use this engine and metadata to define and interact with your tables.
    print ("Connected")
    
    ## BUT WHAT COMMANDS?
    #GRANT SELECT, INSERT, UPDATE, DELETE ON your_database_name.* TO 'shankar'@'host'; 

    return

"""
shivam who created table

sudo mysqldump -u root -p wtengine > wtengine_dump.sql


"""

if __name__=='__main__':
    branches=[]
    branches+=['dev_try_connect']
    branches+=['dev_try_connect_2']

    for b in branches:
        globals()[b]()
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
