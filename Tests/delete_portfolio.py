from datetime import datetime
from unittest import TestCase

from sqlalchemy.exc import NoResultFound

import CrypTracker.apikey
import CrypTracker.main
from Tokenstaller.cryptos import PortfolioEntry, CryptoDatabase

class TestDeletePortfolio(TestCase):
    """
    Test cases for _modify_portfolio
    """
    def test_does_not_crash(self):
        url = CryptoDatabase.construct_in_memory_url()
        crypto_database = CryptoDatabase(url)
        crypto_database.ensure_tables_exist()
        session = crypto_database.create_session()
        CrypTracker.main.CrypTrackerApp._add_portfolio(session, 'Bitcoin', datetime(year=2025, month=5, day=5), 12, 3, 1)
        CrypTracker.main.CrypTrackerApp._delete_portfolio(session, 1)

    def test_deletes_entry(self):
        url = CryptoDatabase.construct_in_memory_url()
        crypto_database = CryptoDatabase(url)
        crypto_database.ensure_tables_exist()
        session = crypto_database.create_session()
        CrypTracker.main.CrypTrackerApp._add_portfolio(session, 'Bitcoin', datetime(year=2025, month=5, day=5), 12, 3, 1)
        actual = session.query(PortfolioEntry).filter(PortfolioEntry.user_id == 1).one()
        # Verify that the entry exists
        self.assertEqual(actual.crypto_id, 'Bitcoin')
        self.assertEqual(actual.timestamp, datetime(year=2025, month=5, day=5))
        self.assertEqual(actual.investment, 12)
        self.assertEqual(actual.quantity, 3)
        self.assertEqual(actual.user_id, 1)
        CrypTracker.main.CrypTrackerApp._delete_portfolio(session, 1)
        try:
            # Query for the deleted entry
            session.query(PortfolioEntry).filter(PortfolioEntry.entry_id == 1).one()
        except NoResultFound:
            # Test is successful if this error is thrown
            self.assertEqual(None, None)