import logging

from telegram.ext import Application, CommandHandler, MessageHandler, filters

from app.config import TOKEN
from app.handlers.commands import (
    handle_calc,
    handle_chat,
    handle_crypto,
    handle_fact,
    handle_start,
    handle_userinfo,
    handle_weather,
)


def build_application() -> Application:
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", handle_start))
    app.add_handler(CommandHandler("curiosidad", handle_fact))
    app.add_handler(CommandHandler("calcula", handle_calc))
    app.add_handler(CommandHandler("criptomoneda", handle_crypto))
    app.add_handler(CommandHandler("clima", handle_weather))
    app.add_handler(CommandHandler("usuario", handle_userinfo))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_chat))
    logging.info("Bot operativo. Modo escucha activado.")
    return app
