from __future__ import annotations

import argparse
import logging
import sys

from .bot import PolymarketArbBot, format_opportunity
from .config import load_config


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Polymarket arbitrage bot")
    parser.add_argument("market_ids", nargs="+", help="Market IDs to scan")
    parser.add_argument("--once", action="store_true", help="Run once and exit")
    parser.add_argument("--log-level", default="INFO")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    logging.basicConfig(level=getattr(logging, args.log_level.upper(), logging.INFO))
    config = load_config()
    bot = PolymarketArbBot(config)
    opportunities = bot.run_batch(args.market_ids)
    for opportunity in opportunities:
        print(format_opportunity(opportunity))
    if not opportunities:
        print("No opportunities found.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
