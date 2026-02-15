import unittest
from decimal import Decimal

from polymarket_bot.strategy import ArbitrageStrategy
from polymarket_bot.types import OrderBook, OrderBookLevel, OrderBookSide


class TestArbitrageStrategy(unittest.TestCase):
    def test_detects_positive_edge(self) -> None:
        strategy = ArbitrageStrategy(min_edge=Decimal("0.01"), max_order_size=Decimal("5"))
        orderbook = OrderBook(
            market_id="test",
            yes=OrderBookSide([OrderBookLevel(price=Decimal("0.45"), size=Decimal("10"))]),
            no=OrderBookSide([OrderBookLevel(price=Decimal("0.45"), size=Decimal("7"))]),
        )
        opportunities = list(strategy.find_opportunities(orderbook))
        self.assertEqual(len(opportunities), 1)
        self.assertEqual(opportunities[0].size, Decimal("5"))

    def test_ignores_no_edge(self) -> None:
        strategy = ArbitrageStrategy(min_edge=Decimal("0.01"), max_order_size=Decimal("5"))
        orderbook = OrderBook(
            market_id="test",
            yes=OrderBookSide([OrderBookLevel(price=Decimal("0.6"), size=Decimal("10"))]),
            no=OrderBookSide([OrderBookLevel(price=Decimal("0.4"), size=Decimal("7"))]),
        )
        opportunities = list(strategy.find_opportunities(orderbook))
        self.assertEqual(opportunities, [])


if __name__ == "__main__":
    unittest.main()
