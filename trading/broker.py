from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockLatestQuoteRequest
from alpaca.trading.client import TradingClient

# TODO: continue reading https://alpaca.markets/sdks/python/trading.html and create functions for getting all assets and submitting orders


class Broker:
    '''
    Each Broker object represents a different broker used when trading. 
    
    '''
    def __init__(self, api_key, api_secret):
        self.api_key  = api_key
        self.api_secret = api_secret

class AlpacaAPI(Broker):
    def __init__(self, api_key, api_secret):
        super().__init__(api_key, api_secret)
        self.client = StockHistoricalDataClient(self.api_key, self.api_secret)
        self.trading_client = TradingClient(self.api_key, self.api_secret, paper=True)

    def get_last_price(self, symbol:str):
        multisymbol_request_params = StockLatestQuoteRequest(symbol_or_symbols=[symbol])
        latest_multisymbol_quotes = self.client.get_stock_latest_quote(multisymbol_request_params)
        return latest_multisymbol_quotes[symbol].ask_price
    
    def get_account_details(self):
        return self.trading_client.get_account()
    


