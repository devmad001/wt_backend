
notes="""

RESTART:
sudo service nginx restart

STATUS:
systemctl status nginx.service

SEEING ERROR:
0.0.0.0:80 failed (98: Address already in use)

WHAT LISTENING?
sudo netstat -peanut

/var/log/nginx/error.log

CONFIG FILES?

/etc/nginx/sites-enabled
sudo nginx -t']
    cmds+=['sudo systemctl restart nginx']
systemctl restart nginx']



you can include raw keys in gnix 
            server_name localhost;
            ssl on;
            ssl_certificate /home/attolee/sslkey/example.crt;
            ssl_certificate_key /home/attolee/sslkey/example.key;
            ssl_session_timeout 5m;
            ssl_protocols TLSv1 TLSv1.1 TLSv1.2;
            ssl_ciphers ALL:!ADH:!EXPORT56:-RC4+RSA:+HIGH:+MEDIUM:!EXP;
  
  
FLUIDKIT::::


server {
    listen 443 ssl;
    server_name covid.fluidkit.com;

    location / {
        proxy_set_header Host $host;
        proxy_pass https://127.0.0.1:8080;
    }

    ssl on;
    ssl_certificate /etc/letsencrypt/live/covid.fluidkit.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/covid.fluidkit.com/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;

#    return 301 $scheme://covid.fluidkit.com:8080$request_uri;
#    return 444;

}




SO JON DO STAND ALONE FETCH

echo sudo certbot certonly --standalone -d registryontario.com -d covid.registryontario.com -d coronavirus.registryontario.com

#########################
0)  ensure ufw allow 80
0)  ensure ufw allow 443

1)  stop nginx
sudo service nginx stop

2)
./venv/bin/certbot certonly
...webonly...


nginx still running pid:
 /run/nginx.pid

nginx -s stop

54.221.159.63


WORKS:

Key:
1)
- do stand alone so stop all nginx for now via:
nginx -s stop
- validate no pid at /run/ginx.pid

2)
- ensure IP really pointing correctly from namecheap

3)
python3.8 install or alt for certbot issues on install so virtual env does:
~/venv/bin/certbot certonly --standalone

4)  Note outputs:
certificate and chain:
/etc/letsencrypt/live/auditorkit.com/fullchain.pem
key:
/etc/letsencrypt/live/auditorkit.com/privkey.pem
Your certificate will expire on 2021-07-01. 

uninstall gunix

sudo apt-get remove nginx nginx-common


BUT,
'*.example.com'
or -d www.gretnet.com -d gretnet.com

=====
JON biggest lesson.  may just want to do stand-alone
validation rather then adding in layer of nginx too soon.

"""




