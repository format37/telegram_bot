#!/usr/bin/env python
# -*- coding: utf-8 -*-
# https://github.com/eternnoir/pyTelegramBotAPI/tree/master/examples/webhook_examples

import logging
import ssl
from aiohttp import web
import telebot
import asyncio

WEBHOOK_HOST = 'www.scriptlab.net'
WEBHOOK_PORT = 8443  # 443, 80, 88 or 8443 (port need to be 'open')
WEBHOOK_LISTEN = '0.0.0.0'  # In some VPS you may need to put here the IP addr

SCRIPT_PATH	= '/home/format37_gmail_com/projects/telegram_bot_server/'

#WEBHOOK_SSL_CERT = '/home/format37_gmail_com/cert/fullchain.pem'  # Path to the ssl certificate
#WEBHOOK_SSL_PRIV = '/home/format37_gmail_com/cert/privkey.pem'  # Path to the ssl private key
WEBHOOK_SSL_CERT = SCRIPT_PATH+'webhook_cert.pem'  # Path to the ssl certificate
WEBHOOK_SSL_PRIV = SCRIPT_PATH+'webhook_pkey.pem'  # Path to the ssl private key

# Quick'n'dirty SSL certificate generation:
#
# openssl genrsa -out webhook_pkey.pem 2048
# openssl req -new -x509 -days 3650 -key webhook_pkey.pem -out webhook_cert.pem
#
# When asked for "Common Name (e.g. server FQDN or YOUR name)" you should reply
# with the same value in you put in WEBHOOK_HOST

logger = telebot.logger
telebot.logger.setLevel(logging.INFO)

with open(SCRIPT_PATH+'token.key','r') as file:
	API_TOKEN=file.read().replace('\n', '')
	file.close()
bot = telebot.TeleBot(API_TOKEN)

WEBHOOK_URL_BASE = "https://{}:{}".format(WEBHOOK_HOST, WEBHOOK_PORT)
WEBHOOK_URL_PATH = "/{}/".format(API_TOKEN)

app = web.Application()

# Process webhook calls
async def handle(request):
    print('request',request)
    if request.match_info.get('token') == bot.token:
        request_body_dict = await request.json()
        update = telebot.types.Update.de_json(request_body_dict)
        bot.process_new_updates([update])
        return web.Response()
    else:
        return web.Response(status=403)

# Handle '/start' and '/help'
@bot.message_handler(commands=['help', 'start'])
def send_welcome(message):
    bot.reply_to(message,"t1")

# Handle '/user'
@bot.message_handler(commands=['user'])
def send_user(message):
            bot.reply_to(message,   str(message.from_user.id) )	
	
# Handle '/group'
@bot.message_handler(commands=['group'])
def send_user(message):
            bot.reply_to(message,   str(message.chat.id) )
		

app.router.add_post('/{token}/', handle)
#app.router.add_route('POST', '/{token}/', handle)
#app.router.add_route('GET', '/relay', get_relay_text)

# Remove webhook, it fails sometimes the set if there is a previous webhook
bot.remove_webhook()

# Set webhook
wh_res = bot.set_webhook(url=WEBHOOK_URL_BASE + WEBHOOK_URL_PATH,
                certificate=open(WEBHOOK_SSL_CERT, 'r'))
print('webhook set',wh_res)
print(WEBHOOK_URL_BASE + WEBHOOK_URL_PATH)

# Build ssl context
context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
context.load_cert_chain(WEBHOOK_SSL_CERT, WEBHOOK_SSL_PRIV)

# Start aiohttp server
web.run_app(
    app,
    host=WEBHOOK_LISTEN,
    port=WEBHOOK_PORT,
    ssl_context=context,
)
