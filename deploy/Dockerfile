# ── STAGE 1 : BUILDER (Compilation et installation des roues Python) ──
FROM python:3.11-slim as builder

WORKDIR /app

COPY requirements.txt .

# Installation des dépendances de compilation nécessaires (si requis par certains paquets)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir --user -r requirements.txt


# ── STAGE 2 : IMAGE FINALE DE PRODUCTION (Légère et sécurisée) ──
FROM python:3.11-slim

WORKDIR /app

# Crucial : Installation de libgomp1 requise par LightGBM pour l'inférence
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Récupération des paquets Python installés proprement depuis le builder
COPY --from=builder /root/.local /root/.local
COPY app.py .
COPY models_v7/ ./models_v7/

# Configuration de l'environnement
ENV PATH=/root/.local/bin:$PATH
ENV MODELS_DIR=/app/models_v7

EXPOSE 8080

# HEALTHCHECK natif en Python (évite d'installer curl/wget dans l'image finale)
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/health', timeout=5)" || exit 1

# Lancement de l'API avec Uvicorn
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080", "--workers", "4"]