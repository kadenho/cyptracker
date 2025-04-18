from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

Persisted = declarative_base()


class Coin(Persisted):
    __tablename__ = 'coins'
    coin_id = Column(Integer, primary_key=True)
    symbol = Column(String(4), nullable=False)
    name = Column(String(256), nullable=False)
    coin_values = relationship('CoinValue', back_populates='coin')


class CoinValue(Persisted):
    __tablename__ = 'coin_values'
    price_id = Column(Integer, primary_key=True)
    price = Column(Integer, nullable=False)
    timestamp = Column(DateTime, nullable=False)
    coin = relationship('Coin', back_populates='coin_values')
    coin_id = Column(Integer, ForeignKey('coins.coin_id'), nullable=False)


class CryptoDatabase(object):
    @staticmethod
    def construct_mysql_url(authority, port, database, username, password):
        return f'mysql+mysqlconnector://{username}:{password}@{authority}:{port}/{database}'

    @staticmethod
    def construct_in_memory_url():
        return 'sqlite:///'

    def __init__(self, url):
        self.engine = create_engine(url)
        self.Session = sessionmaker()
        self.Session.configure(bind=self.engine)

    def ensure_tables_exist(self):
        Persisted.metadata.create_all(self.engine)

    def create_session(self):
        return self.Session()
