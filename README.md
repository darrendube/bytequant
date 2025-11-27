![Status](https://img.shields.io/badge/Status-In%20Progress-orange)

# ByteQuant

### Project Overview:
ByteQuant is an autonomous trading engine designed to identify and exploit statistical arbitrage (and other) strategies in US equities.


### (Proposed) Architecture:
The trading engine will wake at a set time each day when the market is closed. Execution will then proceed through the following layers:  
1. **DATA**: Updates the local data store with market data from the previous trading session, and other non-market data that may be required by the strategies (below).
2. **STRATEGY/SIGNAL GENERATION**: Uses market and non-market data (and predefined or ML-based strategies) to generate buy/sell orders or portfolio allocation targets; sets strategy-level risk management limits.
3. **RISK MANAGEMENT**: Sets further risk limits to the orders, and ensures that portfolio-level risk limits have not been breached.
4. **EXECUTION**: Optimises orders to minimise commission, then sends orders to the broker
