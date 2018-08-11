'''
Функции сервера:
-Встает на прослушку
-Отправляет принимает сообщения

'''

import sys
import os
from socket import socket, AF_INET, SOCK_STREAM
import select
import logging
import time
import log.log_config as log_config
from log.log import Log
from jim.config import *
from jim.protocol import JimMessage, JimResponse
from alchemy import db_action
from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import qApp

# Запуск логгирования скрипта
logger = logging.getLogger('server')
log = Log(logger)

# путь к ГУЙ
gui_path = os.path.join(os.getcwd(), 'gui\server_gui.ui')


# Описание класса Сервер с методами Запуск, Чтение/Запись сообщений.
class Server:
    def __init__(self, addr, port):
        self.addr = addr
        self.port = port
        self.socket = self.launch()
        self.clients = []  # список подключенных клиентов

    # метод запуска сервера с параметрами
    def launch(self):
        sock = socket(AF_INET, SOCK_STREAM)
        sock.bind((self.addr, self.port))
        sock.listen(30)
        sock.settimeout(0.2)
        return sock

    # метод чтения запросов от клиентов
    @log
    def read_requests(self, write_clients):
        all_messages = []
        # Перебираем всех клиентов из тех кто пишет
        for sock in write_clients:
            try:
                # пробуем читать что пишет клиент
                bytemsg = sock.recv(1024)
                jimmsg = JimMessage.create_from_bytes(bytemsg)
                # добавляем сообщение в список всех сообщений
                all_messages.append(jimmsg)
            except:
                # Если произошла ошибка, то заносим время и ip в базу
                db_action.add_login_history(str(time.ctime(time.time())), str(addr))
                print('Клиент {} {} отключился'.format(sock.fileno(), sock.getpeername()))
                # Отключаем пользователя у которого ошибка
                self.clients.remove(sock)
        # перебрав всех пишущих клиентов получаем список всех сообщений
        return all_messages

    # отправка ответов клиентам
    @log
    def write_responses(self, messages, read_clients):
        # перебираем клиентов из списка читающих
        for sock in read_clients:
            # Для каждого сообщения из списка всех сообщений на отправку
            for message in messages:
                try:
                    # пробуем отправить сообщение в байтах
                    sock.send(bytes(message))
                except:
                    # Если произошла ошибка при отправке, то заносим в базу время и адрес
                    db_action.add_login_history(str(time.ctime(time.time())), str(addr))
                    print('Клиент {} {} отключился'.format(sock.fileno(), sock.getpeername()))
                    sock.close()
                    # отключаем клиента если ошибка
                    self.clients.remove(sock)

    # метод создающий подключения и читающий - отправляющий сообщения
    def get_connection(self):
        try:
            # создаем соединение и ожидаем подключение
            conn, addr = self.socket.accept()
            # первым всегда идет Пресенс, поэтому принимаем байты
            presence_msg_bytes = conn.recv(1024)
            # переводим байты в сообщение
            presence_msg = JimMessage.create_from_bytes(presence_msg_bytes)
            # Если сообщение - Пресенс запрос
            if presence_msg.action == PRESENCE:
                # готовим ответ - что все ОК
                presence_response = JimResponse(**{RESPONSE: OK})
                # отправляем ответ клиенту в байтах
                conn.send(bytes(presence_response))
            else:
                # Если сообщение от клиента не является Пресенс запросом то отправляем код Ошибки
                presence_response = JimResponse(**{RESPONSE: WRONG_REQUEST})
                conn.send(bytes(presence_response))
        except OSError as e:
            pass
        else:
            print("Получен запрос на соединение от {}".format(str(addr)))
            # добавляется клиент в общий список клиентов
            self.clients.append(conn)
            try:
                # так как произолшло подключение клиента к серверу, заносим историю в базу
                db_action.add_login_history(str(time.ctime(time.time())), str(addr))
                # Проверяем есть ли клиент в базе
                if not db_action.client_in_base(conn.fileno()):
                    # Если клиента нет в базе, добавляем
                    db_action.add_client(conn.fileno(), addr)
            except:
                print('ошибка тут')
        finally:
            wait = 0
            read = []
            write = []
            try:
                # разбиваем клиентов по спискам - 1) Читаем сообщения от первых 2) Пишем вторым 3) Ошибочные
                read, write, e = select.select(self.clients, self.clients, [], wait)
            except:
                pass
            # список запросов считываем от пишущих клиентов
            requests = self.read_requests(read)
            # отправляем ответы читающим
            self.write_responses(requests, write)


# Класс, обрабатывающий ГУЙ
class ServerWindow(QtWidgets.QMainWindow):
    # делаем загрузку УЙ из нарисованного файла в редакторе
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi(gui_path, self)

    # функция вывода списка контактов
    def show_contact_list(self):
        # получаем список контактов из базы
        list_contacts = db_action.get_clients()
        # очищаем виджет от данных (обновление)
        window.listWidget_ClientList.clear()
        # выводим каждый контакт из полученного списка на экран виджета
        for contact in list_contacts:
            window.listWidget_ClientList.addItem(contact)

    def show_history(self):
        pass


if __name__ == '__main__':
    print('сервер запущен и вроде работает')
    addr = 'localhost'
    port = 8888
    server = Server(addr, port)  # экземпляр класса сервер с заданными адресом и портом

    # вызов интерфейса
    app = QtWidgets.QApplication(sys.argv)
    window = ServerWindow()

    while True:
        server.get_connection()
        # Привязка кнопки выхода
        window.actionMenu_Exit.triggered.connect(qApp.exit)
        # привязка вкладки с контактами
        window.show_contact_list()

        # показать и обновить интерфейс
        window.show()
        sys.exit(app.exec_())