from .trade import Trade
import time

class Order:
    
    def __init__(self, side, symbol, asset_type, qty, order_type, conditions = {}, limit_price = None, time_in_force = None):
        self.side = side
        self.symbol = symbol
        self.asset_type = asset_type # equity, forex, fixed income
        self.qty = qty
        self.order_type = order_type
        self.conditions = conditions
        self.limit_price = limit_price
        self.time_in_force = time_in_force # for limit order
        self.status = 'open' # set to filled if succesful, cancelled if rejected by cost_optimiser, rejected if rejected by the broker
                                  # if set to filled, create a new Trade object

    def cancel(self):
        self.status = 'cancelled'

    def mark_as_filled(self, price):
        """Set order's status to filled"""
        self.status = 'filled'
        return Trade(self.side, self.symbol, self.asset_type, self.qty, price, time.time)
    
  