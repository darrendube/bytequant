from sqlalchemy import Column, Integer, Float, String, TIMESTAMP, ForeignKey, JSON
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.sql import func

import uuid
import base64

# Helper function for id/primary key generation
'''Generate a Base64-encoded UUID (22 chars in length)'''
def gen_base64_uuid():
    uid = uuid.uuid4()
    return base64.urlsafe_b64encode(uid.bytes).rstrip(b"=").decode("ascii")

# SQLAlchemy models for the database

class Base(DeclarativeBase):
    pass

class Strategy(Base):
    __tablename__ = 'strategy'
    strategy_id = Column(String(22), primary_key=True, default=gen_base64_uuid)
    name = Column(String, nullable=False)
    status = Column(String, default='active')
    parameters = Column(JSON)
    started_at = Column(TIMESTAMP, default=func.now())

    positions = relationship("Position", back_populates="strategy", cascade="all, delete-orphan")

class Position(Base):
    __tablename__ = 'position'
    position_id = Column(String(22), primary_key=True, default=gen_base64_uuid)
    strategy_id = Column(String(22), ForeignKey('strategy.strategy_id'))
    symbol = Column(String)
    side = Column(String)
    qty = Column(Integer)
    entry_price = Column(Float)
    status = Column(String, default='active')

    strategy = relationship("Strategy", back_populates="positions")

class Order(Base):
    __tablename__ = 'order'
    order_id = Column(String(22), primary_key=True, default=gen_base64_uuid)
    strategy_id = Column(String(22), ForeignKey('strategy.strategy_id'))
    symbol = Column(String)
    side = Column(String)
    qty = Column(Integer)
    status = Column(String)
    broker_order_id = Column(String)
    created_at = Column(TIMESTAMP, default=func.now())

    strategy = relationship("Strategy")

class Trade(Base):
    __tablename__ = 'trade'
    trade_id = Column(String(22), primary_key=True, default=gen_base64_uuid)
    order_id = Column(String(22), ForeignKey('order.order_id'))
    strategy_id = Column(String(22), ForeignKey('strategy.strategy_id'))
    symbol = Column(String)
    qty = Column(Integer)
    price = Column(Float)
    commission = Column(Float)
    time = Column(TIMESTAMP)

    order = relationship("Order")
    strategy = relationship("Strategy")

class EquityCurve(Base):
    __tablename__ = 'equity_curve'
    id = Column(String(22), primary_key=True, default=gen_base64_uuid)
    timestamp = Column(TIMESTAMP, default=func.now())
    total_value = Column(Float)
    cash = Column(Float)


