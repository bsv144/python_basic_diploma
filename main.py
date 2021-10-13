import hotelsapi
import telebot
import json
import re
from typing import Dict
import states

with open('secret.json', 'r') as fconfig:
    secure_config = json.load(fconfig)


TOKEN_TELEGRAM = secure_config['TOKEN_TELEGRAM']
API_KEY = secure_config['API_KEY']


#Максимальное кол-во результатов в ответе
MAX_SEARCH_RESULT = 20
#Максимальное кол-во фотогорафий для одного отеля
MAX_PHOTE_RESULT = 5

hotels = hotelsapi.hotels(API_KEY)
bot = telebot.TeleBot(TOKEN_TELEGRAM, parse_mode=None)

bot.set_my_commands([
    telebot.types.BotCommand("lowprice", "Вывод самых дешёвых отелей"),
    telebot.types.BotCommand("highprice", "Вывод самых дорогих отелей"),
    telebot.types.BotCommand("bestdeal", "Вывод наиболее подходящих отелей"),
    telebot.types.BotCommand("history", "История ввода"),
    telebot.types.BotCommand("cancel", "отмена ввод последней команды")
])


chat_info = dict()

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
			/cancel - отмена ввод последней команды
	''')

@bot.message_handler(commands=['lowprice'])
def command_lowprice(message : telebot.types.Message) -> None:
    '''
    Начальное состояние команды lowprice
    :param message:
    :return:
    '''
    chat_id = message.chat.id
    global chat_info
    chat_info[chat_id] = {'command' : 'lowprice',
                          'city' : None,
                          'results_count' : None,
                          'photo_in' : None,
                          'photo_count' : None}
    bot.send_message(chat_id=chat_id ,text='Введите город поиска')
    # Для FSM регистрируем callback функцию для следующего шага
    bot.register_next_step_handler(message, state_get_city, chatinfo=chat_info)

@bot.message_handler(commands=['highiprice'])
def command_highiprice(message : telebot.types.Message) -> None:
    '''
    Начальное состояние команды highiprice
    :param message:
    :return:
    '''
    chat_id = message.chat.id
    global chat_info
    chat_info[chat_id] = {'command' : 'highiprice',
                          'city' : None,
                          'results_count' : None,
                          'photo_in' : None,
                          'photo_count' : None}
    bot.send_message(chat_id=chat_id ,text='Введите город поиска')
    # Для FSM регистрируем callback функцию для следующего шага
    bot.register_next_step_handler(message, state_get_city, chatinfo=chat_info)


@bot.message_handler(commands=['bestdeal'])
def command_highiprice(message : telebot.types.Message) -> None:
    '''
    Начальное состояние команды bestdeal
    :param message:
    :return:
    '''
    chat_id = message.chat.id
    global chat_info
    chat_info[chat_id] = {'command' : 'bestdeal',
                          'city' : None,
                          'results_count' : None,
                          'photo_in' : None,
                          'photo_count' : None}
    bot.send_message(chat_id=chat_id ,text='Введите город поиска')
    # Для FSM регистрируем callback функцию для следующего шага
    bot.register_next_step_handler(message, state_get_city, chatinfo=chat_info)


@bot.message_handler(commands=['cancel'])
def concel_last_command(message):
    chat_id = message.chat.id
    global chat_info
    if chat_id in chat_info:
        del chat_info[chat_id]
        bot.send_message(chat_id=chat_id ,text='Последняя команда отменена.')


@bot.message_handler(commands=['history'])
def command_history(message):
    '''
    Коман6да вывода истории введенных ранее команд
    :param message:
    :return:
    '''
    chat_id = message.chat.id
    bot.send_message(chat_id=chat_id ,text='История ранее введенных команд')



@bot.message_handler(message=lambda m: True)
def not_recognizing_command(message):
    '''
    Обработка неизвестных команд и текста
    :param message:
    :return:
    '''
    bot.reply_to(message, "Вы ввели неверную команду?")
    send_help(message)

"""
def cancel_command(func):
    '''
    Декоратор обрабатывающий команду отмены последней введенной команды в ходе её выполнения
    :param func:
    :return:
    '''
    def wrapper(message : telebot, chatinfo: Dict):
        if telebot.util.is_command(message.text) and telebot.util.extract_command(message.text):
            concel_last_command(message)
            return
        return func(message, chatinfo)
    return wrapper
"""

def run_api(chat_id: int, chatinfo: Dict) -> None:
    '''
    Вспомогательная функция для запуска api hottels
    :param chat_id:
    :param chatinfo:
    :return:
    '''
    if chatinfo[chat_id]['command'] == 'lowprice':
        bot.send_message(chat_id=chat_id, text='Выполняется подборка дешёвых отелей по введенным вами параметрам....')
        # TODO hotels_get_lowprice(chatinfo)
    elif chatinfo[chat_id]['command'] == 'highiprice':
        bot.send_message(chat_id=chat_id, text='Выполняется подборка наиболее дорогих отелей по введенным вами параметрам....')
        # TODO hotels_get_highprice(chatinfo)


@states.cancel_command(concel_last_command)
def state_get_city(message : telebot.types.Message, chatinfo: Dict) -> None:
    '''
    Коллбэк функция для FSM
    Получить город
    :param message: telebot.types.Message
    :return: None
    '''
    chat_id = message.chat.id
    pat_city = re.compile(r'^\w+-?\s*\w*$')
    city = pat_city.search(message.text)
    if city:
        chatinfo[chat_id]['city'] = city.group(0)
        if chatinfo[chat_id]['command'] in ['lowprice', 'highiprice']:
            bot.register_next_step_handler(message=message, callback=state_get_result_count, chatinfo=chat_info)
            bot.send_message(chat_id=chat_id, text=f'Введите кол-во выводимых результатов. (Макчимальное колличество: {MAX_SEARCH_RESULT})')
    else:
        bot.send_message(chat_id=chat_id, text='Введите город поиска')
        bot.register_next_step_handler(message=message, callback=state_get_city, chat_info=chat_info)

@states.cancel_command(concel_last_command)
def state_get_result_count(message : telebot.types.Message, chatinfo: Dict) -> None:
    '''
    Коллбэк функция для FSM
    Получить кол-во выводимых результатов
    :param message: telebot.types.Message
    :return: None
    '''
    chat_id = message.chat.id
    if message.text.isdigit():
        result_count = int(message.text) if int(message.text) <  MAX_SEARCH_RESULT else MAX_SEARCH_RESULT
    else:
        result_count = MAX_SEARCH_RESULT
        bot.send_message(chat_id=chat_id, text=f'Кол-во выводимых результатов установлено {MAX_SEARCH_RESULT}')
    chatinfo[chat_id]['results_count'] = result_count
    if chatinfo[chat_id]['command'] in ['lowprice', 'highiprice', 'bestdeal']:
        bot.register_next_step_handler(message=message, callback=state_get_photo_in, chatinfo=chat_info)
        markup = telebot.types.ReplyKeyboardMarkup(row_width=2, one_time_keyboard=True)
        item_btn_yes = telebot.types.KeyboardButton('Да')
        item_btn_no = telebot.types.KeyboardButton('Нет')
        markup.add(item_btn_yes, item_btn_no)
        bot.send_message(chat_id=chat_id, text='Вводить фотогафии (да/нет) ?', reply_markup=markup)

@states.cancel_command(concel_last_command)
def state_get_photo_in(message : telebot.types.Message, chatinfo: Dict) -> None:
    '''
    Коллбэк функция для FSM
    Выводить в результатах запроса фото или нет
    :param message: telebot.types.Message
    :return: None
    '''
    chat_id = message.chat.id
    if message.text.lower() == 'да':
        chatinfo[chat_id]['photo_in'] = 1
        bot.register_next_step_handler(message=message, callback=state_get_photo_count, chatinfo=chat_info)
        bot.send_message(chat_id=chat_id, text='Кол-во выводимых фотографий в результатах поиска')
    else:
        run_api(chat_id, chatinfo)



@states.cancel_command(concel_last_command)
def state_get_photo_count(message : telebot.types.Message, chatinfo: Dict) -> None:
    '''
    Коллбэк функция для FSM
    Кол-во выводимых фотографий
    :param message:
    :return:
    '''
    chat_id = message.chat.id
    if message.text.isdigit():
        photo_count = int(message.text) if int(message.text) <  MAX_PHOTE_RESULT else MAX_PHOTE_RESULT
    else:
        photo_count = MAX_PHOTE_RESULT
        bot.send_message(chat_id=chat_id, text=f'Кол-во выводимых фотографий {MAX_PHOTE_RESULT}')
    chatinfo[chat_id]['photo_count'] = photo_count
    if chatinfo[chat_id]['command'] in ['lowprice', 'highiprice']:
        bot.register_next_step_handler(message=message, callback=state_get_photo_in, chatinfo=chat_info)
        bot.send_message(chat_id=chat_id, text='Вводить фотогафии (да/нет) ?')
    #TODO

# TODO диапазон цен

# TODO диапазон расстояния от центра

if __name__ == '__main__':
    print("Слушаем сообщения от Telegram")
    bot.infinity_polling()