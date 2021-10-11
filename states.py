import telebot
from typing import Dict, Callable

def cancel_command(cancel_func: Callable[[telebot.types.Message], None]):
    '''
    Декоратор обрабатывающий команду отмены последней введенной команды в ходе её выполнения
    :param func:
    :return:
    '''
    def cancel(func):
        def wrapper(message : telebot, chatinfo: Dict):
            if telebot.util.is_command(message.text) and telebot.util.extract_command(message.text):
                cancel_func(message)
                return
            return func(message, chatinfo)
        return wrapper
    return cancel