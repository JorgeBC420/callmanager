"""
config.py - Configuración centralizada del proyecto CallManager
Carga desde: 1) Variables de entorno 2) Archivo .env 3) Valores por defecto
"""
import os
from datetime import timedelta
from dotenv import load_dotenv
import logging

# Cargar variables de entorno desde .env
load_dotenv()

logger = logging.getLogger(__name__)

# ========== SERVIDOR ==========
SERVER_HOST = os.environ.get('CALLMANAGER_HOST', '0.0.0.0')
SERVER_PORT = int(os.environ.get('CALLMANAGER_PORT', 5000))
SECRET_KEY = os.environ.get('CALLMANAGER_SECRET_KEY', 'dev-secret-change-in-production')
DEBUG = os.environ.get('FLASK_ENV') == 'development'

# ========== VALIDACIONES DE SEGURIDAD EN STARTUP ==========
if SECRET_KEY == 'dev-secret-change-in-production' and os.environ.get('FLASK_ENV') == 'production':
    logger.error("🚨 ERROR CRÍTICO: SECRET_KEY no está configurada en producción. Configura CALLMANAGER_SECRET_KEY en .env")
    raise ValueError("SECRET_KEY must be changed for production")

# ========== BASE DE DATOS ==========
DATABASE_PATH = os.environ.get('DATABASE_PATH', os.path.join(os.path.dirname(__file__), 'contacts.db'))
BACKUP_DIR = os.environ.get('BACKUP_DIR', os.path.join(os.path.dirname(__file__), 'backups'))
BACKUP_INTERVAL_MINUTES = int(os.environ.get('BACKUP_INTERVAL_MINUTES', 30))
BACKUP_KEEP_DAYS = int(os.environ.get('BACKUP_KEEP_DAYS', 7))

# Pool de conexiones SQLite
DB_POOL_SIZE = int(os.environ.get('DB_POOL_SIZE', 10))
DB_MAX_OVERFLOW = int(os.environ.get('DB_MAX_OVERFLOW', 20))
DB_TIMEOUT_SECONDS = int(os.environ.get('DB_TIMEOUT_SECONDS', 30))

# ========== AUTENTICACIÓN ==========
ENABLE_AUTH = os.environ.get('ENABLE_AUTH', 'true').lower() == 'true'
DEFAULT_API_KEY = os.environ.get('CALLMANAGER_API_KEY', 'dev-key-change-in-production')
AUTH_TOKENS = {
    'dev-key-change-in-production': 'Desarrollador',
    # Agregar más tokens según sea necesario en .env como comma-separated
}

# Validación de API_KEY en producción
if DEFAULT_API_KEY == 'dev-key-change-in-production' and os.environ.get('FLASK_ENV') == 'production':
    logger.error("🚨 ERROR CRÍTICO: API_KEY no está configurada en producción. Configura CALLMANAGER_API_KEY en .env")
    raise ValueError("API_KEY must be changed for production")

# ========== LOCKS ==========
DEFAULT_LOCK_DURATION_MINUTES = 10
MAX_LOCK_DURATION_MINUTES = 60
CLEANUP_INTERVAL_SECONDS = 300  # Limpiar locks vencidos cada 5 minutos

# ========== SOCKET.IO ==========
SOCKETIO_ASYNC_MODE = os.environ.get('SOCKETIO_ASYNC_MODE', 'eventlet')
SOCKETIO_CORS_ORIGINS = os.environ.get('SOCKETIO_CORS_ORIGINS', "*")

# ========== LOGGING ==========
LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
LOG_FILE = os.environ.get('LOG_FILE', os.path.join(os.path.dirname(__file__), 'callmanager.log'))

# ========== INTERPHONE (CLIENTE) ==========
INTERPHONE_PATH = os.path.join(
    os.environ.get('LOCALAPPDATA', ''), 
    'InterPhone', 
    'InterPhone.exe'
)
INTERPHONE_WINDOW_TITLE_REGEX = "InterPhone - .*"
INTERPHONE_CALL_TIMEOUT_SECONDS = int(os.environ.get('INTERPHONE_CALL_TIMEOUT_SECONDS', 5))

# ========== CLIENTE UI ==========
DEFAULT_SERVER_URL = os.environ.get('CALLMANAGER_SERVER_URL', 'http://127.0.0.1:5000')
CLIENT_WINDOW_WIDTH = int(os.environ.get('CLIENT_WINDOW_WIDTH', 1000))
CLIENT_WINDOW_HEIGHT = int(os.environ.get('CLIENT_WINDOW_HEIGHT', 700))

# ========== VALIDACIONES ==========
PHONE_REGEX = r'^\+?[\d\s\-\(\)]{7,}$'  # Al menos 7 dígitos
MIN_NAME_LENGTH = 1
MAX_NAME_LENGTH = 200
MIN_NOTE_LENGTH = 0
MAX_NOTE_LENGTH = 2000

# ========== ESTADOS DINÁMICOS POR VISIBILIDAD (INACTIVIDAD) ==========
# Los estados se asignan automáticamente basados en cuándo fue la última actualización
STATUS_AUTO_RULES = {
    # Estado: (meses_sin_visibilidad, descripción)
    'NO_EXISTE': (3, 'Número no existe - 3 meses sin visibilidad'),
    'SIN_RED': (6, 'Sin red - 6 meses sin visibilidad'),
    'NO_CONTACTO': (8, 'No quieren contacto - 8 meses sin visibilidad'),
}

# ========== PRIORIDADES DE ORDENAMIENTO AL CARGAR ==========
# Menores números = Mayor visibilidad/prioridad
STATUS_PRIORITY = {
    'NC': 1,                    # No Contesta - MÁXIMA PRIORIDAD
    'CUELGA': 2,               # Cuelgan - ALTA PRIORIDAD (dependiendo del vendedor)
    'SIN_GESTIONAR': 3,        # Sin gestionar - NORMAL
    'INTERESADO': 4,           # Interesado - MEDIA
    'SERVICIOS_ACTIVOS': 10,   # Servicios activos - BAJA PRIORIDAD
    'NO_EXISTE': 20,           # No existe - MUY BAJA
    'SIN_RED': 21,             # Sin red - MUY BAJA
    'NO_CONTACTO': 22,         # No quieren contacto - MÍNIMA
}

# ========== RATE LIMITING ==========
RATE_LIMIT_PER_HOUR = int(os.environ.get('RATE_LIMIT_PER_HOUR', 1000))
IMPORT_RATE_LIMIT_PER_MINUTE = int(os.environ.get('IMPORT_RATE_LIMIT_PER_MINUTE', 10))

# ========== HTTPS / SSL ==========
SSL_CONTEXT = os.environ.get('SSL_CONTEXT', 'none')  # 'adhoc', ruta a .pem, o 'none'
ENABLE_HEALTH_CHECK = os.environ.get('ENABLE_HEALTH_CHECK', 'true').lower() == 'true'
ENABLE_METRICS = os.environ.get('ENABLE_METRICS', 'true').lower() == 'true'

# ========== VALIDACIÓN DE CONFIGURACIÓN ==========
logger.info("=" * 60)
logger.info(f"📋 Configuración cargada - Ambiente: {os.environ.get('FLASK_ENV', 'development')}")
logger.info(f"🔐 Autenticación: {'Habilitada' if ENABLE_AUTH else 'Deshabilitada'}")
logger.info(f"📊 Rate Limiting: {RATE_LIMIT_PER_HOUR}/hora, {IMPORT_RATE_LIMIT_PER_MINUTE}/min import")
logger.info("=" * 60)
