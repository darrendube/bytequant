class Trade:
    '''
    Represents a closed (successful) trade
    '''
    def __init__(self, side, symbol, asset_type, qty, price, timestamp):
        self.side = side
        self.symbol = symbol
        self.asset_type = asset_type # equity, forex, fixed income
        self.qty = qty
        self.price = price # the price you manaeged to trade at
        self.timestamp = timestamp
