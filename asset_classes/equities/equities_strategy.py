class EquitiesStrategy:
    def __init__(self, portfolio, broker):
        self.portfolio = portfolio
        self.broker = broker

    def get_trades(self, instructions):
        return []