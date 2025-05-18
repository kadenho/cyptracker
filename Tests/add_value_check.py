from datetime import datetime
from unittest import TestCase
import CrypTracker.main
from Tokenstaller.cryptos import CryptoDatabase, ValueCheck

class TestAddValueCheck(TestCase):
    """
    Test cases for _add_value_check
    """

    def test_does_not_crash(self):
        url = CryptoDatabase.construct_in_memory_url()
        crypto_database = CryptoDatabase(url)
        crypto_database.ensure_tables_exist()
        session = crypto_database.create_session()
        CrypTracker.main.CrypTrackerApp._add_value_check(session, 2, 4, datetime(year=2025, month=5, day=5), 34, 1)

    def test_all_information_inserted(self):
        url = CryptoDatabase.construct_in_memory_url()
        crypto_database = CryptoDatabase(url)
        crypto_database.ensure_tables_exist()
        session = crypto_database.create_session()
        CrypTracker.main.CrypTrackerApp._add_value_check(session, 2, 4, datetime(year=2025, month=5, day=5), 34, 1)
        actual = session.query(ValueCheck).filter(ValueCheck.user_id == 1).one()
        self.assertEqual(actual.change_from_investment, 2)
        self.assertEqual(actual.change_from_previous, 4)
        self.assertEqual(actual.timestamp, datetime(year=2025, month=5, day=5))
        self.assertEqual(actual.total_value, 34)
        self.assertEqual(actual.user_id, 1)
