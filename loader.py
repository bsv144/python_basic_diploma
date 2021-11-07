import json
import hotelsapi
from telebot import TeleBot, logger
from peewee import PeeweeException
from peewee import *
import datetime
import logging
from flask import Flask


# Логирование данных
logging.basicConfig(filename='telegramBot.log',
                    format='%(asctime)s %(message)s',
                    #ncoding='utf-8',
                    level=logging.WARNING)


# Получить параметры с файла конфигурации
with open('secret.json', 'r') as fConfig:
    secure_config = json.load(fConfig)

TOKEN_TELEGRAM = secure_config['TOKEN_TELEGRAM']
API_KEY = secure_config['API_KEY']

# Максимальное кол-во результатов в ответе
MAX_SEARCH_RESULT = 20
# Максимальное кол-во фотогорафий для одного отеля
MAX_PHOTO_RESULT = 3

hotels = hotelsapi.Hotels(API_KEY)
bot = TeleBot(TOKEN_TELEGRAM, parse_mode=None)
bot.MAX_SEARCH_RESULT = MAX_SEARCH_RESULT
bot.MAX_PHOTO_RESULT = MAX_PHOTO_RESULT
logger.setLevel(logging.WARNING)

# Объект HTTP сервера
serverHTTP = Flask(__name__)

# Инициализаяци БД для хранения истории
db = SqliteDatabase('telegram_bot.db')


# Описание модели БД
class BaseModel(Model):
    class Meta:
        database = db


class History(BaseModel):
    userId = IntegerField(index=True)
    dt = DateTimeField(default=datetime.datetime.now)
    userRequest = BlobField()
    requestResult = BlobField()


try:
    db.connect()
    db.create_tables([History])
except PeeweeException as err:
    logging.warning("Ошибка подключения к базе данных:", err)

# Словарь для хранения текущей информации по диалогам
chat_info = dict()


# Объект для хранения информации по текущему диалогу
class UserRequest:
    def __init__(self):
        self.Command = None
        self.City = None
        self.Price_min = None
        self.Price_max = None
        self.Distance_min = None
        self.Distance_max = None
        self.Search_result_count = MAX_SEARCH_RESULT
        self.Photo_count = MAX_PHOTO_RESULT
        self.Photo_out = True

    def __str__(self):
        out = list()
        if self.Command:
            out.append(f'Тип поиска: {self.Command}')
        if self.City:
            out.append(f'Город: {self.City}')
        if self.Price_min:
            out.append(f'Цена min: {self.Price_min}')
        if self.Price_max:
            out.append(f'Цена max: {self.Price_max}')
        if self.Distance_min:
            out.append(f'Расстояние min: {self.Distance_min}')
        if self.Distance_max:
            out.append(f'Расстояние min: {self.Distance_max}')
        return '\n'.join(out)

