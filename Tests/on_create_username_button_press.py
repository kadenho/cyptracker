from unittest import TestCase
import CrypTracker.apikey
import CrypTracker.main
import tempMain
from Tokenstaller.cryptos import CryptoDatabase

class TestUsernameButtonPress(TestCase):
    """
    Test cases for on_create_username_button_press
    """

    def test_create_movie_does_not_crash(self):
        url = CryptoDatabase.construct_in_memory_url()
        crypto_database = CryptoDatabase(url)
        crypto_database.ensure_tables_exist()
        session = crypto_database.create_session()
        CrypTracker.main.CrypTrackerApp._on_create_username_button_press(session, 'Example')

class TestUsernameButtonPressTemp(TestCase):
    """
    Test cases for on_create_username_button_press
    """

    def test_create_movie_does_not_crash(self):
            url = CryptoDatabase.construct_in_memory_url()
            crypto_database = CryptoDatabase(url)
            crypto_database.ensure_tables_exist()
            session = crypto_database.create_session()
            tempMain.CrypTrackerAppTemp._on_create_username_button_press(session, 'Example')
