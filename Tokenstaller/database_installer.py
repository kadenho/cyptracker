from sys import stderr

from datetime import datetime

from sqlalchemy.exc import SQLAlchemyError

from cryptos import CryptoDatabase, Crypto, CryptoPrice, PortfolioEntry


def add_starter_data(session):
    bitcoin = Crypto(name='Bitcoin', symbol='btc', crypto_id ='bitcoin')
    ethereum = Crypto(name='ethereum', symbol='eth', crypto_id ='ethereum')
    dogecoin = Crypto(name='Dogecoin', symbol='doge', crypto_id='dogecoin')
    hawktuah = Crypto(name='Hawk Tuah', symbol='hawktuah', crypto_id= 'hawk-tuah')
    tyler = Crypto(name='Tyler', symbol='tyler', crypto_id= 'tyler')
    tyler_2 = Crypto(name='Tyler', symbol='tyler', crypto_id= 'tyler-2')
    session.add(bitcoin)
    session.add(ethereum)
    session.add(dogecoin)
    session.add(hawktuah)
    session.add(tyler)
    session.add(tyler_2)

    # Price of Ethereum on April 10th 2025
    eth_price_1 = CryptoPrice(crypto_id= 'ethereum', date= datetime.fromisoformat('2025-04-10'), price= 20)
    session.add(eth_price_1)


    # April 10th 2025 Portfolio Entry (10 Eth)

    entry_1 = PortfolioEntry(date=datetime.fromisoformat('2025-04-10'), crypto_id='ethereum', quantity= 10, investment= 200, entry_id = 1)
    session.add(entry_1)


def main():
    try:
        url = CryptoDatabase.construct_mysql_url('localhost', 3306, 'cryptos', 'root', 'weak')
        crypto_database = CryptoDatabase(url)
        crypto_database.ensure_tables_exist()
        print('Tables created.')
        session = crypto_database.create_session()
       # add_starter_data(session)
       # session.commit()
        print('Records created.')
    except SQLAlchemyError as exception:
        print('Database setup failed!', file=stderr)
        print(f'Cause: {exception}', file=stderr)
        exit(1)


if __name__ == '__main__':
    main()
