from datetime import datetime
from pydantic import BaseModel


class MarketSnapshot(BaseModel):
    market_id: str
    expiration: datetime
    strike_price: float
    polymarket_up_price: float
    polymarket_down_price: float
    kalshi_yes_price: float
    kalshi_no_price: float


class StrategyResult(BaseModel):
    name: str
    total_cost: float
    expected_profit: float


class Opportunity(BaseModel):
    market: MarketSnapshot
    strategies: list[StrategyResult]
    best_strategy: StrategyResult
