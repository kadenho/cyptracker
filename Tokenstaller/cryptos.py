import sqlalchemy
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime, Index, \
    ForeignKeyConstraint, BigInteger
from sqlalchemy.orm import sessionmaker, relationship

Persisted = sqlalchemy.orm.declarative_base()


class Crypto(Persisted):
    __tablename__ = 'cryptos'
    crypto_id = Column(String(64), primary_key=True)
    name = Column(String(256), nullable=False)
    symbol = Column(String(64), nullable=False)
    prices = relationship('CryptoPrice', uselist=True, back_populates='crypto', cascade='all, delete-orphan')


class PortfolioEntry(Persisted):
    __tablename__ = 'portfolio_entries'

    entry_id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, nullable=False)
    crypto_id = Column(String(64), nullable=False)
    user_id = Column(Integer, ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False)
    quantity = Column(BigInteger, nullable=False)
    investment = Column(BigInteger, nullable=False)

    __table_args__ = (
        ForeignKeyConstraint(
            ['crypto_id', 'timestamp'],
            ['crypto_prices.crypto_id', 'crypto_prices.timestamp'],
            ondelete='CASCADE'
        ),
    )

    user = relationship('User', back_populates='portfolio_entries')

    crypto_price = relationship(
        'CryptoPrice',
        back_populates='entries',
        primaryjoin='and_(PortfolioEntry.timestamp==CryptoPrice.timestamp, '
                    'PortfolioEntry.crypto_id==CryptoPrice.crypto_id)'
    )


class CryptoPrice(Persisted):
    __tablename__ = 'crypto_prices'
    crypto_id = Column(String(64), ForeignKey('cryptos.crypto_id', ondelete='CASCADE'), primary_key=True,
                       nullable=False)
    timestamp = Column(DateTime, primary_key=True, nullable=False)
    price = Column(BigInteger, nullable=False)
    crypto = relationship('Crypto', back_populates='prices')
    entries = relationship(
        'PortfolioEntry',
        back_populates='crypto_price',
        primaryjoin=
        'and_(PortfolioEntry.timestamp==CryptoPrice.timestamp, ' 'PortfolioEntry.crypto_id==CryptoPrice.crypto_id)',
        cascade='all, delete-orphan'
    )
    __table_args__ = (
        Index('idx_crypto_id', 'crypto_id'),
        Index('idx_timestamp', 'timestamp'),
    )


class ValueCheck(Persisted):
    __tablename__ = 'value_checks'
    value_check_id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, nullable=False)
    user_id = Column(Integer, ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False)
    total_value = Column(BigInteger, nullable=False)
    change_from_previous = Column(BigInteger, nullable=True)
    change_from_investment = Column(BigInteger, nullable=False)
    user = relationship('User', back_populates='value_checks')


class User(Persisted):
    __tablename__ = 'users'
    user_id = Column(Integer, primary_key=True)
    username = Column(String(256), nullable=False)
    portfolio_entries = relationship('PortfolioEntry', uselist=True, back_populates='user')
    value_checks = relationship('ValueCheck', uselist=True, back_populates='user')


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
