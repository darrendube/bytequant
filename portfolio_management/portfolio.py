class Portfolio:

    def __init__(self, positions = None, cash = 0):
        self.positions = positions
        self.cash = 0
        self.value = None

    def update_positions(self, trades, cash):
        '''Given a list of trades, updates the positions. also pass in the new cash level'''
        pass
       

    def update_value(self):
        '''Updates the total value of the portfolio.
            Probably update it directly from alpaca in the future
        '''
        total_val = 0
        # TODO: maybe update prices of each position first?
        for position in self.positions:
            total_val += position.current_price * position.qty
        self.value = total_val

    def get_asset_types(self):
        '''Returns a list of asset types found in the portfolio (equity, fixed_income, or forex)'''
        asset_types = []
        for position in self.positions:
            asset_types += [position.asset_type]
        return list(set(asset_types))
    
    def is_blank(self):
        if len(self.positions) == 0:
            return True
        return False



    