from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import telebot
import logging
import json

# Initialize FastAPI
app = FastAPI()

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

@app.get("/test")
async def call_test():
    logger.info('Test endpoint called')
    return JSONResponse(content={"status": "ok"})

# Simple text message handler function
def handle_text_message(bot, message):
    logger.info(f'Received message from {message.chat.id}: {message.text}')

# Initialize bot
def init_bot(bot_config):
    bot = telebot.TeleBot(bot_config['TOKEN'])
    
    @bot.message_handler(func=lambda message: True)
    def message_handler(message):
        handle_text_message(bot, message)

    webhook_url = f"https://{bot_config['WEBHOOK_HOST']}:{bot_config['WEBHOOK_PORT']}/{bot_config['TOKEN']}/"
    bot.remove_webhook()
    bot.set_webhook(url=webhook_url)

    return bot

# Load bot configurations
with open('bots.json') as bots_file:
    bots_config = json.load(bots_file)

# Initialize bots and set webhooks
bots = {}
for bot_key, bot_instance in bots_config.items():
    bots[bot_instance['TOKEN']] = init_bot(bot_instance)
    logger.info(f'Bot {bot_key} initialized with webhook')

@app.post("/{token}/")
async def handle_request(token: str, request: Request):
    if token in bots:
        bot = bots[token]
        request_body_dict = await request.json()
        update = telebot.types.Update.de_json(request_body_dict)
        bot.process_new_updates([update])
        return JSONResponse(content={"status": "ok"})
    else:
        logger.error(f'Invalid token: {token}')
        return JSONResponse(content={"status": "error"}, status_code=403)
