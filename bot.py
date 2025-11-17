import logging
import os
import ast
import operator as op
from typing import Optional

import dotenv
import requests
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")

dotenv.load_dotenv()
TOKEN = os.getenv("TOKEN")
if TOKEN is None:
    logging.critical("Variable TOKEN ausente. Abortando...")
    raise SystemExit(1)


FACT_ENDPOINT = "https://uselessfacts.jsph.pl/random.json?language=en"
LIBRETRANSLATE_ENDPOINT = "https://libretranslate.de/translate"
MYMEMORY_ENDPOINT = "https://api.mymemory.translated.net/get"
TRANSLATE_TIMEOUT = 8  # segundos
HEADERS = {
    "Accept": "application/json",
    "User-Agent": "TelegramBot/1.0 (+https://example.com)"
}

SAFE_OPS = {
    ast.Add: op.add,
    ast.Sub: op.sub,
    ast.Mult: op.mul,
    ast.Div: op.truediv,
    ast.FloorDiv: op.floordiv,
    ast.Mod: op.mod,
    ast.Pow: op.pow,
    ast.USub: op.neg,
}


# --- Reemplaza la función translate_text por esta versión robusta ---
def translate_text(text: str, source: str = "en", target: str = "es") -> str:
    # 1) LibreTranslate (POST)
    try:
        payload = {"q": text, "source": source, "target": target, "format": "text"}
        resp = requests.post(LIBRETRANSLATE_ENDPOINT, json=payload, timeout=TRANSLATE_TIMEOUT, headers=HEADERS)
        if resp.status_code == 200 and resp.content:
            try:
                data = resp.json()
                translated = data.get("translatedText") or data.get("result")  # por si cambia esquema
                if translated:
                    return translated
                logging.warning("LibreTranslate devolvió JSON válido pero sin 'translatedText'.")
            except ValueError as exc:  # JSON decode error
                logging.warning("LibreTranslate devolvió contenido no-JSON: %s", exc)
        else:
            logging.warning("LibreTranslate status=%s, len=%d", resp.status_code, len(resp.content) if resp.content else 0)
    except requests.RequestException as exc:
        logging.warning("Error conectando a LibreTranslate: %s", exc)

    # 2) MyMemory (GET) - alternativa gratuita
    try:
        params = {"q": text, "langpair": f"{source}|{target}"}
        resp = requests.get(MYMEMORY_ENDPOINT, params=params, timeout=TRANSLATE_TIMEOUT, headers=HEADERS)
        if resp.status_code == 200 and resp.content:
            try:
                data = resp.json()
                # Estructura: {"responseData": {"translatedText": "..."}, ...}
                translated = data.get("responseData", {}).get("translatedText")
                if translated:
                    return translated
                logging.warning("MyMemory devolvió JSON pero sin translatedText.")
            except ValueError as exc:
                logging.warning("MyMemory devolvió contenido no-JSON: %s", exc)
        else:
            logging.warning("MyMemory status=%s, len=%d", resp.status_code, len(resp.content) if resp.content else 0)
    except requests.RequestException as exc:
        logging.warning("Error conectando a MyMemory: %s", exc)

    # 3) Fallback: no traducción
    logging.warning("No fue posible traducir — uso el texto original.")
    return text

def fetch_random_fact() -> str:

    try:
        response = requests.get(FACT_ENDPOINT, timeout=10)
        response.raise_for_status()
        payload = response.json()
        # La API devuelve la clave 'text' con el hecho
        return payload.get("text", "No encontré ningún dato curioso.")
    except requests.RequestException as exc:
        logging.error("Fallé consultando la API: %s", exc)
        return "No puedo consultar la API por el momento."


def is_probably_spanish(text: str) -> bool:
    """
    Heurística simple: busca palabras comunes del español para evitar traducir si ya está en ES.
    No es perfecta pero evita traducciones innecesarias.
    """
    t = text.lower()
    for w in (" el ", " la ", " y ", " de ", " que ", "¡", "¿", "los ", "las ", "un ", "una "):
        if w in t:
            return True
    return False


def safe_eval(node: ast.AST) -> float:
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.Num):  # retrocompatibilidad
        return node.n
    if isinstance(node, ast.UnaryOp) and type(node.op) in SAFE_OPS:
        return SAFE_OPS[type(node.op)](safe_eval(node.operand))
    if isinstance(node, ast.BinOp) and type(node.op) in SAFE_OPS:
        left = safe_eval(node.left)
        right = safe_eval(node.right)
        return SAFE_OPS[type(node.op)](left, right)
    raise ValueError("Operación no permitida")


async def handle_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "¡Hola! Usa /curiosidad para un dato, /calc 2+2 para calcular o conversa conmigo."
    )


async def handle_fact(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    fact = fetch_random_fact()

    if is_probably_spanish(fact):
        fact_es = fact
    else:
        fact_es = translate_text(fact, source="en", target="es")
    await update.message.reply_text(fact_es)


async def handle_calc(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    expr = " ".join(context.args)
    if not expr:
        await update.message.reply_text("Indica una expresión. Ej: /calc 5 * (3 + 2)")
        return
    try:
        tree = ast.parse(expr, mode="eval")
        result = safe_eval(tree.body)
        await update.message.reply_text(f"Resultado: {result}")
    except Exception:
        await update.message.reply_text("Expresión inválida o no permitida.")


async def handle_chat(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = update.message.text.lower()
    if any(greet in text for greet in ("hola", "buenas", "hey")):
        reply = "¡Hola! ¿Cómo va todo?"
    elif "gracias" in text:
        reply = "¡De nada! ¿En qué más te ayudo?"
    elif "adiós" in text or "nos vemos" in text:
        reply = "¡Hasta luego! Aquí estaré."
    else:
        reply = "Puedo contarte curiosidades o ayudarte con cálculos simples."
    await update.message.reply_text(reply)


def run_bot() -> None:
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", handle_start))
    app.add_handler(CommandHandler("curiosidad", handle_fact))
    app.add_handler(CommandHandler("calc", handle_calc))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_chat))
    logging.info("Bot operativo. Modo escucha activado.")
    app.run_polling(poll_interval=1.0)


if __name__ == "__main__":
    run_bot()