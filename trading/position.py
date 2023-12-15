from trade import *

class Position:

    def __init__(self, type, symbol, asset_type, qty, entry_price, holding_period = None, trades:list[Trade]=None, unrealised_profit = None, current_price = None):
        self.type = type # long or short
        self.symbol = symbol
        self.asset_type = asset_type # equity, forex, fixed income
        self.qty = qty
        self.entry_price = entry_price # average price the asset was acquired
        self.current_price = current_price 
        self.holding_period = holding_period # time passed since particular position was first opened
        self.trades = trades # list of trades that 
        self.unrealised_profit = (current_price-entry_price) if current_price is not None else None

  
    def update_price(self, new_price):
        '''Updates current price of Position, and updates the unrealised profit on this position'''
        self.current_price = new_price
        self.unrealised_profit = self.current_price - self.entry_price

    def get_current_price(self):
        return self.current_price
    
   

