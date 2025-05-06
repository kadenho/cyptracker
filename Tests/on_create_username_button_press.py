from unittest import TestCase
import CrypTracker.apikey
import CrypTracker.main
from Tokenstaller.cryptos import CryptoDatabase
from Tokenstaller.cryptos import User

class TestUsernameButtonPress(TestCase):
    """
    Test cases for on_create_username_button_press
    """

    def does_not_crash(self):
        url = CryptoDatabase.construct_in_memory_url()
        crypto_database = CryptoDatabase(url)
        crypto_database.ensure_tables_exist()
        session = crypto_database.create_session()
        CrypTracker.main.CrypTrackerApp._on_create_username_button_press(session, 'Example')

    def test_create_movie_does_not_crash(self):
        url = CryptoDatabase.construct_in_memory_url()
        crypto_database = CryptoDatabase(url)
        crypto_database.ensure_tables_exist()
        session = crypto_database.create_session()
        CrypTracker.main.CrypTrackerApp._on_create_username_button_press(session, 'Example')
        actual = session.query(User).filter(User.username == 'Example').one()
        self.assertEqual(actual.username, 'Example')
