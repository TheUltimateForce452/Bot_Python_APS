import logging
from typing import Optional

import requests

from app.config import BINANCE_TICKER_ENDPOINT, HEADERS, SUPPORTED_CRYPTO


def resolve_crypto_choice(choice: str) -> Optional[dict]:
    key = choice.strip().lower()
    for name, meta in SUPPORTED_CRYPTO.items():
        if key == name or key in meta["aliases"]:
            return {**meta, "key": name}
    return None


def fetch_crypto_price(symbol: str) -> Optional[float]:
    params = {"symbol": symbol.upper()}
    try:
        response = requests.get(BINANCE_TICKER_ENDPOINT, params=params, timeout=8, headers=HEADERS)
        response.raise_for_status()
        data = response.json()
        price_raw = data.get("price")
        if price_raw is None:
            logging.warning("Binance sin precio para %s", symbol)
            return None
        return float(price_raw)
    except (requests.RequestException, ValueError, TypeError) as exc:
        logging.error("Error al consultar precio %s: %s", symbol, exc)
        return None
