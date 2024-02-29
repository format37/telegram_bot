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
You need to replace yourdomain.com with your domain in all the following steps.
```
sudo apt-get install nginx
```
* Enable the site:
```
sudo ln -s /etc/nginx/sites-available/yourdomain.com /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```
* Getting the SSL Certificate
```
sudo certbot --nginx -d yourdomain.com
```
* Enabling auto-renewal
```
sudo certbot renew --dry-run
```
* Don't forget to replace yourdomain.com with your domain in the docker-compose.yml
* Build the docker image
```
sh build.sh
```
* Update the config.json and bots.json with your configuration  
* Run
```
sh run.sh
```