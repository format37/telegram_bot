from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import telebot
import os
import logging
import ssl
import requests
import json

# Initialize FastAPI
app = FastAPI()

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

@app.get("/test")
async def call_test():
    logger.info('call_test')
    return JSONResponse(content={"status": "ok"})


# Initialize bot
def default_bot_init(bot_token_env):
    logger.info(f'default_bot_init. API_TOKEN: {bot_token_env}')
    bot = telebot.TeleBot(bot_token_env)

    # Read config.json
    with open('config.json') as config_file:
        config = json.load(config_file)

    # Set webhook
    WEBHOOK_URL_BASE = f"https://{config['WEBHOOK_HOST']}:{config['WEBHOOK_PORT']}"
    WEBHOOK_URL_PATH = f"/{bot_token_env}/"

    # logger.info(f'WEBHOOK_URL_BASE: {WEBHOOK_URL_BASE}')
    # logger.info(f'WEBHOOK_URL_PATH: {WEBHOOK_URL_PATH}')

    bot.remove_webhook()
    # log WEBHOOK_URL_BASE
    # logger.info(f'WEBHOOK_URL_BASE: {WEBHOOK_URL_BASE}')
    # log WEBHOOK_URL_PATH
    # logger.info(f'WEBHOOK_URL_PATH: {WEBHOOK_URL_PATH}')
    wh_res = bot.set_webhook(
        url=f"{WEBHOOK_URL_BASE}{WEBHOOK_URL_PATH}", 
        certificate=open('webhook_cert.pem', 'r'),
        allowed_updates=['message', 'callback_query']
        )
    logger.info(f'webhook set: {wh_res}')

    return bot


def get_bot_feature_by_token(token, feature):
    # logger.info(f'get_bot_feature_by_token. token: {token}, feature: {feature}')
    # logger.info(f'bots: {bots}')
    for bot_key, bot_instance in bots.items():
        if bot_instance['TOKEN'] == token:
            return bot_instance[feature]
    return None


@app.post("/{token}/")
async def handle(token: str, request: Request):
    # logger.info(f'handle. Received token: {token}')
    request_body_dict = await request.json()
    # logger.info(f'Received request payload: {request_body_dict}')
    update = telebot.types.Update.de_json(request_body_dict)

    bot = get_bot_feature_by_token(token, 'bot')
    if bot != None:
        # logger.info(f'Received bot: {bot.token}')
        if update.message:
            # logger.info('update.message')
            # if update.message.photo:
                # logger.info(f"Image received: {update.message.photo[0].file_id}")
            bot.process_new_updates([update])
            # logger.info('After processing new updates.')
        else:
            logger.info(f'update have no candidate: {update}')

        return JSONResponse(content={"status": "ok"})
    else:
        logger.info(f'Failed to retrieve bot object: {token}')
        raise HTTPException(status_code=403, detail="Invalid token")


# General message handler function
def generic_message_handler(bot, message):
    body = message.json
    # logger.info('generic_message_handler from ' + bot.token)
    logger.info(f'body: {body}')
    BOT_PORT = get_bot_feature_by_token(bot.token, 'PORT')
    message_url = f'http://localhost:{BOT_PORT}/message'
    # logger.info(f'### Sending message_url: {message_url}')
    # logger.info(f'body: {body}')
    
    headers = {'Authorization': f'Bearer {bot.token}'}
    # result = requests.post(message_url, json=body)
    result = requests.post(message_url, json=body, headers=headers)

    # logger.info(f'result: {str(result)}')
    if result.status_code != 200:
        logger.error(f"Failed to send message. Status code: {result.status_code}, Response: {result.content}")
    else:
        if result.headers['Content-Type'].startswith('image/'):
            # FileResponse with image
            bot.send_photo(message.chat.id, result.content)
        elif result.headers['Content-Type'] == 'application/json':
            # logger.info(f'generic_message_handler result: {str(result.text)}')
            result_message = json.loads(result.text)
            logger.info(f'generic_message_handler application/json result_message: {result_message}')
            if result_message['type'] == 'text':
                logger.info(f'generic_message_handler text from {bot.token}')
                bot.reply_to(message, result_message['body'])
            
            elif result_message['type'] == 'keyboard':
                logger.info(f'generic_message_handler keyboard from {bot.token}')
                keyboard_dict = result_message['body']
                if 'keyboard_type' in result_message and result_message['keyboard_type'] == 'inline':
                    logger.info(f'{message.chat.id} inline keyboard from {bot.token}')
                    keyboard = telebot.types.InlineKeyboardMarkup(
                        row_width=keyboard_dict['row_width']                        
                    )
                    # resize_keyboard=keyboard_dict['resize_keyboard'],
                    logger.info(f'{message.chat.id} inline key button list length: {len(keyboard_dict["buttons"])}')
                    """for button_definition in keyboard_dict['buttons']:
                        logger.info(f'Adding button: {button_definition["text"]}')
                        button = telebot.types.InlineKeyboardButton(
                            text=button_definition['text']
                        )
                        # callback_data=button_definition['callback_data']
                        keyboard.add(button)"""
                    
                    for button_group in keyboard_dict['buttons']:
                        buttons = []
                        for button_definition in button_group:
                            logger.info(f'Adding button: {button_definition["text"]}')
                            button = telebot.types.InlineKeyboardButton(
                                text=button_definition['text'],
                                callback_data=button_definition['callback_data']
                            )
                            buttons.append(button)
                        keyboard.add(*buttons)

                else:
                    logger.info(f'{message.chat.id} reply keyboard from {bot.token}')
                    keyboard = telebot.types.ReplyKeyboardMarkup(
                        row_width=keyboard_dict['row_width'], 
                        resize_keyboard=keyboard_dict['resize_keyboard'],
                    )
                    for button_definition in keyboard_dict['buttons']:
                        # logger.info(f'button callback_data: {button_definition["callback_data"]}')
                        button = telebot.types.KeyboardButton(
                            text=button_definition['text'],
                            request_contact=button_definition['request_contact']
                        )
                        keyboard.add(button)
                    
                bot.send_message(
                    message.chat.id, 
                    keyboard_dict['message'], 
                    reply_markup=keyboard
                )
            elif result_message['type'] == 'image':
                logger.info(f'generic_message_handler image from {bot.token}')
                bot.send_photo(message.chat.id, result_message['body'])
            elif result_message['type'] == 'empty':
                logger.info(f'generic_message_handler empty from {bot.token}')
                pass            


content_types=[
    'text',
    'photo',
    'document',
    'audio',
    'video',
    'sticker',
    'contact',
    'location',
    'venue',
    'voice',
    'video_note',
    'new_chat_members',
    'left_chat_member',
    'new_chat_title',
    'new_chat_photo',
    'delete_chat_photo',
    'group_chat_created',
    'supergroup_chat_created',
    'channel_chat_created',
    'migrate_to_chat_id',
    'migrate_from_chat_id',
    'pinned_message',
    'invoice',
    'successful_payment',
    'connected_website',
    'passport_data',
    'proximity_alert_triggered',
    'dice',
    'poll',
    'poll_answer',
    'my_chat_member',
    'chat_member'
    ]


with open('bots.json') as bots_file:
    bots = json.load(bots_file)
    # logger.info(f'bots: {bots}')

for bot_key, bot_instance in bots.items():
    bot_instance['bot'] = default_bot_init(bot_instance['TOKEN'])
    @bot_instance['bot'].message_handler(content_types=content_types)
    def message_handler(message, bot=bot_instance['bot']):  # Default to the current bot instance
        # logger.info(f'### message_handler from bot:{bot.token} or {bot_instance["TOKEN"]} message: {message} ###')
        # generic_message_handler(bot_instance['bot'], message)
        generic_message_handler(bot, message)
