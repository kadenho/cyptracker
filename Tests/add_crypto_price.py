from unittest import TestCase
import CrypTracker.main
from Tokenstaller.cryptos import CryptoDatabase, CryptoPrice
from datetime import datetime

class AddCryptoPriceTest(TestCase):
    """
    Test cases for add_crypto_price
    """
    @staticmethod
    def test_does_not_crash():
        url = CryptoDatabase.construct_in_memory_url()
        crypto_database = CryptoDatabase(url)
        crypto_database.ensure_tables_exist()
        session = crypto_database.create_session()
        CrypTracker.main.CrypTrackerApp._add_crypto_price(session, 'Bitcoin', 200, datetime(year=2025, month=5, day=5))

    def test_inserts_correct_id_name_symbol(self):
        url = CryptoDatabase.construct_in_memory_url()
        crypto_database = CryptoDatabase(url)
        crypto_database.ensure_tables_exist()
        session = crypto_database.create_session()
        CrypTracker.main.CrypTrackerApp._add_crypto_price(session, 'Bitcoin', 200, datetime(year=2025, month=5, day=5))
        actual = session.query(CryptoPrice).filter(CryptoPrice.crypto_id == 'Bitcoin').one()
        self.assertEqual(actual.crypto_id, 'Bitcoin')
        self.assertEqual(actual.price, 20000)
        self.assertEqual(actual.timestamp, datetime(year=2025, month=5, day=5))