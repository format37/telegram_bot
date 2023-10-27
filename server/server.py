from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import telebot
import os
import logging
import ssl
import requests

# Initialize FastAPI
app = FastAPI()

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Environment variables
WEBHOOK_HOST = os.environ.get('WEBHOOK_HOST', '')
WEBHOOK_PORT = os.environ.get('WEBHOOK_PORT', '')
# 443, 80, 88 or 8443 (port need to be 'open')
WEBHOOK_LISTEN = '0.0.0.0'  # In some VPS you may need to put here the IP addr
WEBHOOK_SSL_CERT = 'webhook_cert.pem'
WEBHOOK_SSL_PRIV = 'webhook_pkey.pem'

# Quick'n'dirty SSL certificate generation:
#
# openssl genrsa -out webhook_pkey.pem 2048
# openssl req -new -x509 -days 3650 -key webhook_pkey.pem -out webhook_cert.pem
#
# When asked for "Common Name (e.g. server FQDN or YOUR name)" you should reply
# with the same value in you put in WEBHOOK_HOST


@app.get("/test")
async def call_test():
    logger.info('call_test')
    return JSONResponse(content={"status": "ok"})


# Initialize bot
def default_bot_init(bot_token_env):
    API_TOKEN = os.environ.get(bot_token_env, '')
    bot = telebot.TeleBot(API_TOKEN)

    # Set webhook
    WEBHOOK_URL_BASE = f"https://{WEBHOOK_HOST}:{WEBHOOK_PORT}"
    WEBHOOK_URL_PATH = f"/{API_TOKEN}/"

    logger.info(f'WEBHOOK_URL_BASE: {WEBHOOK_URL_BASE}')
    logger.info(f'WEBHOOK_URL_PATH: {WEBHOOK_URL_PATH}')
    logger.info(f'WEBHOOK_SSL_CERT: {WEBHOOK_SSL_CERT}')

    bot.remove_webhook()
    wh_res = bot.set_webhook(url=f"{WEBHOOK_URL_BASE}{WEBHOOK_URL_PATH}", certificate=open(WEBHOOK_SSL_CERT, 'r'))
    logger.info(f'webhook set: {wh_res}')

    return bot


@app.post("/{token}/")
async def handle(token: str, request: Request):
    request_body_dict = await request.json()
    update = telebot.types.Update.de_json(request_body_dict)

    if token == pantherabot.token:
        pantherabot.process_new_updates([update])
        return JSONResponse(content={"status": "ok"})
    else:
        raise HTTPException(status_code=403, detail="Invalid token")


# bots = []

# === @pantherabot ++
pantherabot = default_bot_init('PANTHERABOT_TOKEN')
@pantherabot.message_handler()
def pantherabot_message(message):
    logger.info(f'pantherabot_message from: {message.chat.id}')
    body = message.json
    BOT_PORT = os.environ.get('PANTHERABOT_PORT', '')
    # Send message to the server    
    message_url = f'http://localhost:{BOT_PORT}/message'
    result = requests.post(message_url, json=body)
    if result.status_code != 200:
        logger.error(f"Failed to send message. Status code: {result.status_code}, Response: {result.content}")
    else:
        logger.info(f'result: {str(result.text)}')
        # INFO:server:result: {"status":"ok","message":"test answer"}
        # reply by result['message']
        pantherabot.reply_to(message, result.text.['message'])
# === @pantherabot --
