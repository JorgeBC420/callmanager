"""
CallManager Client Module
Módulo principal del cliente de CallManager

Componentes:
- AI Assistant (Chat IA con Ollama)
- Recording Manager (Grabación automática)
- Call Manager App (Interfaz gráfica)
- Call Tracking (Rastreo de tiempo)
- Metrics Dashboard (Dashboards de métricas)
- Authentication (Gestión de roles y autenticación)

Versión: 1.0.1.2
"""

__version__ = "1.0.1.2"
__author__ = "CallManager System"
__date__ = "2025-11-22"

# Importar componentes principales
try:
    from .ai_assistant import AICopilot, initialize_ai_copilot, get_ai_copilot
except ImportError:
    pass

try:
    from .recording_manager import AudioRecorder, initialize_audio_recorder, get_audio_recorder
except ImportError:
    pass

try:
    from .call_tracking import CallTracker
except ImportError:
    pass

try:
    from .auth_context import AuthContext
except ImportError:
    pass

__all__ = [
    "AICopilot",
    "initialize_ai_copilot",
    "get_ai_copilot",
    "AudioRecorder",
    "initialize_audio_recorder",
    "get_audio_recorder",
    "CallTracker",
    "AuthContext",
]
