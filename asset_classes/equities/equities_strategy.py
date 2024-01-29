from utils import measures
from trading.broker import AlpacaAPI
from datetime import date, datetime
import time


class EquitiesStrategy:
    def __init__(self, portfolio, broker):
        self.portfolio = portfolio
        self.broker: AlpacaAPI = broker

    def get_trades(self, instructions):
        '''
        Given target weights of each risk profile, generate a list of trades to get portfolio to desired risk level
        TODO: exchange != OTC for low and medium risk, only for high risk
        '''
        target_weights = instructions

        # Calculate portfolio's current risk profile in equities
        # TODO: currently using Volatility as measure of risk.
        #  Could use other utils (as listed below) and maybe have a voting system?

        curr_risk_profile_values = self.get_risk_profile()

        assets_list = self.broker.get_all_assets('us_equity')
        # TODO: loop through assets list checking price history until you come across one that fits volatility profile
        # TODO: then in later iterations of project, can sort by liquidity first (high liquidity = lower risk, low liquidity = higher risk)



        return []

    def get_risk_profile(self):
        risk_profile = []
        pos_val = {}
        for position in self.portfolio.positions:
            if position.asset_type == 'equity':
                # assign symbol:value of position pair to dict
                pos_val[position.symbol] = position.get_value()

            # convert values in dict to proportions
            tot_val = sum(pos_val.values())
            pos_proportion = {symbol: val / tot_val for symbol, val in pos_val.items()}

            # calculate volatility for each symbol and store in new dict
            pos_vol = {}
            for symbol in pos_proportion.keys():
                # TODO: find a way to say start=today's date - 50 days or something, and end=today's date. But in datetime format
                pos_vol[symbol] = measures.volatility(self.broker.get_historical_bar_data(symbol, date.today(), date.today()))

        return risk_profile
        


'''
Measures of risk:

 - Volatility: Calculate the historical volatility of the stock, often measured by standard deviation. Higher volatility generally implies higher risk.

 - Beta: Evaluate the stock's beta, which utils its sensitivity to market movements. A beta greater than 1 indicates higher volatility compared to the market.

 - Historical Performance: Review the stock's historical performance, including drawdowns during market downturns. Consider how the stock has behaved in different market conditions.

 - Fundamental Analysis: Assess the fundamental factors affecting the stock, such as earnings growth, debt levels, and industry dynamics. Strong fundamentals can contribute to lower risk.

 - Dividend History: Analyze the stock's dividend history. Dividend-paying stocks, especially those with a consistent and growing dividend, may be considered lower risk.

 - News and Events: Stay informed about news and events related to the stock, as unexpected developments can significantly impact its risk profile.

'''
