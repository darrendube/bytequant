from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockLatestQuoteRequest
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import GetAssetsRequest, MarketOrderRequest, LimitOrderRequest, GetOrdersRequest
from alpaca.trading.enums import AssetClass, OrderSide, TimeInForce, QueryOrderStatus
from order import Order
import datetime

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
    
    def get_assets(self, asset_class:str):
        '''
        TODO: support searching for assets with other parameters using GetAssetsRequest

        asset_class : str
            'us_equity' | 'crypto'
        '''
        if asset_class == 'us_equity':
            return self.trading_client.get_all_assets(GetAssetsRequest(asset_class=AssetClass.US_EQUITY))
        elif asset_class == 'crypto':
            return self.trading_client.get_all_assets(GetAssetsRequest(asset_class=AssetClass.CRYPTO))
        
    def submit_order(self, order:Order):
        order_side = OrderSide.BUY if order.side.lower()=='buy' else OrderSide.SELL
        time_in_force = order.time_in_force if order.time_in_force is not None else TimeInForce.DAY
        
        if order.order_type == 'market':
            order_data = MarketOrderRequest(
                symbol = order.symbol,
                qty = order.qty,
                side = order_side,
                time_in_force = time_in_force
            )

            return self.trading_client.submit_order(order_data=order_data)

        elif order.order_type == 'limit':
            order_data = LimitOrderRequest(
                symbol = order.symbol,
                limit_price = order.limit_price,
                side = order_side,
                time_in_force = TimeInForce.FOK # Fill-or-Kill. maybe change this/ set as in market order above
            )

            return self.trading_client.submit_order(order_data=order_data)
        
    def get_orders(self, status=None, limit=None, after:datetime=None, until:datetime=None, side=None):
        args_dict = {}
        if status is not None:
            if status=='all':
                args_dict['status'] = QueryOrderStatus.ALL
            elif status=='open':
                args_dict['status'] = QueryOrderStatus.OPEN
            elif status=='closed'
                args_dict['status'] = QueryOrderStatus.CLOSED
        request_params = GetOrdersRequest(

        )



