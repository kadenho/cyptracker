from random import uniform, randint
from sys import stderr

from datetime import datetime, timedelta

from sqlalchemy.exc import SQLAlchemyError

from cryptos import CryptoDatabase, Crypto, CryptoPrice, PortfolioEntry, User


def add_starter_data(session):
    tyler_thiede = User(username='Tyler Thiede')

    bitcoin = Crypto(name='Bitcoin', symbol='btc', crypto_id='bitcoin')
    ethereum = Crypto(name='ethereum', symbol='eth', crypto_id='ethereum')
    dogecoin = Crypto(name='Dogecoin', symbol='doge', crypto_id='dogecoin')
    hawktuah = Crypto(name='Hawk Tuah', symbol='hawktuah', crypto_id='hawk-tuah')
    tyler = Crypto(name='Tyler', symbol='tyler', crypto_id='tyler')
    tyler_2 = Crypto(name='Tyler', symbol='tyler', crypto_id='tyler-2')

    session.add(tyler_thiede)
    session.add(bitcoin)
    session.add(ethereum)
    session.add(dogecoin)
    session.add(hawktuah)
    session.add(tyler)
    session.add(tyler_2)

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
