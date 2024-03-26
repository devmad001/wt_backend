1.

apt install python3.10
apt install python3-pip
pip install -r requirements_dev.txt
pip install mysqlclient
pip install fastapi sqlalchemy
sudo apt-get update
sudo apt-get install pkg-config
 
sudo apt install mysql-server
sudo apt install libmysqlclient-dev
sudo apt install mysql-client
sudo apt install mysql-server -y

sudo mysql_secure_installation

sudo mysql
    mysql> CREATE USER 'watchtower'@'%' IDENTIFIED BY 'WTuser321!';
    mysql> GRANT ALL PRIVILEGES ON * .* TO 'watchtower'@'%';
    mysql> FLUSH PRIVILEGES;
    mysql> create database wtengine;

-copy dump.sql into local machine 
    mysql -u watchtower -p wtengine < dump.sql

-copy FINAWARE_CONFIGS into local machine's specific folder
    change ip into 127.0.0.1 in db_config.ini

-make directory named CASE_FILES_STORAGE, CASE_FILES_GOOGLE_SYNC in same level with sever code
-make storage in CASE_FILES_STORAGE
-make directory named 'logs' in w_datasetes and make file named info.log 
-copy file 'w_config_dashboard.json' into wt_backend
-copy google.prod_COMMITED_TO_GIT.json and google.staging_COMMITED_TO_GIT.json in z_apiengine/services/external_interfaces
-run python FASTMAIN_prod_auto_server.py
sudo wget -P /usr/local/share/tessdata/ https://github.com/tesseract-ocr/tessdata/raw/main/eng.traineddata
sudo wget -P /usr/local/share/tessdata/ https://github.com/tesseract-ocr/tessdata/raw/main/osd.traineddata


-apt-get install -y python3-certbot-nginx     

-sudo nano /etc/nginx/conf.d/coredev.conf
-type the following content into file
    server {
        listen 80;
        listen [::]:80;
        root /var/www/html;
        server_name coredev.epventures.co;

        location / {
            proxy_pass http://localhost:8008;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload";
            client_max_body_size 0;
        }

        location /.well-known/carddav {
        return 301 $scheme://$host/remote.php/dav;
        }

        location /.well-known/caldav {
        return 301 $scheme://$host/remote.php/dav;
        }

    }

-sudo certbot --nginx -d coredev.epventures.co
-sudo ln -s /etc/nginx/sites-available/coredev.epventures.co /etc/nginx/sites-enabled/

-sudo chown -R root:www-data /etc/letsencrypt/live
-sudo chown -R root:www-data /etc/letsencrypt/archive
-sudo chmod -R 750 /etc/letsencrypt/live
-sudo chmod -R 750 /etc/letsencrypt/archive
-sudo nginx -t
-sudo systemctl reload nginx


2.

-create github action workflow with main.yml
    name: Remote SSH
    on: [push]

    jobs:
    deploy:
        runs-on: ubuntu-latest
        steps:
        - name: Checkout code
            uses: actions/checkout@v2

        - name: Deploy to EC2
            uses: appleboy/ssh-action@master
            with:
            host: 3.23.126.187
            username: ubuntu
            key: ${{ secrets.SSH_KEY }}
            script: |
                cd /home/ubuntu/server/wt-backend/
                git pull

-copy private key into git secret key with variable named 'SSH_KEY'



