FROM python:3.11-slim

# Instalar LibreOffice con fuentes básicas
RUN apt-get update && apt-get install -y \
    libreoffice \
    libreoffice-writer \
    fonts-liberation \
    --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py .

# Cloud Run usa PORT=8080 por defecto
ENV PORT=8080
EXPOSE 8080

CMD gunicorn --bind 0.0.0.0:$PORT --timeout 60 --workers 1 app:app
