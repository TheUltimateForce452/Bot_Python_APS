# ProyectoAPS — Bot de Telegram en Python

Bot en Python que:
- Envía datos curiosos en español con `/curiosidad` (traduce automáticamente desde inglés).
- Evalúa expresiones aritméticas seguras con `/calcula`.
- Obtiene precios de criptomonedas con `/criptomoneda`.
- Muestra pronóstico del clima con `/clima`.
- Muestra tus datos públicos con `/usuario`.
- Responde de forma amistosa a mensajes de chat comunes.

Se construye con `python-telegram-bot`, usa `requests` para llamadas HTTP y `python-dotenv` para configurar el token desde `.env`. El despliegue en contenedor está preparado con un `dockerfile` multi-stage.

---

## Funcionalidades
- **`/start`**: Mensaje de bienvenida y ayuda rápida.
- **`/curiosidad`**: Usa `https://uselessfacts.jsph.pl/random.json` y traduce al español con un flujo de respaldo: primero LibreTranslate, luego MyMemory. (Ver [`app.services.translation.translate_text`](app/services/translation.py))
- **`/calcula <expresión>`**: Evalúa de forma segura expresiones numéricas: `+ - * / // % ** ()` y unario `-`. (Ver [`app.utils.math_eval.evaluate_expression`](app/utils/math_eval.py))
- **`/criptomoneda <nombre>`**: Precio spot en USDT desde Binance. Soportadas: Bitcoin, Ethereum, Pepe, BNB, Solana, Dogecoin, XRP, Cardano. (Ver [`app.services.crypto.fetch_crypto_price`](app/services/crypto.py))
  - Ejemplo: `/criptomoneda bitcoin`
- **`/clima <ciudad>`**: Pronóstico (actual y próximos días) vía Open-Meteo. Ciudades: CDMX, NYC, Paris, Barcelona. (Ver [`app.services.weather.fetch_weather_forecast`](app/services/weather.py))
  - Ejemplo: `/clima cdmx`
- **`/usuario`**: Muestra nombre, username, id y otros datos públicos del perfil de Telegram. (Ver [`app.handlers.commands.handle_userinfo`](app/handlers/commands.py))
- **Chat libre**: Intenciones básicas: saludo, despedida, agradecimiento, ayuda, estado de ánimo, preguntas genéricas (Ver [`app.handlers.commands.handle_chat`](app/handlers/commands.py)).

## Cómo funciona
- **Polling**: Usa long polling (`Application.run_polling`) (Ver [`app.app_factory.build_application`](app/app_factory.py)).
- **Traducción con fallback**: LibreTranslate (POST) → MyMemory (GET). Manejo de timeouts y formato (Ver [`app.services.translation.translate_text`](app/services/translation.py)).
- **Cálculo seguro**: AST con lista blanca de operaciones (Ver [`app.utils.math_eval.SAFE_OPS`](app/utils/math_eval.py)).
- **Criptomonedas**: Consulta directa a endpoint público de Binance (Ver [`app.services.crypto.BINANCE_TICKER_ENDPOINT`](app/services/crypto.py)).
- **Clima**: Open-Meteo con parámetros de latitud, longitud y zona horaria (Ver [`app.config.OPEN_METEO_ENDPOINT`](app/config.py)).
- **Heurística de idioma**: Evita traducir si detecta español (Ver [`app.services.translation.is_probably_spanish`](app/services/translation.py)).

## Requisitos
- Python 3.10+
- Dependencias en `requirements.txt`: `python-telegram-bot`, `requests`, `python-dotenv`.

## Configuración
Archivo `.env`:
```dotenv
TOKEN=123456789:ABCDEF_tu_token_de_telegram
```

Variables opcionales para Docker:
- `BOT_MODE` (polling | webhook) — actualmente solo se usa `polling`.
- `WEBHOOK_URL`, `WEBHOOK_PORT` — reservadas para futura implementación webhook.

## Ejemplos de uso
```
/curiosidad
/calcula 5 * (3 + 2) ** 2
/criptomoneda eth
/clima paris
/usuario
```

## Ejecución local
```pwsh
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python bot.py
```

## Docker
```pwsh
docker build -t proyectoaps .
docker run --rm --name proyectoaps --env-file .env proyectoaps
```

## Estructura
- `bot.py`: Punto de entrada.
- `app/app_factory.py`: Construcción de la aplicación Telegram.
- `app/handlers/commands.py`: Handlers de comandos y chat.
- `app/services/`: Integraciones externas (`facts`, `translation`, `crypto`, `weather`).
- `app/utils/math_eval.py`: Evaluación aritmética segura.
- `app/config.py`: Configuración y constantes.

## Solución de problemas
- Sin respuesta: revisa `TOKEN`, red, firewall.
- Traducción no ocurre: ambos servicios fallaron, se devuelve original.
- Precio/Clima vacío: puede ser fallo temporal de API.
- Expresión rechazada: operador no permitido o sintaxis inválida.

## Próximos pasos
- Modo webhook completo (TLS, validación).
- Más ciudades y criptomonedas.
- Persistencia de historial.
- Mejorar detección de idioma con librerías especializadas.
