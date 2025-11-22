from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from flask_socketio import SocketIO, emit
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from sqlalchemy import create_engine, Column, String, Text, DateTime, Integer, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.pool import Pool
from datetime import datetime, timedelta
import bcrypt
import jwt
import json
import os
import logging
import shutil
import re
import secrets
from functools import wraps
from dateutil.relativedelta import relativedelta

# Importar configuración centralizada (carga .env automáticamente)
try:
    from config import *
except ImportError:
    # Valores por defecto si config.py no existe
    SERVER_HOST = '0.0.0.0'
    SERVER_PORT = 5000
    SECRET_KEY = 'dev-secret-change-in-production'
    DATABASE_PATH = 'contacts.db'
    BACKUP_DIR = 'backups'
    BACKUP_INTERVAL_MINUTES = 30
    ENABLE_AUTH = True
    DEFAULT_LOCK_DURATION_MINUTES = 10
    MAX_LOCK_DURATION_MINUTES = 60
    CLEANUP_INTERVAL_SECONDS = 300
    LOG_LEVEL = 'INFO'
    LOG_FILE = 'callmanager.log'
    PHONE_REGEX = r'^\+?[\d\s\-\(\)]{7,}$'
    MIN_NAME_LENGTH = 1
    MAX_NAME_LENGTH = 200
    MAX_NOTE_LENGTH = 2000
    AUTH_TOKENS = {'dev-key-change-in-production': 'Desarrollador'}
    RATE_LIMIT_PER_HOUR = 1000
    IMPORT_RATE_LIMIT_PER_MINUTE = 10
    DB_POOL_SIZE = 10
    DB_MAX_OVERFLOW = 20

# ========== LOGGING ==========
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = SECRET_KEY

# ========== RATE LIMITING ==========
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=[f"{RATE_LIMIT_PER_HOUR} per hour"]
)

socketio = SocketIO(app, cors_allowed_origins=SOCKETIO_CORS_ORIGINS, async_mode=SOCKETIO_ASYNC_MODE)

logger.info("=" * 60)
logger.info("CallManager Server Starting")
logger.info(f"Host: {SERVER_HOST}, Port: {SERVER_PORT}")
logger.info(f"Rate Limiting: {RATE_LIMIT_PER_HOUR}/hora (global), {IMPORT_RATE_LIMIT_PER_MINUTE}/min (import)")
logger.info("=" * 60)

# ========== DATABASE SETUP ==========
os.makedirs(BACKUP_DIR, exist_ok=True)

engine = create_engine(
    f'sqlite:///{DATABASE_PATH}',
    connect_args={"check_same_thread": False},
    pool_pre_ping=True,
    pool_size=DB_POOL_SIZE,
    max_overflow=DB_MAX_OVERFLOW
)

# ========== HABILITAR WAL MODE PARA MEJOR CONCURRENCIA ==========
@event.listens_for(Pool, "connect")
def set_sqlite_pragma(dbapi_conn, connection_record):
    """
    Habilitar Write-Ahead Logging (WAL) en SQLite.
    Beneficios:
    - Múltiples lecturas simultáneas sin bloqueos
    - Mejor performance con concurrencia
    - Protección contra corrupciones
    """
    cursor = dbapi_conn.cursor()
    try:
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA synchronous=NORMAL")
        cursor.execute("PRAGMA cache_size=10000")
        cursor.execute("PRAGMA temp_store=MEMORY")
        dbapi_conn.commit()
        logger.debug("✅ WAL mode habilitado para SQLite")
    except Exception as e:
        logger.warning(f"⚠️ No se pudo habilitar WAL mode: {e}")

Base = declarative_base()
session_factory = sessionmaker(bind=engine)
Session = scoped_session(session_factory)


class Contact(Base):
    __tablename__ = 'contacts'
    __table_args__ = {'extend_existing': True}
    
    id = Column(String, primary_key=True)
    phone = Column(String, nullable=False, index=True)
    name = Column(String, nullable=False)
    status = Column(String, default="SIN GESTIONAR", index=True)  # Índice para filtrado
    note = Column(Text, default="")
    coords = Column(String, default="{}")
    last_called_by = Column(String)
    last_called_by_user_id = Column(String, index=True)  # ID del usuario que lo llamó
    last_called_time = Column(DateTime)
    assigned_to_user_id = Column(String, index=True)  # Usuario asignado
    assigned_to_team_id = Column(String, index=True)  # Equipo asignado
    assigned_to_team_name = Column(String)
    last_visibility_time = Column(DateTime, default=datetime.utcnow, index=True)  # Cuándo se vio por última vez
    editors_history = Column(Text, default="[]")
    locked_by = Column(String, index=True)
    locked_until = Column(DateTime, index=True)
    reminder_time = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, index=True)
    version = Column(Integer, default=1)  # Versión para optimistic locking (incrementa con cada update)


class User(Base):
    """
    Modelo de usuario con roles y permisos.
    
    Roles:
    - Agent: Puede hacer llamadas, ver sus propios contactos
    - TeamLead: Puede ver métricas de su equipo + totales de otros equipos
    - ProjectManager: Puede ver todas las métricas
    - TI: Puede accesar configuraciones + métricas
    """
    __tablename__ = 'users'
    __table_args__ = {'extend_existing': True}
    
    id = Column(String, primary_key=True)
    api_key = Column(String, unique=True, nullable=False, index=True)
    username = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)  # Hash de contraseña (bcrypt)
    role = Column(String, default="Agent", index=True)  # Agent, TeamLead, ProjectManager, TI
    team_id = Column(String, index=True)  # Para agrupar agentes en equipos
    team_name = Column(String)  # Nombre del equipo (ej: "Equipo Ventas", "Equipo Support")
    email = Column(String)
    is_active = Column(Integer, default=1, index=True)  # 1 = activo, 0 = inactivo
    last_login = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, index=True)


class UserMetrics(Base):
    """
    Métricas de usuario (llamadas, contactos, etc).
    Se actualiza en tiempo real para dashboards.
    """
    __tablename__ = 'user_metrics'
    __table_args__ = {'extend_existing': True}
    
    id = Column(String, primary_key=True)
    user_id = Column(String, index=True)
    calls_made = Column(Integer, default=0)
    calls_success = Column(Integer, default=0)
    calls_failed = Column(Integer, default=0)
    contacts_managed = Column(Integer, default=0)
    avg_call_duration = Column(Integer, default=0)  # en segundos
    total_talk_time = Column(Integer, default=0)  # Tiempo total hablado en segundos
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class CallLog(Base):
    """
    Registro detallado de cada llamada realizada.
    Se usa para auditoría, reportes y cálculo de métricas.
    """
    __tablename__ = 'call_logs'
    __table_args__ = {'extend_existing': True}
    
    id = Column(String, primary_key=True)
    user_id = Column(String, nullable=False, index=True)
    contact_id = Column(String, index=True)
    contact_phone = Column(String)  # Número de teléfono del contacto
    start_time = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    end_time = Column(DateTime)
    duration_seconds = Column(Integer, default=0)
    status = Column(String, default='COMPLETED', index=True)  # COMPLETED, DROPPED, NO_ANSWER, FAILED
    notes = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.utcnow, index=True)


Base.metadata.create_all(engine)


# ========== VALIDACIÓN Y AUTENTICACIÓN ==========

def validate_phone(phone):
    """Validar formato de teléfono"""
    if not phone or not isinstance(phone, str):
        return False, "Teléfono inválido: debe ser una cadena"
    if not re.match(PHONE_REGEX, phone):
        return False, f"Teléfono no cumple formato: {PHONE_REGEX}"
    return True, ""

def validate_name(name):
    """Validar nombre de contacto"""
    if not name or not isinstance(name, str):
        return False, "Nombre inválido"
    name = name.strip()
    if len(name) < MIN_NAME_LENGTH or len(name) > MAX_NAME_LENGTH:
        return False, f"Nombre debe tener entre {MIN_NAME_LENGTH} y {MAX_NAME_LENGTH} caracteres"
    return True, ""

def validate_note(note):
    """Validar nota de contacto"""
    if not note or not isinstance(note, str):
        return True, ""  # La nota es opcional
    if len(note) > MAX_NOTE_LENGTH:
        return False, f"Nota no puede exceder {MAX_NOTE_LENGTH} caracteres"
    return True, ""

def validate_api_key(api_key):
    """Validar API key para autenticación"""
    if ENABLE_AUTH:
        if not api_key or api_key not in AUTH_TOKENS:
            return False, "API key inválida o no proporcionada"
    return True, ""

def hash_password(password: str) -> str:
    """
    Hash de contraseña usando bcrypt.
    Genera salt automáticamente y retorna string listo para guardar en BD.
    """
    salt = bcrypt.gensalt(rounds=10)  # rounds=10 es estándar (más = más lento pero más seguro)
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def verify_password(password: str, password_hash: str) -> bool:
    """
    Verificar contraseña contra hash almacenado.
    Retorna True si coinciden, False si no.
    """
    try:
        return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
    except Exception as e:
        logger.error(f"Error verifying password: {e}")
        return False

def generate_jwt_token(user_id: str, username: str, role: str) -> str:
    """
    Generar JWT token para sesión del usuario.
    Token expira en 24 horas.
    """
    payload = {
        'user_id': user_id,
        'username': username,
        'role': role,
        'iat': datetime.utcnow(),
        'exp': datetime.utcnow() + timedelta(hours=24)
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    return token

def verify_jwt_token(token: str):
    """
    Verificar y decodificar JWT token.
    Retorna payload si es válido, None si no.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        logger.warning("Token expired")
        return None
    except jwt.InvalidTokenError as e:
        logger.warning(f"Invalid token: {e}")
        return None

def normalize_phone(phone: str) -> str:
    """
    Normalizar número telefónico:
    - Remover caracteres especiales
    - Remover prefijo de país si es necesario
    - Mantener solo dígitos
    
    Ejemplos:
    +506-5123-4567 → 51234567
    +1-555-123-4567 → 5551234567
    555-123-4567 → 5551234567
    """
    if not phone:
        return ""
    
    # Remover todos los caracteres que no sean dígitos o +
    cleaned = re.sub(r'[^\d+]', '', str(phone))
    
    # Si comienza con +, remover el + y código de país
    if cleaned.startswith('+'):
        cleaned = cleaned[1:]  # Remover +
        # Remover primer 1-3 dígitos (códigos de país comunes)
        # +1 (USA), +506 (Costa Rica), +34 (España), etc.
        if len(cleaned) > 10:
            # Si tiene más de 10 dígitos después del +, probablemente tiene código país
            # Asumir que es: [1-3 dígitos código][números locales]
            # Para +506 específico: +506 = 3 dígitos, entonces remover primeros 3
            cleaned = cleaned[3:] if len(cleaned) > 10 else cleaned[-10:]
    
    return cleaned

def require_auth(f):
    """Decorador para validar autenticación en endpoints"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if ENABLE_AUTH:
            api_key = request.headers.get('X-API-Key')
            valid, msg = validate_api_key(api_key)
            if not valid:
                logger.warning(f"Unauthorized access attempt with key: {api_key}")
                return jsonify({'error': msg}), 401
        return f(*args, **kwargs)
    return decorated_function


def require_role(*allowed_roles):
    """
    Decorador para validar que el usuario tiene uno de los roles permitidos.
    
    Uso:
        @require_role('TI', 'ProjectManager')
        def endpoint():
            pass
    
    Roles disponibles:
    - 'Agent': Agentes normales
    - 'TeamLead': Líderes de equipo
    - 'ProjectManager': Jefes de proyecto
    - 'TI': Administradores técnicos
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            api_key = request.headers.get('X-API-Key')
            if not api_key:
                return jsonify({'error': 'API key required'}), 401
            
            # Buscar usuario
            try:
                user = Session.query(User).filter_by(api_key=api_key, is_active=1).first()
                if not user:
                    logger.warning(f"Invalid API key: {api_key}")
                    return jsonify({'error': 'Invalid API key'}), 401
                
                # Verificar rol
                if user.role not in allowed_roles:
                    logger.warning(f"Access denied - User {user.username} (role: {user.role}) tried to access {request.path}")
                    return jsonify({
                        'error': f'Access denied. Required roles: {list(allowed_roles)}, your role: {user.role}'
                    }), 403
                
                # Pasar usuario a la función
                kwargs['current_user'] = user
                return f(*args, **kwargs)
            except Exception as e:
                logger.error(f"Error in require_role decorator: {e}")
                return jsonify({'error': 'Authentication error'}), 500
        return decorated_function
    return decorator


def get_user_from_api_key(api_key: str):
    """Obtener usuario desde API key"""
    try:
        user = Session.query(User).filter_by(api_key=api_key, is_active=1).first()
        return user
    except Exception as e:
        logger.error(f"Error getting user: {e}")
        return None


# ========== ESTADOS DINÁMICOS Y VISIBILIDAD ==========

def update_contact_status_by_visibility(contact):
    """
    Actualizar estado del contacto automáticamente basado en cuánto tiempo
    lleva sin visibilidad (sin actualización de last_visibility_time)
    
    Reglas:
    - 3 meses sin visibilidad → NO_EXISTE
    - 6 meses sin visibilidad → SIN_RED
    - 8 meses sin visibilidad → NO_CONTACTO
    
    NOTA: No sobrescribe estados establecidos manualmente, solo 
    asigna estos estados si no han sido actualizados en meses.
    """
    try:
        if not contact.last_visibility_time:
            contact.last_visibility_time = contact.created_at or datetime.now()
        
        now = datetime.now()
        
        # Calcular cuántos meses sin visibilidad
        for status_name, (months_threshold, description) in STATUS_AUTO_RULES.items():
            cutoff_date = now - relativedelta(months=months_threshold)
            
            # Si la última visibilidad fue ANTES del umbral, aplicar el estado
            if contact.last_visibility_time < cutoff_date:
                # Solo cambiar si no es un estado manual importante
                if contact.status not in ['INTERESADO', 'SERVICIOS_ACTIVOS', 'NO_EXISTE', 'SIN_RED', 'NO_CONTACTO']:
                    contact.status = status_name
                    logger.info(f"Auto-status for {contact.id}: {status_name} ({description})")
                    return True
    except Exception as e:
        logger.error(f"Error updating visibility status for {contact.id}: {e}")
    
    return False


def get_contacts_sorted_by_priority(db=None):
    """
    Obtener todos los contactos ordenados por prioridad.
    Prioridad según STATUS_PRIORITY (menores números = mayor prioridad).
    
    Orden final:
    1. NC (No Contesta) - MÁXIMA PRIORIDAD
    2. CUELGA - ALTA PRIORIDAD
    3. SIN_GESTIONAR - NORMAL
    4. INTERESADO - MEDIA
    5. SERVICIOS_ACTIVOS - BAJA
    6. NO_EXISTE, SIN_RED, NO_CONTACTO - MÍNIMA
    """
    close_session = False
    if db is None:
        db = Session()
        close_session = True
    
    try:
        contacts = db.query(Contact).all()
        
        # Actualizar estados por visibilidad ANTES de ordenar
        for contact in contacts:
            update_contact_status_by_visibility(contact)
        
        # Commit de cambios de estado automático
        db.commit()
        
        # Ordenar por prioridad usando STATUS_PRIORITY
        def get_priority(contact):
            # Obtener prioridad del estado, si no existe usar valor muy alto
            return STATUS_PRIORITY.get(contact.status, 999)
        
        sorted_contacts = sorted(contacts, key=get_priority)
        
        logger.debug(f"Contacts sorted by priority. Order: {[c.status for c in sorted_contacts[:5]]}")
        
        return sorted_contacts
    
    finally:
        if close_session:
            db.close()


# ========== BACKUP ==========

def create_backup():
    """Crear backup de la base de datos"""
    try:
        if not os.path.exists(DATABASE_PATH):
            logger.debug("No database file to backup yet")
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = os.path.join(BACKUP_DIR, f"contacts_backup_{timestamp}.db")
        shutil.copy2(DATABASE_PATH, backup_file)
        logger.info(f"Backup created: {backup_file}")
        
        # Limpiar backups viejos
        cleanup_old_backups()
        return True
    except Exception as e:
        logger.error(f"Backup failed: {e}")
        return False

def cleanup_old_backups():
    """Eliminar backups más antiguos que BACKUP_KEEP_DAYS"""
    try:
        cutoff_time = datetime.now().timestamp() - (BACKUP_KEEP_DAYS * 86400)
        for fname in os.listdir(BACKUP_DIR):
            fpath = os.path.join(BACKUP_DIR, fname)
            if os.path.isfile(fpath) and os.path.getmtime(fpath) < cutoff_time:
                os.remove(fpath)
                logger.debug(f"Removed old backup: {fname}")
    except Exception as e:
        logger.error(f"Error cleaning old backups: {e}")


def contact_to_dict(r):
    """Convertir Contact ORM a diccionario"""
    try:
        # Incluir información de estado dinámico
        visibility_months = None
        if r.last_visibility_time:
            delta = relativedelta(datetime.now(), r.last_visibility_time)
            visibility_months = delta.months + (delta.years * 12)
        
        return {
            'id': r.id,
            'phone': r.phone,
            'name': r.name,
            'status': r.status,
            'note': r.note,
            'coords': json.loads(r.coords or '{}'),
            'locked_by': r.locked_by,
            'locked_until': r.locked_until.isoformat() if r.locked_until else None,
            'reminder_time': r.reminder_time.isoformat() if r.reminder_time else None,
            'last_called_by': r.last_called_by,
            'last_called_time': r.last_called_time.isoformat() if r.last_called_time else None,
            'last_visibility_time': r.last_visibility_time.isoformat() if hasattr(r, 'last_visibility_time') and r.last_visibility_time else None,
            'visibility_months_ago': visibility_months,  # Información para UI
            'editors_history': json.loads(r.editors_history or '[]'),
            'created_at': r.created_at.isoformat() if hasattr(r, 'created_at') and r.created_at else None,
            'updated_at': r.updated_at.isoformat() if hasattr(r, 'updated_at') and r.updated_at else None,
            'version': r.version if hasattr(r, 'version') else 1
        }
    except Exception as e:
        logger.error(f"Error converting contact {r.id}: {e}")
        raise


def cleanup_expired_locks():
    """Liberar locks vencidos periódicamente"""
    db = Session()
    try:
        expired = db.query(Contact).filter(
            Contact.locked_until < datetime.utcnow(),
            Contact.locked_by.isnot(None)
        ).all()
        
        for contact in expired:
            logger.info(f"Lock expired for contact {contact.id} (was locked by {contact.locked_by})")
            contact.locked_by = None
            contact.locked_until = None
            socketio.emit('contact_unlocked', {'id': contact.id}, broadcast=True)
        
        db.commit()
        if expired:
            logger.info(f"Cleaned {len(expired)} expired locks")
    except Exception as e:
        logger.error(f"Error in cleanup_expired_locks: {e}")
        db.rollback()
    finally:
        Session.remove()


@app.route('/auth/register', methods=['POST'])
@limiter.limit("5 per minute")  # Limitar registros
def register():
    """
    Registrar nuevo usuario.
    
    Body:
    {
        "username": "agente1",
        "password": "mi_contraseña",
        "role": "Agent",
        "team_name": "Equipo Ventas"
    }
    """
    db = Session()
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        password = data.get('password', '').strip()
        role = data.get('role', 'Agent')
        team_name = data.get('team_name', '')
        
        # Validaciones
        if not username or len(username) < 3:
            return jsonify({'error': 'Username debe tener mínimo 3 caracteres'}), 400
        
        if not password or len(password) < 4:
            return jsonify({'error': 'Password debe tener mínimo 4 caracteres'}), 400
        
        if role not in ['Agent', 'TeamLead', 'ProjectManager', 'TI']:
            return jsonify({'error': 'Role inválido'}), 400
        
        # Verificar que no existe usuario
        existing = db.query(User).filter_by(username=username).first()
        if existing:
            return jsonify({'error': 'Usuario ya existe'}), 409
        
        # Crear usuario
        user_id = f"user_{username}_{datetime.utcnow().timestamp()}"
        password_hash = hash_password(password)
        api_key = secrets.token_urlsafe(32)
        
        user = User(
            id=user_id,
            username=username,
            password_hash=password_hash,
            api_key=api_key,
            role=role,
            team_name=team_name,
            is_active=1
        )
        
        db.add(user)
        db.commit()
        
        logger.info(f"New user registered: {username} ({role})")
        
        return jsonify({
            'success': True,
            'user_id': user_id,
            'username': username,
            'role': role,
            'api_key': api_key,
            'message': 'Usuario creado exitosamente. Guarda tu API Key en lugar seguro.'
        }), 201
        
    except Exception as e:
        logger.error(f"Registration error: {e}")
        db.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        db.remove()


@app.route('/auth/login', methods=['POST'])
@limiter.limit("10 per minute")  # Limitar intentos
def login():
    """
    Login de usuario con usuario/contraseña.
    
    Body:
    {
        "username": "agente1",
        "password": "mi_contraseña"
    }
    
    Response:
    {
        "token": "jwt_token_aqui",
        "user": {
            "id": "user_...",
            "username": "agente1",
            "role": "Agent"
        }
    }
    """
    db = Session()
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        password = data.get('password', '').strip()
        
        if not username or not password:
            return jsonify({'error': 'Username y password requeridos'}), 400
        
        # Buscar usuario
        user = db.query(User).filter_by(username=username, is_active=1).first()
        if not user:
            logger.warning(f"Login attempt for non-existent user: {username}")
            return jsonify({'error': 'Usuario o contraseña incorrectos'}), 401
        
        # Verificar contraseña
        if not verify_password(password, user.password_hash):
            logger.warning(f"Failed login attempt for user: {username}")
            return jsonify({'error': 'Usuario o contraseña incorrectos'}), 401
        
        # Generar token JWT
        token = generate_jwt_token(user.id, user.username, user.role)
        
        # Actualizar last_login
        user.last_login = datetime.utcnow()
        db.commit()
        
        logger.info(f"User logged in: {username}")
        
        return jsonify({
            'success': True,
            'token': token,
            'user': {
                'id': user.id,
                'username': user.username,
                'role': user.role,
                'team_name': user.team_name
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Login error: {e}")
        return jsonify({'error': str(e)}), 500
    finally:
        db.remove()


@app.route('/auth/change-password', methods=['POST'])
@require_auth
def change_password():
    """
    Cambiar contraseña del usuario autenticado.
    
    Headers:
    X-API-Key: api_key_valida (o usar JWT token)
    
    Body:
    {
        "old_password": "contraseña_actual",
        "new_password": "nueva_contraseña",
        "confirm_password": "nueva_contraseña"
    }
    """
    db = Session()
    try:
        # Obtener usuario desde API Key
        api_key = request.headers.get('X-API-Key')
        user = db.query(User).filter_by(api_key=api_key, is_active=1).first()
        
        if not user:
            return jsonify({'error': 'Usuario no encontrado'}), 404
        
        data = request.get_json()
        old_password = data.get('old_password', '').strip()
        new_password = data.get('new_password', '').strip()
        confirm_password = data.get('confirm_password', '').strip()
        
        # Validaciones
        if not old_password:
            return jsonify({'error': 'old_password requerida'}), 400
        
        if not verify_password(old_password, user.password_hash):
            logger.warning(f"Failed password change attempt for user: {user.username}")
            return jsonify({'error': 'Contraseña actual incorrecta'}), 401
        
        if len(new_password) < 4:
            return jsonify({'error': 'Nueva contraseña debe tener mínimo 4 caracteres'}), 400
        
        if new_password != confirm_password:
            return jsonify({'error': 'Las contraseñas no coinciden'}), 400
        
        # Actualizar contraseña
        user.password_hash = hash_password(new_password)
        db.commit()
        
        logger.info(f"Password changed for user: {user.username}")
        
        return jsonify({
            'success': True,
            'message': 'Contraseña actualizada exitosamente'
        }), 200
        
    except Exception as e:
        logger.error(f"Password change error: {e}")
        db.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        db.remove()


@app.route('/import', methods=['POST'])
@limiter.limit(f"{IMPORT_RATE_LIMIT_PER_MINUTE} per minute")  # Rate limiting: máximo N imports por minuto
@require_auth
def import_contacts():
    """
    Importar lote de contactos.
    - Si el número YA existe: ACTUALIZA el registro antiguo (no crea duplicado)
    - Si es nuevo: INSERTA nuevo registro
    """
    db = Session()
    try:
        data = request.get_json(force=True)
        if not isinstance(data, list):
            return jsonify({'error': 'Se esperaba una lista de contactos'}), 400

        inserted = 0
        updated = 0
        duplicates_merged = 0
        errors = []

        for idx, c in enumerate(data):
            try:
                # Validar teléfono
                phone = str(c.get('phone', '')).strip()
                valid, msg = validate_phone(phone)
                if not valid:
                    errors.append(f"Row {idx}: {msg}")
                    continue

                # Crear ID único (normalizado)
                cid = normalize_phone(phone)
                
                if not cid:
                    errors.append(f"Row {idx}: Teléfono no válido o vacío")
                    continue
                
                # Validar nombre
                name = str(c.get('name', f'Contacto {cid}')).strip()
                valid, msg = validate_name(name)
                if not valid:
                    errors.append(f"Row {idx}: {msg}")
                    continue

                # Validar nota si existe
                note = str(c.get('note', '')).strip()
                valid, msg = validate_note(note)
                if not valid:
                    errors.append(f"Row {idx}: {msg}")
                    continue

                # ⭐ CLAVE: Buscar si el contacto EXISTE
                obj = db.query(Contact).filter(Contact.id == cid).first()
                
                if obj:
                    # ✅ EXISTE: Actualizar registro antiguo (no crear duplicado)
                    old_name = obj.name
                    old_status = obj.status
                    
                    # Actualizar campos si se proporcionan
                    if name:
                        obj.name = name
                    if 'status' in c and c['status']:
                        obj.status = str(c['status']).strip()
                    if note:
                        obj.note = note
                    
                    # Registrar que fue actualizado
                    obj.updated_at = datetime.utcnow()
                    # ⭐ NUEVO: Registrar que se vio (reset de visibilidad)
                    obj.last_visibility_time = datetime.utcnow()
                    
                    logger.info(f"Updated existing contact: {cid} ({old_name} → {obj.name})")
                    updated += 1
                    duplicates_merged += 1
                    
                else:
                    # ✅ NUEVO: Crear contacto nuevo
                    obj = Contact(
                        id=cid,
                        phone=phone,  # Guardar con formato original (+506...)
                        name=name,
                        status=c.get('status', 'SIN GESTIONAR'),
                        note=note,
                        coords=json.dumps(c.get('coords') or {}),
                        editors_history=json.dumps([]),
                        last_visibility_time=datetime.utcnow(),  # ⭐ NUEVO: Inicializar visibilidad
                        version=1
                    )
                    db.add(obj)
                    inserted += 1
                    logger.debug(f"Inserted new contact: {cid}")

            except Exception as e:
                errors.append(f"Row {idx}: {str(e)}")
                logger.warning(f"Error importing row {idx}: {e}")

        db.commit()
        logger.info(f"Import complete: {inserted} inserted, {updated} updated (merged {duplicates_merged} duplicates)")
        
        socketio.emit('bulk_update', {
            'message': 'imported',
            'inserted': inserted,
            'updated': updated,
            'duplicates_merged': duplicates_merged,
            'errors': errors
        }, broadcast=True)
        
        return jsonify({
            'inserted': inserted,
            'updated': updated,
            'duplicates_merged': duplicates_merged,
            'errors': errors,
            'total': inserted + updated
        }), 201

    except Exception as e:
        logger.error(f"Import error: {e}")
        db.rollback()
        return jsonify({'error': str(e), 'errors': errors}), 500
    finally:
        Session.remove()


@app.route('/export', methods=['GET'])
@require_auth
def export_contacts_excel():
    """
    Exportar todos los contactos a Excel.
    
    Response: Archivo Excel (application/vnd.openxmlformats-officedocument.spreadsheetml.sheet)
    """
    db = Session()
    try:
        import pandas as pd
        from io import BytesIO
        
        # Obtener contactos
        rows = get_contacts_sorted_by_priority(db)
        data = []
        
        for r in rows:
            data.append({
                'ID': r.id,
                'Teléfono': r.phone,
                'Nombre': r.name,
                'Estado': r.status,
                'Nota': r.note or '',
                'Bloqueado Por': r.locked_by or '',
                'Última Actualización': r.updated_at.isoformat() if r.updated_at else '',
                'Creado': r.created_at.isoformat() if r.created_at else ''
            })
        
        # Crear DataFrame
        df = pd.DataFrame(data)
        
        # Crear archivo en memoria
        output = BytesIO()
        df.to_excel(output, index=False, sheet_name='Contactos')
        output.seek(0)
        
        logger.info(f"Exported {len(data)} contacts to Excel")
        
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=f'contactos_callmanager_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
        )
    
    except Exception as e:
        logger.error(f"Export error: {e}")
        return jsonify({'error': str(e)}), 500
    finally:
        db.remove()


@app.route('/contacts', methods=['GET'])
@require_auth
def get_all():
    """
    Obtener todos los contactos ordenados por prioridad.
    
    Orden:
    1. NC (No Contesta) - MÁXIMA PRIORIDAD
    2. CUELGA - ALTA PRIORIDAD
    3. SIN_GESTIONAR - NORMAL
    4. INTERESADO - MEDIA
    5. SERVICIOS_ACTIVOS - BAJA
    6. NO_EXISTE, SIN_RED, NO_CONTACTO - MÍNIMA
    
    Los estados dinámicos se calculan automáticamente basados en visibilidad.
    """
    db = Session()
    try:
        # Usar función que aplica ordenamiento y actualiza estados dinámicos
        rows = get_contacts_sorted_by_priority(db)
        out = [contact_to_dict(r) for r in rows]
        logger.debug(f"Retrieved {len(out)} contacts (sorted by priority)")
        return jsonify(out), 200
    except Exception as e:
        logger.error(f"Error fetching contacts: {e}")
        return jsonify({'error': str(e)}), 500
    finally:
        db.remove()


@socketio.on('update_contact')
def on_update(data):
    """Actualizar campo de contacto con validación y historial"""
    db = Session()
    try:
        cid = data.get('id')
        user = data.get('user', 'unknown')
        fields = data.get('fields', {})

        if not cid:
            emit('error', {'message': 'ID de contacto requerido'})
            return

        obj = db.query(Contact).get(cid)
        if not obj:
            logger.warning(f"Update attempt on non-existent contact: {cid}")
            emit('error', {'message': 'Contacto no encontrado'})
            return

        # Validar que no esté bloqueado por otro usuario
        if obj.locked_by and obj.locked_by != user:
            if obj.locked_until and obj.locked_until > datetime.utcnow():
                logger.warning(f"Update denied: {cid} locked by {obj.locked_by}")
                emit('lock_denied', {
                    'id': cid,
                    'locked_by': obj.locked_by,
                    'locked_until': obj.locked_until.isoformat()
                })
                return

        # Validar e aplicar cambios
        changes_made = False
        
        if 'name' in fields:
            new_name = str(fields['name']).strip()
            valid, msg = validate_name(new_name)
            if not valid:
                emit('error', {'message': f'Nombre inválido: {msg}'})
                return
            
            if new_name != obj.name:
                hist = json.loads(obj.editors_history or '[]')
                hist.insert(0, {
                    'user': user,
                    'field': 'name',
                    'old': obj.name,
                    'new': new_name,
                    'ts': datetime.utcnow().isoformat()
                })
                obj.editors_history = json.dumps(hist[:20])  # Guardar últimos 20 cambios
                obj.name = new_name
                changes_made = True

        if 'status' in fields:
            obj.status = str(fields['status']).strip()
            changes_made = True

        if 'note' in fields:
            new_note = str(fields['note']).strip()
            valid, msg = validate_note(new_note)
            if not valid:
                emit('error', {'message': f'Nota inválida: {msg}'})
                return
            obj.note = new_note
            changes_made = True

        if 'coords' in fields:
            try:
                obj.coords = json.dumps(fields['coords'])
                changes_made = True
            except Exception as e:
                emit('error', {'message': f'Coordenadas inválidas: {e}'})
                return

        if changes_made:
            obj.last_called_by = user
            obj.last_called_time = datetime.utcnow()
            obj.updated_at = datetime.utcnow()
            db.commit()
            logger.info(f"Contact {cid} updated by {user}")

            socketio.emit('contact_updated', {
                'id': cid,
                'fields': fields,
                'user': user,
                'ts': datetime.utcnow().isoformat(),
                'contact': contact_to_dict(obj)
            }, broadcast=True)
        else:
            logger.debug(f"No changes for contact {cid}")

    except Exception as e:
        logger.error(f"Error updating contact {data.get('id', 'unknown')}: {e}")
        db.rollback()
        emit('error', {'message': f'Error actualizando: {str(e)}'})
    finally:
        Session.remove()


@socketio.on('lock_contact')
def on_lock(data):
    """Bloquear un contacto para edición exclusiva"""
    db = Session()
    try:
        cid = data.get('id')
        user = data.get('user', 'unknown')
        dur = int(data.get('duration_minutes', DEFAULT_LOCK_DURATION_MINUTES))

        # Validar duración del lock
        if dur <= 0 or dur > MAX_LOCK_DURATION_MINUTES:
            dur = DEFAULT_LOCK_DURATION_MINUTES
            logger.warning(f"Invalid lock duration {data.get('duration_minutes')}, using default")

        obj = db.query(Contact).get(cid)
        if not obj:
            logger.warning(f"Lock attempt on non-existent contact: {cid}")
            emit('error', {'message': 'Contacto no encontrado'})
            return

        # Si está bloqueado por otro usuario y todavía vigente, rechazar
        if obj.locked_by and obj.locked_by != user:
            if obj.locked_until and obj.locked_until > datetime.utcnow():
                logger.warning(f"Lock denied for {cid}: already locked by {obj.locked_by}")
                emit('lock_denied', {
                    'id': cid,
                    'locked_by': obj.locked_by,
                    'locked_until': obj.locked_until.isoformat(),
                    'message': f'Bloqueado por {obj.locked_by}'
                })
                return

        obj.locked_by = user
        obj.locked_until = datetime.utcnow() + timedelta(minutes=dur)
        db.commit()
        logger.info(f"Contact {cid} locked by {user} for {dur} minutes")

        socketio.emit('contact_locked', {
            'id': cid,
            'locked_by': user,
            'locked_until': obj.locked_until.isoformat(),
            'duration_minutes': dur
        }, broadcast=True)

    except Exception as e:
        logger.error(f"Error locking contact {data.get('id', 'unknown')}: {e}")
        db.rollback()
        emit('error', {'message': f'Error bloqueando: {str(e)}'})
    finally:
        Session.remove()


@socketio.on('unlock_contact')
def on_unlock(data):
    """Desbloquear un contacto"""
    db = Session()
    try:
        cid = data.get('id')
        user = data.get('user', 'unknown')

        obj = db.query(Contact).get(cid)
        if not obj:
            logger.warning(f"Unlock attempt on non-existent contact: {cid}")
            emit('error', {'message': 'Contacto no encontrado'})
            return

        # Solo el dueño del lock puede desbloquear (o admin con None)
        if obj.locked_by and obj.locked_by != user:
            logger.warning(f"Unlock denied: {cid} locked by {obj.locked_by}, attempted by {user}")
            emit('error', {'message': f'Solo {obj.locked_by} puede desbloquear este contacto'})
            return

        if obj.locked_by:
            obj.locked_by = None
            obj.locked_until = None
            db.commit()
            logger.info(f"Contact {cid} unlocked by {user}")

            socketio.emit('contact_unlocked', {
                'id': cid,
                'unlocked_by': user,
                'ts': datetime.utcnow().isoformat()
            }, broadcast=True)
        else:
            logger.debug(f"Unlock request for already unlocked contact {cid}")

    except Exception as e:
        logger.error(f"Error unlocking contact {data.get('id', 'unknown')}: {e}")
        db.rollback()
        emit('error', {'message': f'Error desbloqueando: {str(e)}'})
    finally:
        Session.remove()


def start_background_cleanup():
    """Tarea background: limpiar locks vencidos y hacer backups periódicos"""
    backup_counter = 0
    while True:
        socketio.sleep(CLEANUP_INTERVAL_SECONDS)
        
        try:
            with app.app_context():
                cleanup_expired_locks()
                
                # Hacer backup cada (BACKUP_INTERVAL_MINUTES / CLEANUP_INTERVAL_SECONDS) ciclos
                backup_counter += 1
                backups_per_cycle = (BACKUP_INTERVAL_MINUTES * 60) // CLEANUP_INTERVAL_SECONDS
                
                if backup_counter >= backups_per_cycle:
                    create_backup()
                    backup_counter = 0
        except Exception as e:
            logger.error(f"Error in background task: {e}")


# ========== ENDPOINTS DE MÉTRICAS POR ROL ==========

@app.route('/metrics/personal', methods=['GET'])
@require_role('Agent', 'TeamLead', 'ProjectManager', 'TI')
def get_personal_metrics(current_user):
    """
    Obtener métricas personales del usuario actual.
    Accesible por: Todos
    """
    db = Session()
    try:
        metrics = db.query(UserMetrics).filter_by(user_id=current_user.id).first()
        if not metrics:
            # Si no existen métricas, crear registro vacío
            metrics = UserMetrics(
                id=f"m_{current_user.id}",
                user_id=current_user.id,
                calls_made=0,
                calls_success=0,
                calls_failed=0
            )
            db.add(metrics)
            db.commit()
        
        return jsonify({
            'user_id': current_user.id,
            'username': current_user.username,
            'role': current_user.role,
            'calls_made': metrics.calls_made,
            'calls_success': metrics.calls_success,
            'calls_failed': metrics.calls_failed,
            'contacts_managed': metrics.contacts_managed,
            'avg_call_duration': metrics.avg_call_duration,
            'success_rate': (metrics.calls_success / metrics.calls_made * 100) if metrics.calls_made > 0 else 0
        }), 200
    except Exception as e:
        logger.error(f"Error fetching personal metrics: {e}")
        return jsonify({'error': str(e)}), 500
    finally:
        db.remove()


@app.route('/metrics/team', methods=['GET'])
@require_role('TeamLead', 'ProjectManager', 'TI')
def get_team_metrics(current_user):
    """
    Obtener métricas del equipo del usuario.
    TeamLead: Ve su equipo + totales de otros
    ProjectManager/TI: Ve todo
    """
    db = Session()
    try:
        if current_user.role == 'TeamLead':
            # Solo ver su equipo
            team_users = db.query(User).filter_by(
                team_id=current_user.team_id,
                is_active=1
            ).all()
        else:
            # ProjectManager/TI ven todos los usuarios
            team_users = db.query(User).filter_by(is_active=1).all()
        
        team_metrics = []
        for user in team_users:
            metrics = db.query(UserMetrics).filter_by(user_id=user.id).first()
            if metrics:
                team_metrics.append({
                    'user_id': user.id,
                    'username': user.username,
                    'role': user.role,
                    'team_name': user.team_name,
                    'calls_made': metrics.calls_made,
                    'calls_success': metrics.calls_success,
                    'contacts_managed': metrics.contacts_managed,
                    'success_rate': (metrics.calls_success / metrics.calls_made * 100) if metrics.calls_made > 0 else 0
                })
        
        return jsonify(team_metrics), 200
    except Exception as e:
        logger.error(f"Error fetching team metrics: {e}")
        return jsonify({'error': str(e)}), 500
    finally:
        db.remove()


@app.route('/metrics/all', methods=['GET'])
@require_role('ProjectManager', 'TI')
def get_all_metrics(current_user):
    """
    Obtener métricas consolidadas de toda la organización.
    Accesible solo por: ProjectManager, TI
    """
    db = Session()
    try:
        all_users = db.query(User).filter_by(is_active=1).all()
        total_calls = 0
        total_success = 0
        total_contacts = 0
        
        by_team = {}
        for user in all_users:
            metrics = db.query(UserMetrics).filter_by(user_id=user.id).first()
            if metrics:
                total_calls += metrics.calls_made
                total_success += metrics.calls_success
                total_contacts += metrics.contacts_managed
                
                team = user.team_name or "Sin equipo"
                if team not in by_team:
                    by_team[team] = {
                        'calls_made': 0,
                        'calls_success': 0,
                        'agents': 0
                    }
                by_team[team]['calls_made'] += metrics.calls_made
                by_team[team]['calls_success'] += metrics.calls_success
                by_team[team]['agents'] += 1
        
        return jsonify({
            'total_calls': total_calls,
            'total_success': total_success,
            'total_contacts': total_contacts,
            'total_users': len(all_users),
            'overall_success_rate': (total_success / total_calls * 100) if total_calls > 0 else 0,
            'by_team': by_team
        }), 200
    except Exception as e:
        logger.error(f"Error fetching all metrics: {e}")
        return jsonify({'error': str(e)}), 500
    finally:
        db.remove()


# ========== ENDPOINTS DE RASTREO DE LLAMADAS ==========

@app.route('/api/calls/start', methods=['POST'])
@require_role('Agent', 'TeamLead', 'ProjectManager', 'TI')
def start_call_tracking(current_user):
    """
    Registra el inicio de una llamada.
    
    Parámetros JSON:
    - contact_id: ID del contacto (opcional)
    - contact_phone: Número de teléfono (opcional)
    
    Retorna:
    - call_id: ID único para la sesión de llamada
    - start_time: Timestamp de inicio
    """
    db = Session()
    try:
        data = request.json or {}
        contact_id = data.get('contact_id')
        contact_phone = data.get('contact_phone', '')
        
        # Generar ID único para la llamada
        call_id = f"call_{int(datetime.utcnow().timestamp() * 1000)}_{current_user.id}"
        
        # Crear registro de llamada
        new_call = CallLog(
            id=call_id,
            user_id=current_user.id,
            contact_id=contact_id,
            contact_phone=contact_phone,
            start_time=datetime.utcnow(),
            status='IN_PROGRESS'
        )
        
        db.add(new_call)
        db.commit()
        
        logger.info(f"📞 Llamada iniciada: {call_id} (Usuario: {current_user.username})")
        
        return jsonify({
            'message': 'Call started',
            'call_id': call_id,
            'start_time': new_call.start_time.isoformat()
        }), 201
    except Exception as e:
        db.rollback()
        logger.error(f"Error iniciando rastreo de llamada: {e}")
        return jsonify({'error': str(e)}), 500
    finally:
        db.remove()


@app.route('/api/calls/end', methods=['POST'])
@require_role('Agent', 'TeamLead', 'ProjectManager', 'TI')
def end_call_tracking(current_user):
    """
    Registra el fin de una llamada, calcula duración y actualiza métricas.
    
    Parámetros JSON:
    - call_id: ID de la llamada (requerido)
    - status: COMPLETED, DROPPED, NO_ANSWER, FAILED (default: COMPLETED)
    - notes: Notas adicionales (opcional)
    
    Retorna:
    - duration_seconds: Duración en segundos
    - new_average: Nuevo promedio de duración
    """
    db = Session()
    try:
        data = request.json or {}
        call_id = data.get('call_id')
        status = data.get('status', 'COMPLETED')
        notes = data.get('notes', '')
        
        if not call_id:
            return jsonify({'error': 'call_id is required'}), 400
        
        # Buscar la llamada
        call_log = db.query(CallLog).filter_by(id=call_id).first()
        if not call_log:
            return jsonify({'error': 'Call not found'}), 404
        
        # Registrar fin de llamada
        end_time = datetime.utcnow()
        call_log.end_time = end_time
        call_log.status = status
        call_log.notes = notes
        
        # Calcular duración en segundos
        duration = (end_time - call_log.start_time).total_seconds()
        call_log.duration_seconds = int(duration)
        
        # Obtener o crear métricas del usuario
        metrics = db.query(UserMetrics).filter_by(user_id=call_log.user_id).first()
        
        if not metrics:
            metrics = UserMetrics(
                id=f"m_{call_log.user_id}",
                user_id=call_log.user_id,
                calls_made=0,
                calls_success=0,
                calls_failed=0,
                total_talk_time=0,
                avg_call_duration=0
            )
            db.add(metrics)
        
        # Actualizar contadores
        metrics.calls_made += 1
        
        if status == 'COMPLETED':
            metrics.calls_success += 1
        else:
            metrics.calls_failed += 1
        
        # Acumular tiempo total
        metrics.total_talk_time += int(duration)
        
        # RECALCULAR PROMEDIO
        if metrics.calls_made > 0:
            metrics.avg_call_duration = metrics.total_talk_time // metrics.calls_made
        
        # Guardar cambios
        db.add(call_log)
        db.commit()
        
        logger.info(f"✅ Llamada finalizada: {call_id} | Duración: {int(duration)}s | Estado: {status}")
        
        # Emitir evento SocketIO para actualizar dashboards en vivo
        try:
            socketio.emit('call_ended', {
                'user_id': call_log.user_id,
                'call_id': call_id,
                'duration_seconds': int(duration),
                'status': status,
                'calls_made': metrics.calls_made,
                'avg_duration': metrics.avg_call_duration,
                'total_talk_time': metrics.total_talk_time
            }, skip_sid=request.sid, broadcast=True)
        except:
            pass  # No es crítico si SocketIO falla
        
        return jsonify({
            'message': 'Call ended',
            'call_id': call_id,
            'duration_seconds': int(duration),
            'new_average': metrics.avg_call_duration,
            'calls_made': metrics.calls_made,
            'calls_success': metrics.calls_success,
            'total_talk_time': metrics.total_talk_time
        }), 200
    except Exception as e:
        db.rollback()
        logger.error(f"Error finalizando rastreo de llamada: {e}")
        return jsonify({'error': str(e)}), 500
    finally:
        db.remove()


@app.route('/api/calls/log', methods=['GET'])
@require_role('TeamLead', 'ProjectManager', 'TI')
def get_call_logs(current_user):
    """
    Obtener historial de llamadas (con filtros).
    
    Parámetros query:
    - user_id: Filtrar por usuario (opcional, requerido para no-admin)
    - start_date: Fecha inicio (YYYY-MM-DD)
    - end_date: Fecha fin (YYYY-MM-DD)
    - status: Filtrar por estado
    - limit: Máximo de registros (default: 100)
    
    Retorna:
    - Lista de llamadas con duración, estado, usuario, contacto
    """
    db = Session()
    try:
        limit = request.args.get('limit', 100, type=int)
        limit = min(limit, 1000)  # Máximo 1000 registros
        
        # Filtro base
        query = db.query(CallLog)
        
        # Control de acceso
        if current_user.role not in ['ProjectManager', 'TI']:
            # TeamLead solo ve su equipo
            team_users = db.query(User).filter_by(team_id=current_user.team_id).all()
            user_ids = [u.id for u in team_users]
            query = query.filter(CallLog.user_id.in_(user_ids))
        
        # Filtros opcionales
        user_id = request.args.get('user_id')
        if user_id:
            query = query.filter_by(user_id=user_id)
        
        status = request.args.get('status')
        if status:
            query = query.filter_by(status=status)
        
        start_date = request.args.get('start_date')
        if start_date:
            try:
                start_dt = datetime.strptime(start_date, '%Y-%m-%d')
                query = query.filter(CallLog.start_time >= start_dt)
            except:
                pass
        
        end_date = request.args.get('end_date')
        if end_date:
            try:
                end_dt = datetime.strptime(end_date, '%Y-%m-%d')
                end_dt = end_dt.replace(hour=23, minute=59, second=59)
                query = query.filter(CallLog.start_time <= end_dt)
            except:
                pass
        
        # Ordenar por fecha descendente y limitar
        calls = query.order_by(CallLog.start_time.desc()).limit(limit).all()
        
        result = [{
            'call_id': call.id,
            'user_id': call.user_id,
            'contact_id': call.contact_id,
            'contact_phone': call.contact_phone,
            'start_time': call.start_time.isoformat() if call.start_time else None,
            'end_time': call.end_time.isoformat() if call.end_time else None,
            'duration_seconds': call.duration_seconds,
            'status': call.status,
            'notes': call.notes
        } for call in calls]
        
        return jsonify(result), 200
    except Exception as e:
        logger.error(f"Error fetching call logs: {e}")
        return jsonify({'error': str(e)}), 500
    finally:
        db.remove()


@app.route('/config', methods=['GET'])
@require_role('ProjectManager', 'TI')
def get_config(current_user):
    """
    Obtener configuraciones del sistema.
    Accesible solo por: ProjectManager, TI
    """
    try:
        return jsonify({
            'server_host': SERVER_HOST,
            'server_port': SERVER_PORT,
            'debug': DEBUG,
            'enable_auth': ENABLE_AUTH,
            'rate_limit_per_hour': RATE_LIMIT_PER_HOUR,
            'import_rate_limit_per_minute': IMPORT_RATE_LIMIT_PER_MINUTE,
            'backup_interval_minutes': BACKUP_INTERVAL_MINUTES,
            'backup_keep_days': BACKUP_KEEP_DAYS,
            'socketio_async_mode': SOCKETIO_ASYNC_MODE,
            'status_priority': STATUS_PRIORITY,
            'status_auto_rules': STATUS_AUTO_RULES
        }), 200
    except Exception as e:
        logger.error(f"Error fetching config: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/config', methods=['POST'])
@require_role('TI')  # Solo TI puede modificar configuración
def update_config(current_user):
    """
    Actualizar configuraciones del sistema.
    Accesible solo por: TI
    """
    db = Session()
    try:
        data = request.json
        logger.warning(f"⚠️ Configuration change by {current_user.username}: {list(data.keys())}")
        
        # Aquí va la lógica de actualización de configuración
        # Por ahora solo loguear
        
        return jsonify({'success': True, 'message': 'Configuration updated'}), 200
    except Exception as e:
        logger.error(f"Error updating config: {e}")
        return jsonify({'error': str(e)}), 500
    finally:
        db.remove()


@app.route('/contacts/<contact_id>', methods=['DELETE'])
@require_auth
def delete_contact(contact_id):
    """
    Eliminar un contacto.
    Accesible por: ProjectManager, TI
    """
    db = Session()
    try:
        # Obtener usuario del API key para verificar rol
        api_key = request.headers.get('X-API-Key')
        user = get_user_from_api_key(api_key)
        
        if not user or user.role not in ['ProjectManager', 'TI']:
            return jsonify({'error': 'Access denied. Only ProjectManager and TI can delete contacts'}), 403
        
        # Buscar contacto
        contact = db.query(Contact).filter(Contact.id == contact_id).first()
        if not contact:
            return jsonify({'error': f'Contact not found: {contact_id}'}), 404
        
        # Eliminar
        contact_name = contact.name
        contact_phone = contact.phone
        db.delete(contact)
        db.commit()
        
        logger.warning(f"Contact deleted by {user.username}: {contact_id} ({contact_name} {contact_phone})")
        
        # Notificar a todos los clientes
        socketio.emit('contact_deleted', {
            'id': contact_id,
            'name': contact_name,
            'phone': contact_phone,
            'deleted_by': user.username,
            'ts': datetime.utcnow().isoformat()
        }, broadcast=True)
        
        return jsonify({
            'success': True,
            'message': f'Contact deleted: {contact_name}',
            'id': contact_id
        }), 200
        
    except Exception as e:
        logger.error(f"Error deleting contact {contact_id}: {e}")
        db.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        db.remove()


@app.route('/api/generate_contacts', methods=['POST'])
@require_auth
def api_generate_contacts():
    """
    Generar números telefónicos realistas de Costa Rica.
    
    Request JSON:
    {
        "amount": 100,              # Cantidad de números (default: 100)
        "method": "stratified",     # stratified, simple, random (default: stratified)
        "save": true                # Guardar en BD como contactos (default: false)
    }
    
    Response: Array de números con estructura:
    {
        "phones": [
            {"number": "81234567", "operator": "Kölbi", "formatted": "8123-4567"},
            ...
        ]
    }
    """
    db = Session()
    try:
        data = request.get_json()
        amount = data.get('amount', 100)
        method = data.get('method', 'stratified')
        save_to_db = data.get('save', False)
        
        # Validar parámetros
        if not isinstance(amount, int) or amount <= 0 or amount > 1000:
            return jsonify({'error': 'amount debe ser 1-1000'}), 400
        
        if method not in ['stratified', 'simple', 'random']:
            return jsonify({'error': f'method debe ser: stratified, simple, random'}), 400
        
        # Generar teléfonos
        from phone_generator import generate_cr_phones
        phones = generate_cr_phones(count=amount, method=method)
        
        logger.info(f"Generated {len(phones)} phone numbers (method={method})")
        
        # Opcionalmente guardar en BD
        if save_to_db:
            imported = 0
            for p in phones:
                try:
                    # Evitar duplicados
                    contact_id = p['number']
                    existing = db.query(Contact).filter(Contact.id == contact_id).first()
                    
                    if not existing:
                        contact = Contact(
                            id=contact_id,
                            phone=p['formatted'],  # Guardar con formato
                            name=f"Generated-{p['operator']}-{p['number']}",
                            status='SIN_GESTIONAR',
                            coords=json.dumps({}),
                            editors_history=json.dumps([]),
                            last_visibility_time=datetime.utcnow(),
                            version=1
                        )
                        db.add(contact)
                        imported += 1
                except Exception as e:
                    logger.warning(f"Error saving phone {p['number']}: {e}")
            
            db.commit()
            logger.info(f"Saved {imported} contacts to database")
            
            # Notificar clientes
            socketio.emit('bulk_update', {
                'message': 'contacts_generated',
                'count': imported
            }, broadcast=True)
        
        return jsonify({
            'success': True,
            'count': len(phones),
            'saved': imported if save_to_db else 0,
            'phones': phones
        }), 200
        
    except Exception as e:
        logger.error(f"Error generating contacts: {e}")
        db.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        db.remove()


@app.route('/health', methods=['GET'])
def health_check():
    """Health check para monitoreo"""
    try:
        db = Session()
        db.execute("SELECT 1")
        db.remove()
        return jsonify({'status': 'healthy', 'timestamp': datetime.utcnow()}), 200
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({'status': 'unhealthy', 'error': str(e)}), 500


@app.route('/admin/users', methods=['GET'])
@require_role('TI')
def list_users():
    """Listar todos los usuarios (solo TI)"""
    db = Session()
    try:
        users = db.query(User).filter_by(is_active=1).all()
        user_list = []
        for user in users:
            user_list.append({
                'id': user.id,
                'username': user.username,
                'role': user.role,
                'team_name': user.team_name,
                'email': user.email,
                'last_login': user.last_login.isoformat() if user.last_login else None,
                'created_at': user.created_at.isoformat() if user.created_at else None
            })
        return jsonify(user_list), 200
    except Exception as e:
        logger.error(f"Error listing users: {e}")
        return jsonify({'error': str(e)}), 500
    finally:
        db.remove()


@app.route('/admin/users/<user_id>', methods=['DELETE'])
@require_role('TI')
def delete_user(user_id):
    """Desactivar usuario (solo TI)"""
    db = Session()
    try:
        user = db.query(User).filter_by(id=user_id).first()
        if not user:
            return jsonify({'error': 'Usuario no encontrado'}), 404
        
        # No permitir borrar al último admin
        admin_count = db.query(User).filter_by(role='TI', is_active=1).count()
        if user.role == 'TI' and admin_count <= 1:
            return jsonify({'error': 'No se puede borrar el último admin'}), 400
        
        user.is_active = 0
        db.commit()
        
        logger.info(f"User deactivated: {user.username}")
        
        return jsonify({'success': True, 'message': f'Usuario {user.username} desactivado'}), 200
    except Exception as e:
        logger.error(f"Error deleting user: {e}")
        db.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        db.remove()


if __name__ == '__main__':
    logger.info("=" * 60)
    logger.info("Starting CallManager Server")
    logger.info(f"Host: {SERVER_HOST}:{SERVER_PORT}")
    logger.info(f"Database: {DATABASE_PATH}")
    logger.info(f"Backups: {BACKUP_DIR}")
    logger.info(f"Auth enabled: {ENABLE_AUTH}")
    logger.info("=" * 60)
    logger.warning("IMPORTANT: Make sure port 5000 is open in Windows Firewall")
    logger.warning("IMPORTANT: Run server on a machine with a static IP")
    logger.warning("=" * 60)

    # Crear usuario por defecto si no existen usuarios
    try:
        db = Session()
        user_count = db.query(User).count()
        Session.remove()
        
        if user_count == 0:
            logger.info("Creating default user (admin/1234)...")
            from init_default_user import create_default_user
            create_default_user()
    except Exception as e:
        logger.warning(f"Could not create default user: {e}")

    # Crear backup inicial
    create_backup()

    # Iniciar tarea de limpieza y backup
    socketio.start_background_task(start_background_cleanup)

    # Ejecutar servidor
    socketio.run(app, host=SERVER_HOST, port=SERVER_PORT, debug=DEBUG)
