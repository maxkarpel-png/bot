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


class ConfigError(ValueError):
    """Raised for invalid bot configuration."""


def _to_bool(value: str) -> bool:
    normalized = value.strip().lower()
    return normalized in {"1", "true", "yes", "on"}


def load_config() -> BotConfig:
    config = BotConfig(
        base_url=os.getenv("POLYMARKET_BASE_URL", "https://clob.polymarket.com"),
        gamma_url=os.getenv("POLYMARKET_GAMMA_URL", "https://gamma-api.polymarket.com"),
        api_key=os.getenv("POLYMARKET_API_KEY"),
        api_secret=os.getenv("POLYMARKET_API_SECRET"),
        api_passphrase=os.getenv("POLYMARKET_API_PASSPHRASE"),
        min_edge=Decimal(os.getenv("POLYMARKET_MIN_EDGE", "0.01")),
        max_order_size=Decimal(os.getenv("POLYMARKET_MAX_ORDER_SIZE", "10")),
        dry_run=_to_bool(os.getenv("POLYMARKET_DRY_RUN", "true")),
        orderbook_path=os.getenv("POLYMARKET_ORDERBOOK_PATH", "/book"),
        order_path=os.getenv("POLYMARKET_ORDER_PATH", "/order"),
    )
    validate_config(config)
    return config


def validate_config(config: BotConfig) -> None:
    if config.min_edge < 0:
        raise ConfigError("POLYMARKET_MIN_EDGE must be >= 0")
    if config.max_order_size <= 0:
        raise ConfigError("POLYMARKET_MAX_ORDER_SIZE must be > 0")
    if not config.dry_run:
        missing = [
            name
            for name, value in {
                "POLYMARKET_API_KEY": config.api_key,
                "POLYMARKET_API_SECRET": config.api_secret,
                "POLYMARKET_API_PASSPHRASE": config.api_passphrase,
            }.items()
            if not value
        ]
        if missing:
            raise ConfigError(
                "Live mode requires API credentials. Missing: " + ", ".join(missing)
            )
