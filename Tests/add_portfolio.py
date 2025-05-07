from datetime import datetime
from unittest import TestCase
import CrypTracker.apikey
import CrypTracker.main
from Tokenstaller.cryptos import CryptoDatabase, PortfolioEntry
from Tokenstaller.cryptos import Crypto

class AddPortfolioTest(TestCase):
    """
    Test cases for _add_portfolio
    """
    def test_does_not_crash(self):
        url = CryptoDatabase.construct_in_memory_url()
        crypto_database = CryptoDatabase(url)
        crypto_database.ensure_tables_exist()
        session = crypto_database.create_session()
        CrypTracker.main.CrypTrackerApp._add_portfolio(session, 'Bitcoin', datetime(year=2025, month=5, day=5), 12, 3, 1)

    def test_inserts_correct_crypto_timestamp_investment_quantity_user(self):
        url = CryptoDatabase.construct_in_memory_url()
        crypto_database = CryptoDatabase(url)
        crypto_database.ensure_tables_exist()
        session = crypto_database.create_session()
        CrypTracker.main.CrypTrackerApp._add_portfolio(session, 'Bitcoin', datetime(year=2025, month=5, day=5), 12, 3, 1)
        actual = session.query(PortfolioEntry).filter(PortfolioEntry.user_id == 1).one()
        self.assertEqual(actual.crypto_id, 'Bitcoin')
        self.assertEqual(actual.timestamp, datetime(year=2025, month=5, day=5))
        self.assertEqual(actual.investment, 12)
        self.assertEqual(actual.quantity, 3)
        self.assertEqual(actual.user_id, 1)