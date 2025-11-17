ARG PYTHON_VERSION=3.12-slim
FROM python:${PYTHON_VERSION} AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
	PIP_NO_CACHE_DIR=on \
	PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt ./

RUN --mount=type=cache,target=/root/.cache/pip \
	set -eux; \
	pip install -r requirements.txt

COPY . .

FROM python:${PYTHON_VERSION} AS runtime

LABEL org.opencontainers.image.title="ProyectoAPS" \
	  org.opencontainers.image.description="Imagen de producción de ProyectoAPS" \
	  org.opencontainers.image.source="https://example.com/proyectoaps" \
	  org.opencontainers.image.licenses="MIT"

ENV PYTHONDONTWRITEBYTECODE=1 \
	PYTHONUNBUFFERED=1 \
	BOT_MODE=polling \
	WEBHOOK_URL="" \
	WEBHOOK_PORT=8443

WORKDIR /app

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

RUN groupadd -g 1000 app && useradd -u 1000 -g app -m app

COPY --from=builder /app /app

EXPOSE 8443

USER app

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
	CMD python -c "import os, socket, sys; mode=os.getenv('BOT_MODE','polling'); port=int(os.getenv('WEBHOOK_PORT','8443'));\nif mode=='webhook':\n\t s=socket.socket(); s.settimeout(3)\n\t\n\t try:\n\t\t s.connect(('127.0.0.1', port))\n\t except Exception:\n\t\t sys.exit(1)\n\t else:\n\t\t s.close(); sys.exit(0)\nelse:\n\t sys.exit(0)"

ENTRYPOINT ["python", "bot.py"]
