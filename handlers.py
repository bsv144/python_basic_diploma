import logging
from json import JSONDecodeError
from typing import Dict, Callable
from telebot import types, util
from loader import bot, hotels, History
import re
import pickle


def cancel_command(func):
    """
    Декоратор отмена последней введенной команды в ходе её выполнения
    :param func:
    :return:
    """
    def wrapper(message: types.Message, chatinfo: Dict):
        if util.is_command(message.text) and util.extract_command(message.text).lower() == 'cancel':
            chat_id = message.chat.id
            if chat_id in chatinfo:
                del chatinfo[chat_id]
                bot.send_message(chat_id=chat_id, text='Последняя команда отменена.')
            return
        return func(message, chatinfo)
    return wrapper


def run_api(chat_id: int, chatinfo: Dict) -> None:
    """
    Вспомогательная функция для запуска api функций hottels
    :param chat_id:
    :param chatinfo:
    :return:
    """
    user_request = chatinfo[chat_id]
    request_result = list()
    out = None
    try:
        if user_request.Command == 'lowprice':
            bot.send_message(chat_id=chat_id,
                             text='Выполняется подборка дешёвых отелей по введенным вами параметрам....')
            out = hotels.get_hotels_price_sort(_city=user_request.City, _outCount=user_request.Search_result_count)
        elif user_request.Command == 'highprice':
            bot.send_message(chat_id=chat_id,
                             text='Выполняется подборка наиболее дорогих отелей по введенным вами параметрам....')
            out = hotels.get_hotels_price_sort(_city=user_request.City, _outCount=user_request.Search_result_count,
                                               _sort='PRICE_HIGHEST_FIRST')
        elif user_request.Command == 'bestdeal':
            bot.send_message(chat_id=chat_id,
                             text='Выполняется подборка наиболее дорогих отелей по введенным вами параметрам....')
            out = hotels.get_hotels_bestdeal(_city=user_request.City, _outCount=user_request.Search_result_count,
                                             _priceMin=int(user_request.Price_min),
                                             _priceMax=int(user_request.Price_max),
                                             _distanceMin=float(user_request.Distance_min),
                                             _distanceMax=float(user_request.Distance_max))
    except JSONDecodeError:
        bot.send_message(chat_id=chat_id,
                         text="Упс. Произошла ошибка. Попробуйте повторить запрос чуть позже.")
        return
    logging.warning(f'{chat_id} - {user_request} - {out}')
    if out is None or len(out) == 0:
        bot.send_message(chat_id=chat_id,
                         text="По вашему запросу отсутствуют результаты поиска.")
    else:
        for hotel in out:
            # Расстояние до центра города
            landmark = hotel['landmarks'][0]['distance']
            price = f"{hotel['ratePlan']['price']['current']} {hotel['ratePlan']['price']['info']} " \
                    f"{hotel['ratePlan']['price']['summary']}"
            address = hotel['address']['streetAddress']
            name = hotel['name']
            bot.send_message(chat_id=chat_id,
                             text=f"Название: {name}\nАдрес: {address}\nДо центра: {landmark}\nЦена: {price}")
            request_result.append(
                dict(_hotel=f"Название: {name}\nАдрес: {address}\nДо центра: {landmark}\nЦена: {price}",
                     _photo=list()))
            if user_request.Photo_out:
                photo = hotels.get_hotels_photos(_hotelId=hotel['id'])
                if len(photo) >= user_request.Photo_count:
                    for photo_index in range(user_request.Photo_count):
                        image_url_template = photo[photo_index]['baseUrl']
                        image_url = image_url_template.replace('{size}', 'z')
                        bot.send_photo(chat_id=chat_id, photo=image_url)
                        request_result[-1]['_photo'].append(image_url)

    history = History(userId=chat_id,
                      userRequest=pickle.dumps(user_request),
                      requestResult=pickle.dumps(request_result))
    history.save()


@cancel_command
def state_get_city(message: types.Message, chatinfo: Dict) -> None:
    """
    Коллбэк функция для FSM
    Получить город
    :param chatinfo:
    :param message: types.Message
    :return: None
    """
    chat_id = message.chat.id
    pat_city = re.compile(r'^\w+-?\s*\w*$')
    user_request = chatinfo[chat_id]
    city = pat_city.search(message.text)
    if city:
        user_request.City = city.group(0)
        if user_request.Command in ['lowprice', 'highprice', 'bestdeal']:
            bot.register_next_step_handler(message=message, callback=state_get_result_count, chatinfo=chatinfo)
            bot.send_message(chat_id=chat_id,
                             text=f'Введите кол-во выводимых результатов. '
                                  f'(Макчимальное колличество: {bot.MAX_SEARCH_RESULT})')
    else:
        bot.send_message(chat_id=chat_id, text='Введите город поиска')
        bot.register_next_step_handler(message=message, callback=state_get_city, chat_info=chatinfo)


@cancel_command
def state_get_result_count(message: types.Message, chatinfo: Dict) -> None:
    """
    Коллбэк функция для FSM
    Получить кол-во выводимых результатов
    :param chatinfo:
    :param message: bot.types.Message
    :return: None
    """
    chat_id = message.chat.id
    user_request = chatinfo[chat_id]
    if message.text.isdigit():
        result_count = int(message.text) if int(message.text) < bot.MAX_SEARCH_RESULT else bot.MAX_SEARCH_RESULT
    else:
        result_count = bot.MAX_SEARCH_RESULT
        bot.send_message(chat_id=chat_id,
                         text=f'Кол-во выводимых результатов установлено {bot.MAX_SEARCH_RESULT}')
    user_request.Search_result_count = result_count
    if user_request.Command in ['lowprice', 'highprice', 'bestdeal']:
        bot.register_next_step_handler(message=message, callback=state_get_photo_in, chatinfo=chatinfo)
        markup = types.ReplyKeyboardMarkup(row_width=2, one_time_keyboard=True)
        item_btn_yes = types.KeyboardButton('Да')
        item_btn_no = types.KeyboardButton('Нет')
        markup.add(item_btn_yes, item_btn_no)
        bot.send_message(chat_id=chat_id, text='Вводить фотогафии (да/нет) ?', reply_markup=markup)


@cancel_command
def state_get_photo_in(message: types.Message, chatinfo: Dict) -> None:
    """
    Коллбэк функция для FSM
    Выводить в результатах запроса фото или нет
    :param chatinfo:
    :param message: telebot.types.Message
    :return: None
    """
    chat_id = message.chat.id
    user_request = chatinfo[chat_id]
    if message.text.lower() == 'да':
        print('Да')
        user_request.Photo_out = True
        bot.register_next_step_handler(message=message, callback=state_get_photo_count, chatinfo=chatinfo)
        bot.send_message(chat_id=chat_id, text=f'Кол-во выводимых фотографий в результатах поиска '
                                               f'(Макчимальное колличество: {bot.MAX_PHOTO_RESULT})')
    else:
        user_request.Photo_out = False
        if user_request.Command in ['bestdeal']:
            bot.send_message(chat_id=chat_id, text=f'Введите диапазон цен через пробел (MIN MAX)')
            bot.register_next_step_handler(message=message, callback=state_get_price_max_min, chatinfo=chatinfo)
        else:
            run_api(chat_id, chatinfo)


@cancel_command
def state_get_photo_count(message: types.Message, chatinfo: Dict) -> None:
    """
    Коллбэк функция для FSM
    Кол-во выводимых фотографий
    :param chatinfo:
    :param message:
    :return:
    """
    chat_id = message.chat.id
    user_request = chatinfo[chat_id]
    # Если введено число то выводим кол-во фотографий но не больше чем заданное максимальное кол-во
    # если ввели что-то непонятное, то берём заданное максимальное кол-во выводимых фотографий
    if message.text.isdigit():
        photo_count = int(message.text) if int(message.text) < bot.MAX_PHOTO_RESULT else bot.MAX_PHOTO_RESULT
    else:
        photo_count = bot.MAX_PHOTO_RESULT
        bot.send_message(chat_id=chat_id, text=f'Кол-во выводимых фотографий {bot.MAX_PHOTO_RESULT}')
    user_request.Photo_count = photo_count
    if user_request.Command in ['bestdeal']:
        bot.send_message(chat_id=chat_id, text=f'Введите диапазон цен через пробел (MIN MAX)')
        bot.register_next_step_handler(message=message, callback=state_get_price_max_min, chatinfo=chatinfo)
    else:
        run_api(chat_id, chatinfo)


@cancel_command
def state_get_price_max_min(message: types.Message, chatinfo: Dict) -> None:
    """
     Коллбэк функция для FSM
     Диапазон цен
     :param chatinfo:
     :param message:
     :return:
     """
    chat_id = message.chat.id
    result = message.text.split()
    try:
        result = list(map(int, result))
    except ValueError:
        bot.register_next_step_handler(message=message, callback=state_get_price_max_min, chatinfo=chatinfo)
        bot.send_message(chat_id=chat_id, text=f'Введите диапазон цен через пробел (MIN MAX)')
    else:
        if len(result) == 2:
            # Проверяем, что введены два числа через пробел
            user_request = chatinfo[chat_id]
            if result[0] > result[1]:
                user_request.Price_min = result[1]
                user_request.Price_max = result[0]
            else:
                user_request.Price_min = result[0]
                user_request.Price_max = result[1]
            bot.register_next_step_handler(message=message, callback=state_get_distance_max_min, chatinfo=chatinfo)
            bot.send_message(chat_id=chat_id, text=f'Введите через пробел диапазон расстояния от центра (MIN MAX)')
        else:
            bot.register_next_step_handler(message=message, callback=state_get_price_max_min, chatinfo=chatinfo)
            bot.send_message(chat_id=chat_id, text=f'Введите диапазон цен через пробел (MIN MAX)')


@cancel_command
def state_get_distance_max_min(message: types.Message, chatinfo: Dict) -> None:
    """
     Коллбэк функция для FSM Диапазон расстояний
     :param chatinfo:
     :param message:
     :return:
     """
    chat_id = message.chat.id
    result = message.text.split()
    try:
        result = list(map(float, result))
    except ValueError:
        bot.register_next_step_handler(message=message, callback=state_get_distance_max_min, chatinfo=chatinfo)
        bot.send_message(chat_id=chat_id, text=f'Введите через пробел диапазон расстояния от центра (MIN MAX)')
    else:
        if len(result) == 2:
            user_request = chatinfo[chat_id]
            if result[0] > result[1]:
                user_request.Distance_min = result[1]
                user_request.Distance_max = result[0]
            else:
                user_request.Distance_min = result[0]
                user_request.Distance_max = result[1]
            run_api(chat_id, chatinfo)
        else:
            bot.register_next_step_handler(message=message, callback=state_get_distance_max_min, chatinfo=chatinfo)
            bot.send_message(chat_id=chat_id, text=f'Введите через пробел диапазон расстояния от центра (MIN MAX)')


def state_get_history_top(message: types.Message) -> None:
    """
    Коллбэк функция для FSM колличество выводимых результатов истории
    :param message:
    :return:
    """
    chat_id = message.chat.id
    if not message.text.isdigit():
        bot.send_message(chat_id=chat_id, text=f'Кол-во выводимых результатов установлено: 3')
        result_count = 3
    else:
        result_count = int(message.text)
    query = History.select().where(History.userId == chat_id).order_by(History.dt.desc()).limit(result_count)
    for record in query:
        ur = pickle.loads(record.userRequest)
        rr = pickle.loads(record.requestResult)
        bot.send_message(chat_id=chat_id, text=f'Запись от {record.dt}')
        bot.send_message(chat_id=chat_id, text=ur)
        for hotel in rr:
            bot.send_message(chat_id=chat_id, text=hotel['_hotel'])
            for image_url in hotel['_photo']:
                bot.send_photo(chat_id=chat_id, photo=image_url)
