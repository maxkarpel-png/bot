from __future__ import annotations

import logging
from decimal import Decimal
from typing import Iterable

from .client import PolymarketClient
from .config import BotConfig
from .strategy import ArbitrageStrategy
from .types import ArbitrageOpportunity, OrderBook


logger = logging.getLogger(__name__)


class PolymarketArbBot:
    def __init__(self, config: BotConfig) -> None:
        self.config = config
        self.client = PolymarketClient(config)
        self.strategy = ArbitrageStrategy(config.min_edge, config.max_order_size)

    def scan_market(self, market_id: str) -> list[ArbitrageOpportunity]:
        orderbook = self.client.get_orderbook(market_id)
        opportunities = list(self.strategy.find_opportunities(orderbook))
        logger.info("Found %s opportunities for %s", len(opportunities), market_id)
        return opportunities

    def execute(self, opportunity: ArbitrageOpportunity) -> None:
        if self.config.dry_run:
            logger.info("Dry run: would place orders for %s", opportunity)
            return
        logger.info("Placing arbitrage orders for %s", opportunity.market_id)
        self.client.place_order(
            opportunity.market_id,
            side="yes",
            price=opportunity.yes_price,
            size=opportunity.size,
        )
        self.client.place_order(
            opportunity.market_id,
            side="no",
            price=opportunity.no_price,
            size=opportunity.size,
        )

    def run_once(self, market_id: str) -> list[ArbitrageOpportunity]:
        opportunities = self.scan_market(market_id)
        for opportunity in opportunities:
            self.execute(opportunity)
        return opportunities

    def run_batch(self, market_ids: Iterable[str]) -> list[ArbitrageOpportunity]:
        all_opportunities: list[ArbitrageOpportunity] = []
        for market_id in market_ids:
            all_opportunities.extend(self.run_once(market_id))
        return all_opportunities


def format_opportunity(opportunity: ArbitrageOpportunity) -> str:
    edge_pct = (opportunity.edge * Decimal("100")).quantize(Decimal("0.01"))
    return (
        f"market={opportunity.market_id} action={opportunity.action} "
        f"yes={opportunity.yes_price} no={opportunity.no_price} "
        f"edge={edge_pct}% size={opportunity.size}"
    )
