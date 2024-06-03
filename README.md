# Telegram bots server
Local server, for a list of telegram bots, with webhooks and FastAPI.  
![Structure](assets/structure.png)  
The benefit of this structure is that it is possible to serve multiple bots without restarting all bots while working with a specific bot.
## Installation
Use docker image(https://hub.docker.com/r/aiogram/telegram-bot-api)  
or install  locally:
```
sudo apt-get update
sudo apt-get upgrade
sudo apt-get install make git zlib1g-dev libssl-dev gperf cmake g++
git clone --recursive https://github.com/tdlib/telegram-bot-api.git
cd telegram-bot-api
rm -rf build
mkdir build
cd build
cmake -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX:PATH=.. ..
cmake --build . --target install
ls -l telegram-bot-api/bin/telegram-bot-api*
```
## Get API ID and Hash
1. Go to https://my.telegram.org/auth
2. Log in with your phone number
3. Click on [API Development Tools](https://my.telegram.org/apps)
4. Fill in the required fields
5. Click on Create Application
6. Copy the API ID and Hash
## Test run
Replace YOUR_API_ID and YOUR_HASH with your API ID and Hash
```
./bin/telegram-bot-api --api-id=YOUR_API_ID --api-hash=YOUR_HASH --local
```
## Run as a daemon
Edit the file
```
sudo nano /etc/systemd/system/telegram-bot-api.service
```
Paste the following content (replace FOLDER_TO_CLONED_REPO, YOUR_APP_ID and YOUR_HASH with your FOLDER_TO_CLONED_REPO, API ID and Hash)
```
[Unit]
Description=Telegram Bot API
After=network.target

[Service]
Type=simple
ExecStart=FOLDER_TO_CLONED_REPO/telegram-bot-api/bin/telegram-bot-api --api-id=YOUR_APP_ID --api-hash=YOUR_HASH --local
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```
Save and close the file
```
sudo systemctl daemon-reload
sudo systemctl enable telegram-bot-api
sudo systemctl start telegram-bot-api
```
Check the status
```
sudo systemctl status telegram-bot-api
```
Read the logs
```
sudo journalctl -fu telegram-bot-api --since today
```
## Log out your bot from the cloud server (if bot had webhooks at the cloud server)
You have to input the bot token
```
cd logout
python3 -m pip install -r requirements.txt
python3 logout.py
```