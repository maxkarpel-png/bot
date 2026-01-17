import json
from datetime import datetime
from pathlib import Path
from typing import Iterable

import requests

from .models import MarketSnapshot
from .settings import Settings


SAMPLE_DATA_PATH = Path(__file__).with_name("sample_data.json")


def load_sample_markets() -> list[MarketSnapshot]:
    payload = json.loads(SAMPLE_DATA_PATH.read_text())
    return [
        MarketSnapshot(
            market_id=item["market_id"],
            expiration=datetime.fromisoformat(item["expiration"].replace("Z", "+00:00")),
            strike_price=float(item["strike_price"]),
            polymarket_up_price=float(item["polymarket_up_price"]),
            polymarket_down_price=float(item["polymarket_down_price"]),
            kalshi_yes_price=float(item["kalshi_yes_price"]),
            kalshi_no_price=float(item["kalshi_no_price"]),
        )
        for item in payload.get("markets", [])
    ]


def fetch_polymarket_markets(settings: Settings) -> list[dict]:
    response = requests.get(
        settings.polymarket_markets_url,
        timeout=settings.api_timeout_seconds,
    )
    response.raise_for_status()
    payload = response.json()
    return payload.get("markets", payload)


def fetch_kalshi_markets(settings: Settings) -> list[dict]:
    response = requests.get(
        settings.kalshi_markets_url,
        timeout=settings.api_timeout_seconds,
    )
    response.raise_for_status()
    payload = response.json()
    return payload.get("markets", [])


def normalize_markets(
    polymarket_markets: Iterable[dict],
    kalshi_markets: Iterable[dict],
) -> list[MarketSnapshot]:
    snapshots: list[MarketSnapshot] = []
    kalshi_lookup = {
        market.get("ticker"): market
        for market in kalshi_markets
        if isinstance(market, dict)
    }

    for market in polymarket_markets:
        if not isinstance(market, dict):
            continue
        ticker = market.get("ticker") or market.get("id")
        kalshi_market = kalshi_lookup.get(ticker)
        if not kalshi_market:
            continue
        try:
            snapshots.append(
                MarketSnapshot(
                    market_id=str(ticker),
                    expiration=datetime.fromisoformat(
                        market.get("expiration", "1970-01-01T00:00:00Z").replace("Z", "+00:00")
                    ),
                    strike_price=float(market.get("strike_price", 0)),
                    polymarket_up_price=float(market.get("yes_price", 0.5)),
                    polymarket_down_price=float(market.get("no_price", 0.5)),
                    kalshi_yes_price=float(kalshi_market.get("yes_price", 0.5)),
                    kalshi_no_price=float(kalshi_market.get("no_price", 0.5)),
                )
            )
        except (TypeError, ValueError):
            continue

    return snapshots


def load_markets(settings: Settings) -> list[MarketSnapshot]:
    if settings.use_sample_data:
        return load_sample_markets()
    try:
        polymarket_markets = fetch_polymarket_markets(settings)
        kalshi_markets = fetch_kalshi_markets(settings)
    except requests.RequestException:
        return load_sample_markets()

    snapshots = normalize_markets(polymarket_markets, kalshi_markets)
    return snapshots or load_sample_markets()
