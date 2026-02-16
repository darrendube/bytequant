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


if __name__ == '__main__':
    if len(sys.argv) == 1:
        load_market_data()
    signals = statarb.gen_pairs_signals()
    target_portfolio, strategy_allocation, strategy_risk_params = risk.get_target_portfolio(signals)
    success: bool = exec.execute(target_portfolio, strategy_allocation, strategy_risk_params)
    analytics.update_equity_curve()

