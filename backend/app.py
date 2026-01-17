from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from .market_data import load_markets
from .models import Opportunity, StrategyResult
from .settings import load_settings


class OpportunityResponse(BaseModel):
    opportunities: list[Opportunity]
    best: Opportunity | None
    refresh_interval_seconds: int


settings = load_settings()
frontend_path = Path(__file__).resolve().parents[1] / "frontend"
app = FastAPI(title="Polymarket-Kalshi BTC Arbitrage Bot")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}


@app.get("/opportunities", response_model=OpportunityResponse)
async def opportunities() -> OpportunityResponse:
    snapshots = load_markets(settings)
    opportunities_list: list[Opportunity] = []

    for snapshot in snapshots:
        strategies = [
            StrategyResult(
                name="Poly Down + Kalshi Yes",
                total_cost=round(snapshot.polymarket_down_price + snapshot.kalshi_yes_price, 4),
                expected_profit=round(1 - (snapshot.polymarket_down_price + snapshot.kalshi_yes_price), 4),
            ),
            StrategyResult(
                name="Poly Up + Kalshi No",
                total_cost=round(snapshot.polymarket_up_price + snapshot.kalshi_no_price, 4),
                expected_profit=round(1 - (snapshot.polymarket_up_price + snapshot.kalshi_no_price), 4),
            ),
        ]
        best_strategy = min(strategies, key=lambda item: item.total_cost)
        opportunities_list.append(
            Opportunity(
                market=snapshot,
                strategies=strategies,
                best_strategy=best_strategy,
            )
        )

    best = min(opportunities_list, key=lambda item: item.best_strategy.total_cost) if opportunities_list else None
    return OpportunityResponse(
        opportunities=opportunities_list,
        best=best,
        refresh_interval_seconds=settings.refresh_interval_seconds,
    )
