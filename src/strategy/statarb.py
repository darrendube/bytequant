import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
import random
from itertools import combinations
from statsmodels.tsa.stattools import coint

'''Given the file name of a stock, return that stock's closing price data as a pd Series'''
def get_closing_data(file_name):
    stock = pd.read_parquet(f'processed/{file_name}')
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

# get a list of of the files in the processed folder
files = os.listdir('processed')
files = [f for f in files if os.path.isfile(os.path.join('processed', f))]

# randomly sample a subset of 40 stocks
sample_stocks = random.sample(files, k=40)

# test cointegration for each of the 40choose2 pairs of stocks in the random subset
df = pd.DataFrame(columns=['symbol_1', 'symbol_2', 'p_value'])
pairs = list(combinations(sample_stocks, 2))
for pair in pairs:
    df = pd.concat([df, test_coint_pair(*pair)])

df = df.sort_values(by='p_values').dropna()
df = df[df['p_value'] <= 0.05] # filter out the tests that were not significant
cointegrated = df.sample(n=10) # randomly sample 10 pairs that were found to be cointegrated (significance level 0.05)





