class EquitiesStrategy:
    def __init__(self, portfolio, broker):
        self.portfolio = portfolio
        self.broker = broker

    def get_trades(self, instructions):
        target_weights = instructions

        # Calculate portfolio's current risk profile in equities
        # TODO: currently using Volatility as measure of risk. Could use other measures (as listed below) and maybe have a voting system?
        curr_risk_profile_values = [0.0, 0.0, 0.0]
        for position in self.portfolio.positions:
            if position.asset_type=='equity':
                # calculate risk type of asset
                pass
        return []
    
'''
Measures of risk:

 - Volatility: Calculate the historical volatility of the stock, often measured by standard deviation. Higher volatility generally implies higher risk.

 - Beta: Evaluate the stock's beta, which measures its sensitivity to market movements. A beta greater than 1 indicates higher volatility compared to the market.

 - Historical Performance: Review the stock's historical performance, including drawdowns during market downturns. Consider how the stock has behaved in different market conditions.

 - Fundamental Analysis: Assess the fundamental factors affecting the stock, such as earnings growth, debt levels, and industry dynamics. Strong fundamentals can contribute to lower risk.

 - Dividend History: Analyze the stock's dividend history. Dividend-paying stocks, especially those with a consistent and growing dividend, may be considered lower risk.

 - News and Events: Stay informed about news and events related to the stock, as unexpected developments can significantly impact its risk profile.

'''