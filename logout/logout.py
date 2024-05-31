import telebot

def log_out_function(bot):
    return bot.log_out()

def main():
    # Ask token from user input
    token = input('Enter your bot token: ')
    bot = telebot.TeleBot(token)
    # telebot.apihelper.API_URL = "http://localhost:8081/bot{0}/{1}"
    # telebot.apihelper.FILE_URL = "http://localhost:8081"
    print(f'API_URL: {telebot.apihelper.API_URL}')
    print(f'FILE_URL: {telebot.apihelper.FILE_URL}')
    print(f'Log out: {log_out_function(bot)}')
    print('Done')    

if __name__ == "__main__":
    main()
