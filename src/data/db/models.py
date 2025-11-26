from sqlalchemy import Column, Integer, Float, String, TIMESTAMP, ForeignKey, JSON
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.sql import func

# SQLAlchemy models for the database

class Base(DeclarativeBase):
    pass

class Strategy(Base):
    __tablename__ = 'strategies'
    strategy_id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    status = Column(String, default='active')
    parameters = Column(JSON)
    started_at = Column(TIMESTAMP)

    positions = relationship("Position", back_populates="strategy")

class Position(Base):
    __tablename__ = 'positions'
    position_id = Column(Integer, primary_key=True)
    strategy_id = Column(Integer, ForeignKey('strategies.strategy_id'))
    symbol = Column(String)
    side = Column(String)
    qty = Column(Integer)
    entry_price = Column(Float)
    status = Column(String, default='active')

    strategy = relationship("Strategy", back_populates="positions")

class Order(Base):
    __tablename__ = 'orders'
    order_id = Column(Integer, primary_key=True)
    strategy_id = Column(Integer, ForeignKey('strategies.strategy_id'))
    symbol = Column(String)
    side = Column(String)
    qty = Column(Integer)
    status = Column(String)
    broker_order_id = Column(String)
    created_at = Column(TIMESTAMP, default=func.now())

    strategy = relationship("Strategy")

class Trade(Base):
    __tablename__ = 'trades'
    trade_id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey('orders.order_id'))
    strategy_id = Column(Integer, ForeignKey('strategies.strategy_id'))
    symbol = Column(String)
    qty = Column(Integer)
    price = Column(Float)
    commission = Column(Float)
    time = Column(TIMESTAMP)

    order = relationship("Order")
    strategy = relationship("Strategy")

class EquityCurve:
    __tablename__ = 'equity_curve'
    id = Column(Integer, primary_key=True)
    timestamp = Column(TIMESTAMP, default=func.now())
    total_value = Column(Float)
    cash = Column(Float)


