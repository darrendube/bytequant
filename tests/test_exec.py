import unittest
import pandas as pd
from unittest.mock import patch, MagicMock
from src.exec.exec import get_delta, gen_orders

class TestExec(unittest.TestCase):

    def setUp(self):
        self.current = pd.DataFrame({
            'symbol': ['AAPL', 'USD'],
            'value_usd': [1000.0, 50000.0]
        })
        self.target = pd.DataFrame({
            'symbol': ['AAPL', 'USD'],
            'value_usd': [2000.0, 49000.0]
        })

    @patch('src.exec.exec.Broker')
    def test_get_delta(self, mock_broker):
        delta = get_delta(self.current, self.target)
        self.assertIsInstance(delta, pd.DataFrame)
        self.assertIn('value_usd', delta.columns)

    @patch('src.exec.exec.Broker')
    def test_gen_orders(self, mock_broker):
        mock_broker_instance = MagicMock()
        mock_broker_instance.get_market_price.return_value = 150.0
        mock_broker.return_value = mock_broker_instance

        delta = pd.DataFrame({'value_usd': {'AAPL': 1000.0}})
        orders = gen_orders(delta, mock_broker_instance)
        self.assertIsInstance(orders, list)
        if orders:
            self.assertIn('symbol', orders[0])

if __name__ == '__main__':
    unittest.main()