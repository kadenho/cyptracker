from sqlalchemy import create_engine, Column, Integer, String, Date, ForeignKey, ForeignKeyConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship


Persisted = declarative_base()


class Crypto(Persisted):
    __tablename__ = 'cryptos'
    crypto_id = Column(String(64), primary_key=True)
    name = Column(String(256), nullable=False)
    symbol = Column(String(64), nullable=False)
    prices = relationship('CryptoPrice', uselist=True, back_populates='crypto')

class CryptoPrice(Persisted):
    __tablename__ = 'crypto_prices'
    crypto_id = Column(String(64), ForeignKey('cryptos.crypto_id', ondelete='CASCADE'), primary_key=True, nullable=False)
    date = Column(Date, primary_key=True, nullable=False)
    price = Column(Integer, nullable=False)
    crypto = relationship('Crypto', back_populates='prices')
    entries = relationship('PortfolioEntry', uselist=True, back_populates='crypto_price')

class PortfolioEntry(Persisted):
    __tablename__ = 'portfolio_entries'
    entry_id = Column(Integer, primary_key=True, autoincrement=True)
    crypto_id = Column(String(64), nullable=False)
    date = Column(Date, nullable=False)
    quantity = Column(Integer, nullable=False)
    investment = Column(Integer, nullable=False)
    crypto_price = relationship('CryptoPrice', back_populates='entries')

    __table_args__ = (ForeignKeyConstraint(
            ['crypto_id', 'date'],
            ['crypto_prices.crypto_id', 'crypto_prices.date'],
            ondelete='CASCADE'),)


class ValueCheck(Persisted):
    __tablename__ = 'value_checks'
    value_check_id = Column(Integer, primary_key=True)
    date = Column(Date, nullable=False)
    total_value = Column(Integer, nullable=False)
    percentage_change = Column(Integer, nullable=False)


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
