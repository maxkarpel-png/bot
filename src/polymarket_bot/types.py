from dataclasses import dataclass
from decimal import Decimal
from typing import List


@dataclass(frozen=True)
class OrderBookLevel:
    price: Decimal
    size: Decimal


@dataclass(frozen=True)
class OrderBookSide:
    levels: List[OrderBookLevel]


@dataclass(frozen=True)
class OrderBook:
    market_id: str
    yes: OrderBookSide
    no: OrderBookSide


@dataclass(frozen=True)
class ArbitrageOpportunity:
    market_id: str
    action: str
    yes_price: Decimal
    no_price: Decimal
    edge: Decimal
    size: Decimal
