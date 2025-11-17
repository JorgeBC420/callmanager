"""
config.py - Configuración centralizada del proyecto CallManager
"""
import os
from datetime import timedelta

# ========== SERVIDOR ==========
SERVER_HOST = os.environ.get('CALLMANAGER_HOST', '0.0.0.0')
SERVER_PORT = int(os.environ.get('CALLMANAGER_PORT', 5000))
SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-change-in-production')
DEBUG = os.environ.get('FLASK_ENV') == 'development'

# ========== BASE DE DATOS ==========
DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'contacts.db')
BACKUP_DIR = os.path.join(os.path.dirname(__file__), 'backups')
BACKUP_INTERVAL_MINUTES = 30  # Hacer backup cada 30 minutos
BACKUP_KEEP_DAYS = 7  # Mantener backups por 7 días

# ========== AUTENTICACIÓN ==========
ENABLE_AUTH = True
DEFAULT_API_KEY = os.environ.get('CALLMANAGER_API_KEY', 'dev-key-change-in-production')
AUTH_TOKENS = {
    'dev-key-change-in-production': 'Desarrollador',
    # Agregar más tokens según sea necesario
}

# ========== LOCKS ==========
DEFAULT_LOCK_DURATION_MINUTES = 10
MAX_LOCK_DURATION_MINUTES = 60
CLEANUP_INTERVAL_SECONDS = 300  # Limpiar locks vencidos cada 5 minutos

# ========== SOCKET.IO ==========
SOCKETIO_ASYNC_MODE = 'eventlet'
SOCKETIO_CORS_ORIGINS = "*"

# ========== LOGGING ==========
LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
LOG_FILE = os.path.join(os.path.dirname(__file__), 'callmanager.log')

# ========== INTERPHONE (CLIENTE) ==========
INTERPHONE_PATH = os.path.join(
    os.environ.get('LOCALAPPDATA', ''), 
    'InterPhone', 
    'InterPhone.exe'
)
INTERPHONE_WINDOW_TITLE_REGEX = "InterPhone - .*"
INTERPHONE_CALL_TIMEOUT_SECONDS = 5

# ========== CLIENTE UI ==========
DEFAULT_SERVER_URL = os.environ.get('CALLMANAGER_SERVER_URL', 'http://127.0.0.1:5000')
CLIENT_WINDOW_WIDTH = 1000
CLIENT_WINDOW_HEIGHT = 700

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
