class Portfolio:

    def __init__(self, positions = None, cash = 0):
        self.positions = positions
        self.cash = 0
        self.value = None

    def update_positions(self, trades):
        '''Given a list of trades, updates the positions'''
        pass
       

    def update_value(self):
        '''Updates the total value of the portfolio'''
        total_val = 0
        # TODO: maybe update prices of each position first?
        for position in self.positions:
            total_val += position.current_price * position.qty
        self.value = total_val

    