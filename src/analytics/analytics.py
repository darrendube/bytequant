import numpy as np
import pandas as pd
import sys
from src.data.db import crud
from src.exec.broker import AlpacaClient as Broker

def update_equity_curve():
    details = Broker().account_summary()
    print(details)
    crud.add_equity_point(float(details['equity']), float(details['buying_power'])/2)
    # buying power is divided by 2 because account is currently set to 2x leverage

def update_filled_orders():
    open_orders = crud.get_orders(status="open")
    for order in open_orders:
        broker_order = Broker().get_order_by_id(order.broker_order_id)
        if broker_order.status in ['filled', 'partially_filled']:
            crud.update_order(order.order_id, status = broker_order.status)
            crud.create_trade(order.order_id, order.symbol, broker_order.filled_qty, broker_order.filled_avg_price)
            crud.add_position(order.symbol, order.side, broker_order.filled_qty, broker_order.filled_avg_price)
            pass # TODO: update Position table, Order table and trade table
    broker_orders = Broker().get_order_by_id()
