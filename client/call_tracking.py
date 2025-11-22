"""
Call Tracking System - Cliente
Gestiona el ciclo de vida de llamadas y reporta métricas al servidor.

Autor: CallManager System
Versión: 2.0
"""

import requests
import logging
import threading
from datetime import datetime
from typing import Optional, Dict, Tuple

logger = logging.getLogger(__name__)


class CallSession:
    """
    Representa una sesión de llamada activa.
    Rastrea inicio, fin y duración.
    """
    
    def __init__(self, call_id: str, contact_id: Optional[str] = None, 
                 contact_phone: Optional[str] = None):
        self.call_id = call_id
        self.contact_id = contact_id
        self.contact_phone = contact_phone
        self.start_time = datetime.now()
        self.end_time: Optional[datetime] = None
        self.duration_seconds = 0
        self.status = 'IN_PROGRESS'
    
    def end_call(self, status: str = 'COMPLETED') -> int:
        """
        Finalizar la llamada y calcular duración.
        
        Args:
            status: COMPLETED, DROPPED, NO_ANSWER, FAILED
        
        Returns:
            duration_seconds: Duración en segundos
        """
        self.end_time = datetime.now()
        self.status = status
        self.duration_seconds = int((self.end_time - self.start_time).total_seconds())
        return self.duration_seconds
    
    def get_duration(self) -> int:
        """Obtener duración actual (sin finalizar)"""
        if self.end_time:
            return self.duration_seconds
        return int((datetime.now() - self.start_time).total_seconds())
    
    def to_dict(self) -> Dict:
        """Convertir a diccionario para serializar"""
        return {
            'call_id': self.call_id,
            'contact_id': self.contact_id,
            'contact_phone': self.contact_phone,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'duration_seconds': self.duration_seconds,
            'status': self.status
        }


class CallTracker:
    """
    Gestor de rastreo de llamadas (lado cliente).
    
    Comunica con los endpoints:
    - POST /api/calls/start
    - POST /api/calls/end
    """
    
    def __init__(self, base_url: str, api_key: str = ''):
        self.base_url = base_url.rstrip('/')
        self.headers = {
            'Content-Type': 'application/json',
        }
        if api_key:
            self.headers['X-API-Key'] = api_key
        
        self.active_session: Optional[CallSession] = None
        self.session_history = []
        self.lock = threading.RLock()
        self.timer_thread: Optional[threading.Thread] = None
        self.timer_callback = None
    
    def set_timer_callback(self, callback):
        """
        Establecer callback para actualizaciones de timer.
        Útil para actualizar UI cada segundo.
        
        Args:
            callback: Función que recibe (duration_seconds, formatted_time)
        """
        self.timer_callback = callback
    
    def start_call(self, contact_id: Optional[str] = None, 
                   contact_phone: Optional[str] = None) -> Optional[str]:
        """
        Iniciar rastreo de llamada en el servidor.
        
        Args:
            contact_id: ID del contacto
            contact_phone: Número de teléfono
        
        Returns:
            call_id: ID único de la sesión, o None si error
        """
        with self.lock:
            try:
                payload = {
                    'contact_id': contact_id,
                    'contact_phone': contact_phone
                }
                
                response = requests.post(
                    f"{self.base_url}/api/calls/start",
                    json=payload,
                    headers=self.headers,
                    timeout=5
                )
                
                if response.status_code == 201:
                    data = response.json()
                    call_id = data.get('call_id')
                    
                    # Crear sesión local
                    self.active_session = CallSession(call_id, contact_id, contact_phone)
                    self.session_history.append(self.active_session)
                    
                    logger.info(f"⏱️ Llamada iniciada (ID: {call_id})")
                    
                    # Iniciar timer thread
                    self._start_timer_thread()
                    
                    return call_id
                else:
                    error_msg = response.json().get('error', response.text)
                    logger.error(f"❌ Error iniciando llamada: {error_msg}")
                    return None
            except Exception as e:
                logger.error(f"❌ Excepción al iniciar rastreo: {e}")
                return None
    
    def end_call(self, status: str = 'COMPLETED', notes: str = '') -> Optional[Dict]:
        """
        Finalizar rastreo de llamada en el servidor.
        
        Args:
            status: COMPLETED, DROPPED, NO_ANSWER, FAILED
            notes: Notas adicionales
        
        Returns:
            Diccionario con métricas (duration_seconds, new_average, etc)
        """
        with self.lock:
            if not self.active_session:
                logger.warning("⚠️ No hay llamada activa para finalizar")
                return None
            
            try:
                # Finalizar localmente
                duration = self.active_session.end_call(status)
                
                # Enviar al servidor
                payload = {
                    'call_id': self.active_session.call_id,
                    'status': status,
                    'notes': notes
                }
                
                response = requests.post(
                    f"{self.base_url}/api/calls/end",
                    json=payload,
                    headers=self.headers,
                    timeout=5
                )
                
                # Detener timer
                self._stop_timer_thread()
                
                if response.status_code == 200:
                    data = response.json()
                    logger.info(f"✅ Llamada finalizada | Duración: {duration}s | Estado: {status}")
                    
                    self.active_session = None
                    return data
                else:
                    error_msg = response.json().get('error', response.text)
                    logger.error(f"❌ Error finalizando llamada: {error_msg}")
                    self.active_session = None
                    return None
            except Exception as e:
                logger.error(f"❌ Excepción al finalizar rastreo: {e}")
                self.active_session = None
                return None
    
    def get_current_duration(self) -> int:
        """Obtener duración actual (mientras la llamada está activa)"""
        with self.lock:
            if self.active_session:
                return self.active_session.get_duration()
            return 0
    
    def format_duration(self, seconds: int) -> str:
        """Formatear segundos como HH:MM:SS"""
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{secs:02d}"
        return f"{minutes:02d}:{secs:02d}"
    
    def _start_timer_thread(self):
        """Iniciar thread que actualiza el timer cada segundo"""
        if self.timer_thread and self.timer_thread.is_alive():
            return  # Ya existe
        
        def timer_loop():
            while self.active_session:
                try:
                    duration = self.get_current_duration()
                    formatted = self.format_duration(duration)
                    
                    if self.timer_callback:
                        self.timer_callback(duration, formatted)
                    
                    threading.Event().wait(1)  # Esperar 1 segundo
                except:
                    break
        
        self.timer_thread = threading.Thread(target=timer_loop, daemon=True)
        self.timer_thread.start()
    
    def _stop_timer_thread(self):
        """Detener thread del timer"""
        # El thread se detendrá cuando active_session sea None
        if self.timer_thread:
            self.timer_thread.join(timeout=2)
    
    def get_session_history(self, limit: int = 10) -> list:
        """Obtener últimas N sesiones"""
        with self.lock:
            return [s.to_dict() for s in self.session_history[-limit:]]
    
    def get_metrics(self) -> Dict:
        """Obtener métricas de sesiones locales"""
        with self.lock:
            if not self.session_history:
                return {
                    'total_calls': 0,
                    'total_duration': 0,
                    'avg_duration': 0,
                    'longest_call': 0,
                    'shortest_call': 0
                }
            
            completed = [s for s in self.session_history if s.status == 'COMPLETED']
            durations = [s.duration_seconds for s in completed if s.duration_seconds > 0]
            
            return {
                'total_calls': len(self.session_history),
                'completed_calls': len(completed),
                'total_duration': sum(durations),
                'avg_duration': sum(durations) // len(durations) if durations else 0,
                'longest_call': max(durations) if durations else 0,
                'shortest_call': min(durations) if durations else 0
            }


# Instancia global para usar en toda la app
call_tracker: Optional[CallTracker] = None


def initialize_tracker(base_url: str, api_key: str = '') -> CallTracker:
    """
    Inicializar el tracker global.
    
    Args:
        base_url: URL base del servidor (ej: http://localhost:5000)
        api_key: Clave API para autenticación
    
    Returns:
        CallTracker inicializado
    """
    global call_tracker
    call_tracker = CallTracker(base_url, api_key)
    logger.info("📞 Call Tracker inicializado")
    return call_tracker


def get_tracker() -> CallTracker:
    """Obtener instancia del tracker global"""
    global call_tracker
    if call_tracker is None:
        raise RuntimeError("Call Tracker no inicializado. Llamar initialize_tracker() primero.")
    return call_tracker

