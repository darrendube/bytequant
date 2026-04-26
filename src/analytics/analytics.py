import numpy as np
import pandas as pd
import sys
from src.data.db import crud
from src.exec.broker import AlpacaClient as Broker

def update_equity_curve():
    details = Broker().account_summary()
    crud.add_equity_point(float(details['equity']), float(details['buying_power'])/2)
    print(f"Equity updated: ${details['equity']}")

def update_filled_orders():
    open_orders = crud.get_orders(status="open")
    print(f"Checking {len(open_orders)} open orders...")
    for order in open_orders:
        broker_order = Broker().get_order_by_id(order['broker_order_id'])
        if broker_order.status in ['filled', 'partially_filled']:
            crud.update_order(order['order_id'], new_status = broker_order.status)
            crud.create_trade(order['order_id'], order['symbol'], broker_order.filled_qty, broker_order.filled_avg_price)
            crud.add_position(order['symbol'], order['side'], broker_order.filled_qty, broker_order.filled_avg_price)
            print(f"Order {order['order_id']} filled: {broker_order.filled_qty} {order['symbol']}")

