import unittest
import pandas as pd
import numpy as np
from unittest.mock import patch, MagicMock
from src.risk.risk import get_target_portfolio, normalise_weights, gen_new_positions

class TestRisk(unittest.TestCase):

    def setUp(self):
        self.signals = pd.DataFrame({
            'strategy_id': ['strat1', 'strat1'],
            'symbol': ['AAPL', 'GOOGL'],
            'weight': [0.5, -0.5]
        })

    @patch('src.risk.risk.Broker')
    def test_get_target_portfolio_normal(self, mock_broker):
        mock_broker_instance = MagicMock()
        mock_broker_instance.account_summary.return_value = {
            'equity': 100000.0,
            'buying_power': 50000.0
        }
        mock_broker_instance.get_current_portfolio.return_value = pd.DataFrame({
            'symbol': ['AAPL'],
            'value_usd': [1000.0]
        })
        mock_broker.return_value = mock_broker_instance

        target, alloc, risk = get_target_portfolio(self.signals)

        self.assertIsInstance(target, pd.DataFrame)
        self.assertIsInstance(alloc, pd.DataFrame)
        self.assertIsInstance(risk, pd.DataFrame)
        self.assertFalse(alloc.empty)
        self.assertFalse(target.empty)

    def test_normalise_weights(self):
        df = pd.DataFrame({
            'weight': [0.3, 0.7, -0.4, -0.6]
        })
        result = normalise_weights(df)
        self.assertAlmostEqual(result.loc[result['weight'] >= 0, 'weight'].sum(), 1.0)
        self.assertAlmostEqual(abs(result.loc[result['weight'] < 0, 'weight'].sum()), 1.0)

    @patch('src.risk.risk.Broker')
    def test_gen_new_positions(self, mock_broker):
        mock_broker_instance = MagicMock()
        mock_broker.return_value = mock_broker_instance

        positions = gen_new_positions(self.signals, 10000.0)
        self.assertIsInstance(positions, pd.DataFrame)
        self.assertIn('strategy_id', positions.columns)

if __name__ == '__main__':
    unittest.main()