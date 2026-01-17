# Polymarket-Kalshi BTC Arbitrage Bot (Starter)

This repository is a ready-to-run, self-contained version of the Polymarket/Kalshi BTC arbitrage monitor. It ships with:

- A FastAPI backend that calculates arbitrage opportunities.
- A static frontend dashboard served directly by the backend.
- Sample data fallback so the app runs without API keys.

## Quick Start (From Scratch)

### 1) Clone and enter the repo

```bash
git clone https://github.com/CarlosIbCu/polymarket-kalshi-btc-arbitrage-bot.git
cd polymarket-kalshi-btc-arbitrage-bot
```

### 2) Create a virtual environment (recommended)

```bash
python -m venv .venv
```

**Activate (macOS/Linux):**

```bash
source .venv/bin/activate
```

**Activate (Windows PowerShell):**

```powershell
.venv\Scripts\Activate.ps1
```

**Activate (Windows CMD):**

```bat
.venv\Scripts\activate.bat
```

### 3) Install backend dependencies

```bash
pip install -r backend/requirements.txt
```

### 4) Run the API + dashboard

```bash
python -m uvicorn backend.app:app --reload
```

Now open `http://localhost:8000` to view the dashboard.

## Configuration

By default, the app loads `backend/sample_data.json`. To fetch live market data instead:

```bash
export USE_SAMPLE_DATA=false
```

**Windows PowerShell:**

```powershell
$env:USE_SAMPLE_DATA = "false"
```

**Windows CMD:**

```bat
set USE_SAMPLE_DATA=false
```

Optional environment variables:

- `POLYMARKET_MARKETS_URL` (default: `https://clob.polymarket.com/markets`)
- `KALSHI_MARKETS_URL` (default: `https://trading-api.kalshi.com/trade-api/v2/markets`)
- `API_TIMEOUT_SECONDS` (default: `10`)
- `REFRESH_INTERVAL_SECONDS` (default: `2`)

> Note: Kalshi endpoints often require authentication. If the live API fails, the app automatically falls back to sample data.

## Windows Troubleshooting

- If you see `'export' is not recognized`, use the PowerShell or CMD commands above.
- If you see `Could not import module "backend.app"`, make sure you are in the repo root and run:

```bat
python -m uvicorn backend.app:app --reload
```

## Project Layout

```
backend/
  app.py            # FastAPI app + arbitrage math
  market_data.py    # Data ingestion + normalization
  models.py         # Response schemas
  sample_data.json  # Offline fallback
  settings.py       # Environment settings
frontend/
  index.html
  app.js
  styles.css
```

## How the Bot Works

1. **Load markets** from Polymarket + Kalshi (or sample data).
2. **Normalize prices** into a shared snapshot per hourly market.
3. **Compute strategies**:
   - Poly Down + Kalshi Yes
   - Poly Up + Kalshi No
4. **Highlight best opportunity** based on lowest total cost.

## Development Tips

- Update `backend/sample_data.json` to simulate specific scenarios.
- Adjust `REFRESH_INTERVAL_SECONDS` for UI refresh speed.

## License

MIT
