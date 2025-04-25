from datetime import timedelta, datetime
from random import uniform, randint
from sys import stderr

from sqlalchemy.exc import SQLAlchemyError

from cryptos import CryptoDatabase, Crypto, CryptoPrice, PortfolioEntry, User

def add_starter_data(session):
    tyler_thiede = User(username='Tyler Thiede')

    bitcoin = Crypto(name='Bitcoin', symbol='btc', crypto_id='bitcoin', prices=populate_values_list())
    ethereum = Crypto(name='ethereum', symbol='eth', crypto_id='ethereum', prices=populate_values_list())
    dogecoin = Crypto(name='Dogecoin', symbol='doge', crypto_id='dogecoin', prices=populate_values_list())
    hawktuah = Crypto(name='Hawk Tuah', symbol='hawktuah', crypto_id='hawk-tuah', prices=populate_values_list())
    tyler = Crypto(name='Tyler', symbol='tyler', crypto_id='tyler', prices=populate_values_list())
    tyler_2 = Crypto(name='Tyler', symbol='tyler', crypto_id='tyler-2', prices=populate_values_list())

    session.add(tyler_thiede)
    session.add(bitcoin)
    session.add(tyler)
    session.add(tyler_2)
    session.add(ethereum)
    session.add(dogecoin)
    session.add(hawktuah)
    session.commit()

def populate_values_list():
    values_list = []
    current_timestamp = datetime(2025, 1, 30, 23, 0, 0)
    price = randint(1, 50000)
    for i in range(90):
        for j in range(24):
            price_variation = round(price * 0.025, 2)
            price += round(uniform(-price_variation, price_variation))
            if price < 0:
                price = 0
            values_list.append(CryptoPrice(timestamp=current_timestamp, price=price))
            current_timestamp -= timedelta(hours=1)
    return values_list


def main():
    try:
        password = input('What is your MySQL server password? ')
        url = CryptoDatabase.construct_mysql_url('localhost', 3306, 'cryptos', 'root', password)
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
