##### RISK #####
# responsible for setting and enforcing portfolio-level risk constraints #

import numpy as np
import pandas as pd
import sys
sys.path.append('../src/data')
sys.path.append('../data')
from db.session import Session
from db.models import Position

# HELPERS
def normalise_weights(df):
    df = df.copy()
    sump = df.loc[df['weight'] >= 0, 'weight'].sum()
    sumn = -df.loc[df['weight'] < 0, 'weight'].sum()
    if sump > 0: df.loc[df['weight'] >= 0, 'weight'] /= sump
    if sumn > 0: df.loc[df['weight'] < 0, 'weight'] /= sumn
    return df


'''Returns a DataFrame of the current portfolio (in dollar amounts)'''
def get_current_portfolio():
    result = None
    with Session() as session:
        result = session.query(Position.strategy_id, Position.symbol, Position.qty, Position.side).all()
    portfolio = pd.DataFrame(result, columns=['strategy_id', 'symbol', 'qty', 'side'])
    # TODO: query yfinance for latest price to convert qty to value_usd
    portfolio['qty'] = np.where(portfolio['side'] == 'long', portfolio['side'], -portfolio['qty'])
    portfolio['value_usd'] = portfolio['qty'] * 10 # TODO: placeholder; fix this
    return portfolio[['strategy_id', 'symbol', 'value_usd']]

     

'''
Enforces risk limits on current portfolio, closing positions that have violated limits (exp time, stop loss, take profit, etc).
Returns a DataFrame of a "portfolio" that eliminates these positions, along with the cash freed as a result.
'''
def enforce_risk():
    return (pd.DataFrame(columns=['strategy_id', 'symbol', 'value_usd']), 10000.00)

'''
Given the signals output by the strategy module, and the available cash, returns a DataFrame of the desired new positions
'''
def gen_new_positions(signals, cash_available: float):
    # NOTE: for a start, I will constrain total long positions to the available cash, ignoring the cash proceeds of the short positions
    # normalise weights - short weights and long weights must each sum to 1
    positions = normalise_weights(signals)
    positions['value_usd'] = positions['weight'] * cash_available
    print(positions)
    positions['value_usd'] = np.floor(positions['value_usd'] * 100.00) / 100.00 # round dollar values down to the nearest 2 decimal places
    return positions.drop('weight', axis=1)
    

'''Outputs a DataFrame of the target portfolio (in dollar amounts)'''
def get_orders(signals: pd.DataFrame):
    current_portfolio: pd.DataFrame = get_current_portfolio()
    expired_positions, net_cash_freed = enforce_risk()
    cash_available: float = net_cash_freed + current_portfolio[current_portfolio['symbol'] == 'USD']['value_usd'].sum()
    cash_available -= cash_available*0.2 # TODO: determine a better cash buffer
    new_positions: pd.DataFrame = gen_new_positions(signals, cash_available)
    target_portfolio = pd.concat([current_portfolio, expired_positions, new_positions])
    print(target_portfolio) 
    target_portfolio = target_portfolio.groupby('symbol', as_index=False)['value_usd'].sum()

    # TODO: if value_usd in target portfolio is less than, e.g., $0.10, round down to zero ()
    target_portfolio['value_usd'] = target_portfolio['value_usd'].where(target_portfolio['value_usd'].abs() >= 0.1, 0.0) 
    
    # apply strategy-level risk limits (place stop loss and take profit on each strategy)
    
    # TODO: ensure that not more than 5% of the portfolio is held in a single position, and not more than 
    # 10% in a single strategy
    

    return target_portfolio


