from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, emit
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from sqlalchemy import create_engine, Column, String, Text, DateTime, Integer, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.pool import Pool
from datetime import datetime, timedelta
import json
import os
import logging
import shutil
from datetime import datetime as dt_now
import re
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
    last_called_time = Column(DateTime)
    last_visibility_time = Column(DateTime, default=dt_now, index=True)  # Cuándo se vio por última vez
    editors_history = Column(Text, default="[]")
    locked_by = Column(String, index=True)
    locked_until = Column(DateTime, index=True)
    reminder_time = Column(DateTime)
    created_at = Column(DateTime, default=dt_now, index=True)
    updated_at = Column(DateTime, default=dt_now, onupdate=dt_now, index=True)
    version = Column(Integer, default=1)  # Versión para optimistic locking (incrementa con cada update)


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
            contact.last_visibility_time = contact.created_at or dt_now.now()
        
        now = dt_now.now()
        
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
        
        timestamp = dt_now.now().strftime("%Y%m%d_%H%M%S")
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
        cutoff_time = dt_now.now().timestamp() - (BACKUP_KEEP_DAYS * 86400)
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
            delta = relativedelta(dt_now.now(), r.last_visibility_time)
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
            Contact.locked_until < dt_now.utcnow(),
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
                    obj.updated_at = dt_now.utcnow()
                    # ⭐ NUEVO: Registrar que se vio (reset de visibilidad)
                    obj.last_visibility_time = dt_now.utcnow()
                    
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
                        last_visibility_time=dt_now.utcnow(),  # ⭐ NUEVO: Inicializar visibilidad
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
            if obj.locked_until and obj.locked_until > dt_now.utcnow():
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
                    'ts': dt_now.utcnow().isoformat()
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
            obj.last_called_time = dt_now.utcnow()
            obj.updated_at = dt_now.utcnow()
            db.commit()
            logger.info(f"Contact {cid} updated by {user}")

            socketio.emit('contact_updated', {
                'id': cid,
                'fields': fields,
                'user': user,
                'ts': dt_now.utcnow().isoformat(),
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
            if obj.locked_until and obj.locked_until > dt_now.utcnow():
                logger.warning(f"Lock denied for {cid}: already locked by {obj.locked_by}")
                emit('lock_denied', {
                    'id': cid,
                    'locked_by': obj.locked_by,
                    'locked_until': obj.locked_until.isoformat(),
                    'message': f'Bloqueado por {obj.locked_by}'
                })
                return

        obj.locked_by = user
        obj.locked_until = dt_now.utcnow() + timedelta(minutes=dur)
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
                'ts': dt_now.utcnow().isoformat()
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

    # Crear backup inicial
    create_backup()

    # Iniciar tarea de limpieza y backup
    socketio.start_background_task(start_background_cleanup)

    # Ejecutar servidor
    socketio.run(app, host=SERVER_HOST, port=SERVER_PORT, debug=DEBUG)
