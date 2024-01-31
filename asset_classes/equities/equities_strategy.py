from utils import measures
from trading.broker import AlpacaAPI
from datetime import date, datetime
import time
from alpaca.trading.enums import AssetExchange
from trading.order import Order


class EquitiesStrategy:
    def __init__(self, portfolio, broker):
        self.portfolio = portfolio
        self.broker: AlpacaAPI = broker

    def get_trades(self, instructions) -> list[Order]: 
        '''
        Given target weights of each risk profile, generate a list of orders to get portfolio to desired risk level
        TODO: exchange != OTC for low and medium risk, only for high risk
        '''
        LOW_MEDIUM_RISK_VOL_BOUNDARY = 1 # TODO: placeholder value, should be changed to actual
        MEDIUM_HIGH_RISK_VOL_BOUNDARY = 2 # TODO: placeholder value, should be changed to actual
        target_weights = instructions

        # Calculate portfolio's current risk profile in equities
        # TODO: currently using Volatility as measure of risk.
        #  Could use other utils (as listed below) and maybe have a voting system?

        curr_risk_profile_weights = self.get_risk_profile()

        assets_list = self.broker.get_all_assets('us_equity')
        
        potential_assets_dict = {'low':[], 'medium':[], 'high':[]}


        # TODO: loop through assets list checking price history and get about 4 stocks for each risk type
        # TODO: then in later iterations of project, can sort by liquidity first (high liquidity = lower risk, low liquidity = higher risk)
        for asset in assets_list:
            
            # don't consider assets that can't be traded on Alpaca
            if asset['tradable'] == False:
                continue

            asset_vol = self.get_asset_volatility(asset)
            # get 4 low risk stocks
            if asset_vol <= LOW_MEDIUM_RISK_VOL_BOUNDARY and len(potential_assets_dict['low']) < 4:
                if asset.exchange != AssetExchange.OTC:
                    potential_assets_dict['low'] += asset['symbol']
            
            # get 4 medium risk stocks
            if asset_vol > LOW_MEDIUM_RISK_VOL_BOUNDARY and asset_vol <= MEDIUM_HIGH_RISK_VOL_BOUNDARY and len(potential_assets_dict['medium']) < 4:
                if asset.exchange != AssetExchange.OTC:
                    potential_assets_dict['medium'] += asset['symbol']

            # get 4 high risk stocks
            if asset_vol > MEDIUM_HIGH_RISK_VOL_BOUNDARY and len(potential_assets_dict['medium']) < 4:
                if asset.exchange != AssetExchange.OTC:
                    potential_assets_dict['medium'] += asset['symbol']
            
            # Check if we have enough stocks for all the risk profiles
            if len(potential_assets_dict['low']) == 4 and len(potential_assets_dict['low']) == 4 and len(potential_assets_dict['low']) == 4:
                break

        # Then analyse current portfolio risk profile and desired risk profile, and generate trades 
        # 1. convert target proportions to money values using current portfolio's total value
        self.portfolio.update_values()
       
        target_vals = [(weight * self.portfolio.value) for weight in target_weights]
        actual_vals = [(weight * self.portfolio.value) for weight in curr_risk_profile_weights]
        adjustments = [0,0,0] # 
        for i in range(3):
            adjustments[i] = target_vals[i] - actual_vals[i]
            
        # TODO: For now, split adjustments among the 4 stocks evenly
        trades = []
        for risk_type in potential_assets_dict.keys:
            for ticker in potential_assets_dict[risk_type]:
                i = 0 if risk_type=='low' else 1 if risk_type=='medium' else 2
                curr_price = self.broker.get_last_price(ticker)
                side = 'buy' if adjustments[i] > 0 else 'sell'
                trades += Order(side=side, symbol=ticker, asset_type='us_equity', qty=abs(adjustments[i]/4)//curr_price, order_type='market')

        return trades

    def get_portfolio_risk_profile(self):
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

    def get_asset_volatility(self, asset):
        pass
        


'''
Exchanges: AMEX, ARCA, BATS, NYSE, NASDAQ, NYSEARCA, OTC

Measures of risk:

 - Volatility: Calculate the historical volatility of the stock, often measured by standard deviation. Higher volatility generally implies higher risk.

 - Beta: Evaluate the stock's beta, which utils its sensitivity to market movements. A beta greater than 1 indicates higher volatility compared to the market.

 - Historical Performance: Review the stock's historical performance, including drawdowns during market downturns. Consider how the stock has behaved in different market conditions.

 - Fundamental Analysis: Assess the fundamental factors affecting the stock, such as earnings growth, debt levels, and industry dynamics. Strong fundamentals can contribute to lower risk.

 - Dividend History: Analyze the stock's dividend history. Dividend-paying stocks, especially those with a consistent and growing dividend, may be considered lower risk.

 - News and Events: Stay informed about news and events related to the stock, as unexpected developments can significantly impact its risk profile.

'''
