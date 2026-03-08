from src.strategy import (statarb, )
from src.risk import risk
from src.exec import exec
from src.analytics import analytics
from src.data.market import load_market_data
from src.data.db import crud
from src.data.db.models import Base
from src.data.db.session import engine
from dotenv import load_dotenv
import sys

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

# running modes
# 0: normal mode - load data, gen orders, execute, etc
# 1: logging/DB update mode - run only to update DB tables (esp. Position after orders have been filled) + analytics (maybe) - no trading
# 2: test mode - run normally but without updating local historical data store - ONLY FOR TESTING


if __name__ == '__main__':
    if len(sys.argv) == 1 or sys.argv[1] not in ["0", "1", "2"]:
        sys.exit("Missing mode argument: " \
        "\n\t0: normal mode " \
        "\n\t1: logging/DB update mode " \
        "\n\t2: test mode (runs normally but without loading price data first)"
        "\n\nExample: python3 -m src.main 0\n")
    
    if sys.argv[1] == "1":
        print('updating filled orders')
        analytics.update_filled_orders()
        # TODO: some logging mode of some sort

    if sys.argv[1] == "0":
        load_market_data()
    
    if sys.argv[1] in ["0", "2"]:    
        signals = statarb.gen_pairs_signals()
        target_portfolio, strategy_allocation, strategy_risk_params = risk.get_target_portfolio(signals)
        success: bool = exec.execute(target_portfolio, strategy_allocation, strategy_risk_params)
        analytics.update_equity_curve()

    sys.exit(0)

