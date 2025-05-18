from unittest import TestCase
from sqlalchemy.exc import NoResultFound
import CrypTracker.main
from Tokenstaller.cryptos import CryptoDatabase, Crypto


class TestDeleteCrypto(TestCase):
    """
    Test cases for _delete_crypto
    """
    def test_does_not_crash(self):
        url = CryptoDatabase.construct_in_memory_url()
        crypto_database = CryptoDatabase(url)
        crypto_database.ensure_tables_exist()
        session = crypto_database.create_session()
        CrypTracker.main.CrypTrackerApp._add_crypto(session, 'Bitcoin', 'Bitcoin', 'btc')
        CrypTracker.main.CrypTrackerApp._delete_crypto(session, 'Bitcoin')

    def test_does_delete(self):
        url = CryptoDatabase.construct_in_memory_url()
        crypto_database = CryptoDatabase(url)
        crypto_database.ensure_tables_exist()
        session = crypto_database.create_session()
        CrypTracker.main.CrypTrackerApp._add_crypto(session, 'Bitcoin', 'Bitcoin', 'btc')
        actual = session.query(Crypto).filter(Crypto.crypto_id == 'Bitcoin').one()
        # Verify that the entry exists
        self.assertEqual(actual.crypto_id, 'Bitcoin')
        self.assertEqual(actual.name, 'Bitcoin')
        self.assertEqual(actual.symbol, 'btc')
        CrypTracker.main.CrypTrackerApp._delete_crypto(session, 'Bitcoin')
        try:
            # Query for the deleted entry
            session.query(Crypto).filter(Crypto.crypto_id == 'Bitcoin').one()
        except NoResultFound:
            self.assertEqual(None, None)