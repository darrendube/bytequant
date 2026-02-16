import numpy as np
import pandas as pd
import sys
from src.data.db import crud
from src.exec.broker import AlpacaClient as Broker

def update_equity_curve():
    details = Broker().account_summary()
    print(details)
    crud.add_equity_point(float(details['equity']), float(details['buying_power'])/2)
    # buying power is divided by 2 because account is currently set to 2x leverage

