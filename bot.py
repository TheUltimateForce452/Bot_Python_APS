import logging
import os
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

TOKEN = os.getenv("TOKEN")
if TOKEN is None:
    logging.critical("Variable TOKEN ausente. Abortando...")
    raise SystemExit(1)

FACT_ENDPOINT = "https://uselessfacts.jsph.pl/random.json?language=en"


def fetch_random_fact() -> str:
    try:
        response = requests.get(FACT_ENDPOINT, timeout=10)
        response.raise_for_status()
        payload = response.json()
        return payload.get("text", "No encontré ningún dato curioso.")
    except requests.RequestException as exc:
        logging.error("Fallé consultando la API: %s", exc)
        return "No puedo consultar la API por el momento."


async def handle_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "¡Hola! Estoy listo. Usa /curiosidad para leer algo curioso."
    )


async def handle_fact(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    fact = fetch_random_fact()
    await update.message.reply_text(fact)


def run_bot() -> None:
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", handle_start))
    app.add_handler(CommandHandler("curiosidad", handle_fact))
    logging.info("Bot operativo. Modo escucha activado.")
    app.run_polling(poll_interval=1.0)


if __name__ == "__main__":
    run_bot()
