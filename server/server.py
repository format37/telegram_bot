from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import telebot
import logging
import json
import requests
from fastapi import FastAPI, Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
import asyncio

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Initialize FastAPI
app = FastAPI()

# Initialize bots and set webhooks
bots = {}

# Read blocked IP addresses from file
"""def read_blocked_ips():
    with open('blocked.txt', 'r') as blocked_file:
        blocked_ips = blocked_file.readlines()
        blocked_ips = [ip.strip() for ip in blocked_ips]
    return blocked_ips

blocked_ips = read_blocked_ips()

# Middleware for blocking requests from blocked IPs
class BlockIPMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        client_host = request.client.host
        if client_host in blocked_ips:
            raise HTTPException(status_code=403, detail="Access forbidden")
        return await call_next(request)

# Add the middleware to the app
app.add_middleware(BlockIPMiddleware)"""

# Your routes would go here
@app.get("/")
async def read_root():
    return {"Hello": "World"}

@app.get("/test")
async def call_test():
    logger.info('Test endpoint called')
    return JSONResponse(content={"status": "ok"})

# Simple text message handler function
def handle_text_message(bot, message, bot_config):

    if message.chat.type == 'group' and 'group_starters' in bot_config:
        granted_message = False
        for group_starter in bot_config['group_starters']:
            if message.text.startswith(group_starter):
                logger.info(f'Granted message from {message.chat.id}: {message.text}')
                granted_message = True
                break
        if not granted_message:
            return

    # logger.info(f'Received message from {message.chat.id}: {message.text}')
    body = message.json
    # logger.info(f'body: {body}')
    
    BOT_PORT = bot_config['PORT']

    message_url = f'http://localhost:{BOT_PORT}/message'
    # logger.info(f'### Sending message_url: {message_url}')
    headers = {'Authorization': f'Bearer {bot.token}'}
    result = requests.post(message_url, json=body, headers=headers)
    
    if result.status_code != 200:
        logger.error(f"Failed to send message. Status code: {result.status_code}, Response: {result.content}")
    else:
        if result.headers['Content-Type'].startswith('image/'):
            # FileResponse with image
            # bot.send_photo(message.chat.id, result.content)
            # logger.info(f'[{bot.token}] generic_message_handler IMAGE response for {message.chat.id}')
            pass

        # audio document
        elif result.headers['Content-Type'].startswith('audio/'):
            # FileResponse with audio
            # bot.send_audio(message.chat.id, result.content)
            # logger.info(f'[{bot.token}] generic_message_handler AUDIO response for {message.chat.id}')
            pass
            # Call audio
            

        elif result.headers['Content-Type'] == 'application/json':
            # logger.info(f'generic_message_handler result: {str(result.text)}')
            result_message = json.loads(result.text)
            # logger.info(f'generic_message_handler application/json result_message: {result_message}')
            if result_message['type'] == 'text':
                # logger.info(f'generic_message_handler text from {bot.token}')
                bot.reply_to(message, result_message['body'])
            
            elif result_message['type'] == 'keyboard':
                # logger.info(f'generic_message_handler keyboard from {bot.token}')
                keyboard_dict = result_message['body']
                if 'keyboard_type' in result_message and result_message['keyboard_type'] == 'inline':
                    # logger.info(f'{message.chat.id} inline keyboard from {bot.token}')
                    keyboard = telebot.types.InlineKeyboardMarkup(
                        row_width=keyboard_dict['row_width']                        
                    )
                    # resize_keyboard=keyboard_dict['resize_keyboard'],
                    # logger.info(f'{message.chat.id} inline key button list length: {len(keyboard_dict["buttons"])}')
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
                            # logger.info(f'Adding button: {button_definition["text"]}')
                            button = telebot.types.InlineKeyboardButton(
                                text=button_definition['text'],
                                callback_data=button_definition['callback_data']
                            )
                            buttons.append(button)
                        keyboard.add(*buttons)

                else:
                    # logger.info(f'{message.chat.id} reply keyboard from {bot.token}')
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
                # logger.info(f'generic_message_handler image from {bot.token}')
                bot.send_photo(message.chat.id, result_message['body'])
            elif result_message['type'] == 'empty':
                # logger.info(f'generic_message_handler empty from {bot.token}')
                pass


def handle_inline_query(bot, inline_query, bot_config):
    # logger.info(f'Received inline query from {inline_query.from_user.id}: {inline_query.query}')
    
    results = []  # This list should contain one or more objects of types.InlineQueryResult
    # Request results from server
    BOT_PORT = bot_config['PORT']
    inline_query_url = f'http://localhost:{BOT_PORT}/inline'
    headers = {'Authorization': f'Bearer {bot.token}'}
    # logger.info(f'### Sending inline_query_url: {inline_query_url}')
    # body = inline_query.json
    body = {
        "from_user_id": inline_query.from_user.id,
        "inline_query_id": inline_query.id,
        "query": inline_query.query
    }
    # logger.info(f'body type: {type(body)}')
    # logger.info(f'body: {body}')
    result = requests.post(inline_query_url, json=body, headers=headers)
    """
    logger.info(f'### Sending inline_query_url: {inline_query_url}')
    data = {
        "inline_query": inline_query.json
    }
    result = requests.post(inline_query_url, json=data)
    """
    # logger.info(f'inline_query result code: {result.status_code}')
    # logger.info(f'inline_query result headers: {result.headers}')
    # logger.info(f'inline_query result content: {result.content}')
    # result = json.loads(result.text)
    # logger.info(f'inline_query result: {result}')
    
    # Example: Generating one InlineQueryResultArticle
    # try:
    """result_article = telebot.types.InlineQueryResultArticle(
        id='1',
        title=result['title'],
        input_message_content=telebot.types.InputTextMessageContent(
            message_text=result['message_text']
        )
    )
    results.append(result_article)"""

    """# answer 0
    r0 = telebot.types.InlineQueryResultArticle(
        '0',
        answer[0],
        telebot.types.InputTextMessageContent(answer[0]),
    )

    # answer 1
    r1 = telebot.types.InlineQueryResultArticle(
        '1',
        answer[1],
        telebot.types.InputTextMessageContent(answer[1]),
    )

    # answer 2
    r2 = telebot.types.InlineQueryResultArticle(
        '2',
        answer[2],
        telebot.types.InputTextMessageContent(answer[2]),
    )

    answer = [r0, r1, r2]

    calcubot.answer_inline_query(
        inline_query.id,
        answer,
        cache_time=0,
        is_personal=True
    )  # updated"""

    # Actually, result is a dict like {'title': 'Solution', 'message_text': '["2 = 2", "2 = 2", "2"]'}, so we need to iterate in message_text
    """for i, message_text in enumerate(result['message_text']):
        curent_r = telebot.types.InlineQueryResultArticle(
            str(i),
            message_text,
            telebot.types.InputTextMessageContent(message_text),
        )
        results.append(curent_r)"""
    
    # If you have more results, generate them here and append to "results"
        
    """except Exception as e:
        logger.error(f'Error processing inline query: {str(e)}')

    # Sending results to Telegram
    bot.answer_inline_query(inline_query.id, results, cache_time=0, is_personal=True)"""


# Initialize bot
async def init_bot(bot_config):
    bot = telebot.TeleBot(bot_config['TOKEN'])

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
    
    # message_handler
    # @bot.message_handler(func=lambda message: True)
    @bot.message_handler(content_types=content_types)
    def message_handler(message):
        handle_text_message(bot, message, bot_config)

    # callback_query_handler
    @bot.callback_query_handler(func=lambda call: True)
    def callback_query_handler(call):
        # logger.info(f'Received callback query from {call.message.chat.id}: {call.data}')
        pass

    # Inline_query_handler
    @bot.inline_handler(func=lambda query: True)
    def inline_query_handler(query):
        # logger.info(f'Received inline query from {query.from_user.id}: {query.query}')
        handle_inline_query(bot, query, bot_config)

    # Read config.json
    with open('config.json') as config_file:
        config = json.load(config_file)

    webhook_url = f"https://{config['WEBHOOK_HOST']}:{config['WEBHOOK_PORT']}/{bot_config['TOKEN']}/"
    bot.remove_webhook()
    bot.set_webhook(url=webhook_url)

    return bot

@app.post("/{token}/")
async def handle_request(token: str, request: Request):
    if token in bots: 
        bot = bots[token]
        request_body_dict = await request.json()
        # logger.info(f'Received request for bot {token}: {request_body_dict}')
        try:
            update = telebot.types.Update.de_json(request_body_dict)
            bot.process_new_updates([update])
            return JSONResponse(content={"status": "ok"})
        except Exception as e:
            logger.error(f'Error processing request for bot {token}: {str(e)}')
            return JSONResponse(content={"status": "error"}, status_code=500)
    else:
        logger.error(f'Invalid token: {token} Bots: {bots}')
        return JSONResponse(content={"status": "error"}, status_code=403)


async def main():
    global bots
    # Load bot configurations
    with open('bots.json') as bots_file:
        bots_config = json.load(bots_file)

    for bot_key, bot_instance in bots_config.items():
        bots[bot_instance['TOKEN']] = await init_bot(bot_instance)
        logger.info(f'Bot {bot_key} initialized with webhook')

@app.on_event("startup")
async def startup_event():
    await main()
