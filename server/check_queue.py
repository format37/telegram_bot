from telebot import TeleBot
import time
import datetime

bot = TeleBot('your_bot_token')

while (1):
    webhook_info = bot.get_webhook_info()
    pending_update_count = webhook_info.pending_update_count
    datetime_prefix = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"{datetime_prefix} Number of pending updates: {pending_update_count}")
    time.sleep(1)
