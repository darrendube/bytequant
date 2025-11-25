from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class Event:
    timestamp: datetime=field(default_factory=datetime.utcnow)

@dataclass
class Tick(Event):
    symbol: str
    price: float
    volume: float

@dataclass
class Signal(Event):
    symbol: str
    side: str # BUY or SELL
    confidence: float # between 0 and 1

@dataclass
class Order(Event):
    id: str
    symbol: str
    side: str
    type: OrderType # OrderType class with other fields e.g. time in force, limit price
    qty: float

@dataclass
class Trade(Event):
    id: str
    symbol: str
    side: str
    qty: float
    fill_price: float
    fee: float = 0.0


