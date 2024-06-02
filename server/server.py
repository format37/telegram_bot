from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import telebot
import logging
# import logging.config
import json
import requests
from fastapi import FastAPI, Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
import asyncio

# Initialize logging
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)
# logger.setLevel(logging.INFO)
logging.config.fileConfig('logging.ini')
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI()

# Initialize bots and set webhooks
bots = {}


# Your routes would go here
@app.get("/")
async def read_root():
    # Return ok, 200
    return JSONResponse(content={"status": "ok"})


@app.get("/test")
async def call_test():
    logger.info('Test endpoint called')
    return JSONResponse(content={"status": "ok"})


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    logger.warning(f"Invalid HTTP request received:")
    logger.warning(f"Method: {request.method}")
    logger.warning(f"URL: {request.url}")
    logger.warning(f"Headers: {request.headers}")
    # logger.warning(f"Body: {await request.body()}")
    return JSONResponse(content={"status": "error"}, status_code=exc.status_code)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # logger.info(f"Incoming request: {request.method} {request.url}")
        # logger.info(f"Headers: {request.headers}")
        # logger.info(f"Body: {await request.body()}")
        response = await call_next(request)
        return response

app.add_middleware(RequestLoggingMiddleware)


# Simple text message handler function
def handle_text_message(bot, message, bot_config):
    logger.info(f'handle_text_message from {message.chat.id}: {message.text}')
    if message.chat.type == 'group' and 'group_starters' in bot_config:
        granted_message = False
        for group_starter in bot_config['group_starters']:
            if message.text.startswith(group_starter):
                # logger.info(f'Granted message from {message.chat.id}: {message.text}')
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
        logger.error(f"handle_text_message: requests.post status code: {result.status_code}, Response: {result.content}")
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
                            text=button_definition.get('text', ''),
                            request_contact=button_definition.get('request_contact', False),
                            request_location=button_definition.get('request_location', False)
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
    return JSONResponse(content={"status": "ok"})


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
    # result = requests.post(inline_query_url, json=body, headers=headers)
    # Post request with 3 sec timeout
    try:
        result = requests.post(inline_query_url, json=body, headers=headers, timeout=2)
    except Exception as e:
        logger.error(f'Error sending inline query: {str(e)}')
    # Return ok, 200
    return JSONResponse(content={"status": "ok"})

    # from_user_id = inline_query.from_user.id
    # inline_query_id = inline_query.id
    # expression = inline_query.query

    # if result.status_code == 200:
    #     try:
    #         result_message = json.loads(result.text)
    #         answer = result_message['body']
    #         if result_message['type'] != 'inline':
    #             logger.error(f'Inline: Invalid response type: {result_message["type"]}')
    #             return
    #         inline_elements = []
    #         for i in range(len(answer)):    
    #             element = telebot.types.InlineQueryResultArticle(
    #                 str(i),
    #                 answer[i],
    #                 telebot.types.InputTextMessageContent(answer[i]),
    #             )
    #             inline_elements.append(element)
            
            
    #         bot.answer_inline_query(
    #             inline_query_id,
    #             inline_elements,
    #             cache_time=0,
    #             is_personal=True
    #         )
    #     except Exception as e:
    #         logger.error(f'User: {from_user_id} Inline request: {expression}  Error processing inline query: {str(e)}')
    # else:
    #     logger.error(f"Failed to send inline query. Status code: {result.status_code}, Response: {result.content}")


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

    # Cloud server:
    # webhook_url = f"https://{config['WEBHOOK_HOST']}:{config['WEBHOOK_PORT']}/{bot_config['TOKEN']}/"
    # bot.remove_webhook()
    # bot.set_webhook(url=webhook_url)

    # Local server:
    server_api_uri = config['SERVER_API_URI']
    server_file_url = config['SERVER_FILE_URL']
    if server_api_uri != '':
        telebot.apihelper.API_URL = server_api_uri
        logger.info(f'Setting API_URL: {server_api_uri} for bot {bot_config["TOKEN"]}')
    if server_file_url != '':
        telebot.apihelper.FILE_URL = server_file_url
        logger.info(f'Setting FILE_URL: {server_file_url} for bot {bot_config["TOKEN"]}')
    webhook_url = f"http://{config['WEBHOOK_HOST']}:{config['WEBHOOK_PORT']}/{bot_config['TOKEN']}/"
    logger.info(f'Setting webhook url: {webhook_url}')
    logger.info(f'Webhook set: {bot.set_webhook(url=webhook_url, max_connections=100)}')

    return bot


@app.post("/{token}/")
async def handle_request(token: str, request: Request):
    if token in bots: 
        bot = bots[token]
        request_body_dict = await request.json()
        # logger.info(f'handle_request: Received request for bot {token}: {request_body_dict}')
        try:
            text = None
            user_id = None
            if 'message' in request_body_dict and 'text' in request_body_dict['message']:
                text = request_body_dict['message']['text']
                # Get user id if available
                if 'from' in request_body_dict['message'] and 'id' in request_body_dict['message']['from']:
                    user_id = request_body_dict['message']['from']['id']
            else:
                logger.error(f'handle_request: Invalid logger extractor: {request_body_dict}')
            bot_name = bot.get_me().username
            logger.info(f'handle_request {bot_name} from {user_id}: {text}')
        except Exception as e:
            logger.error(f'handle_request: Error logging request for bot {token}: {str(e)}')
        try:
            update = telebot.types.Update.de_json(request_body_dict)
            bot.process_new_updates([update])
            logger.info(f'handle_request: Processed request for bot {token}')
            return JSONResponse(content={"status": "ok"})
        except Exception as e:
            logger.error(f'handle_request: Error processing request for bot {token}: {str(e)}')
            return JSONResponse(content={"status": "error"}, status_code=500)
    else:
        logger.error(f'handle_request: Invalid token: {token} Bots: {bots}')
        return JSONResponse(content={"status": "error"}, status_code=403)


async def main():
    global bots
    # Load bot configurations
    with open('bots.json') as bots_file:
        bots_config = json.load(bots_file)

    for bot_key, bot_instance in bots_config.items():
        if int(bot_instance['active']):
            bots[bot_instance['TOKEN']] = await init_bot(bot_instance)
            logger.info(f'Bot {bot_key} initialized with webhook')
        else:
            logger.info(f'Bot {bot_key} is inactive')


@app.on_event("startup")
async def startup_event():
    await main()
