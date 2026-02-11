# Polymarket Arbitrage Bot

This project provides a configurable Polymarket arbitrage bot that scans markets and places paired YES/NO orders when it detects a positive edge (YES price + NO price < 1). It is designed to run locally on Windows or any system with Python 3.11+.

> **Important**: You must configure valid Polymarket API credentials and confirm the correct CLOB endpoints for your account. This repository does not ship credentials and cannot verify live trading in this environment.

## Features

- Scans one or more market IDs for basic YES/NO arbitrage
- Dry-run mode enabled by default for safety
- Configurable thresholds and order sizing
- Minimal dependencies (stdlib only)

## Requirements

- Python 3.11+
- Polymarket API credentials (API key, secret, passphrase)

## Setup (Windows)

1. Download the repository and open a terminal in the repo folder.
2. Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

3. Configure environment variables (PowerShell example):

```powershell
$env:POLYMARKET_API_KEY = "your-api-key"
$env:POLYMARKET_API_SECRET = "your-api-secret"
$env:POLYMARKET_API_PASSPHRASE = "your-api-passphrase"
$env:POLYMARKET_DRY_RUN = "true"
```

4. Run the bot:

```powershell
pip install -e .
python -m polymarket_bot.cli MARKET_ID_1 MARKET_ID_2
```

## Configuration

| Variable | Default | Purpose |
| --- | --- | --- |
| `POLYMARKET_BASE_URL` | `https://clob.polymarket.com` | CLOB base URL |
| `POLYMARKET_GAMMA_URL` | `https://gamma-api.polymarket.com` | Market metadata API |
| `POLYMARKET_API_KEY` | `(required)` | API key |
| `POLYMARKET_API_SECRET` | `(required)` | API secret |
| `POLYMARKET_API_PASSPHRASE` | `(required)` | API passphrase |
| `POLYMARKET_MIN_EDGE` | `0.01` | Minimum edge to trade |
| `POLYMARKET_MAX_ORDER_SIZE` | `10` | Max size per leg |
| `POLYMARKET_DRY_RUN` | `true` | Skip order placement |
| `POLYMARKET_ORDERBOOK_PATH` | `/book` | Order book endpoint path |
| `POLYMARKET_ORDER_PATH` | `/order` | Order placement endpoint path |

> **Note**: Endpoint paths and authentication signing vary by Polymarket API version. Verify these values against the official CLOB API documentation for your account.

## How it works

1. The bot requests the order book for a given market ID.
2. It looks at the best YES and NO ask prices.
3. If `YES + NO < 1 - min_edge`, it considers the spread an arbitrage edge.
4. When not in dry-run mode, it submits paired YES/NO orders sized by the smaller of the two best-level quantities and `POLYMARKET_MAX_ORDER_SIZE`.

## Verification

Because this environment cannot access Polymarket with credentials, you should validate with a dry run first:

```powershell
$env:POLYMARKET_DRY_RUN = "true"
python -m polymarket_bot.cli MARKET_ID
```

Then set `POLYMARKET_DRY_RUN` to `false` after confirming:

- Market IDs are correct.
- Order book endpoint and auth signing match Polymarket documentation.
- Your account has sufficient funds and permissions.

## Disclaimer

Trading involves financial risk. This repository is provided for educational purposes and **does not** guarantee profitability or connectivity without proper configuration.
