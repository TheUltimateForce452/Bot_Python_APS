## Dockerfile para ProyectoAPS (Bot de Telegram con Python)
# Usa la sintaxis avanzada (BuildKit) si está disponible.
# Puedes habilitar BuildKit al construir: DOCKER_BUILDKIT=1 docker build -t proyectoaps .
# syntax=docker/dockerfile:1.7

# Etapa builder: instala dependencias y prepara artefactos.
ARG PYTHON_VERSION=3.12-slim
FROM python:${PYTHON_VERSION} AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
	PIP_NO_CACHE_DIR=on \
	PYTHONUNBUFFERED=1

WORKDIR /app

# Copiamos SOLO requirements.txt primero para aprovechar la cache de dependencias.
COPY requirements.txt ./

# Instalación de dependencias
RUN --mount=type=cache,target=/root/.cache/pip \
	set -eux; \
	pip install -r requirements.txt

# Copiamos el resto del código fuente.
COPY . .

# (Opcional) Test rápido de sintaxis del bot para fallar pronto en build
# RUN python -m pyflakes . || true

# (Opcional) Ejecuta pasos de build de la app, por ejemplo recopilar estáticos.
# RUN python manage.py collectstatic --noinput || echo "Sin collectstatic"

### Etapa final de runtime ###
FROM python:${PYTHON_VERSION} AS runtime

LABEL org.opencontainers.image.title="ProyectoAPS" \
	  org.opencontainers.image.description="Imagen de producción de ProyectoAPS" \
	  org.opencontainers.image.source="https://example.com/proyectoaps" \
	  org.opencontainers.image.licenses="MIT"

ENV PYTHONDONTWRITEBYTECODE=1 \
	PYTHONUNBUFFERED=1 \
	# Modo de operación: polling o webhook (el token se pasa SOLO al ejecutar, no aquí)
	BOT_MODE=polling \
	# Solo si usas webhook
	WEBHOOK_URL="" \
	WEBHOOK_PORT=8443

WORKDIR /app

# Creamos usuario no root para mayor seguridad.
RUN groupadd -g 1000 app && useradd -u 1000 -g app -m app

# Copiamos las dependencias instaladas desde builder.
COPY --from=builder /usr/local/lib/python*/site-packages /usr/local/lib/python*/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copiamos el código fuente final.
COPY --from=builder /app /app

# Exponemos puerto solo si usas webhook HTTPS (ajusta si usas otro puerto)
EXPOSE 8443

USER app

# Healthcheck: en modo webhook verifica que el puerto esté escuchando; en polling asume healthy.
# No requiere utilidades extra (usa solo Python estándar). Ajusta si tu bot expone endpoint distinto.
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
	CMD python -c "import os, socket, sys; mode=os.getenv('BOT_MODE','polling'); port=int(os.getenv('WEBHOOK_PORT','8443'));\nif mode=='webhook':\n\t s=socket.socket(); s.settimeout(3)\n\t\n\t try:\n\t\t s.connect(('127.0.0.1', port))\n\t except Exception:\n\t\t sys.exit(1)\n\t else:\n\t\t s.close(); sys.exit(0)\nelse:\n\t sys.exit(0)" 

# Punto de entrada: lanza el bot. Ajusta el script según tu proyecto: bot.py, main.py o paquete.
# Se pasan BOT_TOKEN y modo por variables de entorno. Evita bakear secretos en la imagen.
# Ejemplos de comandos de inicio (descomenta el que corresponda y comenta el resto):

# 1) Ejecutar un módulo package (si tu bot está en paquete "bot")
# ENTRYPOINT ["python", "-m", "bot"]

# 2) Ejecutar un archivo concreto
ENTRYPOINT ["python", "bot.py"]

# Puedes definir un CMD separado si necesitas argumentos extra.
# CMD ["--directory", "public"]

# Notas:
#  - Estilos de ejecución:
#      * Polling (sencillo, no requiere exponer puertos): BOT_MODE=polling
#      * Webhook (recomendado para producción): BOT_MODE=webhook, exponiendo WEBHOOK_PORT
#  - Provee BOT_TOKEN por env al correr el contenedor (no lo incluyas en la imagen).
#  - Ajusta PYTHON_VERSION si necesitas otra imagen base (ej: 3.11-slim).
#  - Si tu proyecto usa dependencias del sistema (por ej. para cryptografía), añádelas en la etapa builder.
#  - Añade un .dockerignore para reducir el contexto de build (venv, __pycache__, .git, etc.).
