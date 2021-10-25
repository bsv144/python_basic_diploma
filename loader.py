"""
1 - основной модуль loader.py который погружает все нужное, создает экземпляры
В нем должны подгружаться все нужные константы(токены бота, API)
инициализироваться класс с ботом TeleBot и общий словарь пользователей
"""
import json
import hotelsapi
from telebot import TeleBot

with open('secret.json', 'r') as fconfig:
    secure_config = json.load(fconfig)

TOKEN_TELEGRAM = secure_config['TOKEN_TELEGRAM']
API_KEY = secure_config['API_KEY']

#Максимальное кол-во результатов в ответе
MAX_SEARCH_RESULT = 20
#Максимальное кол-во фотогорафий для одного отеля
MAX_PHOTE_RESULT = 5

hotels = hotelsapi.hotels(API_KEY)
bot = TeleBot(TOKEN_TELEGRAM, parse_mode=None)

class User_request:
    def __init__(self):
        self.Command = None
        self.City = None
        self.Price_min = None
        self.Price_max = None
        self.Distance_min = None
        self.Distance_max = None
        self.Search_result_count = MAX_SEARCH_RESULT
        self.Photo_count = MAX_PHOTE_RESULT
        self.Photo_out = True



