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

portfolio: Portfolio
portfolio_manager = PortfolioManager()
trader = Trader()

if os.path.exists('data/portfolio.pf'):
    with open('data/portfolio.pf','rb') as pf:
        portfolio = pickle.load(pf) # unpickle the Portfolio object stored in data/portfolio.pf
else:
    portfolio = Portfolio(cash=1_000_000) # start off with 1000000 cash if no portfolio already exists


while trading:

    # get portfolio manager to decide which assets to buy/sell and return instructions in dict format
    portfolio_changes:dict = portfolio_manager.evaluate()

    # get strategies to convert instructions to orders
    orders = EquitiesStrategy(portfolio).get_trades(portfolio_changes['equities']) + \
             FixedIncomeStrategy(portfolio).get_trades(portfolio_changes['fixed income']) + \
             ForexStrategy(portfolio).get_trades(portfolio_changes['forex'])
    
    # get trader to execute orders (after cost optimisation) and return successful trades
    filled_orders = trader.execute(orders)

    # update portfolio with successful trades
    portfolio.update(filled_orders) # add new positions or update existing positions with newly filled orders

    # if some condition is True: halt trading and save current portfolio to a file
    if False: 
        with open('data/portfolio.pf','wb') as pf:
            pickle.dump(portfolio, pf)
        trading=False












    