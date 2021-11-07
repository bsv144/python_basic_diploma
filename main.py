from handlers import *
from loader import bot, UserRequest, chat_info, serverHTTP, TOKEN_TELEGRAM
from telebot import types
from flask import request

bot.delete_my_commands()
bot.set_my_commands([
    types.BotCommand("lowprice", "Вывод самых дешёвых отелей"),
    types.BotCommand("highprice", "Вывод самых дорогих отелей"),
    types.BotCommand("bestdeal", "Вывод наиболее подходящих отелей"),
    types.BotCommand("history", "История ввода"),
    types.BotCommand("cancel", "отмена последнего запроса")
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
            /cancel - отмена последнего запроса
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
def cancel_last_command(message: types.Message):
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
    # bot.send_message(chat_id=chat_id, text='История ранее введенных команд')
    bot.send_message(chat_id=chat_id, text='Введите колличество выводимых результатов истории')
    bot.register_next_step_handler(message, state_get_history_top)


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
    from pyngrok import ngrok

    print("Слушаем сообщения от Telegram")
    # bot.infinity_polling()

    # Запускаем ngrok
    http_tunnel = ngrok.connect(5500)
    tunnels = ngrok.get_tunnels()


    @serverHTTP.route('/' + TOKEN_TELEGRAM, methods=['POST'])
    def get_message():
        json_string = request.get_data().decode('utf-8')
        update = types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return "!", 200


    @serverHTTP.route("/")
    def webhook():
        bot.remove_webhook()
        bot.set_webhook(url=tunnels[1].public_url + "/" + TOKEN_TELEGRAM)
        return "!", 200


    bot.remove_webhook()
    bot.set_webhook(url=tunnels[1].public_url + "/" + TOKEN_TELEGRAM)

    serverHTTP.run(host="0.0.0.0", port=5500, debug=False)
    ngrok.kill()
