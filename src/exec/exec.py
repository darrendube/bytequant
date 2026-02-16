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
    print('DELTAL \n')
    print(target_i.subtract(current_i, fill_value=0))
    return target_i.subtract(current_i, fill_value=0)

'''Given delta df, generates order objects'''
def gen_orders(delta, broker):
    # NOTE: alpaca does not support longs on fractional shares so will just
    # round down qty values
    orders = []
    for symbol, notional_value in delta['value_usd'].items():
        # convert notional value to rounded down qty
        if symbol == 'USD': continue
        curr_price = broker.get_market_price(symbol)
        if curr_price is None: continue
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
def execute(target_portfolio, strategy_allocation, strategy_risk_params):
    broker = Broker()
    
    delta_df = get_delta(broker.get_current_portfolio(prices=True), target_portfolio)
    orders: list = gen_orders(delta_df, broker)

    # populate Strategy table
    for row in strategy_allocation.groupby('strategy_id')['symbol'].apply(list).reset_index().itertuples(index=False):
        # compute risk params
        capital_at_risk, sl, tp = 0.0, None, None
        for symbol in row.symbol:
            capital_at_risk += abs(float(strategy_allocation[(strategy_allocation['strategy_id'] == row.strategy_id) & (strategy_allocation['symbol'] == symbol)]['value_usd']))
        if capital_at_risk != 0.0:
            sl = strategy_risk_params[strategy_risk_params['strategy_id'] == row.strategy_id]['stop_loss_frac'] * capital_at_risk
            tp = strategy_risk_params[strategy_risk_params['strategy_id'] == row.strategy_id]['take_profit_frac'] * capital_at_risk
        
        params = {
            'type': 'statarb',
            'take_profit': tp,
            'stop_loss': sl
        }

        crud.create_strategy(strategy_id=row.strategy_id, name=f"Statarb_{'_'.join(row.symbol)}", parameters=params)
    
    print(strategy_risk_params)

    for order in orders:
        broker_order_id = broker.place_order(**order)
        if broker_order_id is not None:
            side = "BUY" if order['qty'] >= 0 else "SELL"
            # update Order table
            db_order = crud.create_order(symbol=order['symbol'], side=side, qty=abs(order['qty']), broker_order_id=str(broker_order_id, ))

            # update StrategyAllocation table
            #print(' CORR STRAT ALLOC ENTRIES:')
            #print(strategy_allocation[strategy_allocation['symbol'] == order['symbol']])
            for row in strategy_allocation[strategy_allocation['symbol'] == order['symbol']].itertuples(index=False):
                crud.allocate_order_to_strategy(row.strategy_id, db_order.order_id, row.value_usd)

        time.sleep(0.5) # to comply with Alpaca 200 reqs/min rate limit

        # TODO: if a symbol cannot be sold short, you must cancel the order of the corresponding long stock
    return True # TODO: perhaps return list of succesful and unsuccesful orders
