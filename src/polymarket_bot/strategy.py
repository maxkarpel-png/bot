from __future__ import annotations

from decimal import Decimal
from typing import Iterable

from .types import ArbitrageOpportunity, OrderBook


class ArbitrageStrategy:
    def __init__(self, min_edge: Decimal, max_order_size: Decimal) -> None:
        self.min_edge = min_edge
        self.max_order_size = max_order_size

    def find_opportunities(self, orderbook: OrderBook) -> Iterable[ArbitrageOpportunity]:
        if not orderbook.yes.levels or not orderbook.no.levels:
            return []

        best_yes = orderbook.yes.levels[0]
        best_no = orderbook.no.levels[0]
        total_price = best_yes.price + best_no.price
        edge = Decimal("1") - total_price
        if edge < self.min_edge:
            return []

        size = min(best_yes.size, best_no.size, self.max_order_size)
        if size <= 0:
            return []

        return [
            ArbitrageOpportunity(
                market_id=orderbook.market_id,
                action="buy_yes_and_no",
                yes_price=best_yes.price,
                no_price=best_no.price,
                edge=edge,
                size=size,
            )
        ]
