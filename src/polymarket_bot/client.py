from __future__ import annotations

import base64
import datetime as dt
import hashlib
import hmac
import json
from decimal import Decimal
from typing import Any, Dict, Iterable
import urllib.error
import urllib.parse
import urllib.request

from .config import BotConfig
from .types import OrderBook, OrderBookLevel, OrderBookSide


class PolymarketClientError(RuntimeError):
    """Raised when the Polymarket API request fails."""


class AuthSigner:
    def __init__(self, api_key: str | None, api_secret: str | None, api_passphrase: str | None) -> None:
        self.api_key = api_key
        self.api_secret = api_secret
        self.api_passphrase = api_passphrase

    def build_headers(self, method: str, path: str, body: str) -> Dict[str, str]:
        if not self.api_key or not self.api_secret or not self.api_passphrase:
            return {}

        timestamp = str(int(dt.datetime.now(tz=dt.timezone.utc).timestamp()))
        message = f"{timestamp}{method.upper()}{path}{body}".encode("utf-8")
        signature = hmac.new(self.api_secret.encode("utf-8"), message, hashlib.sha256).digest()
        signature_b64 = base64.b64encode(signature).decode("utf-8")
        return {
            "POLYMARKET-API-KEY": self.api_key,
            "POLYMARKET-API-PASSPHRASE": self.api_passphrase,
            "POLYMARKET-API-TIMESTAMP": timestamp,
            "POLYMARKET-API-SIGNATURE": signature_b64,
        }


class PolymarketClient:
    def __init__(self, config: BotConfig) -> None:
        self.config = config
        self.signer = AuthSigner(config.api_key, config.api_secret, config.api_passphrase)

    def _request(self, method: str, path: str, payload: Dict[str, Any] | None = None) -> Dict[str, Any]:
        method = method.upper()
        base_url = self.config.base_url.rstrip("/")
        normalized_path = path if path.startswith("/") else f"/{path}"
        url = f"{base_url}{normalized_path}"

        if payload is None or method == "GET":
            body = ""
            data = None
        else:
            body = json.dumps(payload)
            data = body.encode("utf-8")

        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": "polymarket-arb-bot/1.0",
        }
        headers.update(self.signer.build_headers(method, normalized_path, body))

        request = urllib.request.Request(url, method=method, headers=headers, data=data)
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                response_text = response.read().decode("utf-8")
        except urllib.error.HTTPError as exc:
            details = exc.read().decode("utf-8", errors="ignore")
            raise PolymarketClientError(f"HTTP {exc.code} for {method} {normalized_path}: {details}") from exc
        except urllib.error.URLError as exc:
            raise PolymarketClientError(f"Connection failed for {method} {normalized_path}: {exc}") from exc

        if not response_text:
            return {}

        try:
            return json.loads(response_text)
        except json.JSONDecodeError as exc:
            raise PolymarketClientError(
                f"Non-JSON response for {method} {normalized_path}: {response_text[:200]}"
            ) from exc

    def get_orderbook(self, market_id: str) -> OrderBook:
        query = urllib.parse.urlencode({"market": market_id})
        response = self._request("GET", f"{self.config.orderbook_path}?{query}")
        yes_levels = self._parse_levels(response.get("yes", []))
        no_levels = self._parse_levels(response.get("no", []))
        return OrderBook(
            market_id=market_id,
            yes=OrderBookSide(yes_levels),
            no=OrderBookSide(no_levels),
        )

    def place_order(self, market_id: str, side: str, price: Decimal, size: Decimal) -> Dict[str, Any]:
        payload = {
            "market_id": market_id,
            "side": side,
            "price": str(price),
            "size": str(size),
        }
        return self._request("POST", self.config.order_path, payload)

    def get_markets(self) -> list[dict[str, Any]]:
        url = self.config.gamma_url.rstrip("/") + "/markets"
        request = urllib.request.Request(url, headers={"Accept": "application/json"})
        with urllib.request.urlopen(request, timeout=30) as response:
            payload = json.loads(response.read().decode("utf-8"))

        if isinstance(payload, list):
            return payload
        if isinstance(payload, dict) and isinstance(payload.get("markets"), list):
            return payload["markets"]
        raise PolymarketClientError("Unexpected market payload format from Gamma API")

    @staticmethod
    def _parse_levels(levels: Iterable[Dict[str, Any]]) -> list[OrderBookLevel]:
        parsed: list[OrderBookLevel] = []
        for level in levels:
            price = Decimal(str(level.get("price", "0")))
            size = Decimal(str(level.get("size", "0")))
            if price > 0 and size > 0:
                parsed.append(OrderBookLevel(price=price, size=size))
        return parsed
