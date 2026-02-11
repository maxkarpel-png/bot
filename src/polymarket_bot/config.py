from dataclasses import dataclass
from decimal import Decimal
import os


@dataclass(frozen=True)
class BotConfig:
    base_url: str
    gamma_url: str
    api_key: str | None
    api_secret: str | None
    api_passphrase: str | None
    min_edge: Decimal
    max_order_size: Decimal
    dry_run: bool
    orderbook_path: str
    order_path: str


def load_config() -> BotConfig:
    return BotConfig(
        base_url=os.getenv("POLYMARKET_BASE_URL", "https://clob.polymarket.com"),
        gamma_url=os.getenv("POLYMARKET_GAMMA_URL", "https://gamma-api.polymarket.com"),
        api_key=os.getenv("POLYMARKET_API_KEY"),
        api_secret=os.getenv("POLYMARKET_API_SECRET"),
        api_passphrase=os.getenv("POLYMARKET_API_PASSPHRASE"),
        min_edge=Decimal(os.getenv("POLYMARKET_MIN_EDGE", "0.01")),
        max_order_size=Decimal(os.getenv("POLYMARKET_MAX_ORDER_SIZE", "10")),
        dry_run=os.getenv("POLYMARKET_DRY_RUN", "true").lower() == "true",
        orderbook_path=os.getenv("POLYMARKET_ORDERBOOK_PATH", "/book"),
        order_path=os.getenv("POLYMARKET_ORDER_PATH", "/order"),
    )
