"""
client.py
Low-level Binance Spot Test Network REST client.

- Signs requests with HMAC-SHA256.
- Targets https://testnet.binance.vision (Spot Testnet)
- API key and secret are read from environment variables (loaded from .env).

Endpoints used (Binance Spot API /api/v3):
  POST /api/v3/order   — place a new order
  GET  /api/v3/ping    — connectivity check (no auth required)
"""

import hashlib
import hmac
import os
import time
from typing import Any, Dict, Optional
from urllib.parse import urlencode

import requests
from dotenv import load_dotenv

load_dotenv()

from bot.logging_config import setup_logger

logger = setup_logger("trading_bot.client")

TESTNET_BASE_URL = "https://testnet.binance.vision"
ORDER_ENDPOINT   = "/api/v3/order"
PING_ENDPOINT    = "/api/v3/ping"

RECV_WINDOW = 5000


class BinanceFuturesClientError(Exception):
    """Raised for Binance API-level errors (HTTP 4xx / error JSON)."""


class BinanceFuturesClient:
    """
    Binance Spot Test Network REST client.

    Reads credentials from environment variables (or .env file):
        BINANCE_API_KEY    — your testnet API key
        BINANCE_API_SECRET — your testnet API secret
    """

    def __init__(self) -> None:
        self.api_key    = os.environ.get("BINANCE_API_KEY", "").strip()
        self.api_secret = os.environ.get("BINANCE_API_SECRET", "").strip()

        if not self.api_key or not self.api_secret:
            raise EnvironmentError(
                "BINANCE_API_KEY and BINANCE_API_SECRET must be set "
                "as environment variables (or in a .env file)."
            )

        self.session = requests.Session()
        self.session.headers.update({
            "X-MBX-APIKEY": self.api_key,
            "Content-Type": "application/x-www-form-urlencoded",
        })
        logger.debug("BinanceFuturesClient initialised (key=...%s)", self.api_key[-6:])

    # ── Signing ──────────────────────────────────────────────────────────────

    def _sign(self, params: Dict[str, Any]) -> str:
        """Return HMAC-SHA256 hex signature for the given param dict."""
        query_string = urlencode(params)
        return hmac.new(
            self.api_secret.encode("utf-8"),
            query_string.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

    # ── HTTP helpers ─────────────────────────────────────────────────────────

    def _post(self, endpoint: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Add timestamp + recvWindow, sign, POST to the Spot Testnet.
        Logs request (signature redacted) and full response.
        Raises BinanceFuturesClientError on API or HTTP errors.
        """
        params["timestamp"]  = int(time.time() * 1000)
        params["recvWindow"] = RECV_WINDOW
        params["signature"]  = self._sign(params)

        url = TESTNET_BASE_URL + endpoint

        safe_params = {k: v for k, v in params.items() if k != "signature"}
        logger.debug("POST %s | params=%s", endpoint, safe_params)

        try:
            response = self.session.post(url, data=params, timeout=10)
        except requests.exceptions.ConnectionError as exc:
            logger.error("Network error connecting to Binance Testnet: %s", exc)
            raise
        except requests.exceptions.Timeout:
            logger.error("Request to %s timed out.", url)
            raise

        logger.debug("HTTP %s | response: %s", response.status_code, response.text[:800])

        try:
            data = response.json()
        except ValueError:
            response.raise_for_status()
            raise BinanceFuturesClientError(
                f"Non-JSON response (HTTP {response.status_code}): {response.text}"
            )

        if response.status_code != 200:
            code = data.get("code", response.status_code)
            msg  = data.get("msg", response.text)
            logger.error("Binance API error %s: %s", code, msg)
            raise BinanceFuturesClientError(f"Binance error {code}: {msg}")

        return data

    # ── Public methods ───────────────────────────────────────────────────────

    def ping(self) -> bool:
        """Return True if the Binance Spot Testnet is reachable (returns HTTP 200 + {})."""
        try:
            resp = self.session.get(TESTNET_BASE_URL + PING_ENDPOINT, timeout=5)
            return resp.status_code == 200
        except requests.exceptions.ConnectionError as exc:
            logger.error("Ping connection error: %s", exc)
            return False
        except Exception as exc:
            logger.error("Ping failed unexpectedly: %s", exc)
            return False

    def place_order(
        self,
        symbol: str,
        side: str,
        order_type: str,
        quantity: str,
        price: Optional[str] = None,
        time_in_force: str = "GTC",
    ) -> Dict[str, Any]:
        """
        Place a MARKET or LIMIT order on Binance Spot Testnet.

        Parameters
        ----------
        symbol        : e.g. "BTCUSDT"
        side          : "BUY" or "SELL"
        order_type    : "MARKET" or "LIMIT"
        quantity      : order quantity as a string
        price         : required for LIMIT; must be omitted for MARKET
        time_in_force : used only for LIMIT orders (default "GTC")
                        Accepted values per Binance Spot docs: GTC, IOC, FOK

        Returns the raw Binance order response dict.
        """
        params: Dict[str, Any] = {
            "symbol":   symbol,
            "side":     side,
            "type":     order_type,
            "quantity": quantity,
        }

        if order_type == "LIMIT":
            if price is None:
                raise ValueError("price is required for LIMIT orders.")
            params["price"]       = price
            params["timeInForce"] = time_in_force

        return self._post(ORDER_ENDPOINT, params)
