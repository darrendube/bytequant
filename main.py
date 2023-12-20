import math
import numpy as np
import pandas as pd
import pickle
import os
from portfolio_management.portfolio import Portfolio
from portfolio_management.portfolio_manager import PortfolioManager
from asset_classes.equities.equities_strategy import EquitiesStrategy
from asset_classes.fixed_income.fixed_income_strategy import FixedIncomeStrategy
from asset_classes.forex.forex_strategy import ForexStrategy
from trading.trader import Trader
from trading.broker import AlpacaAPI

trading = True

portfolio: Portfolio
portfolio_manager = PortfolioManager(assets=['equities'])
trader = Trader()
broker = AlpacaAPI('PKBHECRAUKBSKI23DYTW', 'LDWQZ3y8Goa27QWDFgla4TbbYgLNn2n7dtbNvQjO')

if os.path.exists('data/portfolio.pf'):
    with open('data/portfolio.pf','rb') as pf:
        portfolio = pickle.load(pf) # unpickle the Portfolio object stored in data/portfolio.pf
else:
    portfolio = Portfolio(cash=1_000_000) # start off with 1000000 cash if no portfolio already exists


while trading:

    # get portfolio manager to decide which assets to buy/sell and return instructions in dict format
    #    TODO: instruction format can be perhaps a target value of holdings of each asset (and maybe each risk category in each asset type)
    #    TODO; can include cash buffer to acocunt for slippage. instructions can adjust buffer if it gets too low/high
    portfolio_targets:dict = portfolio_manager.evaluate(portfolio)

    # get strategies to convert instructions to orders (to fulfil the increase/reduction in their respective assets as outlined by instructions)
    
    orders = EquitiesStrategy(portfolio, broker).get_trades(portfolio_targets['equities']) + \
             FixedIncomeStrategy(portfolio, broker).get_trades(portfolio_targets['fixed income']) + \
             ForexStrategy(portfolio, broker).get_trades(portfolio_targets['forex'])
    
    # get trader to execute orders (after cost optimisation) and return successful trades
    #  TODO: cost optimisation must ensure relative 
    filled_orders = trader.execute(orders)

    # update portfolio with successful trades
    portfolio.update(filled_orders) # add new positions or update existing positions with newly filled orders

    # if some condition is True: halt trading and save current portfolio to a file
    if False: 
        with open('data/portfolio.pf','wb') as pf:
            pickle.dump(portfolio, pf)
        trading=False












    