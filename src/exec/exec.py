# responsible for converting the target portfolio into orders, then sending 
# those orders to the broker #

import numpy as np
import pandas as pd
import sys
sys.path.append('../src/data')
sys.path.append('../data')
sys.path.append('../src/risk')
sys.path.append('../risk')
from risk import get_current_portfolio
from db.session import Session
from db.models import Position
from broker import AlpacaClient as Broker

### HELPERS ###
'''Given current and target portfolio dfs, generates a "Delta" df - the difference
between the target and current portfolio'''
def get_delta(current, target):
    pass

'''Given delta df, generates order objects'''
def gen_orders(delta):
    pass



### TODOS ###
# TODO: create an optimiser function that takes in prospective orders and
# optimises for trading cost

### MAIN FUNCTION ###
'''
Receives target portfolio, generates orders to convert current portfolio to 
desired portfolio, and terminates when all orders have been filled or an error 
is received from the broker.
'''
def execute(target_portfolio):
    broker = Broker()
    
    curr_portfolio = pd.DataFrame()
    delta_df = get_delta(broker.get_current_portfolio(prices=True), target_portfolio)
    orders: list = gen_orders(delta_df)
    
    for order in orders:
        broker.place_order(**order)
        # TODO: perhaps a short sleep to respect broker rate limits
