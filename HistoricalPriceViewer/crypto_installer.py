from datetime import datetime
from sys import stderr
from random import randint, uniform
from sqlalchemy.exc import SQLAlchemyError

from crypto import CryptoDatabase, Coin, CoinValue


def add_starter_data(session):
    """
    add starter data to the database
    """
    session.add(Coin(symbol='SCAM', name='Scam coin', coin_values=populate_values_list()))

    session.add(Coin(symbol='BTC', name='Bitcoin', coin_values=populate_values_list()))

    session.add(Coin(symbol='ETH', name='Ethereum', coin_values=populate_values_list()))

    session.add(Coin(symbol='COIN', name='Coin coin', coin_values=populate_values_list()))

    session.add(Coin(symbol='LOSE', name='Loser coin', coin_values=populate_values_list()))

    session.add(Coin(symbol='DUCK', name='Duck coin', coin_values=populate_values_list()))

    session.add(Coin(symbol='PENG', name='Penguin coin', coin_values=populate_values_list()))

    session.add(Coin(symbol='S&P', name='S&P 500 coin', coin_values=populate_values_list()))

    session.add(Coin(symbol='REAL', name='Real coin', coin_values=populate_values_list()))

    session.add(Coin(symbol='FAKE', name='Fake coin', coin_values=populate_values_list()))

    session.add(Coin(symbol='KH', name='Kaden coin', coin_values=populate_values_list()))
    
    session.add(Coin(symbol='CAT', name='Cat coin', coin_values=populate_values_list()))

    session.add(Coin(symbol='DOG', name='Dog coin', coin_values=populate_values_list()))

    session.commit()


def populate_values_list():
    values_list = []
    price = randint(1, 50000)
    for i in range(30):
        for j in range(24):
            price_variation = round(price * 0.025, 2)
            price += round(uniform(-price_variation, price_variation))
            if price < 0:
                price = 0
            values_list.append(CoinValue(timestamp=datetime(2025, 1, i + 1, j, 0, 0), price=price))
    return values_list


def main():
    try:
        url = CryptoDatabase.construct_mysql_url('localhost', 3306, 'crypto', 'root', 'sqlpassword')
        crypto_database = CryptoDatabase(url)
        crypto_database.ensure_tables_exist()
        print('Tables created.')
        session = crypto_database.create_session()
        add_starter_data(session)
        session.commit()
        print('Records created.')
    except SQLAlchemyError as exception:
        print('Database setup failed!', file=stderr)
        print(f'Cause: {exception}', file=stderr)
        exit(1)


if __name__ == '__main__':
    main()
