import os

import dotenv


dotenv.load_dotenv()

TOKEN = os.getenv("TOKEN")
if TOKEN is None:
    raise RuntimeError("Variable TOKEN ausente. Configura la variable de entorno y reinicia el bot.")


FACT_ENDPOINT = "https://uselessfacts.jsph.pl/random.json?language=en"
LIBRETRANSLATE_ENDPOINT = "https://libretranslate.de/translate"
MYMEMORY_ENDPOINT = "https://api.mymemory.translated.net/get"
TRANSLATE_TIMEOUT = 8  # segundos
HEADERS = {
    "Accept": "application/json",
    "User-Agent": "TelegramBot/1.0 (+https://example.com)"
}
BINANCE_TICKER_ENDPOINT = "https://api.binance.com/api/v3/ticker/price"
OPEN_METEO_ENDPOINT = "https://api.open-meteo.com/v1/forecast"

SUPPORTED_CRYPTO = {
    "bitcoin": {"symbol": "BTCUSDT", "aliases": ("bitcoin", "btc"), "label": "Bitcoin"},
    "ethereum": {"symbol": "ETHUSDT", "aliases": ("ethereum", "eth"), "label": "Ethereum"},
    "pepe": {"symbol": "PEPEUSDT", "aliases": ("pepe",), "label": "Pepe"},
    "binancecoin": {"symbol": "BNBUSDT", "aliases": ("binancecoin", "bnb", "binance"), "label": "BNB"},
    "solana": {"symbol": "SOLUSDT", "aliases": ("solana", "sol"), "label": "Solana"},
    "dogecoin": {"symbol": "DOGEUSDT", "aliases": ("dogecoin", "doge"), "label": "Dogecoin"},
    "xrp": {"symbol": "XRPUSDT", "aliases": ("xrp",), "label": "XRP"},
    "cardano": {"symbol": "ADAUSDT", "aliases": ("cardano", "ada"), "label": "Cardano"},
}

SUPPORTED_CITIES = {
    "cdmx": {
        "aliases": ("ciudad de mexico", "mexico", "df"),
        "lat": 19.4326,
        "lon": -99.1332,
        "label": "CDMX",
        "timezone": "America/Mexico_City",
    },
    "ny": {
        "aliases": ("nyc", "newyork", "new york"),
        "lat": 40.7128,
        "lon": -74.006,
        "label": "NYC",
        "timezone": "America/New_York",
    },
    "paris": {
        "aliases": tuple(),
        "lat": 48.8566,
        "lon": 2.3522,
        "label": "Paris",
        "timezone": "Europe/Paris",
    },
    "barcelona": {
        "aliases": ("bcn",),
        "lat": 41.3874,
        "lon": 2.1686,
        "label": "Barcelona",
        "timezone": "Europe/Madrid",
    },
}
