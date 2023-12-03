import math
import numpy as np
import pandas as pd
import pickle
import os
from portfolio import Portfolio
from portfolio_management.portfolio_manager import PortfolioManager
from asset_classes.equities.equities_strategy import EquitiesStrategy
from asset_classes.fixed_income.fixed_income_strategy import FixedIncomeStrategy
from asset_classes.forex.forex_strategy import ForexStrategy
from trading.trader import Trader

trading = True

while trading:

    portfolio: Portfolio
    portfolio_manager = PortfolioManager()
    trader = Trader()

    if os.path.exists('data/portfolio.pf'):
        with open('data/portfolio.pf') as pf:
            portfolio = pf.load() # unpickle the Portfolio object stored in data/portfolio.pf
    else:
        portfolio = Portfolio(cash=1_000_000) # start off with 1000000 cash if no portfolio already exists

    portfolio_changes:dict = portfolio_manager.evaluate()

    orders = EquitiesStrategy(portfolio).get_trades(portfolio_changes['equities']) + \
             FixedIncomeStrategy(portfolio).get_trades(portfolio_changes['fixed income']) + \
             ForexStrategy(portfolio).get_trades(portfolio_changes['forex'])
    
    










    