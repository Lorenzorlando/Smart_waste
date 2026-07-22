# Uso Python 3.10 slim per un'immagine leggera e stabile con TensorFlow
FROM python:3.10-slim

# Evita la scrittura di file .pyc e forza il flush dell'output dei log
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Installa le dipendenze di sistema minime per Pillow/OpenCV se necessarie
RUN apt-get update && apt-get install -y --no-install-recommends \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    && rm -rf /var/lib/apt/lists/*

# Copia e installa i requisiti Python
COPY requirements.txt .

# Usiamo tensorflow-cpu per ridurre il peso dell'immagine ed evitare crash di RAM
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copia tutto il resto del progetto (app, file .h5, templates .html)
COPY . .

# Porta di default per Flask/Gunicorn
EXPOSE 5000

# Avvio tramite Gunicorn puntando a parteflask.py (variabile app)
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "1", "--threads", "2", "parteflask:app"]
