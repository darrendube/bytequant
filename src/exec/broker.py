from alpaca.trading.client import TradingClient
from alpaca.trading.requests import GetAssetsRequest
from dotenv import load_dotenv
from pathlib import Path
import os

load_dotenv()

class AlpacaClient:
    def __init__(self):
        self.client = TradingClient(os.getenv("ALPACA_KEY"), os.getenv("ALPACA_SECRET"))
    
    ### DATA RETRIEVAL ###

    def account_summary(self):
        details = self.client.get_account()
        return {
            'equity': details.equity,
            'cash': details.cash,
            'buying_power': details.buying_power,
            'status': details.status
        }

    def get_current_portfolio(self, prices=False):
        portfolio = {}
        try:
            alpaca_positions = self.client.list_positions()
            for p in alpaca_positions:
                qty = float(p.qty)
                price = None
                if p.side == 'short':
                    qty = -qty
                if prices:
                    portfolio[p.symbol] = qty*self.get_market_price(p.symbol)
                else:
                    portfolio[p.symbol] = qty
            return pd.Dataframe(list(portfolio.items()), columns=['symbol', 'value_usd'])
        except Exception as e:
            print(f"Error fetching positions: {e}")
            return pd.DataFrame()

    def get_market_price(self, symbol):
        try:
            trade = self.client.get_latest_trade(symbol)
            return float(trade.price)
        except Exception as e:
            print(f"Error fetching price for {symbol}: {e}")
            return None

    ### ORDER EXECUTION ###

    def place_order(self, symbol, qty, order_type="market", limit_price=None):
        # NOTE: negative qty = sell
        side = "buy" if qty > 0 else "sell"
        qty = abs(qty) # Alpaca requires positive qty + side
        
        # Construct arguments dynamically
        order_params = {
            "symbol": symbol,
            "qty": qty,
            "side": side,
            "type": order_type,
            "time_in_force": "gtc" # Good Till Cancelled
        }

        if order_type == "limit":
            if limit_price is None:
                raise ValueError("Limit price required for limit orders")
            order_params["limit_price"] = limit_price

        try:
            order = self.client.submit_order(**order_params)
            print(f"SUCCESS: {side.upper()} {qty} {symbol} sent.")
            return order.id
        except Exception as e:
            print(f"FAILURE: Could not place order for {symbol}: {e}")
            return None

    ''' Circuit breaker to clear board'''
    def cancel_all_orders(self):
        self.api.cancel_all_orders()


