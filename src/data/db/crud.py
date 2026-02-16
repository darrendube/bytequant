from src.data.db.session import SessionLocal
from src.data.db.models import Strategy, Position, Order, Trade, EquityCurve, StrategyAllocation

# session manager wrapper function
def _with_session(crud_func):
    def session_wrapper(*args, **kwargs):
        db_session = SessionLocal()
        try:
            result = crud_func(db_session, *args, **kwargs)
            db_session.commit()
            return result
        except:
            db_session.rollback()
            raise
        finally:
            db_session.close()
    return session_wrapper

### STRATEGY CRUD ###
@_with_session
def create_strategy(db_session, strategy_id=None, name=None, status=None, parameters=None):
    # build dict of fields
    fields = {}
    if strategy_id is not None:
        fields['strategy_id'] = strategy_id
    if name is not None:
        fields['name'] = name
    if status is not None:
        fields['status'] = status
    if parameters is not None:
        fields['parameters'] = parameters

    # add to session
    strategy = Strategy(**fields)
    db_session.add(strategy)
    db_session.flush()  # optional: ensure DB assigns defaults like timestamp

    return strategy

@_with_session
def get_strategies(db_session, strategy_id=None):
    query = db_session.query(Strategy)
    if strategy_id:
        return query.filter(Strategy.strategy_id == strategy_id).first()
    return query.all()


### POSITION CRUD ###
@_with_session
def create_position(db_session, symbol, side, qty, entry_price, status=None, position_id=None):
    # build dict of fields
    fields = {'symbol': symbol, 'side': side, 'qty': qty, 'entry_price': entry_price}
    if position_id is not None: fields['position_id'] = position_id
    if status is not None: fields['status'] = status

    # add to session
    position = Position(**fields)
    db_session.add(position)
    db_session.flush()  # optional: ensure DB assigns defaults like timestamp

    return position

@_with_session
def get_positions(db_session, position_id=None, symbol=None, side=None, status=None):
    query = db_session.query(Position)
    if position_id: query = query.filter(Position.position_id == position_id)
    if symbol: query = query.filter(Position.symbol == symbol)
    if side: query = query.filter(Position.side == side)
    if status: query = query.filter(Position.status == status)
    return query.all()


### ORDER CRUD ###
@_with_session
def create_order(db_session, symbol, side, qty, broker_order_id=None, order_id=None, status=None):
    fields = {'symbol': symbol, 'side': side, 'qty': qty}
    if order_id is not None: fields['order_id'] = order_id
    if broker_order_id is not None: fields['broker_order_id'] = broker_order_id
    if status is not None: fields['status'] = status

    order = Order(**fields)
    db_session.add(order)
    db_session.flush()
    return order

@_with_session
def get_orders(db_session, order_id=None, broker_order_id=None, symbol=None, side=None, status=None):
    query = db_session.query(Order)
    if symbol: query = query.filter(Order.symbol == symbol)
    if side: query = query.filter(Order.side == side)
    if status: query = query.filter(Order.status == status)
    if order_id: query = query.filter(Order.order_id == order_id)
    if broker_order_id: query = query.filter(Order.broker_order_id == broker_order_id)
    return query.all()


### TRADE CRUD ###
@_with_session
def create_trade(db_session, order_id, symbol, qty, price, commission=None, trade_id=None):
    fields = {"order_id": order_id, 'symbol': symbol, 'qty': qty, 'price': price}
    if trade_id is not None: fields['trade_id'] = trade_id
    if commission is not None: fields['commission'] = commission

    trade = Trade(**fields)
    db_session.add(trade)
    db_session.flush()
    return trade

@_with_session
def get_trades(db_session, order_id=None, trade_id=None, symbol=None):
    query = db_session.query(Trade)
    if order_id: query = query.filter(Trade.order_id == order_id)
    if symbol: query = query.filter(Trade.symbol == symbol)
    if trade_id: query = query.filter(Trade.trade_id == trade_id)
    return query.all()


### STRATEGY ALLOCATION CRUD ###
@_with_session
def allocate_order_to_strategy(db_session, strategy_id, order_id, target_qty):
    fields = {'strategy_id': strategy_id, 'order_id': order_id, 'target_qty': target_qty}
    allocation = StrategyAllocation(**fields)
    db_session.add(allocation)
    db_session.flush()
    return allocation

@_with_session
def allocate_trade_to_strategy(db_session, allocation_id, filled_qty):
    allocation = session.get(StrategyAllocation, allocation_id)
    allocation.filled_qty = filled_qty
    db_session.commit()

@_with_session
def get_allocations_by_order_id(db_session, order_id, unfilled=True):
    query = db_session.query(StrategyAllocation).where(StrategyAllocation.order_id == order_id)
    if unfilled: query = query.where(StrategyAllocation.filled_qty.is_(None))
    return query.all()


### EQUITY CURVE CRUD ###
@_with_session
def add_equity_point(db_session, total_value, cash, eq_id=None):
    fields = {'total_value':total_value, 'cash': cash}
    if eq_id is not None: fields['id'] = eq_id

    eq = EquityCurve(**fields)
    db_session.add(eq)
    db_session.flush()
    return eq

@_with_session
def get_equity_curve(db_session):
    return db_session.query(EquityCurve).order_by(EquityCurve.timestamp).all()
