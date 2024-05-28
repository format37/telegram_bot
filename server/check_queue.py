from telebot import TeleBot

bot = TeleBot('your_bot_token')

webhook_info = bot.get_webhook_info()
pending_update_count = webhook_info.pending_update_count

print(f"Number of pending updates: {pending_update_count}")
