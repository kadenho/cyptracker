from datetime import datetime
from unittest import TestCase
import CrypTracker.apikey
import CrypTracker.main
from Tokenstaller.cryptos import PortfolioEntry, CryptoDatabase

class TestModifyPortfolio(TestCase):
    """
    Test cases for _modify_portfolio
    """
    def test_does_not_crash(self):
        url = CryptoDatabase.construct_in_memory_url()
        crypto_database = CryptoDatabase(url)
        crypto_database.ensure_tables_exist()
        session = crypto_database.create_session()
        CrypTracker.main.CrypTrackerApp._add_portfolio(session, 'Bitcoin', datetime(year=2025, month=5, day=5), 12, 3, 1)
        CrypTracker.main.CrypTrackerApp._modify_portfolio(session, 'Bitcoin', datetime(year=2025, month=5, day=5), 1, 12, 3)

    def test_correctly_modifies_entry(self):
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
        CrypTracker.main.CrypTrackerApp._modify_portfolio(session, 'Bootcoin', datetime(year=2025, month=4, day=4), 1, 9, 1)
        self.assertEqual(actual.crypto_id, 'Bootcoin')
        self.assertEqual(actual.timestamp, datetime(year=2025, month=4, day=4))
        self.assertEqual(actual.investment, 9)
        self.assertEqual(actual.quantity, 1)
        self.assertEqual(actual.user_id, 1)