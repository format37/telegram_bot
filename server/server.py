#!/usr/bin/env python
# -*- coding: utf-8 -*-
import ssl
import os
import requests
from aiohttp import web
import telebot
import json
import logging
import pandas as pd
from datetime import datetime as dt
import re
import pickle
import csv
import tempfile
import uuid

# init logging
logging.basicConfig(level=logging.INFO)
# logging.basicConfig(level=logging.WARNING)
logging.getLogger('aiohttp.access').setLevel(logging.WARNING)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

WEBHOOK_HOST = os.environ.get('WEBHOOK_HOST', '')
# 443, 80, 88 or 8443 (port need to be 'open')
WEBHOOK_PORT = os.environ.get('WEBHOOK_PORT', '')
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

async def call_test(request):
    logging.info('call_test')
    content = "ok"
    return web.Response(text=content, content_type="text/html")


def default_bot_init(bot_token_env):
    API_TOKEN = os.environ.get(bot_token_env, '')
    bot = telebot.TeleBot(API_TOKEN)

    WEBHOOK_URL_BASE = "https://{}:{}".format(
        os.environ.get('WEBHOOK_HOST', ''),
        os.environ.get('WEBHOOK_PORT', '')
    )
    WEBHOOK_URL_PATH = "/{}/".format(API_TOKEN)

    # Remove webhook, it fails sometimes the set if there is a previous webhook
    bot.remove_webhook()

    # Set webhook
    wh_res = bot.set_webhook(
        url=WEBHOOK_URL_BASE + WEBHOOK_URL_PATH, certificate=open(WEBHOOK_SSL_CERT, 'r'))
    print(bot_token_env, 'webhook set', wh_res)
    # print(WEBHOOK_URL_BASE + WEBHOOK_URL_PATH)

    return bot


# Process webhook calls
async def handle(request):
    for bot in bots:
        if request.match_info.get('token') == bot.token:
            request_body_dict = await request.json()
            update = telebot.types.Update.de_json(request_body_dict)
            bot.process_new_updates([update])
            return web.Response()

    return web.Response(status=403)


bots = []

# === @pantherabot ++
pantherabot = default_bot_init('PANTHERABOT_TOKEN')
bots.append(pantherabot)

@pantherabot.message_handler(commands=['help', 'start'])
def pantherabot_help_start(message):
    id37bot.reply_to(message, 'hello')
# === @pantherabot --

def main():
    logging.info('Init')
    app = web.Application()
    app.router.add_post('/{token}/', handle)
    app.router.add_route('GET', '/test', call_test)
    # Build ssl context
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(WEBHOOK_SSL_CERT, WEBHOOK_SSL_PRIV)
    logging.info('Starting')
    # Start aiohttp server
    web.run_app(
        app,
        host=WEBHOOK_LISTEN,
        port=os.environ.get('DOCKER_PORT', ''),
        ssl_context=context
    )
    

if __name__ == "__main__":
    main()
