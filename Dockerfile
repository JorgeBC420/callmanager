# === DOCKERFILE PARA CALLMANAGER ===
# Imagen base: Python 3.9 slim (ligera)
FROM python:3.9-slim

# Metadata
LABEL maintainer="Jorge BC <jorge@callmanager.dev>"
LABEL description="CallManager - Gestor de Llamadas Telefónicas"
LABEL version="2.0"

# Variables de entorno
# Evita que Python genere archivos .pyc (más limpio)
ENV PYTHONDONTWRITEBYTECODE=1
# Unbuffered output (mensajes de log en tiempo real)
ENV PYTHONUNBUFFERED=1
# Path para Python modules
ENV PYTHONPATH=/app

# Instalar dependencias del sistema
# - gcc: para compilar paquetes Python
# - libpq-dev: para PostgreSQL (si lo necesitas)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Establecer directorio de trabajo
WORKDIR /app

# Copiar requirements e instalar dependencias Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir gunicorn eventlet

# Copiar código de la aplicación
COPY . .

# Crear usuario no-root para seguridad
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Exponer puerto
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:5000/health', timeout=5)" || exit 1

# Comando para ejecutar en producción
# Usa Gunicorn con eventlet para WebSocket
CMD ["gunicorn", \
     "--worker-class", "eventlet", \
     "--workers", "1", \
     "--bind", "0.0.0.0:5000", \
     "--access-logfile", "-", \
     "--error-logfile", "-", \
     "--log-level", "info", \
     "server:app"]

# Para desarrollo local, usa:
# docker run -p 5000:5000 -v $(pwd):/app callmanager:latest python server.py
