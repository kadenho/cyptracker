from random import uniform, randint
from sys import stderr

from datetime import datetime, timedelta

from sqlalchemy.exc import SQLAlchemyError

from cryptos import CryptoDatabase

def main():
    try:
        password = input('What is your MySQL server password? ')
        url = CryptoDatabase.construct_mysql_url('localhost', 3306, 'cryptos', 'root', password)
        crypto_database = CryptoDatabase(url)
        crypto_database.ensure_tables_exist()
        print('Tables created.')
    except SQLAlchemyError as exception:
        print('Database setup failed!', file=stderr)
        print(f'Cause: {exception}', file=stderr)
        exit(1)


if __name__ == '__main__':
    main()
