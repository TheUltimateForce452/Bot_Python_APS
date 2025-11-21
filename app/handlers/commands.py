from datetime import datetime

from telegram import Update
from telegram.ext import ContextTypes

from app.config import SUPPORTED_CITIES, SUPPORTED_CRYPTO
from app.services.crypto import fetch_crypto_price, resolve_crypto_choice
from app.services.facts import fetch_random_fact
from app.services.translation import is_probably_spanish, translate_text
from app.services.weather import fetch_weather_forecast, resolve_city_choice
from app.utils.math_eval import evaluate_expression


async def handle_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "¡Hola! Usa /curiosidad para datos, /calcula para operaciones, /criptomoneda para precios, "
        "/clima para pronósticos y /usuario para tus datos públicos. O simplemente conversemos :)"
    )


async def handle_fact(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    fact = fetch_random_fact()
    fact_es = fact if is_probably_spanish(fact) else translate_text(fact, source="en", target="es")
    await update.message.reply_text(fact_es)


async def handle_calc(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    expr = " ".join(context.args)
    if not expr:
        await update.message.reply_text("Indica una expresión. Ej: /calcula 5 * (3 + 2)")
        return
    try:
        result = evaluate_expression(expr)
        await update.message.reply_text(f"Resultado: {result}")
    except Exception:
        await update.message.reply_text("Expresión inválida o no permitida.")


async def handle_crypto(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.args:
        options = ", ".join(meta["label"] for meta in SUPPORTED_CRYPTO.values())
        await update.message.reply_text(
            "Usa /criptomoneda <moneda>. Opciones disponibles: " + options
        )
        return

    selection = resolve_crypto_choice(context.args[0])
    if selection is None:
        options = ", ".join(meta["label"] for meta in SUPPORTED_CRYPTO.values())
        await update.message.reply_text(
            "Moneda no soportada. Opciones: " + options
        )
        return

    price = fetch_crypto_price(selection["symbol"])
    if price is None:
        await update.message.reply_text("No pude obtener el precio ahora. Intenta más tarde.")
        return

    price_text = f"{price:,.6f}".rstrip("0").rstrip(".")
    await update.message.reply_text(
        f"{selection['label']} ({selection['symbol']}) cotiza en {price_text} USDT según Binance."
    )


async def handle_weather(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.args:
        options = ", ".join(city["label"] for city in SUPPORTED_CITIES.values())
        await update.message.reply_text(
            "Usa /clima <ciudad>. Ciudades disponibles: " + options
        )
        return

    city_query = " ".join(context.args)
    selection = resolve_city_choice(city_query)
    if selection is None:
        options = ", ".join(city["label"] for city in SUPPORTED_CITIES.values())
        await update.message.reply_text(
            "Ciudad no soportada. Usa una de: " + options
        )
        return

    forecast = fetch_weather_forecast(selection)
    if forecast is None:
        await update.message.reply_text("No pude obtener el clima ahora. Intenta nuevamente más tarde.")
        return

    current = forecast["current"]
    current_temp = current.get("temperature")
    wind = current.get("windspeed")
    local_time = current.get("time")
    if isinstance(local_time, str):
        try:
            parsed_time = datetime.fromisoformat(local_time)
            local_time = parsed_time.strftime("%d/%m %H:%M")
        except ValueError:
            pass
    lines = [
        f"Clima para ---> {selection['label']}:",
        f"Hora local ---> {local_time}" if local_time else "Hora local: N/D",
        f"Ahora ---> {current_temp}°C, viento {wind} km/h",
    ]
    if current.get("weathercode") is not None:
        lines[-1] += f", código {current['weathercode']}"

    daily_entries = forecast.get("daily", [])[:3]
    if daily_entries:
        lines.append("Pronóstico próximos días:")
        for entry in daily_entries:
            lines.append(
                f"{entry['date']}: max {entry['tmax']}°C / min {entry['tmin']}°C, lluvia {entry['precip']} mm"
            )

    await update.message.reply_text("\n".join(lines))


async def handle_userinfo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    if user is None:
        await update.message.reply_text("No pude identificar tus datos públicos, intenta nuevamente.")
        return

    username = f"@{user.username}" if user.username else "(sin usuario)"
    language = user.language_code or "desconocido"
    is_bot = "sí" if user.is_bot else "no"
    lines = [
        "Datos públicos que recibo de tu perfil:",
        f"Nombre completo: {user.full_name or 'N/D'}",
        f"Username: {username}",
        f"ID numérico: {user.id}",
        f"Idioma preferido: {language}",
        f"¿Es bot?: {is_bot}",
        f"Último nombre: {user.last_name or 'N/D'}",
    ]
    if user.first_name and user.last_name:
        lines.append(f"Nombre separado: {user.first_name} / {user.last_name}")

    await update.message.reply_text("\n".join(lines))


async def handle_chat(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = update.message.text.strip()
    lowered = text.lower()
    smalltalk = context.user_data.setdefault("smalltalk", {})
    reply: str

    greetings = ("hola", "buenas", "hey", "saludos")
    farewells = ("adiós", "nos vemos", "chao", "hasta luego")
    gratitude = ("gracias", "muchas gracias", "te agradezco")
    mood_words = {"bien": "¡Me alegra saberlo!", "mal": "Ánimo, aquí estoy para ayudarte."}

    if any(greet in lowered for greet in greetings):
        reply = "¡Hola! Qué gusto leerte. ¿En qué te puedo ayudar hoy?"
        smalltalk["last_intent"] = "greet"
    elif any(word in lowered for word in farewells):
        reply = "¡Hasta luego! Si necesitas algo más, solo envía otro mensaje."
        smalltalk["last_intent"] = "bye"
    elif any(word in lowered for word in gratitude):
        reply = "¡De nada! Siempre es un placer ayudar. ¿Algo más que quieras saber?"
        smalltalk["last_intent"] = "thanks"
    elif "cómo estás" in lowered:
        reply = "¡Listo para ayudarte las 24/7! ¿Qué tienes en mente?"
        smalltalk["last_intent"] = "status"
    elif "ayuda" in lowered or "necesito" in lowered:
        reply = (
            "Claro. Puedo darte curiosidades con /curiosidad, calcular con /calcula, precios con /criptomoneda, "
            "/clima para pronósticos o mostrar tus datos con /usuario."
        )
        smalltalk["last_intent"] = "help"
    elif lowered.endswith("?"):
        reply = "Buena pregunta. Intento tener datos, curiosidades y cálculos listos; dame más detalles y vemos."
        smalltalk["last_intent"] = "question"
    else:
        mood_response = next((msg for word, msg in mood_words.items() if word in lowered), "")
        if mood_response:
            reply = f"{mood_response} ¿Te cuento un dato curioso o hacemos un cálculo?"
            smalltalk["last_intent"] = "mood"
        else:
            last_hint = smalltalk.get("last_intent")
            if last_hint in {"greet", "help"}:
                reply = "Recordatorio: /curiosidad, /calcula, /criptomoneda, /clima y /usuario están listos cuando tú quieras."
            else:
                reply = "Puedo charlar un rato o ayudarte con comandos. ¿Qué te gustaría hacer?"
            smalltalk["last_intent"] = "idle"

    await update.message.reply_text(reply)
