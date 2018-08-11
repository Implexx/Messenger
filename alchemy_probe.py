import os
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

Base = declarative_base()


class ClientContact(Base):
    """Связка контакт-клиент для хранения списка контактов"""
    # Название таблицы
    __tablename__ = 'ClientContact'
    # Первичный ключ
    ClientContactId = Column(Integer, primary_key=True)
    # id клиента
    ClientId = Column(Integer, ForeignKey('Client.ClientId'))
    # id контакта клиента
    ContactId = Column(Integer, ForeignKey('Client.ClientId'))

    def __init__(self, client_id, contact_id):
        self.ClientId = client_id
        self.ContactId = contact_id


class Client(Base):
    """Клиент"""
    # Название таблицы
    __tablename__ = 'Client'
    # Первичный ключ
    ClientId = Column(Integer, primary_key=True)
    # Имя клиента
    Name = Column(String)
    # Информация не обязательное поле
    Info = Column(String)

    def __init__(self, name, info):
        self.Name = name
        if info:
            self.Info = info

    def __repr__(self):
        return "<Client ('%s')>" % self.Name

    def __eq__(self, other):
        # Клиенты равны если равны их имена
        return self.Name == other.Name


# путь до папки где лежит этот модуль
DB_FOLDER_PATH = os.path.dirname(os.path.abspath(__file__))
# путь до файла базы данных
DB_PATH = os.path.join(DB_FOLDER_PATH, 'server.db')
#создаем движок
engine = create_engine('sqlite:///{}'.format(DB_PATH), echo=False)
# Не забываем создать структуру базы данных
Base.metadata.create_all(engine)
# Создаем сессию для работы
Session = sessionmaker(bind=engine)
session = Session()
# Рекомендуется брать 1 сессию и передавать параметром куда нам надо
session = session


class Repo:
    """Серверное хранилище"""

    def __init__(self, session):
        """
        Запоминаем сессию, чтобы было удобно с ней работать
        :param session:
        """
        self.session = session

    def add_client(self, username, info):
        """Добавление клиента"""
        new_item = Client(username, info)
        self.session.add(new_item)
        self.session.commit()

    def client_exists(self, username):
        """Проверка, что клиент уже есть"""
        result = self.session.query(Client).filter(Client.Name == username).count() > 0
        return result

    def get_client_by_username(self, username):
        """Получение клиента по имени"""
        client = self.session.query(Client).filter(Client.Name == username).first()
        return client

    def add_contact(self, client_username, contact_username):
        """Добавление контакта"""
        contact = self.get_client_by_username(contact_username)
        if contact:
            client = self.get_client_by_username(client_username)
            if client:
                cc = ClientContact(client_id=client.ClientId, contact_id=contact.ClientId)
                self.session.add(cc)
                self.session.commit()
            else:
                # raise NoneClientError(client_username)
                pass
        else:
            raise ContactDoesNotExist(contact_username)

    def del_contact(self, client_username, contact_username):
        """Удаление контакта"""
        contact = self.get_client_by_username(contact_username)
        if contact:
            client = self.get_client_by_username(client_username)
            if client:
                cc = self.session.query(ClientContact).filter(
                    ClientContact.ClientId == client.ClientId).filter(
                    ClientContact.ContactId == contact.ClientId).first()
                self.session.delete(cc)
            else:
                # raise NoneClientError(client_username)
                pass

    def get_contacts(self, client_username):
        """Получение контактов клиента"""
        client = self.get_client_by_username(client_username)
        result = []
        if client:
            # Тут нету relationship поэтому берем запросом
            contacts_clients = self.session.query(ClientContact).filter(ClientContact.ClientId == client.ClientId)
            for contact_client in contacts_clients:
                contact = self.session.query(Client).filter(Client.ClientId == contact_client.ContactId).first()
                result.append(contact)
        return result




admin_user = Client('Implex', 'info')
repo = Repo(session)
repo.add_client(admin_user)