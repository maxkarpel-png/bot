from dataclasses import dataclass
import os


@dataclass(frozen=True)
class Settings:
    api_timeout_seconds: float
    use_sample_data: bool
    polymarket_markets_url: str
    kalshi_markets_url: str
    refresh_interval_seconds: int



def load_settings() -> Settings:
    return Settings(
        api_timeout_seconds=float(os.getenv("API_TIMEOUT_SECONDS", "10")),
        use_sample_data=os.getenv("USE_SAMPLE_DATA", "true").lower() == "true",
        polymarket_markets_url=os.getenv(
            "POLYMARKET_MARKETS_URL",
            "https://clob.polymarket.com/markets",
        ),
        kalshi_markets_url=os.getenv(
            "KALSHI_MARKETS_URL",
            "https://trading-api.kalshi.com/trade-api/v2/markets",
        ),
        refresh_interval_seconds=int(os.getenv("REFRESH_INTERVAL_SECONDS", "2")),
    )
