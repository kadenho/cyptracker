from unittest import TestCase
import CrypTracker.main
from Tokenstaller.cryptos import CryptoDatabase
from Tokenstaller.cryptos import Crypto

class AddCryptoTest(TestCase):
    """
    Test cases for add_crypto
    """

    @staticmethod
    def test_does_not_crash():
        url = CryptoDatabase.construct_in_memory_url()
        crypto_database = CryptoDatabase(url)
        crypto_database.ensure_tables_exist()
        session = crypto_database.create_session()
        CrypTracker.main.CrypTrackerApp._add_crypto(session, 'Bitcoin', 'Bitcoin', 'btc')

    def test_inserts_correct_id_name_symbol(self):
        url = CryptoDatabase.construct_in_memory_url()
        crypto_database = CryptoDatabase(url)
        crypto_database.ensure_tables_exist()
        session = crypto_database.create_session()
        CrypTracker.main.CrypTrackerApp._add_crypto(session, 'Bitcoin', 'Bitcoin', 'btc')
        actual = session.query(Crypto).filter(Crypto.crypto_id == 'Bitcoin').one()
        self.assertEqual(actual.crypto_id, 'Bitcoin')
        self.assertEqual(actual.name, 'Bitcoin')
        self.assertEqual(actual.symbol, 'btc')