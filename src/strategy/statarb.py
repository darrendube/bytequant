# stats
import numpy as np
import pandas as pd
from statsmodels.tsa.stattools import coint
from sklearn.neighbors import KernelDensity

# utils
import os
import random
from itertools import combinations
import uuid

PROCESSED_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../data/processed')

'''Given the file name of a stock, return that stock's closing price data as a pd Series'''
def get_closing_data(file_name):
    if '.parquet' not in file_name:
        file_name += '.parquet'
    # stock = pd.read_parquet(f'../data/processed/{file_name}')
    stock = pd.read_parquet(os.path.join(PROCESSED_DIR, file_name))
    return stock['Close']

'''Test a pair of stocks for cointegration for the last `window_length` trading days'''
def test_coint_pair(file1, file2, window_length=252):
    symbol1, symbol2 = file1.replace('.parquet',''), file2.replace('.parquet', '')
    combined = pd.concat([get_closing_data(file1), get_closing_data(file2)], axis=1, join='inner').dropna()
    
    # the default return object if there is an error in the test
    blank_df = pd.DataFrame([{
            'symbol_1': symbol1,
            'symbol_2': symbol2,
            'p_value': np.nan
    }])

    if len(combined) < window_length:
        return blank_df

    # only test for cointegration for the last `window_length` trading days
    combined = combined.iloc[-window_length:]

    x1, x2 = combined.iloc[:,0].values, combined.iloc[:,1].values

    if np.std(x1) == 0 or np.std(x2)==0:
        return blank_df
    try: 
        _, p_value, _ = coint(x1, x2)
        return pd.DataFrame([{
            'symbol_1': symbol1,
            'symbol_2': symbol2,
            'p_value': p_value
        }])
    except:
        return blank_df

'''Generate signals using the pairs statarb (coint+KDE) strategy'''
def gen_pairs_signals(bandwidth=0.3, alpha=0.05):
    # get a list of of the files in the processed folder
    processed_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../data/processed')
    #files = os.listdir(os.path.join(curr_dir, '../data/processed'))
    files = os.listdir(PROCESSED_DIR)
    files = [f for f in files if os.path.isfile(os.path.join(PROCESSED_DIR, f))]

    # randomly sample a subset of 40 stocks
    sample_stocks = random.sample(files, k=40)

    # test cointegration for each of the 40choose2 pairs of stocks in the random subset
    df = pd.DataFrame(columns=['symbol_1', 'symbol_2', 'p_value'])
    pairs = list(combinations(sample_stocks, 2))
    for pair in pairs:
        df = pd.concat([df, test_coint_pair(*pair)])

    df = df.sort_values(by='p_value').dropna()
    df = df[df['p_value'] <= 0.05] # filter out the tests that were not significant
    cointegrated = df.sample(n=10) # randomly sample 10 pairs that were found to be cointegrated (significance level 0.05)

    # for each pair: fit a KDE model and determine if the current spread is significantly different from the mean spread
    # NOTE: bandwidth is a hyperparameter
    flagged_pairs = list()
    for row in df.itertuples(index=False, name="Pair"):
        stock1, stock2 = get_closing_data(row.symbol_1), get_closing_data(row.symbol_2)
        spread = stock1 - stock2
        spread.dropna(inplace=True)
        kde = KernelDensity(kernel='gaussian', bandwidth=bandwidth).fit(spread.values.reshape(-1,1))

        # approximate the distribution's cdf
        x = np.linspace(min(spread)-1, max(spread)+1, 10000)
        pdf = np.exp(kde.score_samples(x.reshape(-1,1)))
        dx = x[1] - x[0]
        cdf = np.cumsum(pdf) * dx
        cdf /= cdf[-1] # make sure cdf is normalised

        # find the critical values for the lower and upper 2.5% tails
        lower_crit = x[np.searchsorted(cdf, alpha/2)]
        upper_crit = x[np.searchsorted(cdf, 1-alpha/2)]

        # flag the stock pair if the current spread is significantly different from the mean
        if not (lower_crit < spread.iloc[-1] < upper_crit):
            flagged_pairs += [{
                'symbol_1':row.symbol_1, 
                'symbol_2': row.symbol_2, 
                'lower_crit': lower_crit,
                'upper_crit': upper_crit,
                'curr_spread': spread.iloc[-1],
                'upper': spread.iloc[-1] > upper_crit
            }]

    flagged_pairs = pd.DataFrame(flagged_pairs)

    # determine confidence weights of each pair
    # weights will all be equal at first TODO: change this
    n = min(20, len(flagged_pairs))
    pairs = flagged_pairs.sample(n=n)
    pairs['weight'] = 0.5

    # generate signals
    signals = list()
    for pair in pairs.itertuples(index=False, name="Pair"):
        strategy_id = str(uuid.uuid4())
        signals += [{
            'strategy_id': strategy_id,
            'symbol': pair.symbol_1,
            'weight': -pair.weight if pair.upper else pair.weight
        }]
        signals += [{
            'strategy_id': strategy_id,
            'symbol': pair.symbol_2,
            'weight': pair.weight if pair.upper else -pair.weight
        }]
    print("SIGNALS: ")
    print(pd.DataFrame(signals))

    return pd.DataFrame(signals)








