# Usa Python 3.10 slim come base leggera
FROM python:3.10-slim

# Variabili d'ambiente per bloccare i file temporanei e ottimizzare TensorFlow
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    TF_CPP_MIN_LOG_LEVEL=2 \
    OMP_NUM_THREADS=1

WORKDIR /app

# Installa le librerie C necessarie per Pillow senza tenere i file d'installazione
RUN apt-get update && apt-get install -y --no-install-recommends \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    && rm -rf /var/lib/apt/lists/*

# Copia solo il file dei requisiti prima di installare (sfrutta la cache delle varie fasi di Docker)
COPY requirements.txt .

# Upgrade di pip e installazione super-stringente SENZA salvataggio di ruote/cache di pip
RUN pip install --no-cache-dir --no-compile --upgrade pip && \
    pip install --no-cache-dir --no-compile -r requirements.txt

# Copia il codice dell'app e i file .h5 / .html
COPY . .

# Espone la porta usata dal container
EXPOSE 5000

# Avvia Gunicorn con 1 solo worker per non sforare i 512 MB di RAM del piano free
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "1", "--threads", "2", "--timeout", "120", "parteflask:app"]
