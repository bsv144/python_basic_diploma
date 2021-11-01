from handlers import *
from loader import bot, UserRequest, chat_info
from telebot import types

bot.delete_my_commands()
bot.set_my_commands([
    types.BotCommand("lowprice", "Вывод самых дешёвых отелей"),
    types.BotCommand("highprice", "Вывод самых дорогих отелей"),
    types.BotCommand("bestdeal", "Вывод наиболее подходящих отелей"),
    types.BotCommand("history", "История ввода"),
    # types.BotCommand("cancel", "отмена ввод последней команды")
])


@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Я Бот, Я умею находить отели по базе Hotels.com")


@bot.message_handler(commands=['help'])
def send_help(message):
    bot.reply_to(message, """
            Бот поиска отелей. 
            Бот поддерживает следующие команды:
            /lowprice - вывод самых дешёвых отелей в городе
            /highprice - вывод самых дорогих отелей в городе
            /bestdeal - вывод отелей, наиболее подходящих по цене и расположению от центра
            /history - история запросов
    """)


@bot.message_handler(commands=['lowprice'])
def command_lowprice(message: types.Message) -> None:
    """
    Начальное состояние команды lowprice
    :param message:
    :return:
    """
    chat_id = message.chat.id
    chat_info.setdefault(chat_id, UserRequest()).Command = 'lowprice'
    bot.send_message(chat_id=chat_id, text='Введите город поиска')
    # Для FSM регистрируем callback функцию для следующего шага
    bot.register_next_step_handler(message, state_get_city, chatinfo=chat_info)


@bot.message_handler(commands=['highprice'])
def command_highiprice(message: types.Message) -> None:
    """
    Начальное состояние команды highprice
    :param message:
    :return:
    """
    chat_id = message.chat.id
    chat_info.setdefault(chat_id, UserRequest()).Command = 'highprice'
    bot.send_message(chat_id=chat_id, text='Введите город поиска')
    # Для FSM регистрируем callback функцию для следующего шага
    bot.register_next_step_handler(message, state_get_city, chatinfo=chat_info)


@bot.message_handler(commands=['bestdeal'])
def command_highiprice(message: types.Message) -> None:
    """
    Начальное состояние команды bestdeal
    :param message:
    :return:
    """
    chat_id = message.chat.id

    chat_info.setdefault(chat_id, UserRequest()).Command = 'bestdeal'
    bot.send_message(chat_id=chat_id, text='Введите город поиска')
    # Для FSM регистрируем callback функцию для следующего шага
    bot.register_next_step_handler(message, state_get_city, chatinfo=chat_info)


@bot.message_handler(commands=['cancel'])
def concel_last_command(message: types.Message):
    chat_id = message.chat.id
    if chat_id in chat_info:
        del chat_info[chat_id]
        bot.send_message(chat_id=chat_id, text='Последняя команда отменена.')


@bot.message_handler(commands=['history'])
def command_history(message: types.Message):
    """
    Коман6да вывода истории введенных ранее команд
    :param message:
    :return:
    """
    chat_id = message.chat.id
    bot.send_message(chat_id=chat_id, text='История ранее введенных команд')


@bot.message_handler(func=lambda m: True)
def not_recognizing_command(message: types.Message):
    """
    Обработка неизвестных команд и текста
    :param message:
    :return:
    """
    bot.reply_to(message, "Вы ввели неверную команду?")
    send_help(message)


if __name__ == '__main__':
    print("Слушаем сообщения от Telegram")
    bot.infinity_polling()
