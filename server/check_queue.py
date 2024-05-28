from telegram.ext import Updater

# Replace with your bot token
BOT_TOKEN = 'YOUR_BOT_TOKEN'

updater = Updater(token=BOT_TOKEN, use_context=True)
dispatcher = updater.dispatcher

def get_pending_updates():
    # Get the last update ID
    last_update_id = updater.dispatcher.bot.get_updates()[-1].update_id if updater.dispatcher.bot.get_updates() else 0
    
    # Get the number of pending updates
    pending_updates = updater.dispatcher.bot.get_updates(offset=last_update_id + 1, timeout=10)
    num_pending = len(pending_updates)
    
    print(f"Number of pending updates: {num_pending}")
    
    # If there are pending updates, print the first one
    if num_pending > 0:
        print(f"First pending update: {pending_updates[0]}")

get_pending_updates()
