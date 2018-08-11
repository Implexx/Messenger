'''
Самописные ошибки для протокола JIM
'''


# ошибка при неправильном Действии в Джим сообщении
class RequiredKeyError(Exception):
    def __init__(self, key):
        self.key = key

    def __str__(self):
        return 'Не хватает обязательного атрибута {}'.format(self.key)


# Ошибка для неверного кода
class ResponseCodeError(Exception):
    def __init__(self, code):
        self.code = code

    def __str__(self):
        return 'Неверный код ответа {}'.format(self.code)


# Ошибка при корявой длине кода ответа
class ResponseCodeLenError(ResponseCodeError):
    def __str__(self):
        return 'Неверная длина кода {}. Длина кода должна быть 3 символа.'.format(self.code)