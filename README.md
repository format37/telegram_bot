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
You need to replace YOUR-DOMAIN.COM with your domain in all the following steps.
```
sudo apt-get install nginx
```
* Create a new configuration file for your domain in the /etc/nginx/sites-available directory:
```
sudo nano /etc/nginx/sites-available/YOUR-DOMAIN.COM
```
* Add the following configuration to the file:
```
server {
    listen 80;
    server_name YOUR-DOMAIN.COM;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```
* Enable the site:
```
sudo ln -s /etc/nginx/sites-available/YOUR-DOMAIN.COM /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```
* Getting the SSL Certificate
```
sudo certbot --nginx -d YOUR-DOMAIN.COM
```
* Enabling auto-renewal
```
sudo certbot renew --dry-run
```
* Replace YOUR-DOMAIN.COM with your domain in files: docker-compose.yml and config.json
* Update the config.json and bots.json with your configuration  
* Run
```
sh compose.sh
```
* Check logs
```
sh logs.sh
```