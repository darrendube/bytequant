import numpy as np
import yfinance as yf
import pandas as pd
import logging
import warnings

from alpaca.trading.requests import GetAssetsRequest
from alpaca.trading.enums import AssetClass
from alpaca.trading.client import TradingClient

from dotenv import load_dotenv
from pathlib import Path
import os

from datetime import datetime
from dateutil.relativedelta import relativedelta
# handles the loading, cleaning, and storing of market ohlcv data

load_dotenv(dotenv_path=Path('../../config/.env'))
warnings.filterwarnings('ignore')
key = os.getenv("ALPACA_KEY")
secret = os.getenv("ALPACA_SECRET")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RAW_DIR = os.path.join(BASE_DIR, 'raw')
PROCESSED_DIR = os.path.join(BASE_DIR, 'processed')

# first fetch list of available tickers from alpaca

#alpaca_client = TradingClient(key, secret)
#assets = alpaca_client.get_all_assets(GetAssetsRequest(asset_class=AssetClass.US_EQUITY))
#symbols = [asset.symbol for asset in assets if asset.tradable and asset.exchange in ['NYSE', 'NASDAQ', 'ARCA'] and asset.status == 'active']

# alpaca does not seem to distinguish between stocks and etfs - will need to get list of tickers from another source
nasdaq_df = pd.read_csv("https://www.nasdaqtrader.com/dynamic/SymDir/nasdaqlisted.txt", sep='|')
other_df = pd.read_csv("https://www.nasdaqtrader.com/dynamic/SymDir/otherlisted.txt", sep='|')
other_df.rename(columns={'ACT Symbol': 'Symbol'}, inplace=True)
symbols_df = pd.concat([nasdaq_df, other_df])[['Symbol', 'Security Name', 'ETF', 'Test Issue']]
symbols_df= symbols_df[(symbols_df['ETF']=='N') & (symbols_df['Test Issue'] == 'N')]
symbols = np.array(symbols_df['Symbol'])

# download the historical prices of those tickers from yfinance (don't redownload data that's already there)
logging.basicConfig(filename='log.txt', level=logging.INFO)

### HELPERS ###
def download_raw_data():
    os.makedirs(RAW_DIR, exist_ok=True)
    count = 0
    for symbol in symbols:
        if count % 100 == 0: print(count)
        count += 1
        try:
            file_path = os.path.join(RAW_DIR, f'{symbol}.csv')
            if os.path.exists(file_path):
                # file exists -> check if existing data is up to date
                with open(file_path, 'rb') as f:
                    existing_df = pd.read_csv(f, index_col=0, parse_dates=True)
                last_date = pd.to_datetime(existing_df.index.max())
                if last_date >= pd.to_datetime(datetime.today().strftime('%Y-%m-%d')):
                    continue # up to date

                # not up to date -> download only missing data
                start_date = (last_date + timedelta(days=1)).strftime('%Y-%m-%d')
                new_df=  yf.download(symbol, start=start_date, progress=False)
                if not new_df.empty:
                    updated_df = pd.concat([existing_df, new_df])
                    updated_df.to_csv(file_path)
                del existing_df, new_df, updated_df
            else:
                # file does not exist: download from scratch
                df = yf.download(symbol, period='20y', progress=False)
                if not df.empty:
                    df.to_csv(file_path)
                else:
                    logging.info(f'{symbol}: no data')
        except Exception as e:
            logging.error(f'{symbol}: download failed -> {e}')
    logging.info(f'total downloaded: {count}')


# TODO: then clean the data into parquet format and store it
def convert_to_parquet():
    os.makedirs(PROCESSED_DIR, exist_ok=True)
    cutoff_date = datetime.today() - relativedelta(years=20)

    for file in os.listdir(RAW_DIR):
        if file.endswith('.csv'):
            csv_path = os.path.join(RAW_DIR, file)
            with open(csv_path, 'rb') as f:
                df = pd.read_csv(f, index_col=0, parse_dates=True, skiprows=[1,2])
            df.index = pd.to_datetime(df.index)
            df = df[df.index >= cutoff_date]

            parquet_path = os.path.join(PROCESSED_DIR, file.replace('.csv', '.parquet'))
            df.to_parquet(parquet_path, engine='pyarrow', index=True)

### MAIN FUNCTION ###
def load_market_data():
    download_raw_data()
    convert_to_parquet()
