"""Константы (ключи, действия, значения, коды ответов) и настройки"""

ENCODING = 'utf-8'
USERNAME_MAX_LENGTH = 25
MESSAGE_MAX_LENGTH = 500

# Ключи протокола (действия)

ACTION = 'action'
TIME = 'time'
USER = 'user'
ERROR = 'error'
ACCOUNT_NAME = 'account_name'
RESPONSE = 'response'
AUTH = 'authenticate'
USER_ID = 'user_id'
ALERT = 'alert'
QUANTITY = 'quantity'

REQUIRED_MESSAGE_KEYS = (ACTION, TIME)
REQUIRED_RESPONSE_KEYS = (RESPONSE,)

# Значения протокола

PRESENCE = 'presence'
MSG = 'msg'
QUIT = 'quit'
TO = 'to'
FROM = 'from'
MESSAGE = 'message'
GET_CONTACTS = 'get_contacts'
ADD_CONTACT = 'add_contact'
DEL_CONTACT = 'del_contact'
CONTACT_LIST = 'contact_list'
ACTIONS = (PRESENCE, MSG, GET_CONTACTS, DEL_CONTACT, ADD_CONTACT, CONTACT_LIST)

# Коды ответов сервера

BASIC_NOTICE = 100
OK = 200
ACCEPTED = 202
WRONG_REQUEST = 400  # неправильный запрос или джейсон обьект
SERVER_ERROR = 500  # ошибка на стороне сервера
RESPONSE_CODES = (BASIC_NOTICE, OK, ACCEPTED, WRONG_REQUEST, SERVER_ERROR)
