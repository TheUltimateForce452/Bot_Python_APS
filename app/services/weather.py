import logging
from datetime import datetime
from typing import Optional

import requests

from app.config import HEADERS, OPEN_METEO_ENDPOINT, SUPPORTED_CITIES


def resolve_city_choice(choice: str) -> Optional[dict]:
    key = choice.strip().lower()
    if not key:
        return None
    for name, meta in SUPPORTED_CITIES.items():
        if key == name or key in meta["aliases"]:
            return {**meta, "key": name}
    return None


def fetch_weather_forecast(city: dict, days: int = 3) -> Optional[dict]:
    params = {
        "latitude": city["lat"],
        "longitude": city["lon"],
        "current_weather": True,
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum",
        "forecast_days": max(1, min(days, 7)),
        "timezone": city["timezone"],
    }
    try:
        response = requests.get(OPEN_METEO_ENDPOINT, params=params, timeout=10, headers=HEADERS)
        response.raise_for_status()
        data = response.json()
        current = data.get("current_weather")
        daily = data.get("daily")
        if not current or not daily:
            logging.warning("Respuesta de clima incompleta para %s", city["label"])
            return None
        entries = []
        for day, tmax, tmin, rain in zip(
            daily.get("time", []),
            daily.get("temperature_2m_max", []),
            daily.get("temperature_2m_min", []),
            daily.get("precipitation_sum", []),
        ):
            try:
                label_date = datetime.strptime(day, "%Y-%m-%d").strftime("%d/%m")
            except ValueError:
                label_date = day
            entries.append({
                "date": label_date,
                "tmax": tmax,
                "tmin": tmin,
                "precip": rain,
            })
        return {"current": current, "daily": entries}
    except requests.RequestException as exc:
        logging.error("Error al consultar clima: %s", exc)
    except ValueError as exc:
        logging.error("Error interpretando clima: %s", exc)
    return None
