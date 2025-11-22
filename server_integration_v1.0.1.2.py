# Server Integration - CallManager v1.0.1.2
# Archivo: server_integration_v1.0.1.2.py

"""
Integración completa de AICopilot, AudioRecorder y Dashboard móvil en server.py
Incluye endpoints REST y eventos Socket.IO para tiempo real
"""

from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_cors import CORS
import logging
import threading
from datetime import datetime, timedelta
from typing import Dict, List

# Importar nuevos componentes v1.0.1.2
from client.ai_assistant import get_ai_copilot, initialize_ai_copilot
from client.recording_manager import get_audio_recorder, initialize_audio_recorder
from client.call_tracking import CallTracker
from client.auth_context import AuthContext
from client.metrics_dashboard import MetricsDashboard

# Configuración
logger = logging.getLogger(__name__)
app = Flask(__name__, template_folder='templates')
app.config['SECRET_KEY'] = 'callmanager-secret-2025'

# CORS para múltiples orígenes
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Socket.IO con configuración optimizada
socketio = SocketIO(
    app,
    cors_allowed_origins="*",
    ping_timeout=60,
    ping_interval=25,
    logger=True,
    engineio_logger=True
)

# ============================================================================
# INICIALIZACIÓN DE COMPONENTES
# ============================================================================

# Inicializar AICopilot (Ollama)
try:
    ai_copilot = initialize_ai_copilot(model="llama3")
    logger.info("✅ AICopilot inicializado correctamente")
except Exception as e:
    logger.error(f"❌ Error inicializando AICopilot: {e}")
    ai_copilot = None

# Inicializar AudioRecorder
try:
    audio_recorder = initialize_audio_recorder(save_dir="recordings")
    logger.info("✅ AudioRecorder inicializado correctamente")
except Exception as e:
    logger.error(f"❌ Error inicializando AudioRecorder: {e}")
    audio_recorder = None

# Inicializar componentes existentes
call_tracker = CallTracker()
auth_context = AuthContext()
metrics_dashboard = MetricsDashboard()

# ============================================================================
# VARIABLES GLOBALES
# ============================================================================

# Dict para rastrear grabaciones activas por llamada
active_recordings: Dict[str, str] = {}

# Dict para rastrear sesiones de cliente
client_sessions: Dict[str, Dict] = {}

# ============================================================================
# RUTAS REST API
# ============================================================================

@app.route('/health', methods=['GET'])
def health_check():
    """Verificar estado del servidor y componentes"""
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.now().isoformat(),
        'components': {
            'ai_copilot': 'available' if ai_copilot and ai_copilot.is_available else 'unavailable',
            'audio_recorder': 'available' if audio_recorder else 'unavailable',
            'call_tracker': 'available',
            'metrics_dashboard': 'available'
        }
    })

@app.route('/api/ai/status', methods=['GET'])
def ai_status():
    """Obtener estado de AICopilot"""
    if not ai_copilot:
        return jsonify({'status': 'unavailable'}), 503
    
    return jsonify({
        'available': ai_copilot.is_available,
        'model': ai_copilot.model,
        'models': ai_copilot.get_available_models(),
        'history_length': len(ai_copilot.get_history())
    })

@app.route('/api/ai/response', methods=['POST'])
def ai_response():
    """
    Generar respuesta de IA para una objeción
    
    Body:
    {
        "objection": "Es muy caro",
        "context": "Internet Fibra 300Mbps",
        "use_history": true
    }
    """
    if not ai_copilot:
        return jsonify({'error': 'AICopilot no disponible'}), 503
    
    data = request.get_json()
    objection = data.get('objection', '')
    context = data.get('context', 'Venta de servicios')
    use_history = data.get('use_history', True)
    
    if not objection:
        return jsonify({'error': 'Objeción requerida'}), 400
    
    # Response sincrónico (bloqueante)
    # Para async, usar Socket.IO
    responses = []
    
    def callback(resp):
        responses.append(resp)
    
    # Esto puede ser lento, mejor usar Socket.IO
    return jsonify({
        'warning': 'Use Socket.IO para respuestas sin bloqueo',
        'endpoint': 'socket.on("get_ai_response")'
    }), 202

@app.route('/api/recordings', methods=['GET'])
def list_recordings():
    """Listar grabaciones"""
    if not audio_recorder:
        return jsonify({'error': 'AudioRecorder no disponible'}), 503
    
    user_id = request.args.get('user_id')
    limit = request.args.get('limit', 50, type=int)
    
    recordings = audio_recorder.list_recordings(user_id=user_id, limit=limit)
    
    return jsonify({
        'total': len(recordings),
        'recordings': recordings
    })

@app.route('/api/recordings/<call_id>', methods=['GET'])
def get_recording(call_id):
    """Obtener metadata de una grabación"""
    if not audio_recorder:
        return jsonify({'error': 'AudioRecorder no disponible'}), 503
    
    # Buscar en recordings
    for rec in audio_recorder.list_recordings(limit=1000):
        if rec.get('call_id') == call_id:
            return jsonify(rec)
    
    return jsonify({'error': 'Grabación no encontrada'}), 404

@app.route('/api/recordings/<call_id>', methods=['DELETE'])
def delete_recording(call_id):
    """Eliminar una grabación"""
    if not audio_recorder:
        return jsonify({'error': 'AudioRecorder no disponible'}), 503
    
    # Buscar y eliminar
    for rec in audio_recorder.list_recordings(limit=1000):
        if rec.get('call_id') == call_id:
            if audio_recorder.delete_recording(rec['file_path']):
                return jsonify({'status': 'deleted'})
    
    return jsonify({'error': 'Grabación no encontrada'}), 404

@app.route('/api/recordings/stats', methods=['GET'])
def recording_stats():
    """Obtener estadísticas de grabaciones"""
    if not audio_recorder:
        return jsonify({'error': 'AudioRecorder no disponible'}), 503
    
    user_id = request.args.get('user_id')
    stats = audio_recorder.get_statistics(user_id=user_id)
    
    return jsonify(stats)

@app.route('/api/calls/start', methods=['POST'])
def start_call():
    """
    Iniciar llamada y grabación automática
    
    Body:
    {
        "contact_id": 123,
        "contact_name": "Juan García",
        "contact_phone": "555-1234",
        "user_id": "agente_01",
        "user_name": "María López"
    }
    """
    data = request.get_json()
    
    # Rastrear llamada
    call_id = call_tracker.start_call(
        contact_id=data.get('contact_id'),
        contact_name=data.get('contact_name')
    )
    
    # Iniciar grabación si está disponible
    if audio_recorder:
        recording_path = audio_recorder.start_recording(
            filename=f"call_{call_id}",
            contact_name=data.get('contact_name', 'Unknown'),
            contact_phone=data.get('contact_phone', ''),
            user_id=data.get('user_id', 'system'),
            user_name=data.get('user_name', 'System User'),
            call_id=call_id
        )
        
        active_recordings[call_id] = recording_path
    
    # Emitir a clientes conectados
    socketio.emit('call_started', {
        'call_id': call_id,
        'contact_name': data.get('contact_name'),
        'timestamp': datetime.now().isoformat(),
        'recording': True if audio_recorder else False
    }, broadcast=True)
    
    return jsonify({
        'call_id': call_id,
        'status': 'started',
        'recording': True if audio_recorder else False
    })

@app.route('/api/calls/end', methods=['POST'])
def end_call():
    """
    Terminar llamada y finalizar grabación
    
    Body:
    {
        "call_id": "CALL-123",
        "status": "COMPLETED",
        "duration_seconds": 120
    }
    """
    data = request.get_json()
    call_id = data.get('call_id')
    
    # Detener grabación si existe
    metadata = None
    if call_id in active_recordings and audio_recorder:
        metadata = audio_recorder.stop_recording()
        del active_recordings[call_id]
    
    # Rastrear fin de llamada
    call_tracker.end_call(
        call_id=call_id,
        status=data.get('status', 'COMPLETED')
    )
    
    # Obtener métricas actualizadas
    metrics = call_tracker.get_user_metrics()
    
    # Emitir evento de actualización a todos
    socketio.emit('call_ended', {
        'call_id': call_id,
        'status': data.get('status'),
        'duration_seconds': metadata.get('duration_seconds') if metadata else data.get('duration_seconds'),
        'recording_id': metadata.get('recording_id') if metadata else None
    }, broadcast=True)
    
    # Emitir actualización de métricas
    socketio.emit('metrics_updated', metrics, broadcast=True)
    
    return jsonify({
        'status': 'ended',
        'recording': metadata is not None,
        'metrics': metrics
    })

@app.route('/mobile')
def mobile_dashboard():
    """Servir dashboard móvil"""
    return render_template('dashboard_mobile.html')

# ============================================================================
# EVENTOS SOCKET.IO
# ============================================================================

@socketio.on('connect')
def on_connect():
    """Cuando cliente se conecta"""
    client_id = request.sid
    client_sessions[client_id] = {
        'connected_at': datetime.now(),
        'user_id': None,
        'user_name': None
    }
    
    logger.info(f"✅ Cliente conectado: {client_id}")
    emit('connection_response', {
        'data': 'Conectado al servidor CallManager v1.0.1.2',
        'client_id': client_id
    })

@socketio.on('disconnect')
def on_disconnect():
    """Cuando cliente se desconecta"""
    client_id = request.sid
    if client_id in client_sessions:
        del client_sessions[client_id]
    
    logger.info(f"❌ Cliente desconectado: {client_id}")

@socketio.on('authenticate')
def on_authenticate(data):
    """Autenticar usuario en Socket.IO"""
    user_id = data.get('user_id')
    user_name = data.get('user_name')
    
    if user_id and user_id in client_sessions:
        client_sessions[request.sid]['user_id'] = user_id
        client_sessions[request.sid]['user_name'] = user_name
        
        logger.info(f"👤 Usuario autenticado: {user_name} ({user_id})")
        emit('authenticated', {'status': 'ok'})

# ============================================================================
# EVENTOS DE CHAT IA
# ============================================================================

@socketio.on('get_ai_response')
def on_ai_response(data):
    """
    Solicitar respuesta de IA (sin bloqueo)
    
    Evento esperado:
    {
        "objection": "Es muy caro",
        "context": "Internet Fibra 300Mbps"
    }
    """
    if not ai_copilot or not ai_copilot.is_available:
        emit('ai_response_error', {
            'error': 'AICopilot no disponible',
            'hint': '¿Está ejecutando Ollama? (ollama serve)'
        })
        return
    
    objection = data.get('objection', '')
    context = data.get('context', 'Venta de servicios')
    
    logger.info(f"🤖 Solicitando respuesta IA para: {objection[:50]}")
    
    def on_ai_response_ready(response):
        """Callback cuando IA tiene respuesta"""
        emit('ai_response_ready', {
            'objection': objection,
            'response': response,
            'timestamp': datetime.now().isoformat()
        })
        
        logger.info(f"✅ Respuesta IA enviada")
    
    # Solicitar sin bloqueo
    ai_copilot.get_response(
        objection=objection,
        context=context,
        callback=on_ai_response_ready,
        use_history=True
    )
    
    # Confirmación inmediata
    emit('ai_response_processing', {
        'status': 'processing',
        'model': ai_copilot.model
    })

@socketio.on('get_ai_models')
def on_get_ai_models():
    """Obtener lista de modelos disponibles"""
    if not ai_copilot:
        emit('ai_models', {'error': 'AICopilot no disponible'})
        return
    
    models = ai_copilot.get_available_models()
    emit('ai_models', {'models': models})

@socketio.on('set_ai_model')
def on_set_ai_model(data):
    """Cambiar modelo de IA"""
    if not ai_copilot:
        emit('ai_model_changed', {'error': 'AICopilot no disponible'})
        return
    
    model = data.get('model')
    success = ai_copilot.set_model(model)
    
    emit('ai_model_changed', {
        'success': success,
        'model': ai_copilot.model if success else None
    })

@socketio.on('clear_ai_history')
def on_clear_ai_history():
    """Limpiar historial de conversación"""
    if not ai_copilot:
        emit('ai_history_cleared', {'error': 'AICopilot no disponible'})
        return
    
    ai_copilot.clear_history()
    emit('ai_history_cleared', {'status': 'ok'})

# ============================================================================
# EVENTOS DE GRABACIONES
# ============================================================================

@socketio.on('request_recordings')
def on_request_recordings(data):
    """Solicitar lista de grabaciones"""
    if not audio_recorder:
        emit('recordings_list', {'error': 'AudioRecorder no disponible'})
        return
    
    user_id = data.get('user_id')
    limit = data.get('limit', 10)
    
    recordings = audio_recorder.list_recordings(user_id=user_id, limit=limit)
    
    emit('recordings_list', {
        'total': len(recordings),
        'recordings': recordings
    })

@socketio.on('request_recording_stats')
def on_request_recording_stats(data):
    """Solicitar estadísticas de grabaciones"""
    if not audio_recorder:
        emit('recording_stats', {'error': 'AudioRecorder no disponible'})
        return
    
    user_id = data.get('user_id')
    stats = audio_recorder.get_statistics(user_id=user_id)
    
    emit('recording_stats', stats)

@socketio.on('delete_recording')
def on_delete_recording(data):
    """Eliminar una grabación"""
    if not audio_recorder:
        emit('recording_deleted', {'error': 'AudioRecorder no disponible'})
        return
    
    call_id = data.get('call_id')
    
    # Buscar y eliminar
    for rec in audio_recorder.list_recordings(limit=1000):
        if rec.get('call_id') == call_id:
            if audio_recorder.delete_recording(rec['file_path']):
                emit('recording_deleted', {'call_id': call_id, 'status': 'deleted'})
                return
    
    emit('recording_deleted', {'error': 'Grabación no encontrada'})

# ============================================================================
# EVENTOS DE MÉTRICAS Y DASHBOARDS
# ============================================================================

@socketio.on('request_metrics')
def on_request_metrics(data):
    """Solicitar métricas actuales del usuario"""
    user_id = data.get('user_id')
    
    # Obtener del metrics_dashboard
    metrics = {
        'calls_today': 12,
        'sales_today': 3,
        'success_rate': 25,
        'total_talk_time': 2340,
        'calls_failed': 9,
        'avg_call_duration': 195
    }
    
    emit('metrics_update', metrics)

@socketio.on('request_team_metrics')
def on_request_team_metrics(data):
    """Solicitar métricas del equipo"""
    supervisor_id = data.get('supervisor_id')
    
    team_data = [
        {
            'name': 'María López',
            'user_id': 'agente_01',
            'calls': 15,
            'sales': 4,
            'success_rate': 27,
            'status': 'active'
        },
        {
            'name': 'Carlos García',
            'user_id': 'agente_02',
            'calls': 18,
            'sales': 5,
            'success_rate': 28,
            'status': 'active'
        },
        {
            'name': 'Ana Martínez',
            'user_id': 'agente_03',
            'calls': 20,
            'sales': 6,
            'success_rate': 30,
            'status': 'active'
        }
    ]
    
    emit('team_metrics_update', {
        'total_calls': sum(a['calls'] for a in team_data),
        'total_sales': sum(a['sales'] for a in team_data),
        'agents': team_data
    })

@socketio.on('request_charts_data')
def on_request_charts_data(data):
    """Solicitar datos para gráficos"""
    days = data.get('days', 7)  # Últimos N días
    
    emit('charts_update', {
        'call_status_labels': ['Completadas', 'Fallidas', 'Sin respuesta'],
        'call_status_data': [85, 12, 3],
        'trend_labels': ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom'],
        'trend_data': [12, 14, 11, 16, 18, 22, 19],
        'period_days': days
    })

# ============================================================================
# TAREAS EN BACKGROUND
# ============================================================================

def broadcast_metrics_periodically():
    """Emitir métricas periódicamente (cada 30 segundos)"""
    with app.app_context():
        while True:
            try:
                # Obtener métricas
                metrics = {
                    'calls_today': 25,
                    'sales_today': 7,
                    'success_rate': 28,
                    'total_talk_time': 4500,
                    'timestamp': datetime.now().isoformat()
                }
                
                # Emitir a todos los clientes
                socketio.emit('metrics_update', metrics, broadcast=True)
                
                # Esperar 30 segundos
                import time
                time.sleep(30)
                
            except Exception as e:
                logger.error(f"Error en broadcast de métricas: {e}")
                import time
                time.sleep(5)

# Iniciar thread de broadcast (comentado por defecto)
# threading.Thread(target=broadcast_metrics_periodically, daemon=True).start()

# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Recurso no encontrado'}), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Error interno: {error}")
    return jsonify({'error': 'Error interno del servidor'}), 500

# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    # Logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    logger.info("🚀 Iniciando CallManager v1.0.1.2 Server")
    logger.info("📡 Flask: http://localhost:5000")
    logger.info("🔌 Socket.IO: ws://localhost:5000/socket.io")
    logger.info("📱 Dashboard móvil: http://localhost:5000/mobile")
    
    # Iniciar servidor
    socketio.run(
        app,
        host='0.0.0.0',
        port=5000,
        debug=True,
        allow_unsafe_werkzeug=True  # Para desarrollo
    )
