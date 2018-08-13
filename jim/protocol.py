"""
Описаны функции перевода сообщений из байты и словарь и обратно
Описаны классы работы с Джим протоколом.
"""


import json
import time
from .config import *
from .errors import RequiredKeyError, ResponseCodeError, ResponseCodeLenError


def bytes_to_dict(byte_msg):
    """
    Преобразовывает байтовую строку в сообщение
    :param byte_msg: байтовая строка
    :return: раскодированный словарь
    """
    # проверка чтоб входящее сообщение было байтами
    if isinstance(byte_msg, bytes):
        jim_msg = byte_msg.decode(ENCODING)
        message = json.loads(jim_msg)
        # проверяем чтоб сообщение после преобразований было словарем
        if isinstance(message, dict):
            return message
        else:
            raise TypeError
    else:
        raise TypeError


def dict_to_bytes(message):
    """
    преобразовывает сообщение в байты
    принимает на вход словарь, преобразовывает в json
    возвращает байтовую строку
    """
    # проверяем чтоб введенное сообщение было словарем
    if isinstance(message, dict):
        jmessage = json.dumps(message)
        byte_msg = jmessage.encode(ENCODING)
        return byte_msg
    else:
        raise TypeError


def send_msg(sock, msg):
    """
    Отправка сообщения в байтах
    :param sock: сокет
    :param msg: сообщение для отправки(словарь)
    :return: Ничего
    """
    byte_presence = dict_to_bytes(msg)
    sock.send(byte_presence)


def get_msg(sock):
    """
    Принимаем сообщение в байтах и декодируем
    :param sock: сокет
    :param msg: принятое сообщение
    :return: None
    """
    byte_response = sock.recv(1024)
    response = bytes_to_dict(byte_response)
    return response


class BaseJimMessage:
    """
    Базовое Джим сообщение
    """
    # Принимает словарь
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    # При переводе в байты будет такое поведение
    def __bytes__(self):
        message_json = json.dumps(self.__dict__)
        message_bytes = message_json.encode(encoding='utf-8')
        return message_bytes

    # перевод из джим сообщения в байты
    @classmethod
    def create_from_bytes(cls, message_bytes):
        message_json = message_bytes.decode(encoding='utf-8')
        message_dict = json.loads(message_json)
        return cls(**message_dict)

    # при вызове как строки будет переводить словарь в строку и выводить
    def __str__(self):
        return str(self.__dict__)


class JimFunctions(BaseJimMessage):
    """
    Класс обработчик всех действий Джим
    """
    def __init__(self, **kwargs):
        if ACTION not in kwargs:
            raise RequiredKeyError(ACTION)
        if TIME not in kwargs:
            raise RequiredKeyError(TIME)
        super().__init__(**kwargs)



    @staticmethod
    def conversion(message):
        """
        метод создающий действие
        :return: обьект, Action или presence
        """
        if ACTION in message:
            action = message[ACTION]
            if action in ACTIONS:
                if action == PRESENCE:
                    return JimAction(message).create_presence
                elif action == DEL_CONTACT:
                    return JimAction.delete_contact()
                elif action == ADD_CONTACT:
                    return JimAction.add_contact()
                elif action == CONTACT_LIST:
                    return JimAction.contact_list()
                elif action == GET_CONTACTS:
                    return JimAction.get_contacts()



class JimAction(JimFunctions):
    """
    Прописаны действия Джин
    """
    @staticmethod
    def create_presence(self, login):
        self.__dict__[ACTION] = PRESENCE
        result = self.__dict__
        result[ACCOUNT_NAME] = login
        return result

    def delete_contact(self, login):
        self.__dict__[ACTION] = GET_CONTACTS
        result = self.__dict__
        result[ACCOUNT_NAME] = login
        return result

    def add_contact(self, login):
        self.__dict__[ACTION] = ADD_CONTACT
        result = self.__dict__
        result[ACCOUNT_NAME] = login
        return result

