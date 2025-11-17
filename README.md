# ProyectoAPS — Bot de Telegram en Python

Bot sencillo en Python que:
- Envía datos curiosos en español con `/curiosidad` (traduce automáticamente desde inglés).
- Evalúa expresiones aritméticas seguras con `/calc`.
- Responde de forma amistosa a mensajes de chat comunes.

Se construye con `python-telegram-bot`, usa `requests` para llamadas HTTP y `python-dotenv` para configurar el token desde `.env`. El despliegue en contenedor está preparado con un `dockerfile` multi-stage.

---

## Funcionalidades
- **`/start`:** Mensaje de bienvenida y ayuda rápida.
- **`/curiosidad`:** Obtiene un hecho aleatorio desde `https://uselessfacts.jsph.pl/random.json` (en inglés) y lo traduce al español. La traducción intenta primero **LibreTranslate** (`https://libretranslate.de/translate`) y, si falla, **MyMemory** (`https://api.mymemory.translated.net/get`). Si ambas fallan, devuelve el hecho original en inglés. Incluye una heurística simple para evitar traducir si el texto ya está en español.
- **`/calc <expresión>`:** Evalúa de forma segura expresiones con números y operadores aritméticos: `+`, `-`, `*`, `/`, `//`, `%`, `**`, paréntesis y el unario `-`. No permite variables ni funciones (usa AST con una lista blanca de operaciones).
- **Chat libre:** Respuestas básicas a saludos (“hola”), agradecimientos (“gracias”) y despedidas.

## Cómo funciona
- **Long polling:** El bot usa long polling con `python-telegram-bot` (no requiere exponer puertos). El `dockerfile` incluye variables para un modo webhook, pero el código actual solo utiliza polling.
- **Traducción robusta:** `translate_text` intenta LibreTranslate (POST JSON) y, si falla, MyMemory (GET). Se manejan timeouts, errores de red y respuestas no-JSON.
- **Cálculo seguro:** Se parsea la expresión con `ast.parse(..., mode="eval")` y se evalúa únicamente con operadores permitidos.

## Requisitos
- **Python:** 3.10+ (la imagen Docker usa 3.12-slim).
- **Dependencias:** listadas en `requirements.txt`:
  - `python-telegram-bot`
  - `requests`
  - `python-dotenv`

## Configuración
- Crea un archivo `.env` con:
  
  ```dotenv
  TOKEN=123456789:ABCDEF_tu_token_de_telegram
  ```

- Alternativamente, en PowerShell puedes exportarlo temporalmente:
  
  ```pwsh
  $env:TOKEN = "123456789:ABCDEF_tu_token_de_telegram"
  ```

Nunca compartas tu token ni lo subas a repos públicos. Si se filtra, revócalo en @BotFather.

## Ejecución local (Windows PowerShell)
```pwsh
# 1) Crear entorno
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 2) Instalar dependencias
pip install -r requirements.txt

# 3) Configurar variables (usa .env o exporta TOKEN)
#    Si usas .env, no necesitas exportar nada aquí

# 4) Ejecutar el bot
python bot.py
```

## Docker
- **Construir imagen:**
  ```pwsh
  docker build -t proyectoaps .
  ```

- **Ejecutar con .env (recomendado):**
  ```pwsh
  docker run --rm --name proyectoaps --env-file .env proyectoaps
  ```


## Estructura del proyecto
- `bot.py`: Lógica del bot (handlers, traducción, cálculo seguro).
- `requirements.txt`: Dependencias de Python.
- `dockerfile`: Build multi-stage para imagen ligera de producción.
- `.dockerignore`: Excluye artefactos locales del build context.
- `.env` (local, no subir): Token del bot.
- `.env.example`: Plantilla de configuración.

## Solución de problemas
- **ImportError: No module named 'dotenv'**: instala `python-dotenv` o vuelve a `pip install -r requirements.txt`.
- **El bot no responde**: verifica `TOKEN`, conexión a Internet o restricciones de firewall/proxy.
- **Traducción en inglés**: puede deberse a límites/caídas de los servicios de traducción; el bot retorna el texto original como respaldo.
- **Healthcheck en Docker**: en polling siempre pasa; si pones `BOT_MODE=webhook` sin implementar webhook, el healthcheck puede fallar.

## Próximos pasos (ideas)
- Implementar modo webhook con TLS y validación.
- Añadir más intenciones de chat y comandos.
- Mejorar detección de idioma y fallback de traducción.
