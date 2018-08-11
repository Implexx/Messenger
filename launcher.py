'''
Срипт автозапуска сервера и приложений
'''

from subprocess import Popen, CREATE_NEW_CONSOLE
from alchemy import db_action

process_list = []

while True:
    user = input("1 Запустить сервер и клиентов\n"
                 "2 Выйти и закрыть соединения\n"
                 "3 Провести очистку баз\n"
                 "Выберите пункт меню =")
    print('---'*10)

    if user == '1':
        process_list.append(Popen('python server.py', creationflags=CREATE_NEW_CONSOLE))
        print('Сервер запущен')

        menu = input('Сколько читающих клиентов запустить? =')
        print('Запуск {} читающих клиентов'.format(menu))
        for i in range(int(menu)):
            process_list.append(Popen('python client.py localhost 8888 r', creationflags=CREATE_NEW_CONSOLE))

        menu = input('Сколько пишущих клиентов запустить? =')
        print('Запуск {} пишущих клиентов'.format(menu))
        for i in range(int(menu)):
            process_list.append(Popen('python client.py localhost 8888 w', creationflags=CREATE_NEW_CONSOLE))

    elif user == '2':
        for process in process_list:
            print('Закрываю {}'.format(process))
            process.kill()
        process_list.clear()
        print('Гудбай')
        break
    elif user == '3':
        db_action.clear_base()
