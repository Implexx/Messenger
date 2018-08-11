'''
Самописные ошибки для сервера и клиента
'''


# Ошибка при неверном выборе режима клиента
class WrongModeError(Exception):
    def __init__(self, mode):
        self.mode = mode

    def __str__(self):
        return 'Неверный режим запуска {}. Режим запуска должен быть или чтение - r' \
               'или запись - w'.format(self.mode)