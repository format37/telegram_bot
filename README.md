# Telegram bots python docker server
Docker server, for a list of telegram bots, with aiohttp and webhooks  
![Structure](assets/structure_v1.png)  
The benefit of this structure is that it is possible to serve multiple bots without restarting all bots while working with a specific bot.
#### installation
* Clone the repo:
```
git clone https://github.com/format37/telegram_bot_server.git
cd telegram_bot_docker
```
* Link your domain name to ip of yor machine  
* Make a cert files on a server machine:  
When asked for "Common Name (e.g. server FQDN or YOUR name)" you need to reply this way: www.your_domain.name
```
openssl genrsa -out server/webhook_pkey.pem 2048
openssl req -new -x509 -days 3650 -key server/webhook_pkey.pem -out server/webhook_cert.pem
```
* Fill the bot token, ports, domain name in docker-compose.yml  
* Run
```
sh compose.sh
```