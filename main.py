import hotelsapi
import telebot
import json

with open('secret.json', 'r') as fconfig:
    secure_config = json.load(fconfig)


TOKEN_TELEGRAM = secure_config['TOKEN_TELEGRAM']
API_KEY = secure_config['API_KEY']


#Максимальное кол-во результатов в ответе
MAX_SEARCH_RESULT = 20
#Максимальное кол-во фотогорафий для одного отеля
MAX_PHOTE_RESULT = 20

hotels = hotelsapi.hotels(API_KEY)
bot = telebot.TeleBot(TOKEN_TELEGRAM, parse_mode=None)

@bot.message_handler(commands=['start'])
def send_welcome(message):
	bot.reply_to(message, "Я Бот, Я умею находить отели по базе Hotels.com")

@bot.message_handler(commands=['help'])
def send_help(message):
	bot.reply_to(message, '''
			Бот поиска отелей. 
			Бот поддерживает следующие команды:
			/lowprice - вывод самых дешёвых отелей в городе
			/highiprice - вывод самых дорогих отелей в городе
			/bestdeal - вывод отелей, наиболее подходящих по цене и расположению от центра
			/history - история запросов
	''')

@bot.message_handler(commands=['lowprice'])
def send_lowprice(message):
	bot.reply_to(message,"команда lowprice")

@bot.message_handler(message=lambda m: True)
def not_recognizing_command(message):
	bot.reply_to(message, "Вы ввели неверную команду?")	
	send_help(message)

if __name__ == '__main__':
    print(TOKEN_TELEGRAM)
    print(API_KEY)
    bot.infinity_polling()
    '''
    exit
    destination = hotels.get_destinationid('Санкт-Петербург')
    print(destination) 
    print() 
    with open('test.json', 'w', encoding='utf-8') as f:
        for pNumber in range(1, 3):
            #print(pNumber)
            f.write(str(pNumber))
            resp = hotels.get_hotels(destination[0], pNumber)
            f.write(json.dumps(resp, indent=5))
            #print()
    '''