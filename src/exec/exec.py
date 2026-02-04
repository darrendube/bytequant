# responsible for converting the target portfolio into orders, then sending 
# those orders to the broker #

import numpy as np
import pandas as pd
import sys
import time
from src.risk import risk
from src.data.db.session import SessionLocal
from src.data.db.models import Position
from src.data.db import crud 
from src.exec.broker import AlpacaClient as Broker


### HELPERS ###
'''Given current and target portfolio dfs, generates a "Delta" df - the difference
between the target and current portfolio'''
def get_delta(current, target):
    print('TARGET:\n')
    print(target)
    print('CURRENT:\n')
    print(current)
    target_i, current_i = target.set_index('symbol'), current.set_index('symbol')
    return target_i.subtract(current_i, fill_value=0)

'''Given delta df, generates order objects'''
def gen_orders(delta, broker):
    # NOTE: alpaca does not support longs on fractional shares so will just
    # round down qty values
    orders = []
    for symbol, notional_value in delta['value_usd'].items():
        # convert notional value to rounded down qty
        curr_price = broker.get_market_price(symbol)
        qty = int(notional_value/curr_price)
        
        # generate order
        orders += [{'symbol': symbol, 'qty': qty}] # TODO: missing strategy info

    return orders

'''Given list of orders, updates Strategy and Order table in DB'''
def update_db(orders):
    for order in orders:
        pass # TODO:


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
    
    delta_df = get_delta(broker.get_current_portfolio(prices=True), target_portfolio)
    orders: list = gen_orders(delta_df, broker)

    # put orders in Order db table
    for order in orders:
        pass

    
    for order in orders:
        broker.place_order(**order)
        time.sleep(0.5) # to comply with Alpaca 200 reqs/min rate limit
        print(f'placed order {order}')
    return True # TODO: perhaps return list of succesful and unsuccesful orders
