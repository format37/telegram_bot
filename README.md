# Telegram bots server
Server, for a list of telegram bots, with webhooks and FastAPI.  
![Structure](assets/structure.png)  
The benefit of this structure is that it is possible to serve multiple bots without restarting all bots while working with a specific bot.
#### Requirements
* Domain name, linked to IP of your machine
* Docker
* Docker-compose
* Telegram bot token
#### Installation & SSL certificate setup
* Clone the repo:
```
git clone https://github.com/format37/telegram_bot.git
cd telegram_bot
```
* Link your domain name to ip of yor machine  
* Install Certbot
```
sudo apt-get update
sudo apt-get install certbot python3-certbot-nginx
```
* Set Up Nginx
```
sudo apt-get install nginx
# Replace yourdomain.com with your domain:
sudo nano /etc/nginx/sites-available/yourdomain.com
```
Paste the following, replacing the yourdomain.com:
```
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    location / {
        proxy_pass http://localhost:8443; # Assuming FastAPI runs on port 8443
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    listen 443 ssl; # managed by Certbot
    ssl_certificate /etc/letsencrypt/live/service.icecorp.ru/fullchain.pem; # managed by Certbot
    ssl_certificate_key /etc/letsencrypt/live/service.icecorp.ru/privkey.pem; # managed by Certbot
    include /etc/letsencrypt/options-ssl-nginx.conf; # managed by Certbot
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem; # managed by Certbot

}
```
* Enable the site, replacing yourdomain.com:
```
sudo ln -s /etc/nginx/sites-available/yourdomain.com /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```
* Getting the SSL Certificate
```
sudo certbot --nginx -d yourdomain.com
```
* Copy the SSL certificate to the project folder
```
sudo cp /etc/letsencrypt/live/service.icecorp.ru/fullchain.pem ./server/webhook_cert.pem
sudo cp /etc/letsencrypt/live/service.icecorp.ru/privkey.pem ./server/webhook_pkey.pem
```
* Build the docker image
```
sh build.sh
```
* Update the config.json and bots.json with your configuration  
* Run
```
sh run.sh
```