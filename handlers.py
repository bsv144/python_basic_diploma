from typing import Dict, Callable
from telebot import types, TeleBot
import re
"""
2 - дочерний handlers.py в нем объявляются все кастомные хендлеры - получение города, количества отлей и прочее
"""


def cancel_command(cancel_func: Callable[[types.Message], None]):
    """
    Декоратор обрабатывающий команду отмены последней введенной команды в ходе её выполнения
    :param func:
    :return:
    """
    def cancel(func):
        def wrapper(message : telebot, chatinfo: Dict):
            if telebot.util.is_command(message.text) and telebot.util.extract_command(message.text):
                cancel_func(message)
                return
            return func(message, chatinfo)
        return wrapper
    return cancel

def run_api(chat_id: int, chatinfo: Dict) -> None:
    """
    Вспомогательная функция для запуска api функций hottels
    :param chat_id:
    :param chatinfo:
    :return:
    """
    if chatinfo[chat_id]['command'] == 'lowprice':
        bot.send_message(chat_id=chat_id, text='Выполняется подборка дешёвых отелей по введенным вами параметрам....')
        # TODO hotels_get_lowprice(chatinfo)
    elif chatinfo[chat_id]['command'] == 'highiprice':
        bot.send_message(chat_id=chat_id, text='Выполняется подборка наиболее дорогих отелей по введенным вами параметрам....')
        # TODO hotels_get_highprice(chatinfo)
    elif chatinfo[chat_id]['command'] == 'bestdeal':
        bot.send_message(chat_id=chat_id, text='Выполняется подборка наиболее дорогих отелей по введенным вами параметрам....')
        # TODO hotels_get_bestdeal(chatinfo)


#@cancel_command(concel_last_command)
def state_get_city(botobj: TeleBot, chatinfo: Dict) -> None:
    """
    Коллбэк функция для FSM
    Получить город
    :param message: telebot.types.Message
    :return: None
    """
    message = botobj
    chat_id = message.chat.id
    pat_city = re.compile(r'^\w+-?\s*\w*$')
    city = pat_city.search(message.text)
    if city:
        chatinfo[chat_id]['city'] = city.group(0)
        if chatinfo[chat_id]['command'] in ['lowprice', 'highiprice']:
            botobj.register_next_step_handler(message=message, callback=state_get_result_count, chatinfo=chatinfo)
            botobj.send_message(chat_id=chat_id, text=f'Введите кол-во выводимых результатов. (Макчимальное колличество: {MAX_SEARCH_RESULT})')
    else:
        botobj.send_message(chat_id=chat_id, text='Введите город поиска')
        botobj.register_next_step_handler(message=message, callback=state_get_city, chat_info=chatinfo)

#@cancel_command(concel_last_command)
def state_get_result_count(message : types.Message, chatinfo: Dict) -> None:
    """
    Коллбэк функция для FSM
    Получить кол-во выводимых результатов
    :param message: telebot.types.Message
    :return: None
    """
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

#@cancel_command(concel_last_command)
def state_get_photo_in(message : types.Message, chatinfo: Dict) -> None:
    """
    Коллбэк функция для FSM
    Выводить в результатах запроса фото или нет
    :param message: telebot.types.Message
    :return: None
    """
    chat_id = message.chat.id
    if message.text.lower() == 'да':
        chatinfo[chat_id]['photo_in'] = 1
        bot.register_next_step_handler(message=message, callback=state_get_photo_count, chatinfo=chat_info)
        bot.send_message(chat_id=chat_id, text='Кол-во выводимых фотографий в результатах поиска')
    else:
        chatinfo[chat_id]['photo_in'] = 0
        if chatinfo[chat_id]['command'] in ['bestdeal']:
            bot.register_next_step_handler(message=message, callback=state_get_price_max_min, chatinfo=chat_info)
        else:
            run_api(chat_id, chatinfo)

#@cancel_command(concel_last_command)
def state_get_photo_count(message : types.Message, chatinfo: Dict) -> None:
    """
    Коллбэк функция для FSM
    Кол-во выводимых фотографий
    :param message:
    :return:
    """
    chat_id = message.chat.id
    # Если введено число то выводим кол-во фотографий но не больше чем заданное максимальное кол-во
    # если ввели что-то непонятное, то берём заданное максимальное кол-во выводимых фотографий
    if message.text.isdigit():
        photo_count = int(message.text) if int(message.text) <  MAX_PHOTE_RESULT else MAX_PHOTE_RESULT
    else:
        photo_count = MAX_PHOTE_RESULT
        bot.send_message(chat_id=chat_id, text=f'Кол-во выводимых фотографий {MAX_PHOTE_RESULT}')
    chatinfo[chat_id]['photo_count'] = photo_count
    if chatinfo[chat_id]['command'] in ['bestdeal']:
        bot.register_next_step_handler(message=message, callback=state_get_price_max_min, chatinfo=chat_info)
    else:
        run_api(chat_id, chatinfo)

#@states.cancel_command(concel_last_command)
def state_get_price_max_min(message : types.Message, chatinfo: Dict) -> None:
    """
     Коллбэк функция для FSM
     Диапазон цен
     :param message:
     :return:
     """
    chat_id = message.chat.id
    tmp_range = re.compile(r'(\d+)\s+(\d+)')
    result = tmp_range.findall(message)
    min = result[0]
    max = result[1]
    # Проверяем, что введены два числа через пробел
    if max > min :
        chatinfo[chat_id]['price_min'] = min
        chatinfo[chat_id]['price_max'] = max
        bot.register_next_step_handler(message=message, callback=state_get_distance_max_min, chatinfo=chat_info)
        bot.send_message(chat_id=chat_id, text=f'Введите через пробел диапазон расстояния от центра (MAX MIN)')
    else:
        bot.register_next_step_handler(message=message, callback=state_get_price_max_min, chatinfo=chat_info)
        bot.send_message(chat_id=chat_id, text=f'Введите диапазон цен через пробел (MAX MIN)')

#@states.cancel_command(concel_last_command)
def state_get_distance_max_min(message : types.Message, chatinfo: Dict) -> None:
    """
     Коллбэк функция для FSM
     Диапазон расстояний
     :param message:
     :return:
     """
    chat_id = message.chat.id
    tmp_range = re.compile(r'(\d+)\s+(\d+)')
    result = tmp_range.findall(message)
    min = result[0]
    max = result[1]
    # Проверяем, что введены два числа через пробел
    if max > min :
        chatinfo[chat_id]['distance_min'] = min
        chatinfo[chat_id]['distance_max'] = max
        run_api(chat_id, chatinfo)
    else:
        bot.register_next_step_handler(message=message, callback=state_get_distance_max_min, chatinfo=chat_info)
        bot.send_message(chat_id=chat_id, text=f'Введите через пробел диапазон расстояния от центра (MAX MIN)')
