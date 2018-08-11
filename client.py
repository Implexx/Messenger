import sys
import logging
import time
from socket import socket, AF_INET, SOCK_STREAM
import log.log_config as log_config
from log.log import Log
from errors import WrongModeError
from jim.protocol import JimMessage, JimResponse
from jim.config import *
from alchemy import db_action

# запуск логгирования скрипта
logger = logging.getLogger('client')
log = Log(logger)


# Описание класса Клиент с методами соединения с сервером и основоного цикла работы
class Client:
    def __init__(self, addr='localhost', port=8888, mode='r'):
        self.addr = addr
        self.port = port
        self.mode = mode
        self.socket = self.__connect()

    # Создает соединение по указанным адресу и порту
    @log
    def __connect(self):
        sock = socket(AF_INET, SOCK_STREAM)
        sock.connect((self.addr, self.port))
        return sock

    # Основной цикл работы клиента
    def main_loop(self):
        # создаем Пресенс сообщение для отправки на сервер
        presence_msg = JimMessage(action=PRESENCE, time=time.time())
        # отправляем Пресенс сообщение на сервер
        self.socket.send(bytes(presence_msg))
        # получаем ответ от сервера и вереводим из байтов
        presence_response_bytes = self.socket.recv(1024)
        presence_response = JimResponse.create_from_bytes(presence_response_bytes)
        # делаем проверку ответа сервера, если ОК то дальше
        if presence_response.response == OK:
            print('Связь с сервером установлена')
            # Если у клиента режим чтения
            if self.mode == 'r':
                while True:
                    # Принимаем бесконечно сообщения, переводим в текст из байтов и выводим на экран
                    message_bytes = self.socket.recv(1024)
                    jimmsg = JimMessage.create_from_bytes(message_bytes)
                    print('Вы получили от {} {} сообщеие >'.format(self.socket.fileno(),
                                                                 self.socket.getpeername()), jimmsg.message)
                    # запись в базу данных историю сообщений
                    db_action.add_client_history(str(time.ctime(time.time())), self.socket.fileno(), jimmsg.message)
            # Если у клиента режим записи
            elif self.mode == 'w':
                while True:
                    # Вводим сообщение
                    message = input('Пошлите сообщение в никуда =')
                    # Формируется Джим сообщение и отправляется в байтах
                    msg = JimMessage(action=MSG, time=time.time(), encoding='utf-8', message=message)
                    self.socket.send(bytes(msg))
                    # производится запись в базу данных истории сообщений
                    db_action.add_client_history(str(time.ctime(time.time())), self.socket.fileno(), message)
            else:
                # если режим клиента не Запись и не Чтение - вызывает самодельную ошибку
                raise WrongModeError(mode)
        # Если пришел ответ с ошибкой, выводим на экран
        elif presence_response.response == SERVER_ERROR:
            print('Ошибка сервера')
        elif presence_response.response == WRONG_REQUEST:
            print('Неверный запрос на сервер')
        else:
            print('Неверный код ответа от сервера')


if __name__ == '__main__':
    addr = 'localhost'
    port = 8888
    try:
        # Проверяется режим
        mode = sys.argv[3]
        if mode not in ('r', 'w'):
            print('Режим должен быть или чтение - r, или запись - w')
            sys.exit(0)
    except IndexError:
        mode = 'r'
    # экземпляр класса Клиент с адресом, портом и режимом
    client = Client(addr, port, mode)

    print('****Для начала работы чата введите свой Логин****')
    login = input('--Login: ')
    # запуск основного цикла
    client.main_loop()