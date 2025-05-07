from unittest import TestCase
import CrypTracker.apikey
import CrypTracker.main
from Tokenstaller.cryptos import CryptoDatabase
from Tokenstaller.cryptos import User

class TestUsernameButtonPress(TestCase):
    """
    Test cases for _add_user
    """
    @staticmethod
    def test_does_not_crash():
        url = CryptoDatabase.construct_in_memory_url()
        crypto_database = CryptoDatabase(url)
        crypto_database.ensure_tables_exist()
        session = crypto_database.create_session()
        CrypTracker.main.CrypTrackerApp._add_user(session, 'Example')

    def test_inserts_correct_username(self):
        url = CryptoDatabase.construct_in_memory_url()
        crypto_database = CryptoDatabase(url)
        crypto_database.ensure_tables_exist()
        session = crypto_database.create_session()
        CrypTracker.main.CrypTrackerApp._add_user(session, 'Example')
        actual = session.query(User).filter(User.username == 'Example').one()
        self.assertEqual(actual.username, 'Example')
