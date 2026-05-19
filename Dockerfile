# ── Build ─────────────────────────────────────────────────────────────────────
FROM python:3.12-slim AS base

# Variáveis de ambiente (não altere aqui; use .env ou docker-compose)
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_APP=app.py \
    FLASK_DEBUG=false

WORKDIR /app

# Dependências do sistema (apenas o necessário para psycopg2-binary)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Instala dependências Python primeiro (aproveita cache do Docker)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia código da aplicação
COPY . .

# Porta exposta pela aplicação
EXPOSE 5000

# Entrypoint: inicializa o banco e sobe com gunicorn em produção
# Em dev (FLASK_DEBUG=true), usa flask run
CMD ["sh", "-c", "\
  python -c 'from app import init_db; init_db()' && \
  gunicorn --bind 0.0.0.0:5000 --workers 2 --timeout 60 app:app \
"]
