from src.strategy import (statarb, )
from src.risk import risk
from src.exec import exec
from src.analytics import analytics
from src.data.market import load_market_data
from src.data.db import crud
from src.data.db.models import Base
from src.data.db.session import engine
from dotenv import load_dotenv
import argparse

# load env vars
load_dotenv()

# db setup
Base.metadata.create_all(bind=engine)

# On a high level:
#  1. update local historical data
#  2. run (one or multiple) strategy modules
#  3. send output of strategies (confidence weights) to risk module
#  4. send output of risk (target portfolio) to exec module (which sends orders to brokers)
#  5. some logging for analytics along the way

def main():
    parser = argparse.ArgumentParser(description="ByteQuant Trading Engine")
    parser.add_argument(
        "mode",
        choices=["normal", "logging", "test"],
        help="Operating mode: normal (full run), logging (update DB), test (skip data load)"
    )
    args = parser.parse_args()

    if args.mode == "logging":
        print("Updating filled orders...")
        analytics.update_filled_orders()
        print("Logging update complete.")

    if args.mode == "normal":
        print("Loading market data...")
        load_market_data()
        print("Market data loaded.")
    
    if args.mode in ["normal", "test"]:    
        print("Generating trading signals...")
        signals = statarb.gen_pairs_signals()
        print("Calculating target portfolio...")
        target_portfolio, strategy_allocation, strategy_risk_params = risk.get_target_portfolio(signals)
        print("Executing orders...")
        success: bool = exec.execute(target_portfolio, strategy_allocation, strategy_risk_params)
        print("Updating analytics...")
        analytics.update_equity_curve()
        print("Run complete.")

if __name__ == '__main__':
    main()

