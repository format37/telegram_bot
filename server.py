#!/usr/bin/env python
# -*- coding: utf-8 -*-
# https://github.com/eternnoir/pyTelegramBotAPI/tree/master/examples/webhook_examples
# https://core.telegram.org/bots/api

import logging
import ssl
from aiohttp import web
import telebot
from telebot import types
import asyncio
import sys
import os

SCRIPT_PATH	= '/home/format37_gmail_com/projects/telegram_bot_server/'
#SCRIPT_PATH	= '/home/dvasilev/projects/telegram_bot_server/'

WEBHOOK_HOST = 'www.scriptlab.net'
#WEBHOOK_HOST = 'www.service.icecorp.ru'
WEBHOOK_PORT = 8443  # 443, 80, 88 or 8443 (port need to be 'open')
WEBHOOK_LISTEN = '0.0.0.0'  # In some VPS you may need to put here the IP addr

WEBHOOK_SSL_CERT = SCRIPT_PATH+'webhook_cert.pem'  # Path to the ssl certificate
WEBHOOK_SSL_PRIV = SCRIPT_PATH+'webhook_pkey.pem'  # Path to the ssl private key

# Quick'n'dirty SSL certificate generation:
#
# openssl genrsa -out webhook_pkey.pem 2048
# openssl req -new -x509 -days 3650 -key webhook_pkey.pem -out webhook_cert.pem
#
# When asked for "Common Name (e.g. server FQDN or YOUR name)" you should reply
# with the same value in you put in WEBHOOK_HOST with www

logger = telebot.logger
telebot.logger.setLevel(logging.INFO)

app = web.Application()
bots	= []

def default_bot_init(WEBHOOK_HOST,WEBHOOK_PORT,WEBHOOK_SSL_CERT, SCRIPT_PATH):

	with open(SCRIPT_PATH+'token.key','r') as file:
		API_TOKEN=file.read().replace('\n', '')
		file.close()
	bot = telebot.TeleBot(API_TOKEN)

	WEBHOOK_URL_BASE = "https://{}:{}".format(WEBHOOK_HOST, WEBHOOK_PORT)
	WEBHOOK_URL_PATH = "/{}/".format(API_TOKEN)

	# Remove webhook, it fails sometimes the set if there is a previous webhook
	bot.remove_webhook()

	# Set webhook
	wh_res = bot.set_webhook(url=WEBHOOK_URL_BASE + WEBHOOK_URL_PATH,certificate=open(WEBHOOK_SSL_CERT, 'r'))
	print('webhook set',wh_res)
	print(WEBHOOK_URL_BASE + WEBHOOK_URL_PATH)

	return bot

# === === === home_cleaners_watcher_bot ++
try:
	HCWB_SCRIPT_PATH	= '/home/format37_gmail_com/projects/cleaner_bot/'
	sys.path.append(HCWB_SCRIPT_PATH)
	from cleaner_bot_script import cleaner_bot_user_authorized
	from cleaner_bot_script import cleaner_bot_stat
	from cleaner_bot_script import cleaner_bot_alert
	from cleaner_bot_script import cleaner_bot_counter_plus
	from cleaner_bot_script import cleaner_bot_counter_minus
	
	cleaner_bot	= default_bot_init(WEBHOOK_HOST,WEBHOOK_PORT,WEBHOOK_SSL_CERT,HCWB_SCRIPT_PATH)
	bots.append( cleaner_bot )	
	script_path = '/home/format37_gmail_com/projects/cleaner_bot/'
	cleaning_group_id = '-440064142'
	
	@cleaner_bot.message_handler(commands=['статистика'])
	def cleaner_bot_stat_func(message):
		if cleaner_bot_user_authorized(message.from_user.id,script_path):
			filepath = cleaner_bot_stat(script_path)
			photo = open(filepath, 'rb')
			cleaner_bot.send_photo(message.chat.id, photo, reply_to_message_id = str(message))
			
	'''
	if message.text=='/cl':
		answer = 'Try this, for example:\n/cl 2+2'
	elif message.text.lower()=='/cl@calcubot':
		answer = 'Try this, for example:\n/cl@CalcuBot 2+2'
	elif message.text[:4]=='/cl@' and message.text[:12].lower()!='/cl@calcubot':
		answer = ''
		pass
	else:
		message_text_prepared = str(message.text)[12:]
	'''			
			
	@cleaner_bot.message_handler(commands=['отмена'])
	def cleaner_bot_task_cancel(message):
		if cleaner_bot_user_authorized(message.from_user.id,script_path):
			if message.text[:8]=='/отмена ':
				task = str(message.text)[8:]
				answer = cleaner_bot_counter_minus(message.from_user.id,script_path,task)
			else:
				answer = 'Ошибка в команде'
			cleaner_bot.reply_to(message, answer)
			
			
	@cleaner_bot.message_handler(commands=['посуда'])
	def cleaner_bot_alert_dishes(message):
		if cleaner_bot_user_authorized(message.from_user.id,script_path):
			task = 'посуда'
			if message.chat.id == message.from_user.id:
				answer = cleaner_bot_alert(script_path,task)
				cleaner_bot.send_message(cleaning_group_id, answer)
			else:
				answer = cleaner_bot_counter_plus(message.from_user.id,script_path,task)
				cleaner_bot.reply_to(message, answer)
				
	@cleaner_bot.message_handler(commands=['мусор'])
	def cleaner_bot_alert_garbage(message):
		if cleaner_bot_user_authorized(message.from_user.id,script_path):
			task = 'мусор'
			if message.chat.id == message.from_user.id:
				answer = cleaner_bot_alert(script_path,task)
				cleaner_bot.send_message(cleaning_group_id, answer)
			else:
				answer = cleaner_bot_counter_plus(message.from_user.id,script_path,task)
				cleaner_bot.reply_to(message, answer)
				
	@cleaner_bot.message_handler(commands=['туалет'])
	def cleaner_bot_alert_toilet(message):
		if cleaner_bot_user_authorized(message.from_user.id,script_path):
			task = 'туалет'
			if message.chat.id == message.from_user.id:
				answer = cleaner_bot_alert(script_path,task)
				cleaner_bot.send_message(cleaning_group_id, answer)
			else:
				answer = cleaner_bot_counter_plus(message.from_user.id,script_path,task)
				cleaner_bot.reply_to(message, answer)

except Exception as e:
	print('home_cleaners_watcher_bot',str(e))
# === === === home_cleaners_watcher_bot --

# === === === id37bot ++
IDBOT_SCRIPT_PATH	= '/home/format37_gmail_com/projects/id37bot/'
idbot	= default_bot_init(WEBHOOK_HOST,WEBHOOK_PORT,WEBHOOK_SSL_CERT,IDBOT_SCRIPT_PATH)
bots.append( idbot )

@idbot.message_handler(commands=['user'])
def idbot_user(message):
	idbot.reply_to(message, str(message.from_user.id))
	
@idbot.message_handler(commands=['group'])
def idbot_group(message):
	idbot.reply_to(message, str(message.chat.id))

@idbot.message_handler(commands=['link'])
def idbot_group(message):
	idbot.reply_to(message, 'https://scriptlab.net/telegram/bots/relaybot/relaylocked.php?chat='+str(message.chat.id)+'&text=example')
	
@idbot.inline_handler(func=lambda chosen_inline_result: True)
def query_text(inline_query):
	try:		
		answer	= [
			str(inline_query.from_user.id),
			
			'id: '				+ str(inline_query.from_user.id) 		+ '\n'+
			'is_bot: '			+ str(inline_query.from_user.is_bot) 	+ '\n'+
			'first_name: '		+ str(inline_query.from_user.first_name)+ '\n'+
			'last_name: '		+ str(inline_query.from_user.last_name)	+ '\n'+
			'username: '		+ str(inline_query.from_user.username)	+ '\n'+
			'language_code: '	+ str(inline_query.from_user.language_code)
		]
		responce = [
			types.InlineQueryResultArticle('id', answer[0], types.InputTextMessageContent( answer[0] )),
			types.InlineQueryResultArticle('full', answer[1], types.InputTextMessageContent( answer[1] ))
		]
		idbot.answer_inline_query(inline_query.id, responce)
		
	except Exception as e:
		print(str(e))		
# === === === id37bot --		
		
# === === === rover ++
try:
	ROVER_DELAY = 4
	ROVER_SPEED = 100
	ROVER_SCRIPT_PATH	= '/home/format37_gmail_com/projects/telegram_rover/'
	sys.path.append(ROVER_SCRIPT_PATH)
	from telegram_rover import bot_init as rover_init, move_cmd, move_f, move_b, move_l, move_r, rover_photo, rover_photo_night, rover_send_video_merged, rover_charge_mode
	rover	= rover_init(WEBHOOK_HOST,WEBHOOK_PORT,WEBHOOK_SSL_CERT,ROVER_SCRIPT_PATH)
	bots.append( rover )

	@rover.message_handler(commands=['cmd'])
	def rover_move_cmd(message):
		rover.reply_to(message, move_cmd(message.chat.id,str(message.text)[4:]) )

	@rover.message_handler(commands=['f'])
	def rover_move_f(message):
		rover.reply_to( message, move_f(message.chat.id,ROVER_DELAY,ROVER_SPEED) )
		
	@rover.message_handler(commands=['b'])
	def rover_move_b(message):
		rover.reply_to(message, move_b(message.chat.id,ROVER_DELAY,ROVER_SPEED)	)	
		
	@rover.message_handler(commands=['l'])
	def rover_move_l(message):
		rover.reply_to(message, move_l(message.chat.id,ROVER_DELAY,ROVER_SPEED) )
		
	@rover.message_handler(commands=['r'])
	def rover_move_r(message):
		rover.reply_to(message, move_r(message.chat.id,ROVER_DELAY,ROVER_SPEED) )

	@rover.message_handler(commands=['p'])
	def rover_get_photo(message):
		rover.reply_to(message, rover_photo(message.chat.id) )
	
	@rover.message_handler(commands=['n'])
	def rover_get_photo_night(message):
		rover.reply_to(message, rover_photo_night(message.chat.id) )
		
	@rover.message_handler(commands=['c'])
	def rover_set_charge_mode(message):
		rover.reply_to(message, rover_charge_mode(message.chat.id) )
		
	@rover.message_handler(commands=['v'])
	def rover_send_video(message):
		rover.reply_to(message, rover_send_video_merged(message.chat.id) )
		
except Exception as e:
		print('rover',str(e))
# === === === rover --

# === === === calcubot ++

CALCUBOT_SCRIPT_PATH     = '/home/format37_gmail_com/projects/calcubot_python/'
#CALCUBOT_SCRIPT_PATH     = '/home/dvasilev/projects/calcubot_python/'

sys.path.append(CALCUBOT_SCRIPT_PATH)
from calcubot import calcubot_init, calcubot_about, calcubot_help, calcubot_eval, calcubot_words, calcubot_plot
calcubot	= calcubot_init(WEBHOOK_HOST,WEBHOOK_PORT,WEBHOOK_SSL_CERT, CALCUBOT_SCRIPT_PATH)
bots.append( calcubot )

CALCUBOT_WORDS = calcubot_words(CALCUBOT_SCRIPT_PATH)

@calcubot.inline_handler(func=lambda chosen_inline_result: True)
def query_text(inline_query):
	try:
		message_text_prepared = inline_query.query.strip()
		if message_text_prepared!='':
			god_mode	= inline_query.from_user.id==106129214
			answer	= calcubot_eval(CALCUBOT_SCRIPT_PATH,True,inline_query.query,god_mode,CALCUBOT_WORDS)
			calcubot.answer_inline_query(inline_query.id, answer)
		else:
			answer	= ['Empty expression..']
			responce = [types.InlineQueryResultArticle('result', answer[0], types.InputTextMessageContent( answer[0] ))] 
			calcubot.answer_inline_query(inline_query.id, responce)
	except Exception as e:
		print(str(e))

@calcubot.message_handler(commands=['help', 'start'])
def send_help(message):
	link = calcubot_help(CALCUBOT_SCRIPT_PATH)
	#gif = open(filepath, 'rb')
	#calcubot.send_animation(message.chat.id, link, reply_to_message_id = str(message))
	#calcubot.send_document(message.chat.id, link, reply_to_message_id = str(message))
	calcubot.send_video(message.chat.id, link, reply_to_message_id = str(message))
	
@calcubot.message_handler(commands=['about'])
def send_about(message):
	answer = calcubot_about()
	calcubot.reply_to(message, answer)

@calcubot.message_handler(commands=['cl'])
def send_user(message):
	if message.text=='/cl':
		answer = 'Try this, for example:\n/cl 2+2'
	elif message.text.lower()=='/cl@calcubot':
		answer = 'Try this, for example:\n/cl@CalcuBot 2+2'
	elif message.text[:4]=='/cl@' and message.text[:12].lower()!='/cl@calcubot':
		answer = ''
		pass
	else:
		message_text_prepared = str(message.text)[12:] if message.text[:12].lower()=='/cl@calcubot' else str(message.text)[3:]
		god_mode	= message.from_user.id==106129214
		answer	= calcubot_eval(CALCUBOT_SCRIPT_PATH,False, message_text_prepared,god_mode,CALCUBOT_WORDS)
	if answer != '':
		calcubot.reply_to(message, answer)

@calcubot.message_handler(commands=['plot'])
def send_plot(message):
	if message.text=='/plot':
		answer = 'Try this, for example:\n/plot [ [math.sin(i)*pow(i,4) for i in range(10,30)] ]'
		calcubot.reply_to(message, answer)
	elif message.text.lower()=='/plot@calcubot':
		answer = 'Try this, for example:\n/plot@CalcuBot [ [math.sin(i)*pow(i,4) for i in range(10,30)] ]'
		calcubot.reply_to(message, answer)
	elif message.text[:6]=='/plot@' and message.text[:14].lower()!='/plot@calcubot':
		pass
	else:
		message_text_prepared = str(message.text)[14:] if message.text[:14].lower()=='/plot@calcubot' else str(message.text)[5:]
		god_mode = message.from_user.id==106129214
		answer,filepath = calcubot_plot(CALCUBOT_SCRIPT_PATH, message_text_prepared,god_mode,CALCUBOT_WORDS)
		if filepath=='':
			calcubot.reply_to(message, 'Declined. '+answer)
		else:
			photo = open(filepath, 'rb')
			calcubot.send_photo(message.chat.id, photo, reply_to_message_id = str(message), caption = message_text_prepared)
			os.remove(filepath)
		

@calcubot.message_handler()
def send_pm(message):
	if message.chat.id==message.from_user.id:
		god_mode = message.from_user.id==106129214
		answer	= calcubot_eval(CALCUBOT_SCRIPT_PATH,False, str(message.text),god_mode,CALCUBOT_WORDS)
		calcubot.reply_to(message, answer)
	
# === === === calcubot --

# Process webhook calls
async def handle(request):
	for bot in bots:
		if request.match_info.get('token') == bot.token:
			request_body_dict = await request.json()
			update = telebot.types.Update.de_json(request_body_dict)
			bot.process_new_updates([update])
			return web.Response()

	return web.Response(status=403)
	

app.router.add_post('/{token}/', handle)

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
