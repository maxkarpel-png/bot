# START HERE (Windows quick run)

1. Install **Python 3.11+**.
2. Open PowerShell in this folder.
3. Run:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .
```

4. Set credentials:

```powershell
$env:POLYMARKET_API_KEY = "your-key"
$env:POLYMARKET_API_SECRET = "your-secret"
$env:POLYMARKET_API_PASSPHRASE = "your-passphrase"
$env:POLYMARKET_DRY_RUN = "true"   # keep true for first test
```

5. Run against specific market ids:

```powershell
python -m polymarket_bot.cli MARKET_ID_1 MARKET_ID_2
```

Or discover open markets automatically:

```powershell
python -m polymarket_bot.cli --discover-open-markets 5
```

6. When dry-run output looks good, switch to live mode:

```powershell
$env:POLYMARKET_DRY_RUN = "false"
python -m polymarket_bot.cli MARKET_ID_1
```

---

# Polymarket Arbitrage Bot

This bot scans Polymarket order books and looks for a basic two-leg arbitrage where best YES + best NO is below 1.00 by at least your configured edge threshold.

## What was fixed to make this runnable

- GET requests now send no request body (common API compatibility issue).
- API/network errors return explicit messages.
- Live mode now validates required credentials before trading.
- CLI can discover open markets from Gamma when market IDs are not supplied.

## Strategy logic

1. Read best YES and NO levels from order book.
2. Compute `edge = 1 - (yes + no)`.
3. If `edge >= POLYMARKET_MIN_EDGE`, create opportunity.
4. Size is min(YES size, NO size, `POLYMARKET_MAX_ORDER_SIZE`).
5. In live mode, place YES and NO orders.

## Configuration

| Variable | Default | Purpose |
| --- | --- | --- |
| `POLYMARKET_BASE_URL` | `https://clob.polymarket.com` | CLOB base URL |
| `POLYMARKET_GAMMA_URL` | `https://gamma-api.polymarket.com` | Gamma markets API |
| `POLYMARKET_API_KEY` | unset | API key |
| `POLYMARKET_API_SECRET` | unset | API secret |
| `POLYMARKET_API_PASSPHRASE` | unset | API passphrase |
| `POLYMARKET_MIN_EDGE` | `0.01` | Min edge needed to trade |
| `POLYMARKET_MAX_ORDER_SIZE` | `10` | Cap per leg |
| `POLYMARKET_DRY_RUN` | `true` | If true, never places orders |
| `POLYMARKET_ORDERBOOK_PATH` | `/book` | Orderbook endpoint path |
| `POLYMARKET_ORDER_PATH` | `/order` | Order endpoint path |

## Verify it works

Local verification in this repo:

```bash
PYTHONPATH=src python -m unittest discover -s tests
```

Production verification on your account:

1. Keep `POLYMARKET_DRY_RUN=true` and run bot.
2. Confirm opportunities print correctly and no auth errors.
3. Change to `POLYMARKET_DRY_RUN=false` only after validating endpoint paths and credentials.

## Important notes

- This is a simple arbitrage implementation, not a full risk engine.
- Polymarket API endpoint shapes can change; if needed, update `POLYMARKET_ORDERBOOK_PATH` and `POLYMARKET_ORDER_PATH`.
- Trading is risky; test with small size first.
