import telebot

TOKEN = '2033525413:AAFg_0tFWtKrlW4MufYjDOCqaAbiiT_bNlE'

bot = telebot.TeleBor(TOKEN, parse_mode=None)

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
	pass


@bot.message_handler(message=lambda m: True)
def not_recognizing_command(message):
	bot.reply_to(message, "Вы ввели неверную команду?")	
	send_help(message)