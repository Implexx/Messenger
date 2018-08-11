from sqlalchemy import Column, Table, Integer, String, create_engine, ForeignKey, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

Base = declarative_base()


class Client(Base):
    """
    Описывает таблицу Клиента - Имя и инфо
    """
    __tablename__ = 'clients'
    ClientId = Column(Integer, primary_key=True)
    Name = Column(String, unique=True)
    Info = Column(String)

    def __init__(self, name, info):
        self.Name = name
        self.info = info

    # настройка отображения вывода класса
    def __repr__(self):
        return 'Client ({}) - info:{}'.format(self.Name, self.Info)

    # настрйока как ведет себя класс при сравнении
    def __eq__(self, other):
        return self.Name == other.Name


class LoginHistory(Base):
    """
    Таблица в которой информация по истории входов выходов пользователей
    """
    __tablename__ = 'login_history'
    HistId = Column(Integer, primary_key=True)
    ClientId = Column(Integer)
    LoginTime = Column(String, unique=True)
    ClientIp = Column(String)

    def __init__(self, login_time, client_ip):
        self.LoginTime = login_time
        self.ClientIp = client_ip

    def __repr__(self):
        return 'Клиент с ip {} входил в {}'.format(self.ClientIp, self.LoginTime)


class ContactList(Base):
    """
    Список контактов всех пользователей
    """
    __tablename__ = 'contact_list'
    ClientContactId = Column(Integer, primary_key=True)
    ClientId = Column(Integer)
    ContactId = Column(Integer)

    def __init__(self, client_id, contact_id):
        self.ClientId = client_id
        self.ContactId = contact_id

    def __repr__(self):
        return 'У клиента {} имеется контакт - {}'.format(self.ClientId, self.ContactId)


class ClientHistory(Base):
    """
    История сообщений у пользователя
    """
    __tablename__ = 'client_history'
    MessageId = Column(Integer, primary_key=True)
    MessageTime = Column(String)
    Author = Column(String)
    Message = Column(String)

    def __init__(self, msg_time, msg_author, msg):
        self.MessageTime = msg_time
        self.Author = msg_author
        self.Message = msg

    def __repr__(self):
        return 'В {} от {} сообщение-> {}'.format(self.MessageTime, self.Author, self.Message)


class DBAction:
    """
    Описывает действия с базой
    """
    def __init__(self, session_db):
        self.session = session_db

    def add_client(self, name, info):
        """
        добавить клиента в базу
        :param name: логин
        :param info: дополнительная информация
        :return:
        """
        new_client = Client(name, info)
        try:
            self.session.add(new_client)
            self.session.commit()
        except:
            print('Клиент {} уже существует. Не могу добавить'.format(new_client))
            self.session.rollback()

    def add_login_history(self, login_time, client_ip):
        """
        Добавление в базу историю входа
        :param login_time: время входа
        :param client_ip: айпи клиента
        :return:
        """
        new_item = LoginHistory(login_time, client_ip)
        try:
            self.session.add(new_item)
            self.session.commit()
            login_hist_query = session.query(LoginHistory).filter_by(LoginTime=login_time).all()
            print(login_hist_query)
            # print(new_item)
        except:
            print('Запись {} уже существует. Не могу добавить'.format(new_item))
            self.session.rollback()

    def get_login_history(self):
        pass

    def client_in_base(self, client_name):
        """
        Проверка наличия клиента в базе
        :param client_name:
        :return:
        """
        result = self.session.query(Client).filter(Client.Name == client_name).count() > 0
        return result

    def get_clients(self):
        """
        Получение списка всех клиентов
        :return:
        """
        result = []
        clients_list = self.session.query(Client).all()
        for client in clients_list:
            result.append(str(client.Name))
        return result

    def add_client_history(self, msg_time, author, msg_history):
        """
        добавить запись истории сообщения
        :param msg_time:
        :param author:
        :param msg_history:
        :return:
        """
        new_item = ClientHistory(msg_time, author, msg_history)
        self.session.add(new_item)
        self.session.commit()

    @staticmethod
    def clear_base():
        """
        Очистить всю базу от записей
        :return:
        """
        clients_query = session.query(Client).all()
        for elem in clients_query:
            session.delete(elem)
            session.commit()
        login_hist_query = session.query(LoginHistory).all()
        for elem in login_hist_query:
            session.delete(elem)
            session.commit()
        client_hist_query = session.query(ClientHistory).all()
        for elem in client_hist_query:
            session.delete(elem)
            session.commit()
        contacts_query = session.query(ContactList).all()
        for elem in contacts_query:
            session.delete(elem)
            session.commit()


engine = create_engine('sqlite:///probe_db', echo=False)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()
db_action = DBAction(session)