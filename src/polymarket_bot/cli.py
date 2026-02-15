from __future__ import annotations

import argparse
import logging
import sys

from .bot import PolymarketArbBot, format_opportunity
from .client import PolymarketClientError
from .config import ConfigError, load_config


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Polymarket arbitrage bot")
    parser.add_argument("market_ids", nargs="*", help="Specific market IDs to scan")
    parser.add_argument(
        "--discover-open-markets",
        type=int,
        metavar="N",
        default=0,
        help="Discover first N open markets from Gamma API when market_ids are not passed",
    )
    parser.add_argument("--log-level", default="INFO")
    return parser.parse_args()


def _select_markets(bot: PolymarketArbBot, args: argparse.Namespace) -> list[str]:
    if args.market_ids:
        return args.market_ids
    if args.discover_open_markets <= 0:
        return []

    discovered: list[str] = []
    for market in bot.client.get_markets():
        if market.get("closed"):
            continue
        market_id = str(market.get("id", "")).strip()
        if market_id:
            discovered.append(market_id)
        if len(discovered) >= args.discover_open_markets:
            break
    return discovered


def main() -> int:
    args = parse_args()
    logging.basicConfig(level=getattr(logging, args.log_level.upper(), logging.INFO))

    try:
        config = load_config()
        bot = PolymarketArbBot(config)
        market_ids = _select_markets(bot, args)
    except (ConfigError, PolymarketClientError) as exc:
        print(f"Configuration/startup error: {exc}")
        return 2

    if not market_ids:
        print("No market IDs provided. Use positional market IDs or --discover-open-markets N.")
        return 2

    opportunities = bot.run_batch(market_ids)
    for opportunity in opportunities:
        print(format_opportunity(opportunity))
    if not opportunities:
        print("No opportunities found.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
