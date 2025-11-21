import logging

import requests

from app.config import FACT_ENDPOINT


def fetch_random_fact() -> str:
    try:
        response = requests.get(FACT_ENDPOINT, timeout=10)
        response.raise_for_status()
        payload = response.json()
        return payload.get("text", "No encontré ningún dato curioso.")
    except requests.RequestException as exc:
        logging.error("Fallé consultando la API: %s", exc)
        return "No puedo consultar la API por el momento."
