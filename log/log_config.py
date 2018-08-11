import logging
import logging.handlers
import os

CLIENT_LOG_FILE_PATH = os.path.join('client.log')
SERVER_LOF_FILE_PATH = os.path.join('server.log')

client_logger = logging.getLogger('client')
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
client_handler = logging.FileHandler(CLIENT_LOG_FILE_PATH, encoding='utf-8')
client_handler.setLevel(logging.INFO)
client_handler.setFormatter(formatter)
client_logger.addHandler(client_handler)
client_logger.setLevel(logging.INFO)

server_logger = logging.getLogger('server')
server_handler = logging.handlers.TimedRotatingFileHandler(SERVER_LOF_FILE_PATH, when='d')
server_handler.setFormatter(formatter)
server_logger.addHandler(server_handler)
server_logger.setLevel(logging.INFO)